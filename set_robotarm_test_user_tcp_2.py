# tcp의 위치를 txt에서 읽어오는 구조로 변경했습니다.
# 하지만 move_l_rel에서 적용되지 않는 것 같아서 추가적인 보완이 필요

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

    # 로봇 연결
    robot = rb.Cobot(ROBOT_IP)
    rc = rb.ResponseCollector()

    # 모드 및 속도 설정
    robot.set_operation_mode(rc, rb.OperationMode.Real)
    # robot.set_operation_mode(rc, rb.OperationMode.Simulation)

    robot.set_speed_bar(rc, 0.7)

    get_cb_id(rc, robot) # 컨트롤 박스 ID 읽기

    tool_tcp_info = np.array([0, 0, 0, 0, 0, 0])
    robot.set_tcp_info(rc, tool_tcp_info)

    ans = robot.get_tcp_info(rc)
    print(ans)

    robot.set_user_coordinate(rc, 0, ans[1])

    for i in range(3):
        robot.move_l_rel(rc, linear_xyz[i], target_info[2], target_info[3], rb.ReferenceFrame.Tool)
        if robot.wait_for_move_started(rc, 0.5).is_success():
            robot.wait_for_move_finished(rc)
        rc.error().throw_if_not_empty()

        robot.move_l_rel(rc, -linear_xyz[i], target_info[2], target_info[3], rb.ReferenceFrame.Tool)
        if robot.wait_for_move_started(rc, 0.5).is_success():
            robot.wait_for_move_finished(rc)
        rc.error().throw_if_not_empty()

    for i in range(3):
        robot.move_l_rel(rc, rot_xyz[i], target_info[2], target_info[3], rb.ReferenceFrame.Tool)
        if robot.wait_for_move_started(rc, 0.5).is_success():
            robot.wait_for_move_finished(rc)
        rc.error().throw_if_not_empty()

        robot.move_l_rel(rc, -rot_xyz[i], target_info[2], target_info[3], rb.ReferenceFrame.Tool)
        if robot.wait_for_move_started(rc, 0.5).is_success():
            robot.wait_for_move_finished(rc)
        rc.error().throw_if_not_empty()


    filename = "point_tcp.txt"

    tool_tcp_info = np.loadtxt(filename)
    print(tool_tcp_info)

    robot.set_tcp_info(rc, tool_tcp_info)
    robot.set_tcp_info(rc, tool_tcp_info)

    ans = robot.get_tcp_info(rc)
    print(ans)

    for i in range(3):
        robot.move_l_rel(rc, linear_xyz[i], target_info[2], target_info[3], rb.ReferenceFrame.Tool)
        if robot.wait_for_move_started(rc, 0.5).is_success():
            robot.wait_for_move_finished(rc)
        rc.error().throw_if_not_empty()

        robot.move_l_rel(rc, -linear_xyz[i], target_info[2], target_info[3], rb.ReferenceFrame.Tool)
        if robot.wait_for_move_started(rc, 0.5).is_success():
            robot.wait_for_move_finished(rc)
        rc.error().throw_if_not_empty()

    for i in range(3):
        robot.move_l_rel(rc, rot_xyz[i], target_info[2], target_info[3], rb.ReferenceFrame.Tool)
        if robot.wait_for_move_started(rc, 0.5).is_success():
            robot.wait_for_move_finished(rc)
        rc.error().throw_if_not_empty()

        robot.move_l_rel(rc, -rot_xyz[i], target_info[2], target_info[3], rb.ReferenceFrame.Tool)
        if robot.wait_for_move_started(rc, 0.5).is_success():
            robot.wait_for_move_finished(rc)
        rc.error().throw_if_not_empty()


    # robot.set_tcp_info(rc, -tool_tcp_info)

if __name__ == "__main__":
    _main()
