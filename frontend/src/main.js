import { createApp } from 'vue'
import './style.css'
import 'flowbite'
import App from './App.vue'
import router from './router'
import posthog from 'posthog-js'

const phKey = import.meta.env.VITE_PUBLIC_POSTHOG_KEY
if (phKey) {
  posthog.init(phKey, {
    api_host: import.meta.env.VITE_PUBLIC_POSTHOG_HOST,
    capture_pageview: false,
  })
}

window.posthog = posthog

const app = createApp(App)

router.afterEach((to) => {
  if (phKey) posthog.capture('$pageview', { current_url: to.fullPath })
  // Mise à jour du <title>
  if (to.meta?.title) {
    document.title = to.meta.title
  }

  // Mise à jour ou création du <meta name="description">
  if (to.meta?.description) {
    let descriptionTag = document.querySelector('meta[name="description"]')
    if (!descriptionTag) {
      descriptionTag = document.createElement('meta')
      descriptionTag.setAttribute('name', 'description')
      document.head.appendChild(descriptionTag)
    }
    descriptionTag.setAttribute('content', to.meta.description)
  }
})

app.use(router).mount('#app')
