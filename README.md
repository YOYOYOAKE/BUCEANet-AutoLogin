# BUCEANet-AutoLogin

BUCEA 的校园网每天凌晨三点准时踢所有账号下线，写了个项目保证网络连接。

此项目使用浏览器模拟点击的方式实现自动登录，并提供注册为 Windows 服务的方式保证后台运行。

## 0x01 环境

项目使用 Puppeteer 自带的 Chromium 浏览器，无需额外安装浏览器。

项目依赖 Node.js >= 20 环境，请确保安装了指定版本的 Node.js。

项目使用 PNPM 作为包管理器，请确保安装了 PNPM。

```sh
npm install -g pnpm
```

## 0x02 部署

### 2.1 下载项目

下载项目源代码或克隆仓库。

```sh
git clone https://github.com/YOYOYOAKE/BUCEANet-AutoLogin.git
cd BUCEANet-AutoLogin
```

### 2.2 安装依赖

项目已配置 `.npmrc` 文件使用国内淘宝镜像源，直接安装即可：

```sh
pnpm install
```

> **注意**：如果安装时未自动下载浏览器，需要手动执行浏览器安装命令（见下一步）。

### 2.3 下载 Chromium 浏览器

如果依赖安装后运行出错提示找不到浏览器，需要手动下载 Chrome：

**Windows PowerShell：**

```powershell
$env:PUPPETEER_DOWNLOAD_BASE_URL="https://registry.npmmirror.com/-/binary/chrome-for-testing"
npx puppeteer browsers install chrome
```

**Linux/macOS：**

```sh
export PUPPETEER_DOWNLOAD_BASE_URL="https://registry.npmmirror.com/-/binary/chrome-for-testing"
npx puppeteer browsers install chrome
```

### 2.4 配置账号信息

在 `config.js` 中配置你的校园网用户名和密码：

```js
export default {
  username: '你的学号',
  password: '你的密码'
}
```

### 2.5 运行项目

```sh
pnpm start
```

程序会自动登录校园网，并每分钟检查一次网络连接状态，断线时自动重新登录。

## 0x03 安装与卸载服务

为保证项目随系统自启动，项目提供了安装为系统服务的功能。

安装为系统服务：

```sh
pnpm install-service
```

卸载系统服务：

```sh
pnpm uninstall-service
```