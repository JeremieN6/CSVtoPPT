<template>
  <div class="flex flex-col items-center justify-center min-h-screen bg-white dark:bg-gray-900">
    <div class="p-8 bg-white dark:bg-gray-800 rounded-lg shadow-lg text-center">
      <h1 class="text-2xl font-bold mb-4 text-gray-900 dark:text-white">Merci pour votre achat !</h1>
      <p class="mb-4 text-gray-700 dark:text-gray-300">Déblocage de votre accès premium en cours...</p>
      <div v-if="loading" class="text-blue-600 dark:text-blue-400">Chargement...</div>
      <div v-if="error" class="text-red-600 mt-4">{{ error }}</div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

const loading = ref(true)
const error = ref('')
const router = useRouter()

onMounted(async () => {
  try {
    const response = await fetch('/.netlify/functions/createToken', {
      method: 'POST',
      body: JSON.stringify({
        ua: navigator.userAgent
      })
    })
    const data = await response.json()
    if (data.token) {
      sessionStorage.setItem('premiumToken', data.token)
      // Redirige vers le calculateur après 1s
      setTimeout(() => {
        router.push('/calculateur')
      }, 1000)
    } else {
      error.value = "Erreur lors de la génération du token. Contactez le support."
    }
  } catch (e) {
    error.value = "Erreur lors de la génération du token."
  } finally {
    loading.value = false
  }
})
</script>