import inspect
import rbpodo

def explore_rbpodo_methods(search_keyword="move"):
    """rbpodo.Cobot 클래스의 메서드를 탐색하는 함수"""
    cls = rbpodo.Cobot
    
    print(f"🏷️ 클래스: {cls.__name__} ('{search_keyword}' 관련 메서드)\n")
    
    for name, member in inspect.getmembers(cls):
        if callable(member) and search_keyword.lower() in name.lower():
            print(f"🔹 {name}")
            doc = inspect.getdoc(member)
            
            if doc:
                lines = doc.splitlines()
                print(f"   └ 요약: {lines}")  # 첫 번째 줄
                
                # 전체 docstring이 필요한 경우
                if len(lines) > 1:
                    print("   └ 전체 설명:")
                    for i, line in enumerate(lines):
                        print(f"      {i+1}: {line}")
            else:
                print("   └ 설명: (없음)")
            print()  # 빈 줄 추가

# 사용 예시
explore_rbpodo_methods("move")  # move 관련 메서드 찾기
explore_rbpodo_methods("joint") # joint 관련 메서드 찾기

