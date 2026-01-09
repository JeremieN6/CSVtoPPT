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
                  Connectez vous à votre compte
              </h1>
              <div v-if="error" class="p-4 mb-4 text-sm text-red-800 rounded-lg bg-red-50 dark:bg-gray-800 dark:text-red-400">
                  {{ error }}
              </div>
              <form class="space-y-4 md:space-y-6" @submit.prevent="handleLogin">
                  <div>
                      <label for="email" class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">Email</label>
                      <input
                        v-model="email"
                        @blur="validateEmail"
                        type="email"
                        name="email"
                        id="email"
                        class="bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                        placeholder="nom@entreprise.fr"
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
                        class="bg-gray-50 border border-gray-300 text-gray-900 rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                        required
                      >
                      <p v-if="passwordError" class="mt-1 text-sm text-red-600">{{ passwordError }}</p>
                  </div>
                  <div class="flex items-center justify-between">
                      <div class="flex items-start">
                          <div class="flex items-center h-5">
                            <input v-model="rememberMe" id="remember" aria-describedby="remember" type="checkbox" class="w-4 h-4 border border-gray-300 rounded bg-gray-50 focus:ring-3 focus:ring-primary-300 dark:bg-gray-700 dark:border-gray-600 dark:focus:ring-primary-600 dark:ring-offset-gray-800">
                          </div>
                          <div class="ml-3 text-sm">
                            <label for="remember" class="text-gray-500 dark:text-gray-300">Se souvenir de moi</label>
                          </div>
                      </div>
                      <a href="#" class="text-sm font-medium text-primary-600 hover:underline dark:text-primary-500">Mot de passe oublié ?</a>
                  </div>
                  <button type="submit" :disabled="loading" class="w-full text-white bg-primary-600 hover:bg-primary-700 focus:ring-4 focus:outline-none focus:ring-primary-300 font-medium rounded-lg text-sm px-5 py-2.5 text-center dark:bg-primary-600 dark:hover:bg-primary-700 dark:focus:ring-primary-800 disabled:opacity-50">
                      <span v-if="loading">Connexion...</span>
                      <span v-else>Connexion</span>
                  </button>
                  <p class="text-sm font-light text-gray-500 dark:text-gray-400">
                      Vous n'avez pas encore de compte ? <RouterLink to="/inscription" class="font-medium text-primary-600 hover:underline dark:text-primary-500">S'inscrire</RouterLink>
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
const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || '/api').replace(/\/$/, '')
const AUTH_EVENT = 'csvtoppt-auth-changed'
const email = ref('')
const password = ref('')
const rememberMe = ref(false)
const error = ref('')
const loading = ref(false)
const emailError = ref('')
const passwordError = ref('')

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

const validateLoginForm = () => {
  const isEmailValid = validateEmail()
  const isPasswordValid = validatePassword()
  return isEmailValid && isPasswordValid
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

const handleLogin = async () => {
  error.value = ''
  loading.value = true

  if (!validateLoginForm()) {
    loading.value = false
    return
  }

  try {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: email.value,
        password: password.value,
      }),
    })

    if (!response.ok) {
      const data = await response.json()
      throw new Error(data.detail || 'Erreur de connexion')
    }

    const data = await response.json()
    
    // Stocker le token et les infos utilisateur
    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('user', JSON.stringify(data.user))
    emitAuthChanged(true)
    
    // Rediriger vers le convertisseur
    router.push('/convertisseur')
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}
</script>