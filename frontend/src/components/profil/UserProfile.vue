<template>
  <section class="bg-white py-8 antialiased dark:bg-gray-900 md:py-8">
    <div class="mx-auto max-w-screen-lg px-4 2xl:px-0">
      <nav class="mb-4 flex" aria-label="Breadcrumb">
        <ol class="inline-flex items-center space-x-1 md:space-x-2 rtl:space-x-reverse">
          <li class="inline-flex items-center">
            <RouterLink to="/" class="inline-flex items-center text-sm font-medium text-gray-700 hover:text-primary-600 dark:text-gray-400 dark:hover:text-white">
              <svg class="me-2 h-4 w-4" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24">
                <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m4 12 8-8 8 8M6 10.5V19a1 1 0 0 0 1 1h3v-3a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1v3h3a1 1 0 0 0 1-1v-8.5" />
              </svg>
              Accueil
            </RouterLink>
          </li>
          <li>
            <div class="flex items-center">
              <svg class="mx-1 h-4 w-4 text-gray-400 rtl:rotate-180" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24">
                <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m9 5 7 7-7 7" />
              </svg>
              <RouterLink to="/mon-compte" class="ms-1 text-sm font-medium text-gray-700 hover:text-primary-600 dark:text-gray-400 dark:hover:text-white md:ms-2">Mon compte</RouterLink>
            </div>
          </li>
        </ol>
      </nav>
      <h2 class="mb-4 text-xl font-semibold text-gray-900 dark:text-white sm:text-2xl md:mb-6">Vue générale</h2>
      <div v-if="profileError" class="mb-4 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700 dark:border-red-900/40 dark:bg-red-900/30 dark:text-red-200">
        {{ profileError }}
      </div>
      <div class="grid grid-cols-2 gap-6 border-b border-t border-gray-200 py-4 dark:border-gray-700 md:py-8 lg:grid-cols-4 xl:gap-16">
        <div>
          <svg class="mb-2 h-8 w-8 text-gray-400 dark:text-gray-500" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24">
            <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 4h1.5L9 16m0 0h8m-8 0a2 2 0 1 0 0 4 2 2 0 0 0 0-4Zm8 0a2 2 0 1 0 0 4 2 2 0 0 0 0-4Zm-8.5-3h9.25L19 7H7.312" />
          </svg>
          <h3 class="mb-2 text-gray-500 dark:text-gray-400">Conversions</h3>
          <span class="flex items-center text-2xl font-bold text-gray-900 dark:text-white">
            {{ conversionsThisMonth }}
            <span :class="trendBadgeClasses">
              <svg :class="trendIconClasses" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v13m0-13 4 4m-4-4-4 4" />
              </svg>
              {{ trendLabel }}
            </span>
          </span>
          <p class="mt-2 text-sm text-gray-500 dark:text-gray-400 sm:text-base">
            {{ trendHelperText }}
          </p>
          <p class="mt-1 text-sm text-gray-500 dark:text-gray-400 sm:text-base">
            {{ usageSubtitle }}
          </p>
          <div v-if="hasFiniteLimit" class="mt-4 space-y-2">
            <div class="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
              <span>0</span>
              <span>{{ planLimitCopy }}</span>
            </div>
            <div class="h-2 w-full overflow-hidden rounded-full bg-gray-100 dark:bg-gray-800">
              <div class="h-full rounded-full bg-primary-600 transition-all duration-300" :style="{ width: usageProgress + '%' }"></div>
            </div>
            <p class="text-xs text-gray-500 dark:text-gray-400">{{ lastResetCopy }}</p>
          </div>
          <p v-else class="mt-4 text-xs text-gray-500 dark:text-gray-400">{{ lastResetCopy }}</p>
        </div>
      </div>
      <div class="py-4 md:py-8">
        <div class="mb-4 grid gap-4 sm:grid-cols-2 sm:gap-8 lg:gap-16">
          <div class="space-y-4">
            <div class="flex space-x-4">
              <div>
                <span class="mb-2 inline-block rounded px-2.5 py-0.5 text-xs font-medium" :class="planBadgeClasses">{{ planBadgeLabel }}</span>
                <h2 class="flex items-center text-xl font-bold leading-none text-gray-900 dark:text-white sm:text-2xl">{{ fullName }}</h2>
              </div>
            </div>
            <dl>
              <dt class="font-semibold text-gray-900 dark:text-white">Email</dt>
              <dd class="text-gray-500 dark:text-gray-400">{{ userEmail || 'exemple@mail.com' }}</dd>
            </dl>
            <dl>
              <dt class="font-semibold text-gray-900 dark:text-white">Adresse postale</dt>
              <dd class="flex items-center gap-1 text-gray-500 dark:text-gray-400">
                <svg class="hidden h-5 w-5 shrink-0 text-gray-400 dark:text-gray-500 lg:inline" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24">
                  <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m4 12 8-8 8 8M6 10.5V19a1 1 0 0 0 1 1h3v-3a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1v3h3a1 1 0 0 0 1-1v-8.5" />
                </svg>
                {{ placeholderText(userProfile.address, 'Adresse à saisir') }}
              </dd>
            </dl>
          </div>
          <div class="space-y-4">
            <dl>
              <dt class="font-semibold text-gray-900 dark:text-white">Numéro de téléphone</dt>
              <dd class="text-gray-500 dark:text-gray-400">{{ placeholderText(userProfile.phone, 'Téléphone à saisir') }}</dd>
            </dl>
            <dl>
              <dt class="font-semibold text-gray-900 dark:text-white">Mon entreprise</dt>
              <dd class="text-gray-500 dark:text-gray-400">{{ placeholderText(userProfile.company, "Nom d'entreprise à saisir") }}</dd>
            </dl>
            <dl>
              <dt class="font-semibold text-gray-900 dark:text-white">Plan actuel</dt>
              <dd class="text-gray-500 dark:text-gray-400">{{ planBadgeLabel }}</dd>
                  <!--<dd class="flex items-center mt-2 space-x-4 text-gray-500 dark:text-gray-400">
                    <div class="flex h-12 w-12 shrink-0 items-center justify-center rounded-lg bg-gray-100 dark:bg-gray-700">
                        <img class="h-4 w-auto dark:hidden" src="https://flowbite.s3.amazonaws.com/blocks/e-commerce/brand-logos/visa.svg" alt="" />
                        <img class="hidden h-4 w-auto dark:flex" src="https://flowbite.s3.amazonaws.com/blocks/e-commerce/brand-logos/visa-dark.svg" alt="" />
                    </div>
                    <div>
                        <div class="text-sm">
                        <p class="mb-0.5 font-medium text-gray-900 dark:text-white">Visa ending in 7658</p>
                        <p class="font-normal text-gray-500 dark:text-gray-400">Expiry 10/2024</p>
                        </div>
                    </div>
                </dd>-->
            </dl>
            <div class="flex flex-wrap gap-3 pt-2">
              <button
                type="button"
                class="inline-flex items-center rounded-lg border border-blue-200 px-4 py-2 text-sm font-medium text-blue-700 transition hover:border-blue-400 hover:text-blue-600 dark:border-blue-600 dark:text-blue-100"
                :disabled="isPortalLoading"
                @click="openBillingPortal"
              >
                <svg
                  v-if="isPortalLoading"
                  class="-ms-0.5 me-1.5 h-4 w-4 animate-spin"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  aria-hidden="true"
                >
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
                </svg>
                {{ isPortalLoading ? 'Ouverture du portail…' : 'Gérer mon abonnement' }}
              </button>
            </div>
            <p v-if="billingPortalError" class="text-sm text-red-600 dark:text-red-300">{{ billingPortalError }}</p>
          </div>
        </div>
        <button type="button" data-modal-target="accountInformationModal2" data-modal-toggle="accountInformationModal2" class="inline-flex w-full items-center justify-center rounded-lg bg-primary-700 px-5 py-2.5 text-sm font-medium text-white hover:bg-primary-800 focus:outline-none focus:ring-4 focus:ring-primary-300 dark:bg-primary-600 dark:hover:bg-primary-700 dark:focus:ring-primary-800 sm:w-auto">
          <svg class="-ms-0.5 me-1.5 h-4 w-4" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24">
            <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m14.304 4.844 2.852 2.852M7 7H4a1 1 0 0 0-1 1v10a1 1 0 0 0 1 1h11a1 1 0 0 0 1-1v-4.5m2.409-9.91a2.017 2.017 0 0 1 0 2.853l-6.844 6.844L8 14l.713-3.565 6.844-6.844a2.015 2.015 0 0 1 2.852 0Z" />
          </svg>
          Modifier mes informations
        </button>
      </div>
    </div>

    <div id="accountInformationModal2" tabindex="-1" aria-hidden="true" class="max-h-auto fixed left-0 right-0 top-0 z-50 hidden h-[calc(100%-1rem)] max-h-full w-full items-center justify-center overflow-y-auto overflow-x-hidden antialiased md:inset-0">
      <div class="max-h-auto relative max-h-full w-full max-w-lg p-4">
        <div class="relative rounded-lg bg-white shadow dark:bg-gray-800">
          <div class="flex items-center justify-between rounded-t border-b border-gray-200 p-4 dark:border-gray-700 md:p-5">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Modifier mes informations</h3>
            <button type="button" class="ms-auto inline-flex h-8 w-8 items-center justify-center rounded-lg bg-transparent text-sm text-gray-400 hover:bg-gray-200 hover:text-gray-900 dark:hover:bg-gray-600 dark:hover:text-white" data-modal-toggle="accountInformationModal2">
              <svg class="h-3 w-3" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 14 14">
                <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m1 1 6 6m0 0 6 6M7 7l6-6M7 7l-6 6" />
              </svg>
              <span class="sr-only">Fermer la fenêtre</span>
            </button>
          </div>
          <form class="p-4 md:p-5" @submit.prevent="handleSaveProfile">
            <div class="grid gap-4">
              <div class="grid gap-4 sm:grid-cols-2">
                <div>
                  <label for="first_name" class="mb-2 block text-sm font-medium text-gray-900 dark:text-white">Prénom</label>
                  <input v-model="profileForm.first_name" type="text" id="first_name" class="block w-full rounded-lg border border-gray-300 bg-gray-50 p-2.5 text-sm text-gray-900 focus:border-primary-500 focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white" placeholder="Prénom" />
                </div>
                <div>
                  <label for="last_name" class="mb-2 block text-sm font-medium text-gray-900 dark:text-white">Nom</label>
                  <input v-model="profileForm.last_name" type="text" id="last_name" class="block w-full rounded-lg border border-gray-300 bg-gray-50 p-2.5 text-sm text-gray-900 focus:border-primary-500 focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white" placeholder="Nom" />
                </div>
              </div>
              <div>
                <label for="address" class="mb-2 block text-sm font-medium text-gray-900 dark:text-white">Adresse postale</label>
                <textarea v-model="profileForm.address" id="address" rows="3" class="block w-full rounded-lg border border-gray-300 bg-gray-50 p-2.5 text-sm text-gray-900 focus:border-primary-500 focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white" placeholder="Adresse à saisir"></textarea>
              </div>
              <div>
                <label for="phone" class="mb-2 block text-sm font-medium text-gray-900 dark:text-white">Téléphone</label>
                <input v-model="profileForm.phone" type="text" id="phone" class="block w-full rounded-lg border border-gray-300 bg-gray-50 p-2.5 text-sm text-gray-900 focus:border-primary-500 focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white" placeholder="Téléphone à saisir" />
              </div>
              <div>
                <label for="company" class="mb-2 block text-sm font-medium text-gray-900 dark:text-white">Nom d'entreprise</label>
                <input v-model="profileForm.company" type="text" id="company" class="block w-full rounded-lg border border-gray-300 bg-gray-50 p-2.5 text-sm text-gray-900 focus:border-primary-500 focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white" placeholder="Nom d'entreprise à saisir" />
              </div>
            </div>
            <p class="mt-4 text-sm text-gray-500 dark:text-gray-400">L'email et le mot de passe restent gérés depuis la page d'inscription/connexion.</p>
            <div v-if="saveProfileError" class="mt-4 rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700 dark:border-red-900/40 dark:bg-red-900/20 dark:text-red-100">
              {{ saveProfileError }}
            </div>
            <div v-if="saveProfileMessage" class="mt-4 rounded-md border border-green-200 bg-green-50 px-3 py-2 text-sm text-green-700 dark:border-green-900/40 dark:bg-green-900/20 dark:text-green-100">
              {{ saveProfileMessage }}
            </div>
            <div class="mt-6 border-t border-gray-200 pt-4 dark:border-gray-700 md:pt-5">
              <button type="submit" :disabled="isSavingProfile" class="me-2 inline-flex items-center rounded-lg bg-primary-700 px-5 py-2.5 text-center text-sm font-medium text-white hover:bg-primary-800 focus:outline-none focus:ring-4 focus:ring-primary-300 disabled:cursor-not-allowed disabled:opacity-70 dark:bg-primary-600 dark:hover:bg-primary-700 dark:focus:ring-primary-800">
                <svg v-if="isSavingProfile" class="-ms-0.5 me-2 h-4 w-4 animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" aria-hidden="true">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
                </svg>
                Sauvegarder
              </button>
              <button type="button" data-modal-toggle="accountInformationModal2" class="me-2 rounded-lg border border-gray-200 bg-white px-5 py-2.5 text-sm font-medium text-gray-900 hover:bg-gray-100 hover:text-primary-700 focus:z-10 focus:outline-none focus:ring-4 focus:ring-gray-100 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-white dark:focus:ring-gray-700">
                Annuler
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000'

