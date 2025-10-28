#그리퍼 테스트 하는 코드

import socket
import rbpodo as rb
import numpy as np
import time


ROBOT_IP = "192.168.0.22"
SOCKET_PORT = 5000 



print(f"로봇에 연결 중... IP: {ROBOT_IP}")
robot = rb.Cobot(ROBOT_IP)
rc = rb.ResponseCollector()
print("로봇 연결 성공.")


print("작동 모드를 Real으로 설정합니다. (로봇이 실제 움직입니다!)")
robot.set_operation_mode(rc, rb.OperationMode.Real)


speed_override = 1
print(f"전체 속도 오버라이드 설정: {speed_override*100:.0f}%")
robot.set_speed_bar(rc, speed_override)


try:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((ROBOT_IP, SOCKET_PORT))
    print(f"로봇 스크립트 서버에 소켓 연결되었습니다. IP: {ROBOT_IP}, Port: {SOCKET_PORT}")
except socket.error as e:
    print(f"로봇 스크립트 서버 소켓 연결 실패: {e}")
    print("move_l_relative 함수는 작동하지 않습니다.")
    client_socket = None # 연결 실패 시 None으로 설정

def grip(ord):
    if(ord == "release"):
        robot.set_dout_bit_combination(rc, 0, 3, 1, rb.Endian.LittleEndian)
        time.sleep(0.1)
        robot.set_dout_bit_combination(rc, 0, 3, 0, rb.Endian.LittleEndian)

    elif(ord == "grab"):
        robot.set_dout_bit_combination(rc, 0, 3, 2, rb.Endian.LittleEndian)
        time.sleep(0.1)
        robot.set_dout_bit_combination(rc, 0, 3, 0, rb.Endian.LittleEndian)
        
    else:
        return

# 메인 실행 로직
def main():

    while True:

        grip("grab")

        time.sleep(3)
        
        grip("release")
        
        time.sleep(3)
        
if __name__ == "__main__":
    main()
