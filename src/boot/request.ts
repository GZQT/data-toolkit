import createClient, { type Middleware } from 'openapi-fetch'
import { LoadingBar, Notify } from 'quasar'
import { boot } from 'quasar/wrappers'
import { paths } from 'src/types/api'

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
    LoadingBar.start()
    return req
  },
  onResponse: async (res: Response) => {
    const { body, status, ...resOptions } = res
    LoadingBar.stop()
    if (status >= 400 && status < 500) {
      const newBody = await res.clone().json()
      getErrorMessage(newBody)
      console.error(status, newBody)
      throw new Error(`获取数据失败：${status}`)
    }
    if (status >= 500) {
      try {
        const newBody = await res.clone().json()
        console.error(status, newBody)
        throw new Error(`服务器错误：${newBody.detail}`)
      } catch (e) {
        console.error(status, e)
      } finally {
        Notify.create({
          type: 'negative',
          message: '获取数据失败：服务器内部错误'
        })
      }
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
    return new Response(body, { ...resOptions, status: 200 })
  }
}

const client = createClient<paths>({
  baseUrl: 'http://localhost:8080'
})
client.use(middleware)
// "async" is optional;
// more info on params: https://v2.quasar.dev/quasar-cli/boot-files
export default boot(async (/* { app, router, ... } */) => {
  // something to do
})

export { client }
