import serial
import socket
import rbpodo as rb
import numpy as np
import math
from scipy.spatial.transform import Rotation as R

# 시리얼 포트 설정 (Ubuntu 환경)
ser = serial.Serial(port="/dev/ttyUSB0", baudrate=9600, timeout=0.1)

def write_serial(command):
    message = f"@{command}$"
    ser.write(message.encode())

def read_serial():
    while True:
        if ser.in_waiting > 0:
            response = ser.readline().decode().strip()
            if response:
                if response == "#":
                    return "INIT"
                elif response == "$":
                    return "GRIP"
                elif response == "@":
                    return "RELEASE"

write_serial("D00")
print("@D00$전송완료")

# 초기 로봇 위치 이동
while read_serial() != "INIT":
    pass
print("그리퍼 초기 위치 이동 완료.")

# 로봇 서버 설정
HOST = "192.168.0.100"
PORT = 5000
robot = rb.Cobot("192.168.0.100")
rc = rb.ResponseCollector()
robot.set_operation_mode(rc, rb.OperationMode.Real)
rc = rc.error().throw_if_not_empty()

# 소켓 연결
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))
print("로봇 서버에 연결되었습니다.")

def send_command(command):
    client_socket.sendall(command.encode())
    return client_socket.recv(1024).decode()

def wait_for_motion():
    while True:
        data = client_socket.recv(1024).decode()
        if "info[motion_changed][0]" in data:
            break
        print("로봇이 이동 중입니다. 잠시만 기다려주세요...")

def map_range(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def compute_end_effector_rotation(rx, ry, rz):
    obj_rotation = R.from_euler('ZYX', [rz, ry, rx], degrees=True)
    x_axis_obj = obj_rotation.apply([1, 0, 0])
    y_axis_obj = obj_rotation.apply([0, 1, 0])
    z_axis_obj = obj_rotation.apply([0, 0, 1])
    target_x = x_axis_obj
    target_y = z_axis_obj
    target_z = -y_axis_obj
    new_rotation_matrix = np.column_stack((target_x, target_y, target_z))
    final_rotation = R.from_matrix(new_rotation_matrix)
    ee_rz, ee_ry, ee_rx = final_rotation.as_euler('ZYX', degrees=True)
    return ee_rx, ee_ry, ee_rz

def transform_coordinates(a):
    camera_origin_x = -218.42
    camera_origin_y = -515.77
    xw = a[0] + camera_origin_x
    yw = a[1] + camera_origin_y
    z = 5.00
    dx, dy, dz = 0, 0, 0
    return [xw, yw, z, dx, dy, dz]

i = 1
cases = {
    1: [681.17, -117.55, 35.00, 0, 0, 0],
    2: [681.17, -267.55, 50.00, 0, 0, 0],
    3: [581.17, -267.55, 50.00, 0, 0, 0],
    4: [581.17, -117.55, 50.00, 0, 0, 0]
}

joint = np.array([-90, 0, 90, 0, 90, 0])
robot.move_j(rc, joint, 30, 30)
if robot.wait_for_move_started(rc, 0.5).is_success():
    robot.wait_for_move_finished(rc)
rc = rc.error().throw_if_not_empty()

while True:
    a = [0, 0]  # 외부 시스템에서 제공하는 좌표 입력
    point = transform_coordinates(a)
    robot.set_user_coordinate(rc, 0, point)
    x = point[0]
    y = point[1]
    distance = math.sqrt(x**2 + y**2)
    if distance > 850 or distance < 300:
        print(f"에러: 거리 {distance}가 작업 범위를 벗어났습니다. 좌표를 다시 입력해주세요.")
        continue

    L = 115
    mapped_value = map_range(distance, 850, 300, 100, 300)
    offset = mapped_value + L
    send_command(f'pnt my_local_p={{0, 0, {offset}, 0, 0, 0}}')
    print(mapped_value)
    send_command('pnt my_global_p = point_trans_u2g(my_local_p, 0)')
    rx = point[3]
    ry = point[4]
    rz = point[5]
    ee_rx, ee_ry, ee_rz = compute_end_effector_rotation(rx, ry, rz)
    send_command(f'my_global_p[3] = {ee_rx}')
    send_command(f'my_global_p[4] = {ee_ry}')
    send_command(f'my_global_p[5] = {ee_rz}')
    send_command('move_jl(my_global_p, 30, 30)')
    wait_for_motion()
    send_command(f'move_l_rel(pnt[0, 0, {-mapped_value}, 0, 0, 0], 400, 400, 2)')
    wait_for_motion()
    print("물체 위치에 이동 완료")
    ser.write(b"@B00$")

    while read_serial() != "GRIP":
        pass
    print("파지 완료")

    send_command(f'move_l_rel(pnt[0, 0, {mapped_value/2}, 0, 0, 0], 100, 100, 2)')
    wait_for_motion()

    point1 = cases[i]
    robot.set_user_coordinate(rc, 0, point1)
    offset1 = 150 + 115
    send_command('pnt my_point = {-109.73, -503.92, 498.21, 90, 0, 0}')
    send_command(f'pnt my_local_p={{0, 0, {offset1}, 0, 0, 0}}')
    print(offset1)
    send_command('pnt my_global_p = point_trans_u2g(my_local_p, 0)')
    rx = point1[3]
    ry = point1[4]
    rz = point1[5]
    ee_rx, ee_ry, ee_rz = compute_end_effector_rotation(rx, ry, rz)
    send_command(f'my_global_p[3] = {ee_rx}')
    send_command(f'my_global_p[4] = {ee_ry}')
    send_command(f'my_global_p[5] = {ee_rz}')
    send_command('move_c_points(my_point, my_global_p, 1000, 1000, 0)')
    wait_for_motion()
    send_command(f'move_l_rel(pnt[0, 0, -150, 0, 0, 0], 100, 100, 2)')
    wait_for_motion()
    ser.write(b"@A00$")
    print("물체 위치에 이동 완료")

    while read_serial() != "RELEASE":
        pass
    print("하차 완료")

    send_command(f'move_l_rel(pnt[0, 0, 75, 0, 0, 0], 100, 100, 2)')
    wait_for_motion()

    i = i + 1 if i < 4 else 1

    send_command('move_jl(pnt[-109.73, -503.92, 498.21, 90, 0, 0], 30, 30)')
    wait_for_motion()
