import createClient, { type Middleware } from 'openapi-fetch'
import { LoadingBar, Notify } from 'quasar'
import { paths } from 'src/types/api'
import { paths as remotePaths } from 'src/types/remote-api'

interface ErrorDetail {
  type: string
  loc: string[]
  msg: string
  input: Record<string, unknown>
}

const getErrorMessage = (body: Record<string, unknown>) => {
  const errorDetail = body.detail
  if (Array.isArray(errorDetail)) {
    const detail = errorDetail as ErrorDetail[]
    const message = detail.map(item => {
      return `<li><b>[${item.type}]</b> ${item.loc.join('->')} ${item.msg}</li>`
    })
    Notify.create({
      type: 'warning',
      message: `<div>获取数据失败：<br />${message}</div>`,
      html: true
    })
  } else if (typeof errorDetail === 'string') {
    const message = errorDetail as string
    Notify.create({
      type: 'warning',
      message: `获取数据失败：${message}`
    })
  } else {
    Notify.create({
      type: 'warning',
      message: '获取数据失败：未知错误'
    })
  }
}

const middleware: Middleware = {
  onRequest: async (req) => {
    if (req.method !== 'GET') {
      LoadingBar.start()
    }
    return req
  },
  onResponse: async (res: Response) => {
    const {
      body,
      status,
      ...resOptions
    } = res
    LoadingBar.stop()
    if (status >= 400 && status < 500) {
      const newBody = await res.clone().json()
      getErrorMessage(newBody)
      console.error(status, newBody)
      throw new Error(`获取数据失败：${status}`)
    }
    if (status >= 500) {
      let newBody: { detail: string } | undefined
      try {
        newBody = await res.clone().json()
        console.error(status, newBody)
      } catch (e) {
        console.error(status, e)
      } finally {
        Notify.create({
          type: 'negative',
          message: '获取数据失败：服务器内部错误'
        })
      }
      throw new Error(`服务器错误：${newBody?.detail}`)
    }
    if (status === 201) {
      Notify.create({
        type: 'positive',
        message: '创建成功'
      })
      return undefined
    }
    if (status === 204) {
      Notify.create({
        type: 'positive',
        message: '操作成功'
      })
      return undefined
    }
    // change status of response
    return new Response(body, {
      ...resOptions,
      status: 200
    })
  }
}

const port = 18764
const remoteServer = await window.ApplicationApi.getRemoteServer()

const client = createClient<paths>({
  baseUrl: `http://localhost:${port}`
})

const healthClient = createClient<paths>({
  baseUrl: `http://localhost:${port}`
})

let remoteClient = createClient<remotePaths>({
  baseUrl: remoteServer
})

let healthRemoteClient = createClient<remotePaths>({
  baseUrl: remoteServer
})

const updateRemoteClient = (address: string) => {
  remoteClient = createClient<remotePaths>({ baseUrl: address })
  healthRemoteClient = createClient<remotePaths>({ baseUrl: remoteServer })
}

client.use(middleware)
remoteClient.use(middleware)
export { client, healthClient, port, remoteClient, healthRemoteClient, updateRemoteClient }
