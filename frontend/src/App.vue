<template>
  <div class="app-shell d-flex flex-column min-vh-100">
    <AppHeader />
    <main class="flex-grow-1 py-4 py-lg-5">
      <router-view />
    </main>
    <footer class="border-top border-light-subtle footer-shell">
      <div class="container py-4 d-flex flex-column flex-lg-row justify-content-between gap-3 align-items-lg-center">
        <div>
          <p class="mb-1 fw-bold text-white">Cinema Space</p>
          <p class="mb-0 text-secondary">Кинотеатр с онлайн-бронированием, избранным и личным кабинетом.</p>
        </div>
        <p class="mb-0 text-secondary">Локальная сборка на Vue + FastAPI</p>
      </div>
    </footer>
  </div>
</template>

<script>
import AppHeader from '@/components/AppHeader.vue'

export default {
  name: 'App',
  components: {
    AppHeader
  }
}
</script>
