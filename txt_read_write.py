# txt파일에 읽고 쓰기 예시입니다.

import os
import numpy as np

# 저장할 파일 이름
filename = "point_start.txt"

# 예시로 주어진 6개 값
data = np.array([-156.951, 9.552, 136.832, -56.353, 89.999, 66.82])

# 1️⃣ 파일 존재 확인 및 저장
if not os.path.exists(filename):
    print(f"'{filename}' 파일이 없어서 새로 생성합니다.")
    with open(filename, "w") as f:
        np.savetxt(f, [data], fmt="%.6f")
else:
    print(f"'{filename}' 파일이 존재합니다. 데이터 이어쓰기.")
    with open(filename, "a") as f:
        np.savetxt(f, [data], fmt="%.6f")

print("데이터 저장 완료 ✅")

# 2️⃣ 파일에서 불러오기 (jointarray에 저장)
jointarray = np.loadtxt(filename)
print("\n파일에서 불러온 jointarray:")
print(jointarray)

