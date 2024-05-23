import log from 'electron-log'
import Store from 'electron-store'

import path from 'path'
import { app } from 'electron'

export const confDir = path.join(app.getPath('home'), '.config', 'data-toolkit')

log.initialize()
log.transports.file.resolvePathFn = () => path.join(confDir, 'main.log')
console.log = log.log

export const logger = log.create({ logId: 'default' })
const schema = {
  theme: {
    anyOf: [
      { type: 'boolean' },
      { type: 'string', enum: ['auto'] }
    ],
    default: true
  }
}

export const store = new Store({
  schema,
  cwd: confDir
})
