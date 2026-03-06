#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lexicon 앱 PyInstaller 빌드 스크립트
python build.py
"""

import io
import os
import sys
import subprocess
import shutil
from pathlib import Path

# Windows 콘솔 UTF-8 인코딩 설정
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def check_requirements():
    """PyInstaller 설치 확인"""
    try:
        import PyInstaller
        print("✓ PyInstaller 설치됨")
    except ImportError:
        print("❌ PyInstaller 설치 중...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✓ PyInstaller 설치 완료")

def check_files():
    """필수 파일 확인"""
    required = [
        "run_server.py",
        "static/icon.ico",
        "static/favicon.ico"
    ]
    
    missing = []
    for path in required:
        if not Path(path).exists():
            missing.append(path)
    
    if missing:
        print("❌ 누락 파일:", missing)
        print("   → static/icon.ico (256x256), static/favicon.ico (32x32) 필요")
        return False
    
    print("✓ 모든 파일 확인됨")
    return True

def build_app():
    """실행파일 빌드"""
    print("\n🚀 빌드 시작...")

    # FastAPI와 의존성 패키지들을 명시적으로 포함
    hidden_imports = [
        "fastapi",
        "uvicorn",
        "uvicorn.logging",
        "uvicorn.loops",
        "uvicorn.loops.auto",
        "uvicorn.protocols",
        "uvicorn.protocols.http",
        "uvicorn.protocols.http.auto",
        "uvicorn.protocols.websockets",
        "uvicorn.protocols.websockets.auto",
        "uvicorn.lifespan",
        "uvicorn.lifespan.on",
        "starlette",
        "starlette.applications",
        "starlette.routing",
        "starlette.middleware",
        "starlette.middleware.cors",
        "pydantic",
        "pydantic_core",
        "anyio",
        "h11",
        "httptools",
        "watchfiles",
        "websockets",
        "pythonnet",
        "clr_loader",
        "bottle",
        "webview",
        "app.core.paths",
        "app.core.config",
        "app.core.dependencies",
        "app.core.exceptions",
        "app.api.endpoints.quiz",
        "app.api.endpoints.settings",
        "app.api.endpoints.llm",
        "app.llm.providers",
        "app.llm.service",
        "app.llm.prompts",
        "app.models.requests",
        "app.models.responses",
        "app.utils.data_loader",
        # jaraco 패키지 (pkg_resources 의존성)
        "jaraco",
        "jaraco.text",
        "jaraco.functools",
        "jaraco.context",
        "jaraco.classes",
        "jaraco.collections",
    ]

    # 전체 패키지 수집이 필요한 모듈들
    collect_all = [
        "setuptools",
    ]

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--noconsole",
        "--name", "Lexicon",
        "--icon=static/icon.ico",
        "--add-data", "static;static",
        "--add-data", "app;app",
        "--add-data", "data;data",
        "--distpath", "dist",
        "--workpath", "build",
        "--specpath", ".",
    ]

    # hidden imports 추가
    for module in hidden_imports:
        cmd.extend(["--hidden-import", module])

    # collect-all 추가
    for package in collect_all:
        cmd.extend(["--collect-all", package])

    cmd.append("run_server.py")

    print("명령어:", " ".join(cmd))
    subprocess.check_call(cmd)
    print("✅ 빌드 완료: dist/Lexicon.exe")

def clean_build():
    """이전 빌드 정리"""
    for folder in ["build", "dist", "*.spec"]:
        shutil.rmtree(folder, ignore_errors=True)
    print("🧹 빌드 폴더 정리됨")

def main():
    print("🎯 Lexicon 빌더")
    print("=" * 50)
    
    check_requirements()
    if not check_files():
        return
    
    clean_build()
    build_app()
    
    exe_path = Path("dist/Lexicon.exe")
    if exe_path.exists():
        size = exe_path.stat().st_size / (1024*1024)
        print(f"\n🎉 완성! {exe_path.absolute()}")
        print(f"   📦 크기: {size:.1f} MB")
        print(f"   🚀 테스트: {exe_path}")
    else:
        print("❌ 빌드 실패")

if __name__ == "__main__":
    main()