const userEmail = ref('')
const userPlan = ref('free')
const profileError = ref('')
const userProfile = ref(createEmptyProfile())
const profileForm = ref(createEmptyProfile())
const usageStats = ref(createEmptyUsage())
const isSavingProfile = ref(false)
const saveProfileError = ref('')
const saveProfileMessage = ref('')
const isPortalLoading = ref(false)
const billingPortalError = ref('')

const PLAN_CONFIG = {
  free: {
    badgeLabel: 'Compte Starter',
    badgeClasses: 'bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-100',
    limit: 10,
  },
  pro: {
    badgeLabel: 'Compte Pro',
    badgeClasses: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-100',
    limit: Number.POSITIVE_INFINITY,
  },
}

const resolvedPlan = computed(() => PLAN_CONFIG[userPlan.value] ?? PLAN_CONFIG.free)
const planBadgeLabel = computed(() => resolvedPlan.value.badgeLabel)
const planBadgeClasses = computed(() => resolvedPlan.value.badgeClasses)
const fullName = computed(() => buildFullName(userProfile.value))
const conversionsThisMonth = computed(() => Number(usageStats.value.conversions_this_month ?? 0))
const conversionsLastMonth = computed(() => Number(usageStats.value.conversions_last_month ?? 0))
const planLimitValue = computed(() => resolvedPlan.value.limit ?? Number.POSITIVE_INFINITY)
const hasFiniteLimit = computed(() => Number.isFinite(planLimitValue.value))
const usageProgress = computed(() => {
  if (!hasFiniteLimit.value || planLimitValue.value <= 0) {
    return 0
  }
  const ratio = (conversionsThisMonth.value / planLimitValue.value) * 100
  return Math.min(100, Math.max(0, Math.round(ratio)))
})
const usageSubtitle = computed(() =>
  hasFiniteLimit.value
    ? `${conversionsThisMonth.value}/${planLimitValue.value} conversions ce mois`
    : `${conversionsThisMonth.value} conversions générées`
)
const planLimitCopy = computed(() => (hasFiniteLimit.value ? `${planLimitValue.value} / mois` : 'Illimité'))
const trendDelta = computed(() => conversionsThisMonth.value - conversionsLastMonth.value)
const trendPercent = computed(() => {
  if (conversionsLastMonth.value === 0) {
    return conversionsThisMonth.value === 0 ? 0 : 100
  }
  return Math.round((trendDelta.value / conversionsLastMonth.value) * 100)
})
const trendLabel = computed(() => `${Math.abs(trendPercent.value)}%`)
const isTrendPositive = computed(() => trendDelta.value >= 0)
const trendBadgeClasses = computed(() =>
  isTrendPositive.value
    ? 'ms-2 inline-flex items-center rounded bg-green-100 px-2.5 py-0.5 text-xs font-medium text-green-800 dark:bg-green-900 dark:text-green-200'
    : 'ms-2 inline-flex items-center rounded bg-red-100 px-2.5 py-0.5 text-xs font-medium text-red-800 dark:bg-red-900 dark:text-red-200'
)
const trendIconClasses = computed(() =>
  `-ms-1 me-1 h-4 w-4 ${isTrendPositive.value ? '' : 'rotate-180'}`
)
const trendHelperText = computed(() => {
  if (conversionsLastMonth.value === 0 && conversionsThisMonth.value === 0) {
    return 'Aucune conversion enregistrée sur les deux derniers mois.'
  }
  if (conversionsLastMonth.value === 0) {
    return 'Premières conversions enregistrées ce mois-ci.'
  }
  return `vs ${conversionsLastMonth.value} le mois dernier`
})
const lastResetCopy = computed(() => {
  if (!hasFiniteLimit.value) {
    return 'Conversions illimitées sur votre plan Pro.'
  }
  const raw = usageStats.value.last_reset_date
  if (!raw) {
    return 'Réinitialisation automatique chaque début de mois.'
  }
  const parsed = new Date(raw)
  if (Number.isNaN(parsed.valueOf())) {
    return 'Réinitialisation automatique chaque début de mois.'
  }
  const formatted = new Intl.DateTimeFormat('fr-FR', { day: '2-digit', month: 'long' }).format(parsed)
  return `Dernière remise à zéro le ${formatted}`
})

