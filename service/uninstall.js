import { Service } from 'node-windows'
import path from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

const svc = new Service({
  name: 'BUCEANet-AutoLogin',
  script: path.join(__dirname, '../app.js')
})

svc.on('uninstall', () => {
  console.log('BUCEANet-AutoLogin 服务已卸载')
})

svc.uninstall()