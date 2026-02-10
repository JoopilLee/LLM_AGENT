# meeting_room_agent/app/utils/prompt_manager.py - 프롬프트 YAML 로드 및 제공

from pathlib import Path
from typing import Any, Dict, Optional

import yaml


class PromptManager:
    """`data/prompts/` 경로의 .yml 파일을 로드하고, 키별로 프롬프트 문자열을 제공합니다."""

    DEFAULT_PROMPTS_DIR = "data/prompts"

    def __init__(self, prompts_dir: Optional[str] = None):
        """
        Args:
            prompts_dir: 프롬프트 yml이 있는 디렉터리. None이면 프로젝트 루트 기준 data/prompts 사용.
        """
        if prompts_dir is None:
            # app/utils 기준 → 프로젝트 루트 = parent.parent.parent
            base = Path(__file__).resolve().parent.parent.parent
            prompts_dir = base / self.DEFAULT_PROMPTS_DIR
        self.prompts_dir = Path(prompts_dir)
        self._cache: Dict[str, Dict[str, Any]] = {}

    def _load_yml(self, name: str) -> Dict[str, Any]:
        """캐시 후보 포함, 단일 yml 파일 로드."""
        if name in self._cache:
            return self._cache[name]
        path = self.prompts_dir / f"{name}.yml"
        if not path.exists():
            raise FileNotFoundError(f"Prompt file not found: {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if not isinstance(data, dict):
            raise ValueError(f"Invalid prompt yml (expected dict): {path}")
        self._cache[name] = data
        return data

    def get(self, name: str, **format_params: Any) -> str:
        """
        name에 해당하는 프롬프트의 content를 반환합니다.
        format_params가 있으면 content 문자열에 대해 str.format(**format_params)을 수행합니다.

        Args:
            name: .yml 파일명(확장자 제외). 예: router_intent, book_slots_extract
            **format_params: content 내 {key} 치환용. 예: today="2025-02-10"

        Returns:
            프롬프트 문자열 (앞뒤 공백 제거)
        """
        data = self._load_yml(name)
        content = data.get("content")
        if content is None:
            raise ValueError(f"Prompt '{name}' has no 'content' key in {self.prompts_dir / (name + '.yml')}")
        text = content.strip()
        if format_params:
            text = text.format(**format_params)
        return text

    def list_prompts(self) -> list:
        """로드 가능한 프롬프트 이름 목록 (확장자 제외)."""
        if not self.prompts_dir.exists():
            return []
        return [p.stem for p in self.prompts_dir.glob("*.yml")]
