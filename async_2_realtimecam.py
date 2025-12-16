import logging
import asyncio
import datetime
import rbpodo as rb
import numpy as np
import cv2  # OpenCV 라이브러리 추가 필요 (pip install opencv-python)

logging.basicConfig(format='%(asctime)s.%(msecs)03d %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d,%H:%M:%S',
                    level=logging.INFO)
ROBOT_IP = "192.168.0.100"


class GLOBAL:
    running = True
    q = np.zeros((6,))

async def cam_viewer():
    # 카메라 인덱스 1번 시도 (안되면 0번으로 변경하세요)
    cap = cv2.VideoCapture(2)
    
    # 카메라가 열리지 않았을 경우 예외 처리
    if not cap.isOpened():
        logging.warning("Camera index 1 failed. Trying index 0...")
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            logging.error("No camera found.")
            return

    logging.info("Camera started.")

    while GLOBAL.running:
        ret, frame = cap.read()
        
        if ret:
            # (선택사항) 화면에 현재 로봇 관절 각도 텍스트 띄우기
            text = f"Joint: {np.round(GLOBAL.q, 2)}"
            cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                        0.7, (0, 255, 0), 2)
            
            cv2.imshow("Robot Cam Viewer", frame)
            
            # OpenCV UI 갱신을 위한 짧은 대기 (1ms)
            cv2.waitKey(1)
        else:
            logging.warning("Failed to read frame.")

        # [핵심] 비동기 루프 양보: 
        # 이걸 넣지 않으면 로봇 통신과 move_thread가 멈춥니다.
        # 약 30FPS(0.033초) 주기로 동작하도록 설정
        await asyncio.sleep(0.03)

    # 루프 종료 후 자원 해제
    cap.release()
    cv2.destroyAllWindows()
    logging.info("Camera closed.")


async def get_data():
    data_channel = rb.asyncio.CobotData(ROBOT_IP)

    while GLOBAL.running:
        data = await data_channel.request_data()
        # logging.info(data.sdata.jnt_ref) # 로그가 너무 많으면 주석 처리
        GLOBAL.q = data.sdata.jnt_ref
        await asyncio.sleep(0.1)


async def move_thread():
    robot = rb.asyncio.Cobot(ROBOT_IP)
    rc = rb.ResponseCollector()

    def callback(response: rb.Response):
        # logging.info(f"Callback Message: {response}")
        if response.type() == rb.Response.Type.Error:
            logging.error("An error has occurred in the robot. The program will terminate.")
            exit(-1)

    rc.set_callback(callback)

    await robot.set_operation_mode(rc, rb.OperationMode.Simulation)
    await robot.set_speed_bar(rc, 0.5)

    try:
        logging.info("Initializing Robot Move...")
        await robot.flush(rc)

        # 이동 명령
        await robot.move_j(rc, np.array([0, 0, 0, 0, 0, 0]), 600, 800)
        
        rc = rc.error().throw_if_not_empty()
        
        # 이동 시작 대기
        if (await robot.wait_for_move_started(rc, 0.5)).type() == rb.ReturnType.Success:
            logging.info(f"-- Move started (q: {GLOBAL.q}")
            # 이동 완료 대기
            await robot.wait_for_move_finished(rc)
            logging.info(f"-- Move finished (q: {GLOBAL.q}")
        else:
            logging.warning("-- Move not started ...")
        
        rc = rc.error().throw_if_not_empty()
    finally:
        pass

    logging.info("-- Wait for 2 seconds before closing")
    await asyncio.sleep(2)
    GLOBAL.running = False


async def _main():
    # task 생성 시 바로 실행됩니다.
    task1 = asyncio.create_task(get_data())
    task2 = asyncio.create_task(move_thread())
    task3 = asyncio.create_task(cam_viewer())

    # task2(로봇 이동)가 끝날 때까지 기다립니다.
    # task2가 끝나면 GLOBAL.running이 False가 되어 나머지 task도 종료됩니다.
    await task2 
    await task1
    await task3


if __name__ == "__main__":
    asyncio.run(_main())
