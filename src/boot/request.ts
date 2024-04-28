import createClient from 'openapi-fetch'
import { boot } from 'quasar/wrappers'
import { paths } from 'src/types/api'

const client = createClient<paths>({ baseUrl: '/api' })

// "async" is optional;
// more info on params: https://v2.quasar.dev/quasar-cli/boot-files
export default boot(async (/* { app, router, ... } */) => {
  // something to do
})

export { client }
