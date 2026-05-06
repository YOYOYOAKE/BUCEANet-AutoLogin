from __future__ import annotations

import logging
import os
import subprocess
import sys
import threading
from logging.handlers import RotatingFileHandler
from pathlib import Path

APP_DIR_NAME = "BUCEANet-AutoLogin"
LOGGER_NAME = "buceanet_autologin"
PLAYWRIGHT_BROWSERS_PATH = "PLAYWRIGHT_BROWSERS_PATH"
RUNTIME_DIR_ENV = "BUCEANET_RUNTIME_DIR"

_install_lock = threading.Lock()
_browsers_ready = False


class BrowserInstallError(RuntimeError):
    """Raised when Playwright browser installation fails."""


def runtime_dir() -> Path:
    override = os.environ.get(RUNTIME_DIR_ENV)
    if override:
        return Path(override)

    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        return Path(local_app_data) / APP_DIR_NAME
    if os.name == "nt":
        return Path.home() / "AppData" / "Local" / APP_DIR_NAME
    return Path.home() / ".local" / "state" / "buceanet-autologin"


def logs_dir() -> Path:
    return runtime_dir() / "logs"


def browsers_dir() -> Path:
    return runtime_dir() / "browsers"


def ensure_runtime_dirs() -> None:
    logs_dir().mkdir(parents=True, exist_ok=True)
    browsers_dir().mkdir(parents=True, exist_ok=True)


def configure_playwright_browsers_path() -> Path:
    path = browsers_dir()
    os.environ[PLAYWRIGHT_BROWSERS_PATH] = str(path)
    return path


def configure_logging() -> logging.Logger:
    ensure_runtime_dirs()

    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    file_handler = RotatingFileHandler(
        logs_dir() / "app.log",
        maxBytes=1_000_000,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


def get_logger() -> logging.Logger:
    return logging.getLogger(LOGGER_NAME)


def ensure_browsers_installed() -> None:
    global _browsers_ready

    if _browsers_ready:
        return

    with _install_lock:
        if _browsers_ready:
            return

        ensure_runtime_dirs()
        path = configure_playwright_browsers_path()
        logger = get_logger()
        logger.info("检查 Playwright Chromium: %s", path)

        completed = _run_playwright_install()
        if completed.returncode != 0:
            _log_install_failure(completed)
            raise BrowserInstallError(
                "Playwright Chromium 安装失败，请检查网络连接后重新运行"
            )

        _browsers_ready = True
        logger.info("Playwright Chromium 已就绪")


def _run_playwright_install() -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env[PLAYWRIGHT_BROWSERS_PATH] = str(browsers_dir())
    return subprocess.run(
        [sys.executable, "-m", "playwright", "install", "chromium"],
        check=False,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def _log_install_failure(completed: subprocess.CompletedProcess[str]) -> None:
    output = "\n".join(
        line
        for line in (completed.stdout.strip(), completed.stderr.strip())
        if line
    )
    if output:
        get_logger().error("Playwright Chromium 安装失败:\n%s", output)
