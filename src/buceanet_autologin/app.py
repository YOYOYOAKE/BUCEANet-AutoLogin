from __future__ import annotations

import argparse
import sys
import threading
from collections.abc import Sequence
from dataclasses import dataclass
from typing import cast
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from playwright.sync_api import Error as PlaywrightError

from .runtime import (
    BrowserInstallError,
    configure_logging,
    ensure_browsers_installed,
    get_logger,
)
from .service import ServiceError, install_service, uninstall_service

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
    arguments = list(sys.argv[1:] if argv is None else argv)
    if arguments == ["service-run"]:
        from .service import run_service

        run_service()
        return 0

    parser = _build_parser()
    args = parser.parse_args(arguments)
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

        if command == "install-service":
            install_service(_credentials_from_args(args))
            return 0

        if command == "uninstall-service":
            uninstall_service()
            return 0

        if command == "install-chrome":
            ensure_browsers_installed()
            logger.info("Playwright Chromium 安装完成")
            return 0

    except (BrowserInstallError, ConfigError, PlaywrightError, ServiceError) as exc:
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

    ensure_browsers_installed()
    auto_login(credentials)


def run_forever(
    credentials: Credentials,
    stop_event: threading.Event | None = None,
) -> None:
    logger = get_logger()
    stop_signal = threading.Event() if stop_event is None else stop_event

    try:
        run_once(credentials)
    except PlaywrightError:
        logger.exception("登录失败")

    while not stop_signal.wait(POLL_INTERVAL_SECONDS):
        try:
            check_network_and_login(credentials)
        except PlaywrightError:
            logger.exception("登录失败")


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

    install_service_parser = subparsers.add_parser(
        "install-service",
        help="安装并启动 Windows 服务",
    )
    _add_credentials_options(install_service_parser)

    subparsers.add_parser(
        "uninstall-service",
        help="停止并卸载 Windows 服务",
    )

    subparsers.add_parser(
        "install-chrome",
        help="手动安装 Playwright Chromium 浏览器",
    )

    return parser


def _add_credentials_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("-i", "--id", dest="student_id", required=True, help="校园网学号")
    parser.add_argument("-p", "--password", required=True, help="校园网密码")


def _credentials_from_args(args: argparse.Namespace) -> Credentials:
    student_id = cast(str | None, getattr(args, "student_id", None))
    password = cast(str | None, getattr(args, "password", None))
    return create_credentials(student_id, password)
