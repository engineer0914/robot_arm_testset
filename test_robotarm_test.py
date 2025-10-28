# 로봇팔의 테스트 코드
# 1.컨트롤 박스 정보 출력
# 2.각 관절별 전후 n도씩 이동
# 3.공압 그리퍼 동작 테스트

import rbpodo as rb
import numpy as np
import time

# ====== 로봇 IP 읽기 ======
def read_robot_ip(filename="IP_robotarm.txt"):
    """IP_robotarm.txt 파일에서 로봇 IP 주소를 읽어옵니다."""
    try:
        with open(filename, 'r') as file:
            ip_address = file.read().strip()
            return ip_address
    except FileNotFoundError:
        print(f"Error: {filename} 파일을 찾을 수 없습니다.")
        return None
    except Exception as e:
        print(f"파일 읽기 오류: {e}")
        return None


# ====== 그리퍼 제어 함수 ======
def grip(command, robot, rc):
    """그리퍼 제어: 'grab' 또는 'release'"""
    try:
        if command == "release":
            print("🔹 그리퍼: 릴리즈 동작")
            robot.set_dout_bit_combination(rc, 0, 3, 1, rb.Endian.LittleEndian)
            time.sleep(0.1)
            robot.set_dout_bit_combination(rc, 0, 3, 0, rb.Endian.LittleEndian)

        elif command == "grab":
            print("🔹 그리퍼: 집기 동작")
            robot.set_dout_bit_combination(rc, 0, 3, 2, rb.Endian.LittleEndian)
            time.sleep(0.1)
            robot.set_dout_bit_combination(rc, 0, 3, 0, rb.Endian.LittleEndian)
    except Exception as e:
        print(f"그리퍼 제어 오류: {e}")


# ====== 메인 루틴 ======
def _main():
    # 파일에서 IP 주소 읽기
    robot_ip = read_robot_ip()
    if robot_ip is None:
        print("로봇 IP 주소를 읽을 수 없어 프로그램을 종료합니다.")
        return

    print(f"\n✅ 로봇 IP: {robot_ip}")
    ROBOT_IP = robot_ip

    # 로봇 연결
    robot = rb.Cobot(ROBOT_IP)
    rc = rb.ResponseCollector()
    
    # 모드 및 속도 설정
    robot.set_operation_mode(rc, rb.OperationMode.Real)
    robot.set_speed_bar(rc, 0.5)

    print(f"------------------------------------")
    print(f"\n1️⃣ 컨트롤 박스 정보\n")

    res, cb_info = robot.get_control_box_info(rc)
    if res.is_success():
        print(f"컨트롤 박스 정보: {cb_info}\n")

    # 조인트 각도 읽기
    joint_angles = []
    for i in range(6):  # J0 ~ J5
        _, out = robot.get_system_variable(rc, getattr(rb.SystemVariable, f"SD_J{i}_ANG"))
        rc = rc.error().throw_if_not_empty()
        joint_angles.append(out)

    joint_array = np.array(joint_angles, dtype=float)
    print(f"현재 조인트 각도: {joint_array}\n")

    # 테스트 파라미터
    step = 5
    acc = 200
    vel = 200

    # ====== 각 조인트 순차 테스트 ======
    for i in range(6):
        try:
            print(f"\n=== 🔸 Joint {i} 테스트 시작 ===")

            robot.flush(rc)
            original_pos = joint_array.copy()

            # 1️⃣ -3도 이동
            down_pos = original_pos.copy()
            down_pos[i] -= 3
            print(f"Joint {i} -{step}° -3도 이동 중...")
            robot.move_j(rc, down_pos, 200, 400)
            if robot.wait_for_move_started(rc, 0.1).type() == rb.ReturnType.Success:
                robot.wait_for_move_finished(rc)
            rc.error().throw_if_not_empty()

            # 2️⃣ +3도 이동 (원위치로 복귀)
            up_pos = original_pos.copy()
            up_pos[i] += 3
            print(f"Joint {i} +{step}° +3도 이동 중...")
            robot.move_j(rc, up_pos, 200, 400)
            if robot.wait_for_move_started(rc, 0.1).type() == rb.ReturnType.Success:
                robot.wait_for_move_finished(rc)
            rc.error().throw_if_not_empty()

            # 3️⃣ 다시 원래 위치로 복귀
            print(f"Joint {i} 원위치 복귀 중...")
            robot.move_j(rc, original_pos, 200, 400)
            if robot.wait_for_move_started(rc, 0.1).type() == rb.ReturnType.Success:
                robot.wait_for_move_finished(rc)
            rc.error().throw_if_not_empty()

        except Exception as e:
            print(f"⚠️ 로봇 제어 오류 (Joint {i}): {e}")
            try:
                robot.stop(rc)  # 안전 정지
            except:
                pass
        finally:
            time.sleep(0.5)  # 관절 간 안전 간격

    print("\n✅ 모든 조인트 테스트 완료.")

    try:    
        # ====== 그리퍼 테스트 (각 관절 테스트 후 3회) ======
        for j in range(3):
            print(f"  ➜ 그리퍼 테스트 {j+1}/3")
            grip("grab", robot, rc)
            time.sleep(0.1)
            grip("release", robot, rc)
            time.sleep(0.1)
    except Exception as e:
        print(f"⚠️ 로봇 제어 오류 (Joint {i}): {e}")
        try:
            robot.stop(rc)  # 안전 정지
        except:
            pass
    finally:
        time.sleep(0.5)  # 관절 간 안전 간격
        
    print("\n✅ 공압 동작 테스트 완료.")

if __name__ == "__main__":
    _main()
