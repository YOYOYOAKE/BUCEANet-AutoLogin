# BUCEANet-AutoLogin

BUCEA 的校园网每天凌晨三点准时踢所有账号下线，写了个项目保证网络连接。

此项目使用浏览器模拟点击的方式实现自动登录，并支持安装为 Windows 服务来保持后台运行。

## 安装

安装命令行工具：

```powershell
uv tool install git+https://github.com/YOYOYOAKE/BUCEANet-AutoLogin
```

首次使用前需要手动安装 Playwright Chromium：

```powershell
buceanet-autologin install-chrome
```

浏览器和日志统一存储在 `%PROGRAMDATA%\BUCEANet-AutoLogin`。

## 前台运行

执行一次登录：

```powershell
buceanet-autologin run -i <学号> -p <密码>
```

持续运行并定时检测网络：

```powershell
buceanet-autologin run forever -i <学号> -p <密码>
```

`run forever` 会先登录一次，然后常驻前台轮询。

## Windows 服务

安装、卸载服务需要管理员权限。

安装并启动服务：

```powershell
buceanet-autologin install-service -i <学号> -p <密码>
```

停止并卸载服务：

```powershell
buceanet-autologin uninstall-service
```

服务名称为 `BUCEANet-AutoLogin`。账号参数会写入 Windows 服务参数。

## 开发

克隆仓库后先同步依赖：

```powershell
uv sync
```

从源码运行命令行入口：

```powershell
uv run buceanet-autologin --help
uv run buceanet-autologin install-chrome 
uv run buceanet-autologin run -i <学号> -p <密码>
uv run buceanet-autologin run forever -i <学号> -p <密码>
```

类型检查与构建：

```powershell
uv run pyright
uv build
```

所有文件统一存储在 `%PROGRAMDATA%\BUCEANet-AutoLogin`。调试服务时可以直接运行：

```powershell
uv run buceanet-autologin install-service -i <学号> -p <密码>
uv run buceanet-autologin uninstall-service
```
