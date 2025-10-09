import inspect
import rbpodo

cls = rbpodo.Cobot
print(f"🏷️ 클래스: {cls.__name__}\n")

for name, member in inspect.getmembers(cls):
    if callable(member):
        print(f"🔹 {name} (메서드/호출 가능)")
        doc = inspect.getdoc(member)
        if doc:
            print(f"   └ 설명: {doc.splitlines()[0]}")
        else:
            print("   └ 설명: (없음)")

