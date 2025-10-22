# txt에서 읽고 난 후의 값을 초기값으로 유저 위치 설정하는 코드입니다.

import os
import rbpodo as rb
import robotarm_functions as ra_fs
import numpy as np

# ====== 메인 루틴 ======
def _main():
    # 파일에서 IP 주소 읽기
    robot_ip = ra_fs.read_robot_ip()
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
    # robot.set_operation_mode(rc, rb.OperationMode.Simulation)
    robot.set_speed_bar(rc, 0.7)

    # 저장할 파일 이름
    filename = "point_start.txt"

    jointarray = np.loadtxt(filename)
    print("\n파일에서 불러온 jointarray:")
    print(jointarray)

    robot.set_user_coordinate(rc, 0, jointarray)

    # robot.set_tcp_info(rc, np.array([0, 0, 0, 0, 0, 0]))

    # ra_fs.robot_move_startpoint(rc, robot) # 시작점 이동

    # pos = ra_fs.get_tcp(rc, robot)
    # print(pos[1])


if __name__ == "__main__":
    _main()


