# BUCEANet-AutoLogin

BUCEA 的校园网每天凌晨三点准时踢所有账号下线，写了个项目保证网络连接。

此项目使用浏览器模拟点击的方式实现自动登录，并支持安装当前用户登录自启动任务来保持后台运行。

## 安装

安装命令行工具：

```powershell
uv tool install git+https://github.com/YOYOYOAKE/BUCEANet-AutoLogin
```

第一次运行会自动下载 Playwright Chromium 到 `%LOCALAPPDATA%\BUCEANet-AutoLogin\browsers`。

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

## 自启动

安装当前用户登录自启动任务，并立即在后台启动：

```powershell
buceanet-autologin install-startup -i <学号> -p <密码>
```

删除当前用户登录自启动任务：

```powershell
buceanet-autologin uninstall-startup
```

任务名称为 `BUCEANet-AutoLogin`。账号参数会写入当前用户计划任务的启动命令；日志写入 `%LOCALAPPDATA%\BUCEANet-AutoLogin\logs\app.log`。

## 开发

克隆仓库后先同步依赖：

```powershell
uv sync
```

从源码运行命令行入口：

```powershell
uv run buceanet-autologin --help
uv run buceanet-autologin run -i <学号> -p <密码>
uv run buceanet-autologin run forever -i <学号> -p <密码>
```

类型检查与构建：

```powershell
uv run pyright
uv build
```

运行时文件默认写入 `%LOCALAPPDATA%\BUCEANet-AutoLogin`，包括日志和 Playwright 浏览器。调试自启动时可以用 Windows 任务计划程序查看 `BUCEANet-AutoLogin`，或直接运行：

```powershell
uv run buceanet-autologin install-startup -i <学号> -p <密码>
uv run buceanet-autologin uninstall-startup
```
