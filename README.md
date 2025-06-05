# BUCEANet-AutoLogin

BUCEA 的校园网每天凌晨三点准时踢所有账号下线，写了个项目保证网络连接。

此项目使用浏览器模拟点击的方式实现自动登录，并提供注册为 Windows 服务的方式保证后台运行。

## 0x01 环境

项目依靠 Chrome 浏览器运行，请确保安装了 Chrome 浏览器。

项目依赖 Node.js >= 20 环境，请确保安装了指定版本的 Node.js。

项目使用 PNPM 作为包管理器，请确保安装了 PNPM。

```sh
npm install -g pnpm
```

## 0x02 部署

下载项目源代码或克隆仓库。

```sh
git clone https://github.com/YOYOYOAKE/BUCEANet-AutoLogin.git
```

进入项目根目录后安装项目所需依赖。

```sh
pnpm install
```

然后在`config.js`中配置用户名、密码，以及 Chrome 浏览器的路径。

```js
export default {
  username: 'username',
  password: 'password',
  chromePath: 'chromePath' // 转译反斜杠：C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe 
}
```

然后运行项目。

```sh
pnpm start
```

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