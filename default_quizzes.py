"""기본 퀴즈 데이터: 주제 - 개발 도구 기초 (리눅스 · Docker · Git)."""

from quiz import Quiz

def create_default_quizzes():
    """state.json 이 없거나 손상되었을 때 사용할 기본 퀴즈 목록을 만든다."""
    return [
        Quiz(
            "현재 작업 디렉토리의 절대 경로를 출력하는 리눅스 명령어는?",
            ["ls", "pwd", "cd", "echo"],
            2,
            "print working directory 의 줄임말",
        ),
        Quiz(
            "chmod 755 를 적용한 파일의 권한 표기로 올바른 것은?",
            ["rwxr-xr-x", "rw-r--r--", "rwx------", "r-xr-xr-x"],
            1,
            "r=4, w=2, x=1 을 더한 값이 7, 5, 5",
        ),
        Quiz(
            "호스트의 8080 포트를 컨테이너의 80 포트에 연결하는 docker run 옵션은?",
            ["-v 8080:80", "-p 80:8080", "-p 8080:80", "-e 8080:80"],
            3,
            "-p 호스트포트:컨테이너포트 순서",
        ),
        Quiz(
            "컨테이너를 삭제해도 데이터를 유지하려면 무엇을 연결해야 할까?",
            ["docker logs", "Docker 볼륨", "docker stats", "이미지 태그"],
            2,
            "docker volume create 로 만든다",
        ),
        Quiz(
            "Dockerfile 에서 베이스 이미지를 지정하는 명령어는?",
            ["RUN", "COPY", "FROM", "EXPOSE"],
            3,
            "Dockerfile 의 첫 줄에 주로 온다",
        ),
        Quiz(
            "원격 저장소의 변경 사항을 가져와 현재 브랜치에 합치는 Git 명령어는?",
            ["git push", "git clone", "git pull", "git init"],
            3,
            "'끌어온다'는 뜻",
        ),
        Quiz(
            "새 브랜치를 만들면서 바로 그 브랜치로 이동하는 명령어는?",
            ["git checkout -b feature", "git merge feature", "git branch -d feature", "git log feature"],
            1,
            "-b 옵션은 branch 를 새로 만든다는 뜻",
        ),
    ]
