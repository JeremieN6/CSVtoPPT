<template>
  <div>
    <RouterView />

    <div class="fixed right-4 top-4 z-50 space-y-2" v-if="toastVisible">
      <div
        v-if="toastType === 'success'"
        class="flex w-full max-w-xs items-center rounded-lg bg-white p-4 text-gray-500 shadow-sm dark:bg-gray-800 dark:text-gray-400"
        role="alert"
      >
        <div
          class="inline-flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-green-100 text-green-500 dark:bg-green-800 dark:text-green-200"
        >
          <svg class="h-5 w-5" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 20 20">
            <path
              d="M10 .5a9.5 9.5 0 1 0 9.5 9.5A9.51 9.51 0 0 0 10 .5Zm3.707 8.207-4 4a1 1 0 0 1-1.414 0l-2-2a1 1 0 0 1 1.414-1.414L9 10.586l3.293-3.293a1 1 0 0 1 1.414 1.414Z"
            />
          </svg>
          <span class="sr-only">Check icon</span>
        </div>
        <div class="ms-3 text-sm font-normal">{{ toastMessage }}</div>
        <button
          type="button"
          class="ms-auto -mx-1.5 -my-1.5 inline-flex h-8 w-8 items-center justify-center rounded-lg bg-white p-1.5 text-gray-400 hover:bg-gray-100 hover:text-gray-900 focus:ring-2 focus:ring-gray-300 dark:bg-gray-800 dark:text-gray-500 dark:hover:bg-gray-700 dark:hover:text-white"
          aria-label="Fermer"
          @click="closeToast"
        >
          <span class="sr-only">Fermer</span>
          <svg class="h-3 w-3" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 14 14">
            <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m1 1 6 6m0 0 6 6M7 7l6-6M7 7l-6 6" />
          </svg>
        </button>
      </div>

      <div
        v-else
        class="flex w-full max-w-xs items-center rounded-lg bg-white p-4 text-gray-500 shadow-sm dark:bg-gray-800 dark:text-gray-400"
        role="alert"
      >
        <div
          class="inline-flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-red-100 text-red-500 dark:bg-red-800 dark:text-red-200"
        >
          <svg class="h-5 w-5" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 20 20">
            <path
              d="M10 .5a9.5 9.5 0 1 0 9.5 9.5A9.51 9.51 0 0 0 10 .5Zm3.707 11.793a1 1 0 1 1-1.414 1.414L10 11.414l-2.293 2.293a1 1 0 0 1-1.414-1.414L8.586 10 6.293 7.707a1 1 0 0 1 1.414-1.414L10 8.586l2.293-2.293a1 1 0 0 1 1.414 1.414L11.414 10l2.293 2.293Z"
            />
          </svg>
          <span class="sr-only">Error icon</span>
        </div>
        <div class="ms-3 text-sm font-normal">{{ toastMessage }}</div>
        <button
          type="button"
          class="ms-auto -mx-1.5 -my-1.5 inline-flex h-8 w-8 items-center justify-center rounded-lg bg-white p-1.5 text-gray-400 hover:bg-gray-100 hover:text-gray-900 focus:ring-2 focus:ring-gray-300 dark:bg-gray-800 dark:text-gray-500 dark:hover:bg-gray-700 dark:hover:text-white"
          aria-label="Fermer"
          @click="closeToast"
        >
          <span class="sr-only">Fermer</span>
          <svg class="h-3 w-3" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 14 14">
            <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m1 1 6 6m0 0 6 6M7 7l6-6M7 7l-6 6" />
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { RouterView, useRoute, useRouter } from 'vue-router'

const toastVisible = ref(false)
const toastMessage = ref('')
const toastType = ref('success')
let toastTimer

const showToast = (message, type) => {
  toastMessage.value = message
  toastType.value = type
  toastVisible.value = true
  if (toastTimer) {
    clearTimeout(toastTimer)
  }
  toastTimer = window.setTimeout(() => {
    toastVisible.value = false
  }, 5000)
}

const closeToast = () => {
  toastVisible.value = false
  if (toastTimer) {
    clearTimeout(toastTimer)
  }
}

const router = useRouter()
const route = useRoute()

const removeCheckoutQuery = () => {
  const cleanedQuery = { ...route.query }
  delete cleanedQuery.checkout
  router.replace({ path: route.path, query: cleanedQuery, hash: route.hash })
}

const handleCheckoutStatus = (status) => {
  const normalized = status.toLowerCase()
  if (normalized === 'success') {
    showToast('Votre abonnement est activé.', 'success')
    router.replace({ path: '/convertisseur' })
    return
  }

  showToast("Quelque chose s'est mal passé… Veuillez réessayer ou contacter le support.", 'danger')
  router.replace({ path: '/#pricing' })
  removeCheckoutQuery()
}

watch(
  () => route.query.checkout,
  (status) => {
    if (!status) {
      return
    }
    handleCheckoutStatus(String(status))
  },
  { immediate: true }
)
</script>
