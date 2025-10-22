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

    # robot.set_tcp_info(rc, np.array([0, 0, 0, 0, 0, 0]))

    ra_fs.robot_move_startpoint(rc, robot) # 시작점 이동

    pos = robot.get_tcp_info(rc)
    print(pos[1])

    # robot.set_user_coordinate(rc, 0, pos[1])

if __name__ == "__main__":
    _main()
