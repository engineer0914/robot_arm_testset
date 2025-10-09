import threading
import socket
import rbpodo as rb
import numpy as np
import time

# ======= 각 로봇의 IP 주소와 포트 =======
ROBOT_IPS = ["192.168.0.22", "192.168.0.21", "192.168.0.20"]  # 각 로봇 IP로 변경
SOCKET_PORT = 5000

# === 로봇별 동작 함수 집합 ===
def robot_task(robot_idx):
    ROBOT_IP = ROBOT_IPS[robot_idx]
    
    print(f"로봇 {robot_idx+1}({ROBOT_IP}) 연결 중...")
    robot = rb.Cobot(ROBOT_IP)
    rc = rb.ResponseCollector()

    # 소켓 연결
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((ROBOT_IP, SOCKET_PORT))
        print(f"로봇{robot_idx+1} 스크립트 서버 소켓 연결됨.")
    except socket.error as e:
        print(f"로봇{robot_idx+1} 소켓 연결 오류: {e}")
        client_socket = None

    # 작동 모드 및 속도 설정
    robot.set_operation_mode(rc, rb.OperationMode.Real)
    robot.set_speed_bar(rc, 1)
    
    # 샘플 포즈 (각 로봇별 다르게 줘야 공간 충돌 방지!)
    pose_initiate = np.array([
        -135.0+10*robot_idx, 0.0, 90.0,   # 첫 관절 각도값을 로봇별로 약간씩 다르게!
        0.0, 90.0, 45.0
    ])

    # --- 간단한 이동 시나리오 ---
    try:
        print(f"[{robot_idx+1}] 초기 자세 이동")
        robot.move_j(rc, pose_initiate, 20, 20)
        robot.flush(rc)
        rc.clear()
        if robot.wait_for_move_started(rc, 5.0).is_success():
            robot.wait_for_move_finished(rc)
        
        # 상대 이동 예시(소켓 명령)
        def send_command(command):
            if client_socket is None:
                print("소켓 없음")
                return
            try:
                client_socket.sendall(command.encode())
                response = client_socket.recv(1024).decode()
                return response
            except:
                print("소켓통신 오류")
                return

        # 로봇별 직교이동(예: z축 -50mm)
        disp = [0.0, 0.0, -100.0, 0.0, 0.0, 0.0]
        command = f"move_l_rel(pnt[{', '.join(map(str, disp))}], 200, 200, 2)"
        send_command(command)
        print(f"[{robot_idx+1}] 상대이동 명령 전송!")

        time.sleep(1.0)  # 모든 로봇 동작 사이에 약간의 텀 주기
        # 그리퍼 동작 등 추가도 가능
        
    except Exception as e:
        print(f"[{robot_idx+1}] 에러: {e}")

    print(f"== 로봇 {robot_idx+1} 작업 완료 ==")

# === 메인: 3대의 스레드 생성, 병렬 실행 ===
def main():
    threads = []
    for idx in range(3):
        t = threading.Thread(target=robot_task, args=(idx,))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    print("모든 로봇 작업 종료")

if __name__ == "__main__":
    main()
