"""퀴즈 게임 전체 흐름(메뉴 · 퀴즈 풀기 · 추가 · 목록 · 점수)을 관리하는 QuizGame 클래스."""

import os
import random
from datetime import datetime

from default_quizzes import create_default_quizzes
from quiz import Quiz
from storage import StateStore

LINE = "=" * 40
THIN_LINE = "-" * 40

class QuitGame(Exception):
    """Ctrl+C(KeyboardInterrupt) 또는 입력 종료(EOFError) 시 게임을 안전하게 끝내기 위한 신호."""

class QuizGame:
    """퀴즈 목록과 최고 점수를 가지고 게임 전체를 진행한다."""

    HINT_PENALTY = 0.5  # 힌트를 본 문제는 맞혀도 절반 점수
    HISTORY_SHOW = 5    # 점수 확인 화면에 보여 줄 최근 기록 수

    def __init__(self, state_path="state.json"):
        self.quizzes = []  # Quiz 객체 목록 (load 에서 채움)
        self.best_score = None   # 최고 점수(0~100). 아직 풀지 않았으면 None
        self.best_record = None  # 최고 점수를 낸 기록 {"correct": 맞힌 수, "total": 문제 수}
        self.history = []        # 모든 게임 기록 (날짜/시간, 문제 수, 정답 수, 점수)
        self.store = StateStore(state_path)
        self.echo_input = os.environ.get("QUIZ_ECHO_INPUT") == "1"  # 파일로 입력할 때 입력값도 화면에 표시
        # QUIZ_RANDOM_SEED 를 주면 출제 순서가 매번 같아진다 (테스트/시연용). 없으면 매번 무작위.
        self.random = random.Random(os.environ.get("QUIZ_RANDOM_SEED"))
        # 메뉴 번호 → (이름, 실행할 메서드). 메뉴를 추가할 때 이 목록만 고치면 된다.
        self.menu = [
            ("퀴즈 풀기", self.play_quiz),
            ("퀴즈 추가", self.add_quiz),
            ("퀴즈 목록", self.list_quizzes),
            ("점수 확인", self.show_score),
            ("퀴즈 삭제", self.delete_quiz),
            ("종료", None),
        ]

    # ------------------------------------------------------------------ 실행 흐름
    def run(self):
        """프로그램 시작점: 데이터를 불러오고, 종료를 고를 때까지 메뉴를 반복한다."""
        print(LINE)
        print("        🎯 나만의 퀴즈 게임 🎯")
        print(LINE)
        try:
            self.load()
            while True:
                choice = self.select_menu()
                name, action = self.menu[choice - 1]
                if action is None:
                    break
                action()
        except QuitGame:
            print("\n⚠️ 입력이 중단되었습니다.")
            if self.save():
                print("💾 현재까지의 데이터를 저장했습니다.")
            print("👋 게임을 안전하게 종료합니다.")
            return
        self.save()
        print("👋 게임을 종료합니다. 다음에 또 만나요!")

    def show_menu(self):
        """메뉴 목록을 출력한다."""
        print()
        print(LINE)
        for number, (name, _) in enumerate(self.menu, start=1):
            print(f"{number}. {name}")
        print(LINE)

    def select_menu(self):
        """메뉴를 보여 주고 올바른 번호를 받을 때까지 반복한다."""
        self.show_menu()
        return self.read_number("선택: ", 1, len(self.menu))

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

    def read_number(self, prompt, low, high, allowed_words=()):
        """low~high 범위의 정수를 받을 때까지 반복한다."""
        while True:
            text = self.read_line(prompt)
            if text == "":
                print(f"⚠️ 입력이 비어 있습니다. {low}-{high} 사이의 숫자를 입력하세요.")
                continue
            if text.lower() in allowed_words:  # 예: 힌트 보기 'h'
                return text.lower()
            try:
                number = int(text)
            except ValueError:
                print(f"⚠️ 잘못된 입력입니다. {low}-{high} 사이의 숫자를 입력하세요.")
                continue
            if not low <= number <= high:
                print(f"⚠️ 범위를 벗어났습니다. {low}-{high} 사이의 숫자를 입력하세요.")
                continue
            return number

    def read_text(self, prompt):
        """비어 있지 않은 문자열을 받을 때까지 반복한다."""
        while True:
            text = self.read_line(prompt)
            if text:
                return text
            print("⚠️ 빈 값은 입력할 수 없습니다. 다시 입력하세요.")

    # ------------------------------------------------------------------ 퀴즈 풀기
    def play_quiz(self):
        """퀴즈를 출제하고 정답 여부와 결과를 보여 준 뒤 최고 점수를 갱신한다."""
        if not self.quizzes:
            print("\n📭 등록된 퀴즈가 없습니다. 먼저 퀴즈를 추가해 주세요.")
            return

        available = len(self.quizzes)
        count = self.read_number(f"몇 문제를 풀까요? (1-{available}): ", 1, available)
        selected = self.random.sample(self.quizzes, count)  # 순서를 무작위로 섞어서 count 개 출제
        print(f"\n📝 퀴즈를 시작합니다! (총 {count}문제, 힌트를 보면 해당 문제는 절반 점수)")

        correct = 0
        points = 0.0
        hints_used = 0
        for number, quiz in enumerate(selected, start=1):
            print(THIN_LINE)
            quiz.display(number)
            used_hint = False
            while True:
                if quiz.has_hint() and not used_hint:
                    answer = self.read_number("정답 입력 (1-4, 힌트: h): ", 1, Quiz.CHOICE_COUNT, ("h",))
                else:
                    answer = self.read_number("정답 입력 (1-4): ", 1, Quiz.CHOICE_COUNT)
                if answer != "h":
                    break
                used_hint = True
                hints_used += 1
                print(f"💡 힌트: {quiz.hint}")

            if quiz.is_correct(answer):
                correct += 1
                points += self.HINT_PENALTY if used_hint else 1
                print("✅ 정답입니다!" + (" (힌트 사용: 절반 점수)" if used_hint else ""))
            else:
                print(f"❌ 오답입니다. 정답은 {quiz.answer}번 '{quiz.choices[quiz.answer - 1]}' 입니다.")
            print()

        total = count
        score = round(points / total * 100)
        print(LINE)
        print(f"🏆 결과: {total}문제 중 {correct}문제 정답! ({score}점, 힌트 {hints_used}회 사용)")
        self.record_result(score, correct, total, hints_used)
        if self.best_score is None or score > self.best_score:
            self.best_score = score
            self.best_record = {"correct": correct, "total": total}
            print("🎉 새로운 최고 점수입니다!")
        print(LINE)
        self.save()

    def record_result(self, score, correct, total, hints_used):
        """게임 한 판의 결과를 기록 히스토리에 추가한다."""
        self.history.append({
            "played_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total": total,
            "correct": correct,
            "hints_used": hints_used,
            "score": score,
        })

    # ------------------------------------------------------------------ 퀴즈 추가
    def add_quiz(self):
        """문제, 선택지 4개, 정답 번호를 입력받아 새 퀴즈를 등록한다."""
        print("\n📌 새로운 퀴즈를 추가합니다.")
        question = self.read_text("문제를 입력하세요: ")
        choices = [self.read_text(f"선택지 {index}: ") for index in range(1, Quiz.CHOICE_COUNT + 1)]
        answer = self.read_number(f"정답 번호 (1-{Quiz.CHOICE_COUNT}): ", 1, Quiz.CHOICE_COUNT)
        hint = self.read_line("힌트 (없으면 Enter): ")
        self.quizzes.append(Quiz(question, choices, answer, hint))
        self.save()
        print(f"\n✅ 퀴즈가 추가되었습니다! (총 {len(self.quizzes)}개)")

    # ------------------------------------------------------------------ 퀴즈 목록
    def list_quizzes(self):
        """등록된 퀴즈의 문제 목록을 출력한다."""
        if not self.quizzes:
            print("\n📭 등록된 퀴즈가 없습니다.")
            return
        print(f"\n📋 등록된 퀴즈 목록 (총 {len(self.quizzes)}개)")
        print(THIN_LINE)
        for number, quiz in enumerate(self.quizzes, start=1):
            mark = " 💡" if quiz.has_hint() else ""
            print(f"[{number}] {quiz.question}{mark}")
        print(THIN_LINE)

    # ------------------------------------------------------------------ 점수 확인
    def show_score(self):
        """최고 점수를 보여 준다. 아직 풀지 않았으면 안내한다."""
        if self.best_score is None:
            print("\n📭 아직 퀴즈를 풀지 않았습니다. 1번 '퀴즈 풀기'로 도전해 보세요!")
            return
        detail = ""
        if self.best_record:
            detail = f" ({self.best_record['total']}문제 중 {self.best_record['correct']}문제 정답)"
        print(f"\n🏆 최고 점수: {self.best_score}점{detail}")
        if self.history:
            print(f"\n🕘 최근 기록 (전체 {len(self.history)}회 중 최근 {min(len(self.history), self.HISTORY_SHOW)}회)")
            print(THIN_LINE)
            for record in self.history[-self.HISTORY_SHOW:][::-1]:
                print(
                    f"{record['played_at']} | {record['total']}문제 중 {record['correct']}개 정답"
                    f" | 힌트 {record['hints_used']}회 | {record['score']}점"
                )
            print(THIN_LINE)

    # ------------------------------------------------------------------ 퀴즈 삭제
    def delete_quiz(self):
        """번호를 골라 퀴즈를 삭제하고 파일에 반영한다."""
        if not self.quizzes:
            print("\n📭 삭제할 퀴즈가 없습니다.")
            return
        self.list_quizzes()
        count = len(self.quizzes)
        number = self.read_number(f"삭제할 퀴즈 번호 (1-{count}, 취소: 0): ", 0, count)
        if number == 0:
            print("↩️ 삭제를 취소했습니다.")
            return
        removed = self.quizzes.pop(number - 1)
        self.save()
        print(f"🗑️ '{removed.question}' 퀴즈를 삭제했습니다. (남은 퀴즈 {len(self.quizzes)}개)")

    # ------------------------------------------------------------------ 저장 / 불러오기
    def load(self):
        """state.json 을 불러온다. 없거나 손상되었으면 기본 퀴즈로 시작(복구)한다."""
        data, message = self.store.load()
        if data is not None:
            try:
                quizzes = [Quiz.from_dict(item) for item in data.get("quizzes", [])]
                best_score = data.get("best_score")
                if best_score is not None and (
                    not isinstance(best_score, int) or isinstance(best_score, bool) or not 0 <= best_score <= 100
                ):
                    raise ValueError("best_score 는 0~100 사이의 정수여야 합니다")
                best_record = data.get("best_record")
                history = data.get("history", [])
                if not isinstance(history, list):
                    raise ValueError("history 는 목록이어야 합니다")
            except (ValueError, TypeError, AttributeError) as error:
                backup = self.store.backup_corrupted()
                message = f"⚠️ state.json 내용이 올바르지 않아 기본 퀴즈로 복구합니다. ({error}, 원본 보관: {backup})"
            else:
                self.quizzes = quizzes
                self.best_score = best_score
                self.best_record = best_record if isinstance(best_record, dict) else None
                self.history = history
                best_text = f"{best_score}점" if best_score is not None else "기록 없음"
                print(f"📂 저장된 데이터를 불러왔습니다. (퀴즈 {len(quizzes)}개, 최고점수 {best_text})")
                return

        print(message)
        self.quizzes = create_default_quizzes()
        self.best_score = None
        self.best_record = None
        self.history = []
        self.save()

    def save(self):
        """퀴즈 목록과 최고 점수를 state.json 에 저장한다. 성공하면 True."""
        data = {
            "quizzes": [quiz.to_dict() for quiz in self.quizzes],
            "best_score": self.best_score,
            "best_record": self.best_record,
            "history": self.history,
        }
        return self.store.save(data)
