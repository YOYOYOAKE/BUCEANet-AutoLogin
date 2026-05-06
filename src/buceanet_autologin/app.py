from __future__ import annotations

import argparse
import threading
from collections.abc import Sequence
from dataclasses import dataclass
from typing import cast
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .runtime import BrowserInstallError, configure_logging, get_logger
from .startup import StartupError, install_startup, uninstall_startup

NETWORK_CHECK_URL = "https://www.cnki.net/"
NETWORK_TIMEOUT_SECONDS = 5.0
POLL_INTERVAL_SECONDS = 60.0


class ConfigError(ValueError):
    """Raised when required command line configuration is missing."""


@dataclass(frozen=True, slots=True)
class Credentials:
    student_id: str
    password: str


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    command = cast(str, args.command)
    logger = configure_logging()

    try:
        if command == "run":
            credentials = _credentials_from_args(args)
            mode = cast(str | None, getattr(args, "mode", None))
            if mode == "forever":
                stop_event = threading.Event()
                try:
                    run_forever(credentials, stop_event)
                except KeyboardInterrupt:
                    stop_event.set()
                    logger.info("正在退出")
            else:
                run_once(credentials)
            return 0

        if command == "install-startup":
            install_startup(_credentials_from_args(args))
            return 0

        if command == "uninstall-startup":
            uninstall_startup()
            return 0

    except (BrowserInstallError, ConfigError, StartupError) as exc:
        logger.error("%s", exc)
        return 2

    parser.error("未知命令")
    return 2


def create_credentials(student_id: str | None, password: str | None) -> Credentials:
    normalized_student_id = "" if student_id is None else student_id.strip()
    normalized_password = "" if password is None else password

    missing: list[str] = []
    if not normalized_student_id:
        missing.append("-i")
    if not normalized_password:
        missing.append("-p")

    if missing:
        names = ", ".join(missing)
        raise ConfigError(f"缺少必要参数: {names}")

    return Credentials(student_id=normalized_student_id, password=normalized_password)


def run_once(credentials: Credentials) -> None:
    from .portal import auto_login

    auto_login(credentials)
    get_logger().info("登录完成")


def run_forever(
    credentials: Credentials,
    stop_event: threading.Event | None = None,
) -> None:
    stop_signal = threading.Event() if stop_event is None else stop_event

    run_once(credentials)

    while not stop_signal.wait(POLL_INTERVAL_SECONDS):
        check_network_and_login(credentials)


def check_network_and_login(credentials: Credentials) -> None:
    from .portal import auto_login

    logger = get_logger()
    request = Request(
        NETWORK_CHECK_URL,
        headers={"User-Agent": "buceanet-autologin/1.0"},
    )

    try:
        with urlopen(request, timeout=NETWORK_TIMEOUT_SECONDS) as response:
            response.read(1)
    except HTTPError as exc:
        logger.debug("网络检查返回 HTTP %s，", exc.code)
    except (OSError, TimeoutError, URLError):
        logger.info("网络连接失败，重新登录")
        auto_login(credentials)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="buceanet-autologin",
        description="BUCEA campus network auto-login",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="运行自动登录")
    run_parser.add_argument(
        "mode",
        choices=["forever"],
        nargs="?",
        help="持续运行并定时检测网络",
    )
    _add_credentials_options(run_parser)

    install_startup_parser = subparsers.add_parser(
        "install-startup",
        help="安装当前用户登录自启动任务",
    )
    _add_credentials_options(install_startup_parser)

    subparsers.add_parser(
        "uninstall-startup",
        help="删除当前用户登录自启动任务",
    )

    return parser


def _add_credentials_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("-i", "--id", dest="student_id", required=True, help="校园网学号")
    parser.add_argument("-p", "--password", required=True, help="校园网密码")


def _credentials_from_args(args: argparse.Namespace) -> Credentials:
    student_id = cast(str | None, getattr(args, "student_id", None))
    password = cast(str | None, getattr(args, "password", None))
    return create_credentials(student_id, password)
