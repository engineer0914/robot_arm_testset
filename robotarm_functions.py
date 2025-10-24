# 로봇팔 함수 정리화
# 직선이동 함수화
# 컨트롤 박스읽기 함수화

import rbpodo as rb
import numpy as np
import time

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

def read_joint(rc, robot):
    joint_angles = []
    for i in range(6):  # J0 ~ J5
        _, out = robot.get_system_variable(rc, getattr(rb.SystemVariable, f"SD_J{i}_ANG"))
        rc = rc.error().throw_if_not_empty()
        joint_angles.append(out)

    joint_array = np.array(joint_angles, dtype=float)
    print(f"현재 조인트 각도: {joint_array}\n")
    return joint_array
