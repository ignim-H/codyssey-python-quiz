"""퀴즈 게임 실행 파일.  사용법: python main.py"""

import sys

from quiz_game import QuizGame

# 프로젝트 루트(이 파일이 있는 폴더)의 state.json 에 저장한다. 어느 위치에서 실행해도 같은 파일을 쓴다.

def use_utf8_console():
    """Windows 터미널(Git Bash 등)에서도 한글/이모지가 깨지지 않도록 입출력을 UTF-8 로 맞춘다."""
    for stream in (sys.stdin, sys.stdout):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

def main():
    use_utf8_console()
    game = QuizGame()
    game.run()

if __name__ == "__main__":
    main()
