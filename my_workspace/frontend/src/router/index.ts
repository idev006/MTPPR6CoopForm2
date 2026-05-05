import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth.store'
import { ROLES } from '@/constants/roles'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('@/pages/LoginPage.vue'),
      meta: { requiresAuth: false },
    },
    {
      path: '/',
      name: 'dashboard',
      component: () => import('@/pages/DashboardPage.vue'),
      meta: { requiresAuth: true, roles: [ROLES.BORROWER] },
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('@/pages/ProfilePage.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/applications/ordinary/new',
      name: 'application-ordinary-new',
      component: () => import('@/pages/OrdinaryApplicationPage.vue'),
      meta: { requiresAuth: true, roles: [ROLES.BORROWER] },
    },
    {
      path: '/applications/emergency/new',
      name: 'application-emergency-new',
      component: () => import('@/pages/EmergencyApplicationPage.vue'),
      meta: { requiresAuth: true, roles: [ROLES.BORROWER] },
    },
    {
      path: '/applications/new',
      name: 'application-new',
      redirect: { name: 'application-ordinary-new' },
    },
    {
      path: '/applications/:id',
      name: 'application-detail',
      component: () => import('@/pages/ApplicationDetailPage.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/staff',
      name: 'staff-dashboard',
      component: () => import('@/pages/staff/StaffDashboardPage.vue'),
      meta: { requiresAuth: true, roles: [ROLES.STAFF] },
    },
    {
      path: '/staff/applications/:id',
      name: 'staff-review',
      component: () => import('@/pages/staff/ReviewPage.vue'),
      meta: { requiresAuth: true, roles: [ROLES.STAFF] },
    },
    {
      path: '/staff/cockpit',
      name: 'staff-cockpit',
      component: () => import('@/pages/staff/SystemCockpitPage.vue'),
      meta: { requiresAuth: true, roles: [ROLES.STAFF] },
    },
    {
      path: '/403',
      name: 'forbidden',
      component: () => import('@/pages/ForbiddenPage.vue'),
      meta: { requiresAuth: false },
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: () => import('@/pages/NotFoundPage.vue'),
      meta: { requiresAuth: false },
    },
  ],
})

// Route guard
router.beforeEach((to) => {
  const auth = useAuthStore()

  // 1. ยังไม่ login → ไปหน้า login
  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }

  // 2. ไม่มีสิทธิ์ตาม role → แสดงหน้า 403
  const allowedRoles = to.meta.roles as string[] | undefined
  if (allowedRoles && auth.isAuthenticated && !auth.hasRole(allowedRoles)) {
    return { name: 'forbidden' }
  }
})

export default router
