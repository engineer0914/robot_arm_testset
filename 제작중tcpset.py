# tcp를 먼저 세팅합니다.

import rbpodo as rb
import numpy as np
import time
import robotarm_functions as ra_fs

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
    robot.set_speed_bar(rc, 0.7)

    point_tcp = np.array([0, 0, 0, 0, 0, 0])

    robot.set_tcp_info(rc, point_tcp) # tcp는 설정후 다음 스크립트에서 제대로 적용된다.

    robot.set_tcp_info(rc, point_tcp) # tcp는 설정후 다음 스크립트에서 제대로 적용된다.

    pos = ra_fs.get_tcp(rc, robot)
    print(pos[1])


    # # tcp 원하는 값 배열 여기에 입력

    # point_tcp_wish = np.array([0, -200, 0, 0, 0, 0])

    # # tcp txt 읽어오기

    # filename = "point_tcp.txt"

    # point_tcp = np.loadtxt(filename)
    # print("\n파일에서 불러온 point_tcp:")
    # print(point_tcp)

    # # 각 배열별로 확인



    # # 값이 다르다면 덮어쓰기


    # # 같다면 무시


    # # 이후 txt로 설정된 값으로 tcp 세팅후 종료

    # robot.set_tcp_info(rc, point_tcp) # tcp는 설정후 다음 스크립트에서 제대로 적용된다.

    # # 확인

    # pos = ra_fs.get_tcp(rc, robot)
    # print(pos[1])




if __name__ == "__main__":
    _main()
