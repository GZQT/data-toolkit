import { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('layouts/BlankLayout.vue'),
    // redirect: '/task'
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
        path: 'dau',
        component: () => import('pages/dau/DauPage.vue')
      }
    ]
  },
  // Always leave this as last one,
  // but you can also remove it
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue')
  }
]

export default routes
