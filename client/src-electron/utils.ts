import log from 'electron-log'
import Store from 'electron-store'

import path from 'path'
import { app } from 'electron'
import gNet from 'net'

export const confDir = path.join(app.getPath('home'), 'data-toolkit')

log.initialize()

const logger = log.create({ logId: 'default' })
console.log = log.log
logger.transports.file.resolvePathFn = () => path.join(confDir, 'main.log')
export { logger }

const schema = {
  theme: {
    anyOf: [
      { type: 'boolean' },
      {
        type: 'string',
        enum: ['auto']
      }
    ],
    default: true
  }
}

export const store = new Store({
  schema,
  cwd: confDir
})

export const sleep = (ms: number) => {
  return new Promise(resolve => setTimeout(resolve, ms))
}

/**
 * Find an available port
 * @returns {Promise<number>} - A promise that resolves to an available port number
 */
export const getAvailablePort = (): Promise<number> => {
  return new Promise((resolve, reject) => {
    const server = gNet.createServer()
    server.listen(0, () => {
      const port = (server.address() as gNet.AddressInfo).port
      server.close(() => {
        resolve(port)
      })
    })
    server.on('error', (err) => {
      reject(err)
    })
  })
}

/**
 * Check if a specific port is in use
 * @param {number} port - The port number to check
 * @returns {Promise<boolean>} - A promise that resolves to true if the port is in use, false otherwise
 */
export const checkPortInUse = (port: number): Promise<boolean> => {
  return new Promise((resolve, reject) => {
    const server = gNet.createServer()
    server.once('error', (err: Error) => {
      if (err.name.includes('EADDRINUSE')) {
        resolve(true)
      } else {
        reject(err)
      }
    })
    server.once('listening', () => {
      server.close(() => {
        resolve(false)
      })
    })
    server.listen(port)
  })
}
