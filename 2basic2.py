# 로봇팔 IP를 txt에 적어두고, 여기서 읽어와서 참고해서 단순 동작 테스트 하는 코드

import rbpodo as rb
import numpy as np
import os

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
    
    try:
        robot = rb.Cobot(robot_ip)
        rc = rb.ResponseCollector()

        robot.set_operation_mode(rc, rb.OperationMode.Simulation)
        robot.set_speed_bar(rc, 0.5)

        robot.flush(rc)

        robot.move_j(rc, np.array([0, 0, 0, 0, 0, 90]), 200, 400)
        if robot.wait_for_move_started(rc, 0.1).type() == rb.ReturnType.Success:
            robot.wait_for_move_finished(rc)
        rc.error().throw_if_not_empty()
    except Exception as e:
        print(f"로봇 제어 오류: {e}")
    finally:
        pass

if __name__ == "__main__":
    _main()