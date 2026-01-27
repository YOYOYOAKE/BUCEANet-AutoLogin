import autoLogin from './utils/autoLogin.js'
import userConfig from './config.js'
import logger from './utils/logger.js';

if (userConfig.username === 'username' || userConfig.password === 'password') {
  logger.error('请先在 config.js 中配置用户名和密码！')
  console.error('错误：请先在 config.js 中配置用户名和密码！')
  process.exit(1)
}

async function checkNet() {
  try {
    await fetch('https://www.cnki.net/', {
      timeout: 5000
    })
  } catch (e) {
    if(e.message === 'fetch failed') {
      logger.info('网络连接失败，尝试重新登录')
      await autoLogin(userConfig)
    } else {
      logger.error('检查网络时发生错误:', e)
    }
  }
}

await autoLogin(userConfig)
logger.info('登录完成')

setInterval(checkNet, 60000)

process.stdin.resume()