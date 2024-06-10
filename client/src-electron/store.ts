import Store, { Schema } from 'electron-store'
import { confDir } from './utils'

export type ConfigSchemaType = {
  theme: boolean | 'auto',
  remoteServer: string
}

const schema: Schema<ConfigSchemaType> = {
  theme: {
    anyOf: [
      { type: 'boolean' },
      {
        type: 'string',
        enum: ['auto']
      }
    ],
    default: true
  },
  remoteServer: { type: 'string', default: 'http://localhost:8880' }
}

export const STORE_KEYS: { [key: string]: keyof ConfigSchemaType } = {
  THEME: 'theme',
  REMOTE_SERVER: 'remoteServer'
}

export const store = new Store<ConfigSchemaType>({
  schema,
  cwd: confDir
})
