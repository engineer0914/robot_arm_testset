import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.spatial.transform import Rotation as R
import rbpodo as rb
import robotarm_functions as ra_fs
import numpy as np

################################################################################################################################

# --- 헬퍼 함수: 회전 행렬 생성 (함수 외부에 유지) ---
def get_rotation_matrix_x(angle_deg):
    """Global X-axis rotation matrix (degrees)"""
    angle_rad = np.radians(angle_deg)
    return np.array([
        [1, 0, 0],
        [0, np.cos(angle_rad), -np.sin(angle_rad)],
        [0, np.sin(angle_rad),  np.cos(angle_rad)]
    ])

def get_rotation_matrix_y(angle_deg):
    """Global Y-axis rotation matrix (degrees)"""
    angle_rad = np.radians(angle_deg)
    return np.array([
        [np.cos(angle_rad), 0, np.sin(angle_rad)],
        [0, 1, 0],
        [-np.sin(angle_rad), 0, np.cos(angle_rad)]
    ])

def get_rotation_matrix_z(angle_deg):
    """Global Z-axis rotation matrix (degrees)"""
    angle_rad = np.radians(angle_deg)
    return np.array([
        [np.cos(angle_rad), -np.sin(angle_rad), 0],
        [np.sin(angle_rad),  np.cos(angle_rad), 0],
        [0, 0, 1]
    ])

