"""개별 퀴즈 한 문제를 표현하는 Quiz 클래스."""

class Quiz:
    """문제(question), 선택지 4개(choices), 정답 번호(answer, 1~4)를 가진 퀴즈 한 문제."""

    CHOICE_COUNT = 4

    def __init__(self, question, choices, answer, hint=""):
        self.question = question      # 문제 문장 (str)
        self.choices = list(choices)  # 선택지 4개 (list[str])
        self.answer = answer          # 정답 번호 (int, 1~4)
        self.hint = hint              # 힌트 (str, 없으면 빈 문자열)

    def display(self, number=None):
        """문제와 선택지를 화면에 출력한다."""
        print(f"[문제 {number}]" if number is not None else "[문제]")
        print(self.question)
        print()
        for index, choice in enumerate(self.choices, start=1):
            print(f"  {index}. {choice}")
        print()

    def is_correct(self, choice_number):
        """사용자가 고른 번호가 정답이면 True."""
        return choice_number == self.answer

    def has_hint(self):
        """힌트가 등록되어 있으면 True."""
        return bool(self.hint)

    def to_dict(self):
        """JSON 으로 저장할 수 있는 dict 로 변환한다."""
        data = {
            "question": self.question,
            "choices": self.choices,
            "answer": self.answer,
        }
        if self.hint:
            data["hint"] = self.hint
        return data

    @classmethod
    def from_dict(cls, data):
        """dict 를 Quiz 로 바꾼다. 형식이 잘못되었으면 ValueError 를 발생시킨다."""
        if not isinstance(data, dict):
            raise ValueError("퀴즈 항목이 객체 형식이 아닙니다")

        question = data.get("question")
        choices = data.get("choices")
        answer = data.get("answer")
        hint = data.get("hint", "")

        if not isinstance(question, str) or not question.strip():
            raise ValueError("question 이 비어 있거나 문자열이 아닙니다")
        if (
            not isinstance(choices, list)
            or len(choices) != cls.CHOICE_COUNT
            or not all(isinstance(choice, str) and choice.strip() for choice in choices)
        ):
            raise ValueError("choices 는 비어 있지 않은 문자열 4개여야 합니다")
        # bool 은 int 의 하위 타입이라 따로 걸러낸다 (True == 1 방지)
        if not isinstance(answer, int) or isinstance(answer, bool) or not 1 <= answer <= cls.CHOICE_COUNT:
            raise ValueError("answer 는 1~4 사이의 정수여야 합니다")
        if not isinstance(hint, str):
            raise ValueError("hint 는 문자열이어야 합니다")

        return cls(question.strip(), [choice.strip() for choice in choices], answer, hint.strip())
