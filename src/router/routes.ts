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
        path: 'task',
        component: () => import('pages/task/TaskPage.vue'),
        children: [
          {
            path: ':id?',
            component: () => import('pages/task/TaskContent.vue'),
            children: [
              {
                path: 'generator',
                component: () => import('pages/task/TaskGenerator.vue')
              },
              {
                path: 'file',
                component: () => import('pages/task/TaskFile.vue')
              },
              {
                path: 'table',
                component: () => import('pages/task/TaskTable.vue')
              },
              {
                path: 'chart',
                component: () => import('pages/task/TaskChart.vue')
              }
            ]
          }
        ]
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
