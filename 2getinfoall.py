# 컨트롤 박스 상태 읽어오는 다양한 함수
# 하지만 다이렉트 연결만 가능하다.

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
    print(f"")
    print(f"1. 컨트롤 박스 정보")
    print(f"")

    res, cb_info = robot.get_control_box_info(rc)
    if res.is_success():
        print(f"")
        print(f"컨트롤 박스 정보: {cb_info}")

    res, cb_info = robot.get_robot_state(rc)
    if res.is_success():
        print(f"")
        print(f"로봇 상태: {cb_info}")


    print(f"")
    print(f"tcp 정보 얻기")
    print(robot.get_tcp_info(rc))


    print(f"")
    print(f"tfc 정보 얻기")
    print(robot.get_tfc_info(rc))


    # foward kinematics 계산

    print(f"------------------------------------")
    print(f"")
    print(f"2. 정기구학 계산")
    print(f"")

    pnt = np.zeros((6,))
    robot.calc_fk_tcp(rc, pnt, 0, 0, 0, 0, 0, 0)
    print(pnt)

    [res, pnt] = robot.calc_fk_tcp(rc, np.zeros((6,)))
    print(pnt)


    # 시스템 정보 얻기

    print(f"------------------------------------")
    print(f"")
    print(f"3. 시스템 정보 얻기 = 1번 조인트 각도")
    print(f"")

    [_, out] = robot.get_system_variable(rc, rb.SystemVariable.SD_J1_ANG)
    rc = rc.error().throw_if_not_empty()

    print(out)

    print(f"")
    print(f"3. 시스템 정보 얻기 = 1번 조인트 온도")
    print(f"")
    
    [_, out] = robot.get_system_variable(rc, rb.SystemVariable.SD_TEMPERATURE_MC0)
    rc = rc.error().throw_if_not_empty()
    
    print(out)
    
    print(f"")
    print(f"4. 시스템 정보 얻기 = 비상정지 상태 1이면 해제, 0이면 비상정지 눌림")
    print(f"")
    if(out == 1):
        print("해제 상태")
        
    else:
        print("비상 정지 상태")


    [_, out] = robot.get_system_variable(rc, rb.SystemVariable.SD_EMG_BUTTON_STATE)
    print(out)


if __name__ == "__main__":
    _main()