function createEmptyProfile() {
  return {
    first_name: '',
    last_name: '',
    address: '',
    phone: '',
    company: '',
  }
}

function createEmptyUsage() {
  return {
    conversions_this_month: 0,
    conversions_last_month: 0,
    last_reset_date: null,
  }
}

function buildFullName(profile) {
  const first = normalizeField(profile.first_name)
  const last = normalizeField(profile.last_name)
  if (first || last) {
    return [first, last].filter(Boolean).join(' ')
  }
  return 'Prenom Nom'
}

function normalizeField(value) {
  if (value === null || value === undefined) {
    return ''
  }
  return String(value).trim()
}

function placeholderText(value, fallback) {
  const normalized = normalizeField(value)
  return normalized.length > 0 ? normalized : fallback
}

function pickProfileFields(payload = {}) {
  return {
    first_name: payload.first_name ?? '',
    last_name: payload.last_name ?? '',
    address: payload.address ?? '',
    phone: payload.phone ?? '',
    company: payload.company ?? '',
  }
}

function applyProfile(payload = {}) {
  userProfile.value = {
    ...userProfile.value,
    ...pickProfileFields(payload),
  }
  profileForm.value = { ...createEmptyProfile(), ...userProfile.value }
}

function applyUsage(payload = {}) {
  usageStats.value = {
    conversions_this_month:
      Number(payload.conversions_this_month ?? usageStats.value.conversions_this_month ?? 0),
    conversions_last_month:
      Number(payload.conversions_last_month ?? usageStats.value.conversions_last_month ?? 0),
    last_reset_date: payload.last_reset_date ?? usageStats.value.last_reset_date ?? null,
  }
}

