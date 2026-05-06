from collections.abc import Sequence
from typing import Any

class ServiceFramework:
    def __init__(self, args: Sequence[str]) -> None: ...
    def ReportServiceStatus(self, serviceStatus: int) -> None: ...

def InstallService(
    pythonClassString: str,
    serviceName: str,
    displayName: str,
    startType: int | None = None,
    description: str | None = None,
    **kwargs: Any,
) -> None: ...
def ChangeServiceConfig(
    pythonClassString: str,
    serviceName: str,
    startType: int | None = None,
    displayName: str | None = None,
    description: str | None = None,
    **kwargs: Any,
) -> None: ...

def StartService(
    serviceName: str,
    args: Sequence[str] | None = None,
    machine: str | None = None,
) -> None: ...
def StopService(serviceName: str, machine: str | None = None) -> None: ...
def RemoveService(serviceName: str, machine: str | None = None) -> None: ...
def SetServiceCustomOption(serviceName: str, option: str, value: int | str) -> None: ...
def GetServiceCustomOption(
    serviceName: str,
    option: str,
    defaultValue: int | str | None = None,
) -> int | str | None: ...
