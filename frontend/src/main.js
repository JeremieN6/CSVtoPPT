import { createApp } from 'vue'
import './style.css'
import 'flowbite'
import App from './App.vue'
import router from './router'

const app = createApp(App)

router.afterEach((to) => {
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
