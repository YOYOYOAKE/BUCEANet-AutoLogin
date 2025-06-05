import { Service } from 'node-windows'
import path from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

const svc = new Service({
  name: 'BUCEANet-AutoLogin',
  description: 'BUCEA校园网自动登录服务',
  script: path.join(__dirname, '../app.js'),
  nodeOptions: [],
  grow: 0.5,
  wait: 2,
  maxRestarts: 3,
  maxRetries: 3,
  stopparentfirst: true,
  logpath: path.join(__dirname, '../logs'),
})

svc.on('install', () => {
  svc.start()
  console.log('BUCEANet-AutoLogin 服务已安装')
})

svc.on('alreadyinstalled', () => {
  svc.start()
})

svc.on('error', (err) => {
  console.error('服务错误:', err)
})

svc.on('start', () => {
  console.log('服务已启动')
})

svc.install()