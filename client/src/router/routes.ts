import { RouteRecordRaw } from 'vue-router'
import { isElectron } from 'src/utils/action'
import _ from 'lodash'

let routes: RouteRecordRaw[] = [
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue')
  }
]

const electronRoutes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('layouts/BlankLayout.vue'),
    children: [
      {
        path: '',
        component: () => import('pages/boot/BootPage.vue')
      }
    ]
  },
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      {
        path: 'generator',
        component: () => import('pages/task/TaskPage.vue'),
        children: [
          {
            path: ':id',
            component: () => import('pages/task/TaskGenerator.vue')
          }
        ]
      },
      {
        path: 'merge',
        component: () => import('pages/merge/MergePage.vue')
      },
      {
        path: 'dau',
        component: () => import('pages/dau/DauPage.vue')
      },
      {
        path: 'report',
        component: () => import('pages/report/ReportPage.vue')
      }
    ]
  }
]

const webRoutes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('layouts/WebMainLayout.vue'),
    children: [
      {
        path: '',
        component: () => import('pages/dashboard/DashboardPage.vue')
      }
    ]
  }
]

if (isElectron()) {
  routes = _.concat(electronRoutes, routes)
} else {
  routes = _.concat(webRoutes, routes)
}

export default routes
