# 조인트를 읽고, txt파일에 씁니다. 나중에 txt파일에서 위치를 불러와서 사용합니다.

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

    joint = ra_fs.read_joint(rc, robot)
    print(joint)

    robot.set_user_coordinate(rc, 0, joint)

    # robot.set_tcp_info(rc, np.array([0, 0, 0, 0, 0, 0]))

    # ra_fs.robot_move_startpoint(rc, robot) # 시작점 이동

    # pos = ra_fs.get_tcp(rc, robot)
    # print(pos[1])


    # 저장할 파일 이름
    filename = "point_start.txt"

    # 예시로 관절 초기값들
    data = ra_fs.read_joint(rc, robot)

    # 1️⃣ 파일 존재 확인 및 저장
    if not os.path.exists(filename):
        print(f"'{filename}' 파일이 없어서 새로 생성합니다.")
        with open(filename, "w") as f:
            np.savetxt(f, [data], fmt="%.6f")
    else:
        print(f"'{filename}' 파일이 존재합니다. 데이터 덮어쓰기.")
        with open(filename, "w") as f:
            np.savetxt(f, [data], fmt="%.6f")

    print("데이터 저장 완료 ✅")

    # 2️⃣ 파일에서 불러오기 (jointarray에 저장)
    jointarray = np.loadtxt(filename)
    print("\n파일에서 불러온 jointarray:")
    print(jointarray)





if __name__ == "__main__":
    _main()









