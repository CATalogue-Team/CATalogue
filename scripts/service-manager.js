import { spawn } from 'child_process'

export default function serviceManager() {
  let dbProcess, apiProcess

  return {
    name: 'service-manager',
    configureServer(server) {
      // 启动数据库
      const startDB = () => new Promise((resolve) => {
        dbProcess = spawn('pg_ctl', ['-D', 'pgdata', 'start'], {
          stdio: 'inherit',
          shell: true
        })
        dbProcess.on('close', resolve)
      })

      // 启动API服务
      const startAPI = () => new Promise((resolve) => {
        apiProcess = spawn('uvicorn', [
          'api.main:app',
          '--port', '8000'
        ], {
          stdio: 'inherit',
          shell: true
        })
        apiProcess.on('close', resolve)
      })

      // 启动服务
      server.httpServer?.once('listening', async () => {
        await startDB()
        await startAPI()
      })

      // 关闭服务
      server.httpServer?.on('close', () => {
        if (apiProcess) {
          apiProcess.kill('SIGINT')
        }
        if (dbProcess) {
          spawn.sync('pg_ctl', ['-D', 'pgdata', 'stop'], {
            stdio: 'inherit',
            shell: true
          })
        }
      })
    }
  }
}
