from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

APP_DIR_NAME = "BUCEANet-AutoLogin"
_PLAYWRIGHT_BROWSERS_PATH = "PLAYWRIGHT_BROWSERS_PATH"


class BrowserInstallError(RuntimeError):
    """Raised when Playwright browser installation fails or browser is not found."""


def runtime_dir() -> Path:
    return Path(os.environ["PROGRAMDATA"]) / APP_DIR_NAME


def _browsers_dir() -> Path:
    return runtime_dir() / "browsers"


def _configure_browsers_env() -> Path:
    path = _browsers_dir()
    os.environ[_PLAYWRIGHT_BROWSERS_PATH] = str(path)
    return path


def check_browsers_installed() -> bool:
    """检查 Playwright Chromium 是否已安装。"""
    _configure_browsers_env()
    return any(_browsers_dir().glob("chromium-*"))


def install_browsers() -> bool:
    """安装 Playwright Chromium，已安装时覆盖。返回是否安装成功。"""
    browsers_path = _browsers_dir()
    browsers_path.mkdir(parents=True, exist_ok=True)
    _configure_browsers_env()

    completed = subprocess.run(
        [sys.executable, "-m", "playwright", "install", "chromium"],
        check=False,
        env={**os.environ, _PLAYWRIGHT_BROWSERS_PATH: str(browsers_path)},
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    return completed.returncode == 0
