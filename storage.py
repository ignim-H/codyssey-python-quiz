"""state.json 파일 저장/불러오기를 담당하는 StateStore 클래스."""

import json
import os
import time
from pathlib import Path

class StateStore:
    """JSON 파일(UTF-8)로 게임 상태를 저장하고 불러온다."""

    def __init__(self, path):
        self.path = Path(path)

    def load(self):
        """(데이터 dict 또는 None, 안내 메시지) 를 돌려준다.

        - 파일이 없으면: (None, 기본 데이터 사용 안내)
        - JSON 이 깨졌거나 최상위가 객체가 아니면: 손상 파일을 .bak 으로 옮기고 (None, 복구 안내)
        - 읽기 오류(권한 등)면: (None, 오류 안내)
        """
        if not self.path.exists():
            return None, "📄 저장 파일이 없어 기본 퀴즈로 시작합니다."
        try:
            with self.path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except (json.JSONDecodeError, UnicodeDecodeError):
            backup = self.backup_corrupted()
            return None, f"⚠️ {self.path.name} 파일이 손상되어 기본 퀴즈로 복구합니다. (원본 보관: {backup})"
        except OSError as error:
            return None, f"⚠️ {self.path.name} 파일을 읽을 수 없어 기본 퀴즈로 시작합니다. ({error})"

        if not isinstance(data, dict):
            backup = self.backup_corrupted()
            return None, f"⚠️ {self.path.name} 형식이 올바르지 않아 기본 퀴즈로 복구합니다. (원본 보관: {backup})"
        return data, None

    REPLACE_RETRIES = 5  # Windows 에서 파일이 잠깐 잠겨 있을 때 다시 시도할 횟수

    def save(self, data):
        """데이터를 임시 파일에 먼저 쓴 뒤 교체한다. 저장 중 오류가 나도 기존 파일은 깨지지 않는다."""
        temp_path = self.path.with_name(self.path.name + ".tmp")
        try:
            with temp_path.open("w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=2)
            self._replace_with_retry(temp_path)
            return True
        except OSError as error:
            print(f"⚠️ 저장에 실패했습니다: {error}")
            return False

    def _replace_with_retry(self, temp_path):
        """임시 파일로 state.json 을 교체한다.

        Windows 에서는 방금 저장한 파일을 백신 검사 등이 잠깐 붙잡고 있으면
        교체가 PermissionError(WinError 5)로 거부될 수 있어, 잠시 기다렸다가 다시 시도한다.
        """
        for attempt in range(1, self.REPLACE_RETRIES + 1):
            try:
                os.replace(temp_path, self.path)
                return
            except PermissionError:
                if attempt == self.REPLACE_RETRIES:
                    raise
                time.sleep(0.1 * attempt)

    def backup_corrupted(self):
        """손상된 파일을 state.json.bak 으로 옮겨 두고 그 이름을 돌려준다."""
        backup_path = self.path.with_name(self.path.name + ".bak")
        try:
            os.replace(self.path, backup_path)
            return backup_path.name
        except OSError:
            return "보관 실패"
