#그리퍼 테스트 하는 코드

# import serial # 시리얼 통신은 사용하지 않으므로 주석 처리
import socket # 로봇 스크립트 명령 전송을 위한 소켓 통신
import rbpodo as rb # 레인보우 로보틱스 코봇 제어 라이브러리
import numpy as np # 수치 계산 (배열 등)
import time # 시간 지연 사용

# ======= 설정 부분 =======
ROBOT_IP = "192.168.0.22" # 로봇 제어기의 실제 IP 주소로 변경하세요. (예: "10.0.2.7" 등)
# 소켓 통신에 사용할 포트 (로봇 스크립트 인터페이스 포트일 가능성 높음)
# 로봇 매뉴얼에서 스크립트 인터페이스 포트를 확인하세요.
SOCKET_PORT = 5000 
# =======================

# 로봇 연결 (스크립트 시작 시 한 번 실행)
# rbpodo 라이브러리 연결
print(f"로봇에 연결 중... IP: {ROBOT_IP}")
robot = rb.Cobot(ROBOT_IP)
rc = rb.ResponseCollector()
print("로봇 연결 성공.")

# 작동 모드 설정 (스크립트 시작 시 한 번 실행)
# 로봇을 실제로 움직입니다! 주변 안전 확인 필수!
print("작동 모드를 Real으로 설정합니다. (로봇이 실제 움직입니다!)")
robot.set_operation_mode(rc, rb.OperationMode.Real)
#rc.error().throw_if_not_empty() # 에러 발생 시 스크립트 즉시 중단

# 전체 이동 속도 오버라이드 설정 (0.0 ~ 1.0) (스크립트 시작 시 한 번 실행)
# 실제 움직일 때는 낮은 값(예: 0.1 ~ 0.3)으로 시작하는 것이 안전합니다.
speed_override = 1
print(f"전체 속도 오버라이드 설정: {speed_override*100:.0f}%")
robot.set_speed_bar(rc, speed_override)
#rc.error().throw_if_not_empty() # 에러 발생 시 스크립트 즉시 중단

# 소켓 연결 (스크립트 시작 시 한 번 실행)
# 로봇 스크립트 명령 전송을 위한 소켓 연결
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