# --- 새로운 시각화 함수: 특정 시나리오를 그림 ---
def plot_comparison_scenario(initial_matrix, matrix_cond_z, matrix_reference, matrices_y_rotated, matrix_selected, title="Rotation Analysis Visualization"):
    """
    주어진 행렬들을 특정 시나리오에 맞춰 시각화합니다.
    - initial_matrix (함수에 처음 입력된 행렬)의 전체 축 (옅은 회색 점선)
    - matrix_cond_z (조건부 Z 회전 후의 행렬)의 전체 축 (빨강, 초록, 파랑 실선)
    - matrix_reference (Step 4에서 최종 선택된 "참조" 행렬)의 X축 벡터 (핫핑크 실선)
    - matrices_y_rotated (local Y 0, 90, 180, 270도 회전 후의 행렬들)의 X축 벡터 (검은 점선)
    - matrix_selected (Step 6에서 조건 범위를 만족하는 행렬 중 하나)의 전체 축 (진한 특정 색 실선)

    Args:
        initial_matrix (np.ndarray): 함수에 처음 입력된 3x3 회전 행렬.
        matrix_cond_z (np.ndarray): Step 2까지 적용된 3x3 회전 행렬.
        matrix_reference (np.ndarray): Step 4에서 최종 선택된 "참조" 3x3 회전 행렬.
        matrices_y_rotated (dict): '0', '90', '180', '270' 키를 갖는 회전 행렬 딕셔너리 (Step 5 결과).
        matrix_selected (np.ndarray): Step 6에서 조건 범위를 만족하는 3x3 회전 행렬 중 하나.
        title (str): 그래프 제목.
    """
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection='3d')

    # 원점 표시
    ax.scatter(0, 0, 0, color='k', marker='o', s=50)

    # Original Global Axes (참고용)
    ax.quiver(0, 0, 0, 1, 0, 0, color='gray', linestyle=':', alpha=0.5, length=1.0)
    ax.quiver(0, 0, 0, 0, 1, 0, color='gray', linestyle=':', alpha=0.5, length=1.0)
    ax.quiver(0, 0, 0, 0, 0, 1, color='gray', linestyle=':', alpha=0.5, length=1.0, label='Global Axes')

    # initial_matrix 축 그리기 (옅은 회색 점선) - 함수에 처음 들어온 행렬의 자세
    ax.quiver(0, 0, 0, initial_matrix[0,0], initial_matrix[1,0], initial_matrix[2,0], color='lightgray', linestyle='--', length=1.0, arrow_length_ratio=0.1)
    ax.quiver(0, 0, 0, initial_matrix[0,1], initial_matrix[1,1], initial_matrix[2,1], color='lightgray', linestyle='--', length=1.0, arrow_length_ratio=0.1)
    ax.quiver(0, 0, 0, initial_matrix[0,2], initial_matrix[1,2], initial_matrix[2,2], color='lightgray', linestyle='--', length=1.0, arrow_length_ratio=0.1, label='Initial Matrix Axes')

    # matrix_cond_z 축 그리기 (기준 축, Step 2 결과)
    ax.quiver(0, 0, 0, matrix_cond_z[0,0], matrix_cond_z[1,0], matrix_cond_z[2,0], color='r', label='CondZ X', length=1.0, arrow_length_ratio=0.1)
    ax.quiver(0, 0, 0, matrix_cond_z[0,1], matrix_cond_z[1,1], matrix_cond_z[2,1], color='g', label='CondZ Y', length=1.0, arrow_length_ratio=0.1)
    ax.quiver(0, 0, 0, matrix_cond_z[0,2], matrix_cond_z[1,2], matrix_cond_z[2,2], color='b', label='CondZ Z', length=1.0, arrow_length_ratio=0.1)

    # Final Reference Matrix의 X축 벡터 그리기 (핫핑크) - Step 4 최종 결과
    ref_x = matrix_reference[:, 0]
    ax.quiver(0, 0, 0, ref_x[0], ref_x[1], ref_x[2], color='hotpink', linewidth=2, length=1.0, arrow_length_ratio=0.1, label='Final Reference X (Z=0)')


    # matrices_y_rotated의 X축 벡터 그리기 (검은 점선) - Step 5 결과
    for angle_key, matrix in matrices_y_rotated.items():
        rotated_x = matrix[:, 0]
        # Use angle_key directly for label as it's already the desired numerical value
        ax.quiver(0, 0, 0, rotated_x[0], rotated_x[1], rotated_x[2], color='k', linestyle='--', length=1.0, arrow_length_ratio=0.1, label=f'Y_{angle_key:.0f}deg X')

    # matrix_selected의 전체 축 그리기 (진한 특정 색 실선) - Step 6 결과
    if matrix_selected is not None:
        selected_x = matrix_selected[:, 0]
        selected_y = matrix_selected[:, 1]
        selected_z = matrix_selected[:, 2]
        # 다른 색으로 표시
        ax.quiver(0, 0, 0, selected_x[0], selected_x[1], selected_x[2], color='darkorange', linewidth=2, length=1.0, arrow_length_ratio=0.1, label='Selected X')
        ax.quiver(0, 0, 0, selected_y[0], selected_y[1], selected_y[2], color='purple', linewidth=2, length=1.0, arrow_length_ratio=0.1, label='Selected Y')
        ax.quiver(0, 0, 0, selected_z[0], selected_z[1], selected_z[2], color='darkcyan', linewidth=2, length=1.0, arrow_length_ratio=0.1, label='Selected Z')
    else:
        print("No matrix was selected for visualization (no matrix within the ±45 deg range).")


    # 그래프 설정
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title(title)

    # 축 범위 설정 (요청에 따라 Y, Z축 반전)
    ax.set_xlim([-1.2, 1.2])
    ax.set_ylim([1.2, -1.2]) # Y축 반전
    ax.set_zlim([1.2, -1.2]) # Z축 반전

    # 시각적 비율을 동일하게 설정하여 왜곡 방지
    ax.set_box_aspect([1,1,1]) # Matplotlib 3.3 이상

    ax.legend()
    plt.show()

