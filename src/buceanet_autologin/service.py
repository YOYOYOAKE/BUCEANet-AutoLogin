from __future__ import annotations

import ctypes
import os
import platform
import subprocess
import sys
import threading
from collections.abc import Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Protocol, cast

import pywintypes
import servicemanager
import win32service
import win32serviceutil

from .runtime import configure_logging, get_logger

if TYPE_CHECKING:
    from .app import Credentials

SERVICE_NAME = "BUCEANet-AutoLogin"
SERVICE_DISPLAY_NAME = "BUCEANet-AutoLogin"
SERVICE_DESCRIPTION = "BUCEA 校园网自动登录服务"
STUDENT_ID_OPTION = "StudentId"
PASSWORD_OPTION = "Password"

ERROR_SERVICE_ALREADY_RUNNING = 1056
ERROR_SERVICE_DOES_NOT_EXIST = 1060
ERROR_SERVICE_NOT_ACTIVE = 1062
ERROR_SERVICE_EXISTS = 1073


class ServiceError(RuntimeError):
    """Raised when Windows service management cannot continue."""


class _Shell32(Protocol):
    def IsUserAnAdmin(self) -> int: ...


class _WinDll(Protocol):
    shell32: _Shell32


class BUCEANetAutoLoginService(win32serviceutil.ServiceFramework):
    _svc_name_ = SERVICE_NAME
    _svc_display_name_ = SERVICE_DISPLAY_NAME
    _svc_description_ = SERVICE_DESCRIPTION

    def __init__(self, args: Sequence[str]) -> None:
        super().__init__(args)
        self._stop_event = threading.Event()

    def SvcStop(self) -> None:
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self._stop_event.set()

    def SvcDoRun(self) -> None:
        _configure_service_runtime_dir()
        configure_logging()
        logger = get_logger()
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)

        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, ""),
        )

        try:
            from .app import run_forever

            run_forever(_load_service_credentials(), self._stop_event)
        except Exception:
            logger.exception("服务运行失败")
            servicemanager.LogErrorMsg("BUCEANet-AutoLogin 服务运行失败")
            raise
        finally:
            self.ReportServiceStatus(win32service.SERVICE_STOPPED)


def install_service(credentials: Credentials) -> None:
    _ensure_windows()
    _ensure_admin()

    logger = get_logger()

    service_exists = False

    try:
        win32serviceutil.InstallService(
            pythonClassString="",
            serviceName=SERVICE_NAME,
            displayName=SERVICE_DISPLAY_NAME,
            description=SERVICE_DESCRIPTION,
            exeName=sys.executable,
            exeArgs=_service_args(),
            startType=win32service.SERVICE_AUTO_START,
        )
        logger.info("服务安装成功")
    except pywintypes.error as exc:
        if _winerror(exc) != ERROR_SERVICE_EXISTS:
            raise
        service_exists = True
        logger.info("服务已存在，正在更新账号参数")

    if service_exists:
        _stop_service()
        win32serviceutil.ChangeServiceConfig(
            pythonClassString="",
            serviceName=SERVICE_NAME,
            displayName=SERVICE_DISPLAY_NAME,
            description=SERVICE_DESCRIPTION,
            exeName=sys.executable,
            exeArgs=_service_args(),
            startType=win32service.SERVICE_AUTO_START,
        )

    _store_service_credentials(credentials)
    _start_service()


def uninstall_service() -> None:
    _ensure_windows()
    _ensure_admin()

    _stop_service()

    logger = get_logger()
    try:
        win32serviceutil.RemoveService(SERVICE_NAME)
        logger.info("服务卸载成功")
    except pywintypes.error as exc:
        if _winerror(exc) != ERROR_SERVICE_DOES_NOT_EXIST:
            raise
        logger.info("服务不存在")


def _ensure_windows() -> None:
    if platform.system() != "Windows":
        raise ServiceError("Windows 服务仅支持 Windows")


def _ensure_admin() -> None:
    windll_object = getattr(ctypes, "windll", None)
    if windll_object is None:
        raise ServiceError("安装或卸载 Windows 服务需要管理员权限")

    windll = cast(_WinDll, windll_object)
    if not windll.shell32.IsUserAnAdmin():
        raise ServiceError("安装或卸载 Windows 服务需要管理员权限")


def run_service() -> None:
    servicemanager.Initialize()
    servicemanager.PrepareToHostSingle(BUCEANetAutoLoginService)
    servicemanager.StartServiceCtrlDispatcher()


def _service_args() -> str:
    return subprocess.list2cmdline(["-m", "buceanet_autologin", "service-run"])


def _store_service_credentials(credentials: Credentials) -> None:
    win32serviceutil.SetServiceCustomOption(
        SERVICE_NAME,
        STUDENT_ID_OPTION,
        credentials.student_id,
    )
    win32serviceutil.SetServiceCustomOption(
        SERVICE_NAME,
        PASSWORD_OPTION,
        credentials.password,
    )


def _load_service_credentials() -> Credentials:
    from .app import create_credentials

    student_id = win32serviceutil.GetServiceCustomOption(
        SERVICE_NAME,
        STUDENT_ID_OPTION,
        "",
    )
    password = win32serviceutil.GetServiceCustomOption(
        SERVICE_NAME,
        PASSWORD_OPTION,
        "",
    )
    return create_credentials(str(student_id), str(password))


def _start_service() -> None:
    logger = get_logger()
    try:
        win32serviceutil.StartService(SERVICE_NAME)
        logger.info("服务启动成功")
    except pywintypes.error as exc:
        if _winerror(exc) != ERROR_SERVICE_ALREADY_RUNNING:
            raise
        logger.info("服务已在运行")


def _stop_service() -> None:
    logger = get_logger()
    try:
        win32serviceutil.StopService(SERVICE_NAME)
        logger.info("服务已停止")
    except pywintypes.error as exc:
        if _winerror(exc) not in {
            ERROR_SERVICE_NOT_ACTIVE,
            ERROR_SERVICE_DOES_NOT_EXIST,
        }:
            raise


def _configure_service_runtime_dir() -> None:
    program_data = os.environ.get("PROGRAMDATA", r"C:\ProgramData")
    os.environ.setdefault(
        "BUCEANET_RUNTIME_DIR",
        str(Path(program_data) / SERVICE_NAME),
    )


def _winerror(exc: pywintypes.error) -> int:
    return int(exc.winerror)
