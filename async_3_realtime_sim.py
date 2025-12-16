import logging
import asyncio
import datetime
import rbpodo as rb
import numpy as np
import cv2

# [중요] Matplotlib 충돌 방지 (Qt 에러 해결용)
import matplotlib
matplotlib.use('TkAgg') 
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


try:
    from vector_calculator.functions_sim_for_850 import Transform3D, RobotArm
except ImportError:
    print("오류: 'functions_sim_for_850.py' 파일을 찾을 수 없습니다.")
    exit()

logging.basicConfig(format='%(asctime)s.%(msecs)03d %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d,%H:%M:%S',
                    level=logging.INFO)

ROBOT_IP = "192.168.0.100"

class GLOBAL:
    running = True
    q = np.zeros((6,)) # 실시간 관절 각도 공유 변수

async def mat_plot_sim():
    """
    matplotlib를 이용하여 GLOBAL.q 값을 실시간으로 반영하여 로봇 자세를 그립니다.
    """
    logging.info("Starting 3D Simulation Viewer...")
    
    # functions_sim_for_850.py에 정의된 RobotArm 클래스 사용
    try:
        # dh_param_file 경로가 맞는지 확인하세요
        robot_sim = RobotArm(num_axes=6, dh_param_file='rb5_850_dh.csv')
    except Exception as e:
        logging.error(f"Failed to initialize RobotArm: {e}")
        return

    # Plot 설정
    plt.ion() # Interactive Mode 켜기
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # 뷰 범위 설정
    plot_range = 1000
    ax.set_xlim([-plot_range, plot_range])
    ax.set_ylim([-plot_range, plot_range])
    ax.set_zlim([0, 1200])
    ax.set_xlabel('X [mm]')
    ax.set_ylabel('Y [mm]')
    ax.set_zlabel('Z [mm]')
    ax.set_title("Real-time Robot Simulation")
    ax.view_init(elev=20, azim=45)

    # 초기 빈 그래프 생성 (선과 점)
    line_robot, = ax.plot([], [], [], 'o-', lw=3, markersize=6, color='black', label='Link')
    scat_ee = ax.scatter([], [], [], s=100, c='cyan', marker='X', label='End Effector')
    ax.legend()

    while GLOBAL.running:
        # (1) 현재 관절 각도 가져오기
        current_q = GLOBAL.q
        
        # (2) 로봇 모델 업데이트
        robot_sim.set_joint_angles(current_q)
        
        # (3) 링크 위치 계산 (Forward Kinematics)
        poses = robot_sim.get_all_link_poses()
        
        # (4) 좌표 추출
        points = [np.array([0, 0, 0])] # 베이스 원점
        for pose in poses:
            points.append(pose.get_translation())
        
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        zs = [p[2] for p in points]

        # (5) 그래프 데이터 갱신
        line_robot.set_data(xs, ys)
        line_robot.set_3d_properties(zs)
        
        if points:
            scat_ee._offsets3d = ([xs[-1]], [ys[-1]], [zs[-1]])

        # (6) 화면 그리기
        fig.canvas.draw_idle()
        fig.canvas.flush_events()
        
        # UI 반응성을 위해 잠시 대기
        await asyncio.sleep(0.05)

    plt.close(fig)
    logging.info("Simulation Viewer closed.")


async def cam_viewer():
    # 카메라 0번 시도
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        logging.warning("Camera index 0 failed. Trying index 2...")
        cap = cv2.VideoCapture(2)
        if not cap.isOpened():
            logging.error("No camera found.")
            # 카메라가 없어도 프로그램이 죽지 않도록 리턴
            return

    logging.info("Camera started.")

    while GLOBAL.running:
        ret, frame = cap.read()
        if ret:
            # 로봇 관절 각도 텍스트 오버레이
            text = f"Joint: {np.round(GLOBAL.q, 2)}"
            cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                        0.7, (0, 255, 0), 2)
            
            cv2.imshow("Robot Cam Viewer", frame)
            
            # 키 입력 대기 (1ms) - OpenCV 창 갱신 필수
            cv2.waitKey(1)
        
        # 비동기 양보 (30FPS 제한)
        await asyncio.sleep(0.03)

    cap.release()
    cv2.destroyAllWindows()
    logging.info("Camera closed.")


