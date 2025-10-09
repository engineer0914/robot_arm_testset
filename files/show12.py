# wasdqe move insert
# pay with sudo python3 show12.py

import socket
import rbpodo as rb
import numpy as np
import time
import keyboard  # pip install keyboard

ROBOT_IPS = ["192.168.0.22", "192.168.0.21", "192.168.0.20"]
SOCKET_PORT = 5000

move_step = 100.0

class RobotController:
    def __init__(self, ip, idx):
        self.ip = ip
        self.idx = idx
        self.robot = rb.Cobot(ip)
        self.rc = rb.ResponseCollector()
        self.sock = None
        self._connect()
        self._init_robot()

    def _connect(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.ip, SOCKET_PORT))
            print(f"[{self.idx+1}] 소켓 연결 성공: {self.ip}")
        except socket.error as e:
            print(f"[{self.idx+1}] 소켓 연결 실패: {e}")
            self.sock = None

    def _init_robot(self):
        self.robot.set_operation_mode(self.rc, rb.OperationMode.Real)
        self.robot.set_speed_bar(self.rc, 0.5)
        print(f"[{self.idx+1}] 로봇 초기화 완료")

    def send_command(self, command):
        if not self.sock:
            print(f"[{self.idx+1}] 소켓 미연결 - 명령 전송 불가")
            return None
        try:
            self.sock.sendall(command.encode())
            response = self.sock.recv(1024).decode()
            return response
        except Exception as e:
            print(f"[{self.idx+1}] 소켓 통신 오류: {e}")
            return None

    def move_relative(self, dx=0, dy=0, dz=0):
        disp = [dx, dy, dz, 0, 0, 0]
        speed = 200
        accel = 200
        coord_sys = 2
        command = f"move_l_rel(pnt[{', '.join(map(str, disp))}], {speed}, {accel}, {coord_sys})"
        response = self.send_command(command)
        print(f"[{self.idx+1}] 명령 전송: {command}, 응답: {response}")

def main():
    controllers = [RobotController(ip, idx) for idx, ip in enumerate(ROBOT_IPS)]
    print("W,S: y축 ↑↓ / A,D: x축 ←→ / Q,E: z축 ↑↓ 제어. ESC 누르면 종료.")

    try:
        while True:
            dx = dy = dz = 0.0
            if keyboard.is_pressed('w'): dy += move_step
            if keyboard.is_pressed('s'): dy -= move_step
            if keyboard.is_pressed('a'): dx -= move_step
            if keyboard.is_pressed('d'): dx += move_step
            if keyboard.is_pressed('q'): dz += move_step
            if keyboard.is_pressed('e'): dz -= move_step

            if dx != 0 or dy != 0 or dz != 0:
                print(f"입력 감지됨. dx={dx}, dy={dy}, dz={dz}")
                for ctrl in controllers:
                    ctrl.move_relative(dx, dy, dz)
                time.sleep(0.3)

            if keyboard.is_pressed('esc'):
                print("ESC 입력 감지 - 종료합니다.")
                break

            time.sleep(0.05)

    except KeyboardInterrupt:
        print("키보드 인터럽트로 종료")
    print("프로그램 종료")

if __name__ == "__main__":
    main()
