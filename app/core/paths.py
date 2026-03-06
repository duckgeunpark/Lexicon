"""
앱 전역 경로 레지스트리

PyInstaller 빌드와 개발 환경 모두에서 올바른 경로를 제공합니다.

경로 구조:
  개발 환경:  __file__ 기준 → lexicon/
  빌드 환경:  sys.executable 기준 → dist/ (exe 옆)

  - BASE_DIR: 실행 파일(exe) 또는 프로젝트 루트
  - DATA_DIR: BASE_DIR/data  (config.json, quiz.json 등 - 읽기/쓰기)
  - RESOURCE_DIR: 번들 리소스 (static 등 - 읽기 전용, 빌드 시 _MEIPASS)
"""
import sys
from pathlib import Path
from typing import Optional


_base_dir: Optional[Path] = None
_data_dir: Optional[Path] = None
_resource_dir: Optional[Path] = None


def _is_frozen() -> bool:
    """PyInstaller 번들 환경인지 확인"""
    return getattr(sys, 'frozen', False)


def _detect_base_dir() -> Path:
    """실행 파일 또는 프로젝트 루트 경로 자동 감지"""
    if _is_frozen():
        return Path(sys.executable).parent
    else:
        # app/core/paths.py → 프로젝트 루트(lexicon/)
        return Path(__file__).parent.parent.parent


def _detect_resource_dir() -> Path:
    """번들 리소스 경로 자동 감지"""
    if _is_frozen():
        return Path(sys._MEIPASS)
    else:
        return _detect_base_dir()


def init(base_dir: Path = None, data_dir: Path = None):
    """경로 초기화 (run_server.py에서 최초 1회 호출)

    Args:
        base_dir: 프로젝트/실행파일 기본 경로
        data_dir: 데이터 디렉토리 경로 (기본: base_dir/data)
    """
    global _base_dir, _data_dir, _resource_dir

    _base_dir = (base_dir or _detect_base_dir()).resolve()
    _data_dir = (data_dir or _base_dir / "data").resolve()
    _resource_dir = _detect_resource_dir().resolve()


def get_base_dir() -> Path:
    """프로젝트/실행파일 기본 경로"""
    if _base_dir is None:
        init()
    return _base_dir


def get_data_dir() -> Path:
    """데이터 디렉토리 (config.json, quiz.json 등)"""
    if _data_dir is None:
        init()
    return _data_dir


def get_resource_dir() -> Path:
    """번들 리소스 디렉토리 (static 등)"""
    if _resource_dir is None:
        init()
    return _resource_dir


def get_config_path() -> Path:
    """config.json 절대경로"""
    return get_data_dir() / "config.json"


def get_static_dir() -> Path:
    """static 폴더 절대경로"""
    return get_resource_dir() / "static"
