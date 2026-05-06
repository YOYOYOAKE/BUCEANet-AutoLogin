from __future__ import annotations

import platform
import subprocess
import sys
from typing import TYPE_CHECKING

from .runtime import get_logger

if TYPE_CHECKING:
    from .app import Credentials

TASK_NAME = "BUCEANet-AutoLogin"


class StartupError(RuntimeError):
    """Raised when user startup task management cannot continue."""


def install_startup(credentials: Credentials) -> None:
    _ensure_windows()

    logger = get_logger()

    completed = _run_schtasks(
        [
            "/Create",
            "/TN",
            TASK_NAME,
            "/SC",
            "ONLOGON",
            "/TR",
            _startup_command(credentials),
            "/RL",
            "LIMITED",
            "/F",
        ]
    )
    if completed.returncode != 0:
        raise StartupError(_failure_message("自启动安装失败", completed))

    logger.info("自启动安装成功")
    _start_task()


def uninstall_startup() -> None:
    _ensure_windows()
    logger = get_logger()

    if not _task_exists():
        logger.info("未找到自启动任务")
        return

    _end_task()

    completed = _run_schtasks(["/Delete", "/TN", TASK_NAME, "/F"])
    if completed.returncode != 0:
        raise StartupError(_failure_message("自启动卸载失败", completed))

    logger.info("自启动卸载成功")


def _ensure_windows() -> None:
    if platform.system() != "Windows":
        raise StartupError("自启动仅支持 Windows")


def _task_exists() -> bool:
    completed = _run_schtasks(["/Query", "/TN", TASK_NAME])
    return completed.returncode == 0


def _start_task() -> None:
    logger = get_logger()
    completed = _run_schtasks(["/Run", "/TN", TASK_NAME])
    if completed.returncode == 0:
        logger.info("任务已启动")
        return

    logger.warning(_failure_message("任务未能启动", completed))


def _end_task() -> None:
    completed = _run_schtasks(["/End", "/TN", TASK_NAME])
    if completed.returncode == 0:
        get_logger().info("任务已停止")


def _startup_command(credentials: Credentials) -> str:
    return subprocess.list2cmdline(
        [
            sys.executable,
            "-m",
            "buceanet_autologin",
            "run",
            "forever",
            "-i",
            credentials.student_id,
            "-p",
            credentials.password,
        ]
    )


def _run_schtasks(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["schtasks.exe", *args],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def _failure_message(
    prefix: str,
    completed: subprocess.CompletedProcess[str],
) -> str:
    output = "\n".join(
        line
        for line in (completed.stdout.strip(), completed.stderr.strip())
        if line
    )
    if not output:
        return prefix
    return f"{prefix}: {output}"