# --- 메인 분석 및 처리 함수 ---
def process_and_analyze_matrix_sequence(input_matrix, title="Analysis Result"):
    """
    입력 행렬 (카메라->로봇 변환된 행렬)에 대해 일련의 분석 및 회전 단계를 수행하고 결과를 출력/시각화합니다.

    Args:
        input_matrix (np.ndarray): 분석을 시작할 초기 3x3 회전 행렬 (R_robot에 해당).
        title (str): 출력 및 시각화에 사용할 제목.
    """
    if input_matrix.shape != (3, 3):
        print(f"Error processing matrix '{title}': Input matrix must be 3x3.")
        return

    print(f"\n--- Starting analysis sequence for: {title} ---")
    print("Initial Matrix (after R_cam_to_robot transform):\n", input_matrix)

    # Step 1: Global X 180 degree rotation (applied to the input matrix, which is R_robot)
    # Global rotation is pre-multiplication (R_new = R_global @ R_old)
    matrix_step1 = input_matrix

    # Step 2: Check Y vector Z component and apply conditional local Z 180 rotation
    matrix_step2 = np.copy(matrix_step1) # 다음 단계를 위해 복사
    rotated_y_axis_step1 = matrix_step1[:, 1] # Step 1 후의 Y축

    # Check Y vector's Z component from matrix_step1
    is_y_axis_z_negative_step2 = rotated_y_axis_step1[2] < 0

    if is_y_axis_z_negative_step2:
        print("\n[Condition Met in Step 2] Rotated Y-axis (from Step 1 matrix) Z-component is negative. Applying local Z 180deg rotation.")
        # Local Z-axis 180 rotation applied to the matrix from Step 1
        local_180_deg_z_rotation_matrix = get_rotation_matrix_z(180)
        matrix_step2 = matrix_step1 @ local_180_deg_z_rotation_matrix # Local rotation is post-multiplication
        flip = 1

        print("Matrix after Step 2 (Conditional local Z 180deg rotation):\n", matrix_step2)
    else:
        print("\n[Condition NOT Met in Step 2] Rotated Y-axis (from Step 1 matrix) Z-component is not negative. No conditional rotation applied in Step 2.")
        print("Matrix after Step 2 (same as matrix_step1):\n", matrix_step2)
        flip = 0

    # Step 3: Compare Y vector's X and Y components (from matrix_step2)
    print("\n--- Step 3: Y axis vector component absolute value comparison (from matrix_step2) ---")
    rotated_y_axis_step2 = matrix_step2[:, 1]
    abs_y_axis_x_comp_step3 = abs(rotated_y_axis_step2[0]) # Absolute X component of Y vector from matrix_step2
    abs_y_axis_y_comp_step3 = abs(rotated_y_axis_step2[1]) # Absolute Y component of Y vector from matrix_step2

    print(f"Rotated Y axis vector (from matrix_step2): {rotated_y_axis_step2}")
    print(f"Absolute X component of rotated Y axis (from matrix_step2): {abs_y_axis_x_comp_step3:.6f}")
    print(f"Absolute Y component of rotated Y axis (from matrix_step2): {abs_y_axis_y_comp_step3:.6f}")

    y_comp_higher_step3 = False # Flag for branching in Step 4

    if abs_y_axis_y_comp_step3 > abs_y_axis_x_comp_step3:
        print("Result: Absolute Y component of rotated Y axis (from matrix_step2) is greater than its absolute X component.")
        y_comp_higher_step3 = True
    elif abs_y_axis_x_comp_step3 > abs_y_axis_y_comp_step3:
        print("Result: Absolute X component of rotated Y axis (from matrix_step2) is greater than its absolute Y component.")
        y_comp_higher_step3 = False
    else:
        if np.isclose(abs_y_axis_x_comp_step3, abs_y_axis_y_comp_step3):
             print("Result: Absolute X and Y components of rotated Y axis (from matrix_step2) are equal (or very close). Treating as X component higher case.")
             y_comp_higher_step3 = False # Arbitrarily treat as X higher for tie-breaking
        else:
             print("Result: Neither absolute X nor absolute Y component is strictly greater than the other. Treating as X component higher case.")
             y_comp_higher_step3 = False


    # Step 4: Make TWO reference matrices (X vector Z=0), compare their X vectors, and select one
    print("\n--- Step 4: Calculate two reference matrices and select one ---")
    rotated_x_axis_step2 = matrix_step2[:, 0]
    rotated_y_axis_step2 = matrix_step2[:, 1] # Local Y axis for rotation
    rotated_z_axis_step2 = matrix_step2[:, 2]

    # Calculate the angle needed to make rotated X axis's Z component zero around rotated Y axis (from matrix_step2)
    # This calculation gives one orientation where Rx_z is zero.
    xz_comp_step2 = rotated_x_axis_step2[2]
    zz_comp_step2 = rotated_z_axis_step2[2]

    if np.allclose([xz_comp_step2, zz_comp_step2], [0, 0], atol=1e-9):
        angle_to_zero_z_rad_initial = 0.0
    else:
        angle_to_zero_z_rad_initial = np.arctan2(xz_comp_step2, zz_comp_step2)

    angle_to_zero_z_deg_initial = np.degrees(angle_to_zero_z_rad_initial)

    print(f"Calculated angle around local Y axis (from matrix_step2) to make X vector Z component zero (initial): {angle_to_zero_z_deg_initial:.4f} degrees.")

    # Create the first reference matrix (X vector Z=0)
    # matrix_step2 @ local_Y_rotation(angle_to_zero_z_deg_initial)
    correction_rot_matrix_local_y_initial = get_rotation_matrix_y(angle_to_zero_z_deg_initial)
    matrix_reference_candidate1 = matrix_step2 @ correction_rot_matrix_local_y_initial
    print("\nReference Matrix Candidate 1 (Initial Z=0):\n", matrix_reference_candidate1)
    print("Candidate 1 X vector Z component:", matrix_reference_candidate1[:, 0][2]) # Verification


    # Create the second reference matrix (180 deg from the first around local Y axis)
    # This corresponds to rotating by angle_to_zero_z_deg_initial + 180 degrees
    # or simply rotating the first candidate by local Y 180deg.
    local_180_deg_y_rotation_matrix = get_rotation_matrix_y(180)
    matrix_reference_candidate2 = matrix_reference_candidate1 @ local_180_deg_y_rotation_matrix
    print("\nReference Matrix Candidate 2 (180 deg from Candidate 1 around its local Y):\n", matrix_reference_candidate2)
    print("Candidate 2 X vector Z component:", matrix_reference_candidate2[:, 0][2]) # Verification


    # --- Compare and Select one Reference Matrix based on Step 3 result ---
    ref_x_candidate1 = matrix_reference_candidate1[:, 0]
    ref_x_candidate2 = matrix_reference_candidate2[:, 0]

    matrix_reference_final = None # Variable to store the finally selected reference matrix

    print("\nSelecting final reference matrix based on Step 3 comparison:")

    if y_comp_higher_step3: # If Step 3 result was Y component higher
        print("Step 3 Result: Y component of rotated Y axis was higher than X component.")
        # Select the candidate whose X vector has a POSITIVE X component
        print(f"Candidate 1 X vector X component: {ref_x_candidate1[0]:.6f}")
        print(f"Candidate 2 X vector X component: {ref_x_candidate2[0]:.6f}")
        if ref_x_candidate1[0] > 1e-6: # Check if positive (use tolerance)
             matrix_reference_final = matrix_reference_candidate1
             print("Selected Candidate 1 (Positive X component).")
        elif ref_x_candidate2[0] > 1e-6: # Check if positive (use tolerance)
             matrix_reference_final = matrix_reference_candidate2
             print("Selected Candidate 2 (Positive X component).")
        else:
             # Should ideally not happen for valid rotations unless X components are near zero
             print("Warning: Neither reference candidate X vector has a positive X component. Selecting candidate with largest X component.")
             if ref_x_candidate1[0] > ref_x_candidate2[0]:
                 matrix_reference_final = matrix_reference_candidate1
                 print("Selected Candidate 1 (Largest X component).")
             else:
                 matrix_reference_final = matrix_reference_candidate2
                 print("Selected Candidate 2 (Largest X component).")

    else: # If Step 3 result was X component higher or equal
        print("Step 3 Result: X component of rotated Y axis was higher or equal to X component.")
        # Select the candidate whose X vector has a POSITIVE Y component
        print(f"Candidate 1 X vector Y component: {ref_x_candidate1[1]:.6f}")
        print(f"Candidate 2 X vector Y component: {ref_x_candidate2[1]:.6f}")
        if ref_x_candidate1[1] > 1e-6: # Check if positive (use tolerance)
             matrix_reference_final = matrix_reference_candidate1
             print("Selected Candidate 1 (Positive Y component).")
        elif ref_x_candidate2[1] > 1e-6: # Check if positive (use tolerance)
             matrix_reference_final = matrix_reference_candidate2
             print("Selected Candidate 2 (Positive Y component).")
        else:
             # Should ideally not happen for valid rotations unless Y components are near zero
             print("Warning: Neither reference candidate X vector has a positive Y component. Selecting candidate with largest Y component.")
             if ref_x_candidate1[1] > ref_x_candidate2[1]:
                 matrix_reference_final = matrix_reference_candidate1
                 print("Selected Candidate 1 (Largest Y component).")
             else:
                 matrix_reference_final = matrix_reference_candidate2
                 print("Selected Candidate 2 (Largest Y component).")

    # Verify selection if a matrix was selected
    if matrix_reference_final is not None:
         print("\nFinal Reference Matrix (matrix_reference_final):\n", matrix_reference_final)
         print("Final Reference Matrix X vector:", matrix_reference_final[:, 0])
         print("Final Reference Matrix X vector Z component:", matrix_reference_final[:, 0][2]) # Should be close to zero
    else:
         print("\nError: Could not select a final reference matrix.")
         # Handle error - subsequent steps might fail if matrix_reference_final is None
         # For now, let's return None or raise an error if this happens
         return # Exit function if no matrix selected

    # Step 5: Get 3 more rotation matrices (0, 90, 180, 270 local Y rotations from matrix_step2)
    print("\n--- Step 5: Generate Y-rotated matrices (from matrix_step2) ---")
    # NOTE: These rotations are still relative to matrix_step2, NOT matrix_reference_final
    # The request implies these are the candidates to compare against the final reference.
    matrices_y_rotated = {}
    # Store angles as floats for easier numerical comparison later
    matrices_y_rotated[0.0] = np.copy(matrix_step2) # 0 degree local Y rotation is just the matrix itself
    matrices_y_rotated[90.0] = matrix_step2 @ get_rotation_matrix_y(90)
    matrices_y_rotated[180.0] = matrix_step2 @ get_rotation_matrix_y(180)
    matrices_y_rotated[270.0] = matrix_step2 @ get_rotation_matrix_y(270) # Same as matrix_step2 @ get_rotation_matrix_y(-90)

    print("Matrices after Local Y rotations (0, 90, 180, 270 deg) relative to matrix_step2:")
    for angle, mat in matrices_y_rotated.items():
        # Print only the matrix for brevity
        print(f"  {angle:.0f} deg:\n{mat}")


    # Step 6: Find matrices whose X vector is within ±45 degrees of the FINAL Reference X vector (around local Y axis of matrix_step2)
    print("\n--- Step 6: Find matrices with X vector within ±45 deg of Final Reference X vector ---")
    ref_x_vector_final = matrix_reference_final[:, 0] # Use the FINAL reference X vector
    local_y_axis_for_comparison = matrix_step2[:, 1] # The local Y axis used for all rotations in Step 5

    # Define the acceptable angular range in degrees
    angle_range_deg = 45.0
    angle_range_rad = np.radians(angle_range_deg)

    matching_matrix_keys = [] # To store keys of matrices within the range
    matrix_selected = None # Variable to store the first matrix found within the range (for visualization)
    selected_angle_deg = None # The calculated angle for the selected matrix

    print(f"Checking angles within ±{angle_range_deg} degrees of the Final Reference X vector (around local Y axis from matrix_step2):")

    # Sort keys numerically for consistent output/selection if multiple matches exist
    sorted_angles = sorted(matrices_y_rotated.keys())

    for angle_deg_key in sorted_angles:
        current_matrix = matrices_y_rotated[angle_deg_key]
        current_x_vector = current_matrix[:, 0]

        # Calculate signed angle between ref_x_vector_final and current_x_vector around local_y_axis_for_comparison
        # Handle potential zero vectors (though unlikely for valid rotations)
        if np.linalg.norm(ref_x_vector_final) < 1e-8 or np.linalg.norm(current_x_vector) < 1e-8:
             print(f"Warning: Reference or current X vector for {angle_deg_key:.0f} deg matrix is near zero.")
             continue

        cross_prod = np.cross(ref_x_vector_final, current_x_vector)
        dot_prod = np.dot(ref_x_vector_final, current_x_vector)
        dot_with_axis = np.dot(local_y_axis_for_comparison, cross_prod)

        # Calculate the signed angle in radians
        # Handle potential atan2 input near zero if vectors are parallel or anti-parallel
        if np.isclose(dot_with_axis, 0, atol=1e-9) and np.isclose(dot_prod, 0, atol=1e-9):
            # Vectors are very close or exactly zero length (shouldn't happen for valid matrices)
            # Or vectors are collinear and perpendicular to the axis
             if dot_prod > 0: angle_rad = 0.0
             elif dot_prod < 0: angle_rad = np.pi
             else: angle_rad = 0.0 # Should not happen
        elif np.isclose(dot_with_axis, 0, atol=1e-9) and dot_prod > 0:
             angle_rad = 0.0 # Vectors are parallel
        elif np.isclose(dot_with_axis, 0, atol=1e-9) and dot_prod < 0:
             angle_rad = np.pi # Vectors are anti-parallel
        else:
             angle_rad = np.arctan2(dot_with_axis, dot_prod)


        # Convert to degrees for comparison
        angle_deg = np.degrees(angle_rad)

        # Normalize angle to be within (-180, 180] for easier comparison if needed,
        # but the range [-45, 45] check works directly with calculated angle.
        # angle_deg_normalized = (angle_deg + 180) % 360 - 180

        print(f"  Angle between Final Reference X and Y_{angle_deg_key:.0f}deg X: {angle_deg:.4f} degrees")

        # Check if the angle is within the ±45 degree range
        # Use np.isclose for float comparison near boundaries
        if angle_deg >= -angle_range_deg - 1e-9 and angle_deg <= angle_range_deg + 1e-9:
             print(f"  => Y_{angle_deg_key:.0f}deg matrix is within the ±{angle_range_deg} deg range.")
             matching_matrix_keys.append(angle_deg_key)
             # Select the first matrix found within the range
             if matrix_selected is None: # Only select the very first match
                 matrix_selected = current_matrix
                 selected_angle_deg = angle_deg # Store the actual calculated angle for the selected one


    print("\nSummary of results for Step 6:")
    if matching_matrix_keys:
        print(f"Matrices with X vector within ±{angle_range_deg} deg of Final Reference X vector (around local Y axis): {matching_matrix_keys}")
        print(f"Selected matrix is the one with {matching_matrix_keys[0]:.0f} degrees local Y rotation relative to matrix_step2.")
        print("Selected Matrix (matrix_selected):\n", matrix_selected)
        print(f"Calculated angle between Final Reference X and Selected X: {selected_angle_deg:.4f} degrees.")
    else:
        print(f"No matrix found with X vector within ±{angle_range_deg} deg of Final Reference X vector (around local Y axis).")
        matrix_selected = None # Ensure it's None if no match
        selected_angle_deg = None
        

    # Step 7: Visualize
    print("\n--- Step 7: Visualization ---")
    # Pass the selected matrix (can be None if no match)
    plot_comparison_scenario(
            matrix_step1,         # Initial matrix (R_robot)
            matrix_step2,         # Matrix after Step 2 (conditional Z rotation)
            matrix_reference_final, # Final Reference matrix (from Step 4)
            matrices_y_rotated,   # Y-rotated matrices (from Step 5)
            matrix_selected,      # Selected matrix (from Step 6)
            title=f"{title}: Rotation Analysis"
    )

    print(f"\n--- Analysis sequence finished for: {title} ---")
    return flip, matrix_selected

