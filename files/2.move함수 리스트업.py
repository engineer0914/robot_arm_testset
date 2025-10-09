import inspect
import rbpodo

cls = rbpodo.Cobot
print(f"🏷️ 클래스: {cls.__name__} (move 관련 메서드)\n")

for name, member in inspect.getmembers(cls):
    if callable(member) and "move" in name.lower():
        print(f"🔹 {name}")
        doc = inspect.getdoc(member)
        if doc:
            print(f"   └ 설명: {doc.splitlines()[0]}")
        else:
            print("   └ 설명: (없음)")
        print()  # 함수 사이에 빈 줄 추가

