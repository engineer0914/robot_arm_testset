import logging
import asyncio
import numpy as np
import cv2
import matplotlib

# [중요] Matplotlib 충돌 방지
matplotlib.use('TkAgg') 
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# 클래스 Import
try:
    from vector_calculator.functions_sim_for_850 import Transform3D, RobotArm
except ImportError:
    print("오류: 'functions_sim_for_850.py' 파일을 찾을 수 없습니다.")
    exit()

logging.basicConfig(format='%(asctime)s.%(msecs)03d %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d,%H:%M:%S',
                    level=logging.INFO)

class GLOBAL:
    running = True
    q = np.zeros((6,)) # 현재 로봇 관절 각도 (공유 변수)

# ------------------------------------------------------------------
# [핵심] Jacobian 기반 오프라인 시뮬레이션
# ------------------------------------------------------------------
async def jac_sim():
    logging.info("Starting Jacobian-based Simulation (Offline)...")
    
    # 계산용 로봇 모델 생성
    robot_model = RobotArm(num_axes=6)
    
    # --- 내부 함수 1: Joint Move (관절 이동) ---
    async def sim_move_j(target_q, vel_deg=60.0):
        logging.info(f"Move J -> Target: {target_q}")
        
        start_q = np.copy(GLOBAL.q)
        diff = target_q - start_q
        max_dist = np.max(np.abs(diff))
        
        if max_dist == 0: return
        
        duration = max_dist / vel_deg
        dt = 0.05
        steps = int(duration / dt)
        if steps < 1: steps = 1
        
        for i in range(steps + 1):
            if not GLOBAL.running: break
            t = i / steps
            # Smooth step (Ease-in-out)
            smooth_t = t * t * (3 - 2 * t)
            GLOBAL.q = start_q + diff * smooth_t
            await asyncio.sleep(dt)
        
        GLOBAL.q = target_q # 오차 보정

    # --- 내부 함수 2: Linear Move (직선 이동 via Jacobian) ---
    async def sim_move_l(target_6d, vel_mm=100.0):
        """
        target_6d: [x, y, z, rx, ry, rz] (mm, deg)
        """
        logging.info(f"Move L -> Target: {target_6d}")
        
        target_pos = np.array(target_6d[:3])
        # 목표 회전 (Euler -> Matrix) - 단순화를 위해 위치 제어 위주로 구현
        # (완벽한 6D 제어를 위해서는 쿼터니언 오차 등을 써야 하지만 여기선 약식 구현)
        
        dt = 0.05
        
        while GLOBAL.running:
            # 1. 모델 업데이트
            robot_model.set_joint_angles(GLOBAL.q)
            
            # 2. 현재 EE 위치 파악
            curr_ee = robot_model.get_end_effector_pose()
            curr_pos = curr_ee.get_translation()
            
            # 3. 오차 벡터 계산
            err_pos = target_pos - curr_pos
            dist = np.linalg.norm(err_pos)
            
            if dist < 1.0: # 1mm 이내 도착 시 종료
                break
                
            # 4. 속도 벡터 생성
            speed = min(vel_mm, dist * 2.0) # P제어 느낌으로 감속
            v_vec = (err_pos / dist) * speed
            
            # 6x1 Task Velocity [vx, vy, vz, wx, wy, wz]
            # 여기서는 회전(Orientation)은 유지한다고 가정 (wx=wy=wz=0)
            v_task = np.array([v_vec[0], v_vec[1], v_vec[2], 0, 0, 0])
            
            # 5. Jacobian 역기구학
            J = robot_model.get_jacobian()
            
            # Damped Least Squares (특이점 방지 역행렬)
            lambda_sq = 0.01
            J_inv = J.T @ np.linalg.inv(J @ J.T + lambda_sq * np.eye(6))
            
            dq_rad = J_inv @ v_task
            dq_deg = np.rad2deg(dq_rad)
            
            # 6. 관절 업데이트
            GLOBAL.q = GLOBAL.q + dq_deg * dt
            await asyncio.sleep(dt)

    # ==========================================
    # 시뮬레이션 시나리오 시작
    # ==========================================
    await asyncio.sleep(2)
    
    # 1. 홈으로 이동
    await sim_move_j(np.array([0, 0, 0, 0, 0, 0]))
    await asyncio.sleep(1)
    
    # 2. 준비 자세
    # 
    await sim_move_j(np.array([0, -45, 90, -45, 90, 0]))
    await asyncio.sleep(1)
    
    # 3. Move L 테스트 (현재 자세에서 앞으로 쭉 뻗기)
    # 현재 좌표 계산
    robot_model.set_joint_angles(GLOBAL.q)
    curr_tf = robot_model.get_end_effector_pose()
    curr_xyz = curr_tf.get_translation()
    curr_rpy = curr_tf.get_euler_angles(degrees=True)
    
    # 목표: X축 +150mm, Z축 -50mm
    target_xyz = curr_xyz + np.array([150, 0, -50])
    target_6d = np.concatenate((target_xyz, curr_rpy))
    
    logging.info("--- 직선 이동 시작 (Move L) ---")
    await sim_move_l(target_6d, vel_mm=80.0)
    
    logging.info("Simulation Finished.")
    while GLOBAL.running:
        await asyncio.sleep(1)

# ------------------------------------------------------------------
# 시각화 (기존과 동일)
# ------------------------------------------------------------------
async def mat_plot_sim():
    logging.info("Starting 3D Viewer...")
    robot_sim = RobotArm(num_axes=6) # 뷰어용 모델
    
    plt.ion()
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    ax.set_xlim([-1000, 1000]); ax.set_ylim([-1000, 1000]); ax.set_zlim([0, 1200])
    ax.view_init(elev=20, azim=45)
    
    line_robot, = ax.plot([], [], [], 'o-', lw=3, color='black')
    scat_ee = ax.scatter([], [], [], s=100, c='cyan', marker='X')

    while GLOBAL.running:
        robot_sim.set_joint_angles(GLOBAL.q)
        poses = robot_sim.get_all_link_poses()
        points = [np.array([0,0,0])] + [p.get_translation() for p in poses]
        
        xs, ys, zs = zip(*points)
        line_robot.set_data(xs, ys)
        line_robot.set_3d_properties(zs)
        scat_ee._offsets3d = ([xs[-1]], [ys[-1]], [zs[-1]])
        
        fig.canvas.draw_idle()
        fig.canvas.flush_events()
        await asyncio.sleep(0.05)
    plt.close(fig)

async def _main():
    # 시뮬레이터(jac_sim)와 뷰어(mat_plot_sim) 병렬 실행
    t1 = asyncio.create_task(jac_sim())
    t2 = asyncio.create_task(mat_plot_sim())
    await t1
    await t2

if __name__ == "__main__":
    try:
        asyncio.run(_main())
    except KeyboardInterrupt:
        logging.info("종료")
