"""
중앙 설정 관리자 (Thread-safe Singleton)
"""
import json
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional
import copy


class ConfigManager:
    """Thread-safe 싱글턴 설정 관리자"""

    _instance: Optional["ConfigManager"] = None
    _init_lock = threading.Lock()

    def __init__(self):
        raise RuntimeError("Use ConfigManager.get_instance() instead")

    @classmethod
    def get_instance(cls, config_path: Path = None) -> "ConfigManager":
        """싱글턴 인스턴스 반환"""
        if cls._instance is None:
            with cls._init_lock:
                if cls._instance is None:
                    instance = object.__new__(cls)
                    instance._lock = threading.Lock()
                    instance._config: Dict[str, Any] = {}
                    if config_path:
                        instance._config_path = Path(config_path)
                    else:
                        from . import paths as app_paths
                        instance._config_path = app_paths.get_config_path()
                    instance._load()
                    cls._instance = instance
        return cls._instance

    @property
    def data_dir(self) -> Path:
        """데이터 디렉토리 경로"""
        return self._config_path.parent

    def _load(self):
        """파일에서 설정 로드"""
        if self._config_path.exists():
            with open(self._config_path, 'r', encoding='utf-8') as f:
                self._config = json.load(f)
        else:
            self._config = {}

    def _save(self):
        """현재 설정을 파일로 저장"""
        self._config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._config_path, 'w', encoding='utf-8') as f:
            json.dump(self._config, f, ensure_ascii=False, indent=2)

    def get_all(self) -> Dict[str, Any]:
        """전체 설정 반환 (복사본)"""
        with self._lock:
            return copy.deepcopy(self._config)

    def get(self, key: str, default: Any = None) -> Any:
        """설정 값 조회"""
        with self._lock:
            return copy.deepcopy(self._config.get(key, default))

    def get_section(self, section: str) -> Dict[str, Any]:
        """특정 섹션 반환"""
        with self._lock:
            return copy.deepcopy(self._config.get(section, {}))

    def set(self, key: str, value: Any):
        """단일 키-값 설정"""
        with self._lock:
            self._config[key] = value
            self._save()

    def update(self, data: Dict[str, Any], preserve_sections: List[str] = None):
        """설정 업데이트 (지정된 섹션은 보존)"""
        with self._lock:
            if preserve_sections:
                preserved = {}
                for section in preserve_sections:
                    if section in self._config:
                        preserved[section] = copy.deepcopy(self._config[section])

            self._config.update(data)

            if preserve_sections:
                for section, value in preserved.items():
                    if section not in data:
                        self._config[section] = value

            self._save()

    def replace(self, data: Dict[str, Any], preserve_sections: List[str] = None):
        """설정 전체 교체 (지정된 섹션은 보존)"""
        with self._lock:
            preserved = {}
            if preserve_sections:
                for section in preserve_sections:
                    if section in self._config:
                        preserved[section] = copy.deepcopy(self._config[section])

            self._config = data

            for section, value in preserved.items():
                self._config[section] = value

            self._save()

    def set_section(self, section: str, data: Dict[str, Any]):
        """특정 섹션만 업데이트"""
        with self._lock:
            self._config[section] = data
            self._save()

    def reload(self):
        """파일에서 다시 로드"""
        with self._lock:
            self._load()

    @classmethod
    def reset(cls):
        """테스트용: 싱글턴 인스턴스 리셋"""
        with cls._init_lock:
            cls._instance = None
