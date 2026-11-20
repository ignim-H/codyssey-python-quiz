"""퀴즈 게임 단위 테스트 (표준 라이브러리 unittest 만 사용).

실행: python -m unittest discover -s tests -v
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

# 프로젝트 루트를 import 경로에 추가
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from quiz import Quiz  # noqa: E402
from quiz_game import QuizGame  # noqa: E402
from storage import StateStore  # noqa: E402


class QuizTest(unittest.TestCase):
    def setUp(self):
        self.quiz = Quiz("1+1=?", ["1", "2", "3", "4"], 2, "짝수")

    def test_is_correct(self):
        self.assertTrue(self.quiz.is_correct(2))
        self.assertFalse(self.quiz.is_correct(3))

    def test_dict_round_trip_keeps_hint(self):
        restored = Quiz.from_dict(self.quiz.to_dict())
        self.assertEqual(restored.to_dict(), self.quiz.to_dict())
        self.assertTrue(restored.has_hint())

    def test_from_dict_rejects_bad_data(self):
        bad_items = [
            "not a dict",
            {"question": "", "choices": ["a", "b", "c", "d"], "answer": 1},
            {"question": "q", "choices": ["a", "b"], "answer": 1},
            {"question": "q", "choices": ["a", "b", "c", "d"], "answer": 5},
            {"question": "q", "choices": ["a", "b", "c", "d"], "answer": True},
        ]
        for item in bad_items:
            with self.subTest(item=item), self.assertRaises(ValueError):
                Quiz.from_dict(item)


class StateStoreTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "state.json"
        self.store = StateStore(self.path)

    def tearDown(self):
        self.temp.cleanup()

    def test_missing_file(self):
        data, message = self.store.load()
        self.assertIsNone(data)
        self.assertIn("저장 파일이 없어", message)

    def test_save_and_load_utf8(self):
        self.assertTrue(self.store.save({"quizzes": [], "best_score": 80, "note": "한글"}))
        data, _ = self.store.load()
        self.assertEqual(data["note"], "한글")
        self.assertIn("한글", self.path.read_text(encoding="utf-8"))

    def test_corrupted_file_is_backed_up(self):
        self.path.write_text("{broken", encoding="utf-8")
        data, message = self.store.load()
        self.assertIsNone(data)
        self.assertIn("손상", message)
        self.assertTrue(self.path.with_name("state.json.bak").exists())


class QuizGameTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "state.json"
        self.game = QuizGame(self.path)

    def tearDown(self):
        self.temp.cleanup()

    def test_read_number_retries_until_valid(self):
        inputs = ["abc", "9", "", "  3  "]
        with patch("builtins.input", side_effect=inputs), patch("builtins.print"):
            self.assertEqual(self.game.read_number("선택: ", 1, 6), 3)

    def test_first_run_uses_default_quizzes_and_creates_file(self):
        with patch("builtins.print"):
            self.game.load()
        self.assertGreaterEqual(len(self.game.quizzes), 5)
        self.assertTrue(self.path.exists())

    def test_invalid_schema_recovers_with_defaults(self):
        self.path.write_text(json.dumps({"quizzes": [{"question": "x"}], "best_score": 50}), encoding="utf-8")
        with patch("builtins.print"):
            self.game.load()
        self.assertGreaterEqual(len(self.game.quizzes), 5)
        self.assertIsNone(self.game.best_score)

    def test_ctrl_c_saves_and_exits_safely(self):
        with patch("builtins.input", side_effect=KeyboardInterrupt), patch("builtins.print"):
            self.game.run()  # 예외가 밖으로 나오지 않아야 한다
        self.assertTrue(self.path.exists())

    def test_best_score_persists_between_runs(self):
        with patch("builtins.print"):
            self.game.load()
        self.game.quizzes = [Quiz("q", ["a", "b", "c", "d"], 1)]
        with patch("builtins.input", side_effect=["1", "1"]), patch("builtins.print"):
            self.game.play_quiz()
        self.assertEqual(self.game.best_score, 100)

        reloaded = QuizGame(self.path)
        with patch("builtins.print"):
            reloaded.load()
        self.assertEqual(reloaded.best_score, 100)
        self.assertEqual(len(reloaded.history), 1)


if __name__ == "__main__":
    unittest.main()
