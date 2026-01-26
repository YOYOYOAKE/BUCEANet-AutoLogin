import puppeteer from 'puppeteer'
import logger from './logger.js'

export default async (userConfig) => {
  const browser = await puppeteer.launch({
    headless: true
  })
  const page = await browser.newPage()

  try {
    await page.goto('http://10.1.1.131/srun_portal_success?ac_id=1&theme=pro')

    try {
      await page.click('#logout')
      await page.waitForSelector('.btn-confirm')
      await page.click('.btn-confirm')

      await new Promise(resolve => setTimeout(resolve, 3000))
      await page.reload()
    }
    catch (e) { }

    await page.waitForSelector('#username')
    await page.waitForSelector('#password')

    await page.type('#username', userConfig.username)
    await page.type('#password', userConfig.password)

    await page.waitForSelector('#login-account')
    await page.click('#login-account')

    await new Promise(resolve => setTimeout(resolve, 3000))
  } catch (e) {
    logger.error('自动登录失败', e)
  } finally {
    await browser.close()
  }
}