const hydrateFromStoredUser = () => {
  const rawUser = localStorage.getItem('user')
  if (!rawUser) {
    return
  }

  try {
    const cachedUser = JSON.parse(rawUser)
    if (cachedUser?.email) {
      userEmail.value = cachedUser.email
    }
    if (cachedUser?.plan) {
      userPlan.value = cachedUser.plan
    }
    applyProfile(cachedUser)
    applyUsage(cachedUser)
  } catch (error) {
    console.warn('Unable to parse cached user', error)
  }
}

const fetchProfile = async () => {
  const token = localStorage.getItem('access_token')
  if (!token) {
    profileError.value = 'Connectez-vous pour retrouver vos informations.'
    return
  }

  profileError.value = ''

  try {
    const response = await fetch(`${API_BASE_URL}/auth/me`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })

    if (!response.ok) {
      let message = 'Impossible de récupérer vos informations.'
      try {
        const body = await response.json()
        if (body?.detail) {
          message = body.detail
        }
      } catch (parseError) {
        console.warn('Unable to parse /auth/me error response', parseError)
      }
      throw new Error(message)
    }

    const data = await response.json()
    if (data?.email) {
      userEmail.value = data.email
    }
    if (data?.plan) {
      userPlan.value = data.plan
    }
    applyProfile(data)
    applyUsage(data)
    localStorage.setItem('user', JSON.stringify(data))
  } catch (error) {
    hydrateFromStoredUser()
    const fallbackMessage = error instanceof Error ? error.message : 'Impossible de récupérer vos informations.'
    profileError.value = `${fallbackMessage} (Affichage des données mises en cache)`
  }
}

