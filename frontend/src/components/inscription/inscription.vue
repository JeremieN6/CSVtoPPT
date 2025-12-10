<template>
    <section class="bg-gray-50 dark:bg-gray-900 p-8">
  <div class="flex flex-col items-center justify-center px-6 py-8 mx-auto md:h-screen lg:py-0">
    <RouterLink to="/" class="flex items-center p-6">
        <span class="text-4xl">📃</span>
        <span class="self-center text-xl font-semibold text-gray-700 whitespace-nowrap dark:text-white">CSVtoPPT</span>
    </RouterLink>
      <div class="w-full bg-white rounded-lg shadow dark:border md:mt-0 sm:max-w-md xl:p-0 dark:bg-gray-800 dark:border-gray-700">
          <div class="p-6 space-y-4 md:space-y-6 sm:p-8">
              <h1 class="text-xl font-bold leading-tight tracking-tight text-gray-900 md:text-2xl dark:text-white">
                  Créez un compte 
              </h1>
              <div v-if="error" class="p-4 mb-4 text-sm text-red-800 rounded-lg bg-red-50 dark:bg-gray-800 dark:text-red-400">
                  {{ error }}
              </div>
              <form class="space-y-4 md:space-y-6" @submit.prevent="handleRegister">
                  <div>
                      <label for="email" class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">Email</label>
                      <input
                        v-model="email"
                        @blur="validateEmail"
                        type="email"
                        name="email"
                        id="email"
                        class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                        placeholder="nom@entreprise.com"
                        required
                      >
                      <p v-if="emailError" class="mt-1 text-sm text-red-600">{{ emailError }}</p>
                  </div>
                  <div>
                      <label for="password" class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">Mot de passe</label>
                      <input
                        v-model="password"
                        @blur="validatePassword"
                        type="password"
                        name="password"
                        id="password"
                        placeholder="••••••••"
                        class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                        required
                      >
                      <p v-if="passwordError" class="mt-1 text-sm text-red-600">{{ passwordError }}</p>
                  </div>
                  <div>
                      <label for="confirm-password" class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">Confirmez le mot de passe</label>
                      <input
                        v-model="confirmPassword"
                        @blur="validateConfirmPassword"
                        type="password"
                        name="confirm-password"
                        id="confirm-password"
                        placeholder="••••••••"
                        class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                        required
                      >
                      <p v-if="confirmPasswordError" class="mt-1 text-sm text-red-600">{{ confirmPasswordError }}</p>
                  </div>
                  <div class="flex items-start">
                      <div class="flex items-center h-5">
                        <input v-model="acceptTerms" id="terms" aria-describedby="terms" type="checkbox" class="w-4 h-4 border border-gray-300 rounded bg-gray-50 focus:ring-3 focus:ring-primary-300 dark:bg-gray-700 dark:border-gray-600 dark:focus:ring-primary-600 dark:ring-offset-gray-800">
                      </div>
                      <div class="ml-3 text-sm">
                        <label for="terms" class="font-light text-gray-500 dark:text-gray-300">J'accepte <RouterLink class="font-medium text-primary-600 hover:underline dark:text-primary-500" to="/politique-de-confidentialite">les conditions générales</RouterLink></label>
                      </div>
                  </div>
                  <button type="submit" :disabled="loading" class="w-full text-white bg-primary-600 hover:bg-primary-700 focus:ring-4 focus:outline-none focus:ring-primary-300 font-medium rounded-lg text-sm px-5 py-2.5 text-center dark:bg-primary-600 dark:hover:bg-primary-700 dark:focus:ring-primary-800 disabled:opacity-50">
                      <span v-if="loading">Création...</span>
                      <span v-else>Créer un compte</span>
                  </button>
                  <p class="text-sm font-light text-gray-500 dark:text-gray-400">
                      Vous avez déjà un compte ? <RouterLink to="/connexion" class="font-medium text-primary-600 hover:underline dark:text-primary-500">Connectez-vous ici</RouterLink>
                  </p>
              </form>
          </div>
      </div>
  </div>
</section>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { RouterLink } from 'vue-router'

const router = useRouter()
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000'
const AUTH_EVENT = 'csvtoppt-auth-changed'
const name = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const acceptTerms = ref(false)
const error = ref('')
const loading = ref(false)
const emailError = ref('')
const passwordError = ref('')
const confirmPasswordError = ref('')

const validateEmail = () => {
  if (!email.value.includes('@')) {
    emailError.value = 'Veuillez renseigner une adresse mail valide'
    return false
  }
  emailError.value = ''
  return true
}

const validatePassword = () => {
  if (password.value.length < 8) {
    passwordError.value = 'Veuillez saisir un mot de passe plus long (8 caractères minimum)'
    return false
  }
  passwordError.value = ''
  return true
}

const validateConfirmPassword = () => {
  if (password.value !== confirmPassword.value) {
    confirmPasswordError.value = 'Les mots de passes sont différents.'
    return false
  }
  confirmPasswordError.value = ''
  return true
}

const validateRegisterForm = () => {
  const isEmailValid = validateEmail()
  const isPasswordValid = validatePassword()
  const isConfirmValid = validateConfirmPassword()
  return isEmailValid && isPasswordValid && isConfirmValid
}

const emitAuthChanged = (authenticated) => {
  if (typeof window === 'undefined') {
    return
  }
  window.dispatchEvent(
    new CustomEvent(AUTH_EVENT, {
      detail: { authenticated: Boolean(authenticated) },
    }),
  )
}

const handleRegister = async () => {
  error.value = ''

  if (!validateRegisterForm()) {
    return
  }

  if (!acceptTerms.value) {
    error.value = 'Vous devez accepter les conditions générales'
    return
  }

  loading.value = true

  try {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: email.value,
        password: password.value,
        name: name.value,
      }),
    })

    if (!response.ok) {
      const data = await response.json()
      throw new Error(data.detail || 'Erreur lors de l\'inscription')
    }

    // Inscription réussie, rediriger vers la page de connexion
    emitAuthChanged(false)
    router.push('/connexion')
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}
</script>