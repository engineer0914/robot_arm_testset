import inspect
import rbpodo

cls = rbpodo.Cobot
print(f"🏷️ 클래스: {cls.__name__} (move 관련 메서드 - 상세 정보)\n")

for name, member in inspect.getmembers(cls):
    if callable(member) and "move" in name.lower():
        print(f"🔹 {name}")
        doc = inspect.getdoc(member)
        if doc:
            lines = doc.splitlines()
            # 첫 줄(요약)은 항상 표시
            print(f"   📝 요약: {lines[0]}")
            # 두 번째 줄이 있으면 표시, 없으면 "(설명 없음)"
            if len(lines) >= 2 and lines[1].strip():
                print(f"   📋 상세: {lines[1]}")
            else:
                print(f"   📋 상세: (설명 없음)")
            # 세 번째 줄이 있으면 표시, 없으면 "(설명 없음)"
            if len(lines) >= 3 and lines[2].strip():
                print(f"   💡 추가: {lines[2]}")
            else:
                print(f"   💡 추가: (설명 없음)")
        else:
            print("   └ 설명: (없음)")
        print()  # 함수 사이 빈 줄