const handleSaveProfile = async () => {
  const token = localStorage.getItem('access_token')
  if (!token) {
    saveProfileError.value = 'Connectez-vous pour modifier vos informations.'
    return
  }

  saveProfileError.value = ''
  saveProfileMessage.value = ''
  isSavingProfile.value = true

  try {
    const response = await fetch(`${API_BASE_URL}/auth/profile`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(profileForm.value),
    })

    if (!response.ok) {
      let message = 'Impossible de sauvegarder vos informations.'
      try {
        const body = await response.json()
        if (body?.detail) {
          message = body.detail
        }
      } catch (parseError) {
        console.warn('Unable to parse profile update error response', parseError)
      }
      throw new Error(message)
    }

    const updatedUser = await response.json()
    if (updatedUser?.email) {
      userEmail.value = updatedUser.email
    }
    if (updatedUser?.plan) {
      userPlan.value = updatedUser.plan
    }
    applyProfile(updatedUser)
    applyUsage(updatedUser)

    try {
      const cachedUser = JSON.parse(localStorage.getItem('user') ?? '{}')
      const usageSnapshot = { ...usageStats.value }
      const mergedUser = { ...cachedUser, ...usageSnapshot, ...updatedUser }
      localStorage.setItem('user', JSON.stringify(mergedUser))
    } catch (storageError) {
      console.warn('Unable to merge cached user with updated data', storageError)
      const fallbackPayload = { ...usageStats.value, ...updatedUser }
      localStorage.setItem('user', JSON.stringify(fallbackPayload))
    }

    saveProfileMessage.value = 'Informations mises à jour.'
  } catch (error) {
    const fallbackMessage = error instanceof Error ? error.message : 'Impossible de sauvegarder vos informations.'
    saveProfileError.value = fallbackMessage
  } finally {
    isSavingProfile.value = false
  }
}

const openBillingPortal = async () => {
  const token = localStorage.getItem('access_token')
  if (!token) {
    billingPortalError.value = 'Connectez-vous pour gérer votre abonnement.'
    return
  }

  billingPortalError.value = ''
  isPortalLoading.value = true

  try {
    const response = await fetch(`${API_BASE_URL}/billing/portal`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })

    if (!response.ok) {
      const payload = await safeJson(response)
      const detail = payload?.detail || "Impossible d'ouvrir le portail Stripe."
      throw new Error(detail)
    }

    const data = await response.json()
    if (!data?.url) {
      throw new Error('URL du portail introuvable.')
    }
    window.location.href = data.url
  } catch (error) {
    billingPortalError.value = error instanceof Error ? error.message : 'Erreur inattendue.'
  } finally {
    isPortalLoading.value = false
  }
}

const safeJson = async (response) => {
  try {
    return await response.json()
  } catch (err) {
    console.warn('Réponse non JSON', err)
    return null
  }
}

onMounted(() => {
  hydrateFromStoredUser()
  fetchProfile()
})
</script>
