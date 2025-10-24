# 수동 조정된 각 6개의 관절 값을 읽어오는 코드입니다.
# show 10파일에 보면 6개의 관절 위치가 적힌 리스트가 있을텐데
# 그부분에 복붙하기 쉽기 위해 만든 코드입니다.

import rbpodo as rb
import numpy as np

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


def _main():
    # 파일에서 IP 주소 읽기
    robot_ip = read_robot_ip()
    if robot_ip is None:
        print("로봇 IP 주소를 읽을 수 없어 프로그램을 종료합니다.")
        return

    print(f"로봇 IP: {robot_ip}")
    ROBOT_IP = robot_ip

    robot = rb.Cobot(ROBOT_IP)
    rc = rb.ResponseCollector()

    # 컨트롤 박스 정보
    print(f"------------------------------------")
    print(f"\n1. 컨트롤 박스 정보\n")

    res, cb_info = robot.get_control_box_info(rc)
    if res.is_success():
        print(f"컨트롤 박스 정보: {cb_info}\n")

    # 조인트 각도 읽기
    joint_angles = []
    for i in range(6):  # J0 ~ J5
        _, out = robot.get_system_variable(rc, getattr(rb.SystemVariable, f"SD_J{i}_ANG"))
        rc = rc.error().throw_if_not_empty()
        joint_angles.append(out)

    # 수평 출력 [0,0,0,0,0,0]
    # print(f"[{','.join(str(angle) for angle in joint_angles)}]")
    print(f"{' '.join(str(angle) for angle in joint_angles)}")


if __name__ == "__main__":
    _main()
