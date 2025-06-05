import autoLogin from './utils/autoLogin.js'
import userConfig from './config.js'
import logger from './utils/logger.js';

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

setInterval(checkNet, 60000)

process.stdin.resume()