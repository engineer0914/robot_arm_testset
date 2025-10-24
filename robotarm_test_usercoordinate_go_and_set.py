# 시작지점 관절을 txt에서 읽어오고, move j로 움직이고 그위치에 tcp를 수정한뒤 그 위치를 유저 0 기준 좌표로 선정하는 코드입니다.

import numpy as np
import robotarm_functions as ra_fs
import rbpodo as rb

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

    filename = "point_ready.txt"

    jointarray = np.loadtxt(filename)
    # print("\n파일에서 불러온 jointarray:")
    # print(jointarray)

    # ra_fs.robot_move_startpoint(rc, robot) # 시작점 이동

    robot.move_j(rc, jointarray, 100, 100)
    if robot.wait_for_move_started(rc, 0.5).is_success():
        robot.wait_for_move_finished(rc)
    rc.error().throw_if_not_empty()

    point_tcp = np.array([-45, -70, 15, 0, 0, 0]) # tcp 위치 수정

    robot.set_tcp_info(rc, point_tcp) # tcp는 설정후 다음 스크립트에서 제대로 적용된다.

    robot.set_tcp_info(rc, point_tcp) # tcp는 설정후 다음 스크립트에서 제대로 적용된다.

    pos = ra_fs.get_tcp(rc, robot)
    print(pos[1])

    robot.set_user_coordinate(rc, 0, pos[1])

if __name__ == "__main__":
    _main()


