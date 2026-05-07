import { createRouter, createWebHistory } from 'vue-router'
import { getStoredUser } from '@/store/session'
import AdminView from '@/views/AdminView.vue'
import AuthView from '@/views/AuthView.vue'
import FavoritesView from '@/views/FavoritesView.vue'
import HomeView from '@/views/HomeView.vue'
import MovieDetailView from '@/views/MovieDetailView.vue'
import MoviesView from '@/views/MoviesView.vue'
import ProfileTicketsView from '@/views/ProfileTicketsView.vue'
import ProfileView from '@/views/ProfileView.vue'
import SearchView from '@/views/SearchView.vue'

const routes = [
  { path: '/', name: 'home', component: HomeView },
  { path: '/auth', name: 'auth', component: AuthView },
  { path: '/movies', name: 'movies', component: MoviesView },
  { path: '/movies/:id', name: 'movie-details', component: MovieDetailView, props: (route) => ({ id: Number(route.params.id) }) },
  { path: '/profile', name: 'profile', component: ProfileView, meta: { requiresAuth: true } },
  { path: '/profile/tickets', name: 'profile-tickets', component: ProfileTicketsView, meta: { requiresAuth: true } },
  { path: '/favorites', name: 'favorites', component: FavoritesView, meta: { requiresAuth: true } },
  { path: '/search', name: 'search', component: SearchView },
  { path: '/admin', name: 'admin', component: AdminView, meta: { requiresAuth: true, requiresAdmin: true } }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  }
})

router.beforeEach((to) => {
  const user = getStoredUser()

  if (to.name === 'auth' && user) {
    return { name: user.role === 'admin' ? 'admin' : 'profile' }
  }

  if (to.meta.requiresAuth && !user) {
    return {
      name: 'auth',
      query: {
        redirect: to.fullPath
      }
    }
  }

  if (to.meta.requiresAdmin && user?.role !== 'admin') {
    return { name: 'profile' }
  }

  return true
})

export default router
