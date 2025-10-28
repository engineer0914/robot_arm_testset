# 로봇팔을 지정한 위치에 유저 좌표계로 기준 0,0,0을 설정하고,
# 이를 기준으로 동작합니다
# 그리고 특정 각도로 진입이 필요할시 기준을 툴 기준으로 바꿔서 진입합니다.

import socket
import rbpodo as rb
import numpy as np

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

def robot_move_linear(rc, robot, target_info):

    vel = target_info[2]
    acc = target_info[3]
    tool_vel = target_info[4]
    tool_acc = target_info[5]

    try:
        print("\n=== 🔸 툴플랜지 선형 움직임 ===")

        robot.move_l_rel(rc, target_info[0], vel, acc, rb.ReferenceFrame.Base)
        if robot.wait_for_move_started(rc, 0.5).is_success():
            robot.wait_for_move_finished(rc)
        rc.error().throw_if_not_empty()

        robot.move_l_rel(rc, target_info[1], tool_vel, tool_acc, rb.ReferenceFrame.Tool)
        if robot.wait_for_move_started(rc, 0.5).is_success():
            robot.wait_for_move_finished(rc)
        rc.error().throw_if_not_empty()
        
    except Exception as e:
        print(f"⚠️ 툴플랜지 이동 오류: {e}")
        try:
            robot.stop(rc)
        except:
            pass

def robot_move_startpoint(rc, robot):

    acc = 200
    vel = 200

    try:
        print("\n=== origin point move ===")

        robot.move_j(rc, np.array([0, 0, 90, 0, 90, 0]), vel, acc)
        if robot.wait_for_move_started(rc, 0.5).is_success():
            robot.wait_for_move_finished(rc)
        rc.error().throw_if_not_empty()
        
    except Exception as e:
        print(f"⚠️ origin 이동 오류: {e}")
        try:
            robot.stop(rc)
        except:
            pass

def get_cb_id(rc, robot):
    """컨트롤 박스 ID를 반환합니다."""
    print(f"------------------------------------")
    print(f"\n 컨트롤 박스 정보\n")

    res, cb_info = robot.get_control_box_info(rc)
    if res.is_success():
        print(f"컨트롤 박스 정보: {cb_info}\n")

    return

def get_tcp(rc, robot):
    pos = robot.get_tcp_info(rc)
    return pos

def get_tfc(rc, robot):
    pos = robot.get_tfc_info(rc)
    return pos

# ====== 메인 루틴 ======
def _main():

    linear_xyz = [
            np.array([100, 0, 0, 0, 0, 0]),   #where from with start angle
            np.array([0, -100, 0, 0, 0, 0]),   # where to direct move distance
            np.array([0, 0, 100, 0, 0, 0]),   # where to direct move distance
        ]

    rot_xyz = [
            np.array([0, 0, 0, 45, 0, 0]),   #where from with start angle
            np.array([0, 0, 0, 0, 45, 0]),   # where to direct move distance
            np.array([0, 0, 0, 0, 0, 45]),   # where to direct move distance
        ]

    target_info = [
            np.array([0, 0, 0, 45, 0, 0]),   #where from with start angle
            np.array([0, -100, 0, 0, 0, 0]),   # where to direct move distance
            200, # 시작지점까지 이동시 velocity
            200, # 시작지점까지 이동시 acceleration
            200, # 툴 직선 이동시 velocity
            200, # 툴 직선 이동시 acceleration
        ]

    # 파일에서 IP 주소 읽기
    robot_ip = read_robot_ip()
    if robot_ip is None:
        print("로봇 IP 주소를 읽을 수 없어 프로그램을 종료합니다.")
        return

    print(f"\n✅ 로봇 IP: {robot_ip}")
    ROBOT_IP = robot_ip
    PORT = 5000

    # 소켓 연결
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((ROBOT_IP, PORT))

    # 로봇 연결
    robot = rb.Cobot(ROBOT_IP)
    rc = rb.ResponseCollector()

    # 모드 및 속도 설정
    robot.set_operation_mode(rc, rb.OperationMode.Real)
    # robot.set_operation_mode(rc, rb.OperationMode.Simulation)

    robot.set_speed_bar(rc, 0.7)



    def send_command(command):
        client_socket.sendall(command.encode())
        return client_socket.recv(1024).decode()

    def wait_for_motion():
        while True:
            data = client_socket.recv(1024).decode()
            if "info[motion_changed][0]" in data:
                break
            print("로봇이 이동 중입니다. 잠시만 기다려주세요...")


    send_command(f'move_l_rel(pnt[0, 0, 0, 30, 0, 0], 200, 200, 2)')
    wait_for_motion()

    send_command(f'')
    wait_for_motion()

    # robot.shutdown(rc, True)
    




if __name__ == "__main__":
    _main()










    # send_command(f'pnt my_local_p={{0, 0, {offset}, 0, 0, 0}}')
    # send_command('pnt my_global_p = point_trans_u2g(my_local_p, 0)')
    # send_command(f'my_global_p[3] = {90}')
    # send_command(f'my_global_p[4] = {0}')
    # send_command(f'my_global_p[5] = {0}')
    # send_command('move_jl(my_global_p, 50, 50)')

    # wait_for_motion()
    # send_command(f'pnt my_local_p={{0, 0, {offset}, 0, 0, 0}}')
    # send_command('pnt my_global_p = point_trans_u2g(my_local_p, 0)')
    # send_command(f'my_global_p[3] = {aee_R[0]}')
    # send_command(f'my_global_p[4] = {aee_R[1]}')
    # send_command(f'my_global_p[5] = {aee_R[2]}')
    # send_command('move_jl(my_global_p, 50, 50)')
    # wait_for_motion()
    # send_command(f'move_l_rel(pnt[0, 0, {-mapped_value}, 0, 0, 0], 500, 500, 2)')
    # wait_for_motion()
    # print("물체 위치에 이동 완료")

    #     send_command(f'move_l_rel(pnt[0, 0, {mapped_value/2}, 0, 0, 0], 500, 500, 2)')
    #     wait_for_motion()

    #     send_command('pnt my_point = {-109.73, -503.92, 498.21, 90, 0, 0}')
    #     send_command(f'pnt my_local_p={{0, 0, {offset1}, 0, 0, 0}}')
    #     send_command('pnt my_global_p = point_trans_u2g(my_local_p, 0)')
    #     send_command(f'my_global_p[3] = {90}')
    #     send_command(f'my_global_p[4] = {0}')
    #     send_command(f'my_global_p[5] = {-15}')
    #     send_command('move_c_points(my_point, my_global_p, 500, 500, 0) ')
    #     wait_for_motion()
    #     send_command(f'move_l_rel(pnt[0, 0, -150, 0, 0, 0], 500, 500, 2)')
    #     wait_for_motion()