async def get_data():
    data_channel = rb.asyncio.CobotData(ROBOT_IP)
    
    # 연결 실패해도 시뮬레이션은 돌 수 있도록 예외처리
    try:
        logging.info("Connecting to Data Channel...")
        while GLOBAL.running:
            # 로봇 연결 상태라면 실제 데이터를 받음
            data = await data_channel.request_data()
            if data is not None:
                GLOBAL.q = data.sdata.jnt_ref
            await asyncio.sleep(0.1)
    except Exception as e:
        logging.warning(f"Data channel error (Simulation Mode?): {e}")
        # 로봇 연결이 안 되면 루프만 유지 (GLOBAL.q는 move_thread가 업데이트한다고 가정)
        while GLOBAL.running:
            await asyncio.sleep(1)


async def move_thread():
    robot = rb.asyncio.Cobot(ROBOT_IP)
    rc = rb.ResponseCollector()

    try:
        # 시뮬레이션 모드 설정
        await robot.set_operation_mode(rc, rb.OperationMode.Simulation)
        await robot.set_speed_bar(rc, 0.5)
        
        logging.info("Initializing Robot Move...")
        await robot.flush(rc)
        
        # [수정됨] 움직임을 확실히 보여주기 위한 루프 생성
        # 프로그램이 실행되는 동안 두 위치를 왔다 갔다 합니다.
        while GLOBAL.running:
            
            # 위치 1: 홈 포지션 (0도)
            logging.info("Moving to Home [0,0,0,0,0,0]...")
            await robot.move_j(rc, np.array([0, 0, 0, 0, 0, 0]), 200, 400)
            
            # 이동이 시작되고 끝날 때까지 대기
            if (await robot.wait_for_move_started(rc, 0.5)).type() == rb.ReturnType.Success:
                await robot.wait_for_move_finished(rc)
                logging.info(f"reached Home. (q: {np.round(GLOBAL.q, 1)})")
            
            await asyncio.sleep(1.0) # 1초 대기

            if not GLOBAL.running: break

            # 위치 2: 움직임 확인용 포지션 (2번 관절 -45도, 3번 관절 45도)
            target_q = np.array([0, -45, 45, 0, 0, 0])
            logging.info(f"Moving to Pose A {target_q}...")
            await robot.move_j(rc, target_q, 200, 400)

            if (await robot.wait_for_move_started(rc, 0.5)).type() == rb.ReturnType.Success:
                await robot.wait_for_move_finished(rc)
                logging.info(f"reached Pose A. (q: {np.round(GLOBAL.q, 1)})")
            
            await asyncio.sleep(1.0) # 1초 대기

    except Exception as e:
        logging.error(f"Robot Control Error: {e}")
        # 실제 로봇 연결이 없을 경우 테스트를 위해 가짜 데이터 생성
        logging.info("Running in Offline Simulation Mode (Fake Data)")
        t = 0
        while GLOBAL.running:
            # 사인파로 움직임 생성
            val = np.sin(t) * 45
            GLOBAL.q = np.array([0, val, -val, 0, 0, 0])
            t += 0.1
            await asyncio.sleep(0.05)

    logging.info("Move thread finished.")
    GLOBAL.running = False


async def _main():
    # 4개의 비동기 태스크 동시 실행
    task1 = asyncio.create_task(get_data())
    task2 = asyncio.create_task(move_thread())
    task3 = asyncio.create_task(cam_viewer())
    task4 = asyncio.create_task(mat_plot_sim())

    # move_thread(task2)가 메인 컨트롤러 역할을 하므로
    # task2가 끝날 때까지 기다렸다가 나머지도 종료
    await task2
    
    # move_thread가 끝나면 GLOBAL.running이 False가 되므로
    # 나머지 태스크들도 자연스럽게 루프를 빠져나오기를 기다림
    await task1
    await task3
    await task4

if __name__ == "__main__":
    try:
        asyncio.run(_main())
    except KeyboardInterrupt:
        logging.info("Program interrupted by User.")