def matrecive(mmat):
    try:
            r_scipy = R.from_matrix(mmat)
            euler_angles_deg = np.degrees(r_scipy.as_euler('ZYX', degrees=False))
            print("\n변환된 오일러 각 (도):")
            print(f"Roll (X축): {euler_angles_deg[0]:.2f} deg")
            print(f"Pitch (Y축): {euler_angles_deg[1]:.2f} deg")
            print(f"Yaw (Z축): {euler_angles_deg[2]:.2f} deg")
    except Exception as e:
            pass
    return euler_angles_deg

def totalmove(amatrix_from_json):
        f_flip, amatrix_from_json = process_and_analyze_matrix_sequence(amatrix_from_json, title="Hardcoded Example Matrix")
        amatrix_from_json = amatrix_from_json @ get_rotation_matrix_x(-90)
        amatrix_from_json = amatrix_from_json @ get_rotation_matrix_z(-90)
        dddeg = matrecive(amatrix_from_json)
        print(dddeg)



# ====== 메인 루틴 ======
def _main():

    # --- Step 0: Apply camera-to-robot transformation ---
    # 카메라 기준 회전 행렬 (R_cam)
    R_cam = R_cam_to_robot = np.array([
        [1,  0,  0],
        [0,  1,  0],
        [0,  0,  1]
    ])

    # 카메라 -> 로봇 변환 회전 행렬 (글로벌 X축 기준 180도 회전)
    # 이는 [[1,0,0], [0,-1,0], [0,0,-1]] 행렬에 해당합니다.
    R_cam_to_robot = np.array([
        [1,  0,   0],
        [0, -1,   0],
        [0,  0,  -1]
    ])

    # 로봇 기준 회전 행렬로 변환 (R_robot = R_cam_to_robot @ R_cam)
    matrix_from_json_robot = R_cam_to_robot @ R_cam
    print("\nMatrix transformed to Robot Frame (R_robot = R_cam_to_robot @ R_cam):\n", matrix_from_json_robot)

    matrix_from_json = matrix_from_json_robot

    matrecive(matrix_from_json)

    for i in range(20):
        matrix_from_json = get_rotation_matrix_z(10) @ matrix_from_json
        totalmove(matrix_from_json)






if __name__ == "__main__":
    _main()





















###################################################################################################
###################################################################################################














