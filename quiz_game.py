"""퀴즈 게임 전체 흐름(메뉴 · 퀴즈 풀기 · 추가 · 목록 · 점수)을 관리하는 QuizGame 클래스."""

import os

from default_quizzes import create_default_quizzes

LINE = "=" * 40
THIN_LINE = "-" * 40

class QuitGame(Exception):
    """Ctrl+C(KeyboardInterrupt) 또는 입력 종료(EOFError) 시 게임을 안전하게 끝내기 위한 신호."""

class QuizGame:
    """퀴즈 목록과 최고 점수를 가지고 게임 전체를 진행한다."""

    def __init__(self):
        self.quizzes = create_default_quizzes()  # Quiz 객체 목록
        self.best_score = None   # 최고 점수(0~100). 아직 풀지 않았으면 None
        self.best_record = None  # 최고 점수를 낸 기록 {"correct": 맞힌 수, "total": 문제 수}
        self.echo_input = os.environ.get("QUIZ_ECHO_INPUT") == "1"  # 파일로 입력할 때 입력값도 화면에 표시
    MENU_ITEMS = ["퀴즈 풀기", "퀴즈 추가", "퀴즈 목록", "점수 확인", "종료"]

    # ------------------------------------------------------------------ 실행 흐름
    def run(self):
        """프로그램 시작점: 데이터를 불러오고, 종료를 고를 때까지 메뉴를 반복한다."""
        print(LINE)
        print("        🎯 나만의 퀴즈 게임 🎯")
        print(LINE)
        try:
            while True:
                choice = self.select_menu()
                if choice == 1:
                    self.play_quiz()
                elif choice == 2:
                    print("🚧 준비 중인 기능입니다.")
                elif choice == 3:
                    print("🚧 준비 중인 기능입니다.")
                elif choice == 4:
                    print("🚧 준비 중인 기능입니다.")
                else:
                    break
        except QuitGame:
            print("\n⚠️ 입력이 중단되었습니다.")
            print("👋 게임을 안전하게 종료합니다.")
            return
        print("👋 게임을 종료합니다. 다음에 또 만나요!")

    def show_menu(self):
        """메뉴 목록을 출력한다."""
        print()
        print(LINE)
        for number, name in enumerate(self.MENU_ITEMS, start=1):
            print(f"{number}. {name}")
        print(LINE)

    def select_menu(self):
        """메뉴를 보여 주고 올바른 번호를 받을 때까지 반복한다."""
        self.show_menu()
        return self.read_number("선택: ", 1, len(self.MENU_ITEMS))

    # ------------------------------------------------------------------ 입력 처리
    def read_line(self, prompt):
        """한 줄을 입력받아 앞뒤 공백을 제거해 돌려준다. Ctrl+C / 입력 종료는 QuitGame 으로 바꾼다."""
        try:
            value = input(prompt)
        except (KeyboardInterrupt, EOFError) as error:
            raise QuitGame from error
        if self.echo_input:
            print(value)
        return value.strip()

    def read_number(self, prompt, low, high):
        """low~high 범위의 정수를 받을 때까지 반복한다."""
        while True:
            text = self.read_line(prompt)
            if text == "":
                print(f"⚠️ 입력이 비어 있습니다. {low}-{high} 사이의 숫자를 입력하세요.")
                continue
            try:
                number = int(text)
            except ValueError:
                print(f"⚠️ 잘못된 입력입니다. {low}-{high} 사이의 숫자를 입력하세요.")
                continue
            if not low <= number <= high:
                print(f"⚠️ 범위를 벗어났습니다. {low}-{high} 사이의 숫자를 입력하세요.")
                continue
            return number

    # ------------------------------------------------------------------ 퀴즈 풀기
    def play_quiz(self):
        """퀴즈를 출제하고 정답 여부와 결과를 보여 준 뒤 최고 점수를 갱신한다."""
        if not self.quizzes:
            print("\n📭 등록된 퀴즈가 없습니다. 먼저 퀴즈를 추가해 주세요.")
            return

        selected = list(self.quizzes)
        print(f"\n📝 퀴즈를 시작합니다! (총 {len(selected)}문제)")
        correct = 0
        for number, quiz in enumerate(selected, start=1):
            print(THIN_LINE)
            quiz.display(number)
            answer = self.read_number("정답 입력 (1-4): ", 1, 4)
            if quiz.is_correct(answer):
                correct += 1
                print("✅ 정답입니다!")
            else:
                print(f"❌ 오답입니다. 정답은 {quiz.answer}번 '{quiz.choices[quiz.answer - 1]}' 입니다.")
            print()

        total = len(selected)
        score = round(correct / total * 100)
        print(LINE)
        print(f"🏆 결과: {total}문제 중 {correct}문제 정답! ({score}점)")
        if self.best_score is None or score > self.best_score:
            self.best_score = score
            self.best_record = {"correct": correct, "total": total}
            print("🎉 새로운 최고 점수입니다!")
        print(LINE)
