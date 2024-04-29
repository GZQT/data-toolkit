import createClient, { type Middleware } from 'openapi-fetch'
import { Notify } from 'quasar'
import { boot } from 'quasar/wrappers'
import { paths } from 'src/types/api'

const middleware: Middleware = {
  onRequest: async (req) => {
    // set "foo" header
    return req
  },
  onResponse: async (res: Response) => {
    const { body, status, ...resOptions } = res
    if (status >= 400 && status < 500) {
      const newBody = await res.clone().json()
      Notify.create({
        type: 'warning',
        message: `获取数据失败：${newBody.message}`
      })
      throw new Error(`获取数据失败：${newBody.message}`)
    }
    if (status >= 500) {
      const newBody = await res.clone().json()
      Notify.create({
        type: 'error',
        message: '获取数据失败：服务器内部错误'
      })
      throw new Error(`获取数据失败：${newBody.message}`)
    }
    if (status === 204) {
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
