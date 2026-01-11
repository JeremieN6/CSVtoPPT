<template>
  <section class="bg-gray-50 py-12 dark:bg-gray-900">
    <div class="mx-auto max-w-screen-xl px-4 lg:px-6">
      <div class="grid gap-10 lg:grid-cols-2 lg:items-start">
        <div class="space-y-5">
          <p class="inline-flex items-center gap-2 rounded-full bg-blue-100 px-4 py-1 text-xs font-semibold uppercase tracking-[0.3em] text-blue-700 dark:bg-blue-900/30 dark:text-blue-300">
            Convertisseur CSV → PPT
          </p>
          <h2 class="text-3xl font-extrabold text-gray-900 dark:text-white">
            Convertissez vos CSV en présentations prêtes à présenter
          </h2>
          <p class="text-base text-gray-500 dark:text-gray-300">
            Téléversez vos données (CSV ou XLSX) puis laissez le pipeline générer automatiquement une présentation PowerPoint
            structurée : analyses, graphiques et slides propres sont produits côté backend.
          </p>
          <ul class="space-y-3 text-sm text-gray-600 dark:text-gray-300">
            <li class="flex items-start gap-3">
              <span class="mt-1 inline-flex h-5 w-5 items-center justify-center rounded-full bg-blue-600 text-xs font-bold text-white">1</span>
              Glissez/déposez votre fichier ou cliquez pour le sélectionner.
            </li>
            <li class="flex items-start gap-3">
              <span class="mt-1 inline-flex h-5 w-5 items-center justify-center rounded-full bg-blue-600 text-xs font-bold text-white">2</span>
              Choisissez un titre et une palette, puis lancez la génération.
            </li>
            <li class="flex items-start gap-3">
              <span class="mt-1 inline-flex h-5 w-5 items-center justify-center rounded-full bg-blue-600 text-xs font-bold text-white">3</span>
              Téléchargez le PPTX produit automatiquement, accompagné d’éventuels avertissements.
            </li>
          </ul>
        </div>
        <div class="rounded-3xl border border-gray-200 bg-white p-8 shadow-lg dark:border-gray-800 dark:bg-gray-900">
          <div class="space-y-6">
            <FileUploader
              :disabled="isLoading"
              :selected-file-name="selectedFile?.name ?? ''"
              @file-selected="handleFileSelected"
              @file-error="handleFileError"
            />

            <div class="grid gap-4 md:grid-cols-2">
              <div>
                <label for="report-title" class="mb-2 block text-sm font-medium text-gray-900 dark:text-gray-100">Titre du rapport</label>
                <input
                  id="report-title"
                  v-model="reportTitle"
                  type="text"
                  class="block w-full rounded-xl border border-gray-300 bg-white px-4 py-2.5 text-sm text-gray-900 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100"
                  placeholder="Performance Q4"
                  :disabled="isLoading"
                />
              </div>
              <div>
                <label for="report-theme" class="mb-2 block text-sm font-medium text-gray-900 dark:text-gray-100">Palette</label>
                <select
                  id="report-theme"
                  v-model="theme"
                  class="block w-full rounded-xl border border-gray-300 bg-white px-4 py-2.5 text-sm text-gray-900 shadow-sm focus:border-blue-500 focus:ring-blue-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-100"
                  :disabled="isLoading"
                >
                  <option value="corporate">Corporate</option>
                  <option value="minimal">Minimal</option>
                  <option value="energetic">Énergique</option>
                </select>
              </div>
            </div>

            <div class="flex flex-col gap-3 sm:flex-col sm:items-center sm:justify-between">
              <p class="text-xs text-gray-500 dark:text-gray-400">
                Formats supportés : CSV/XLSX · Données stockées temporairement · Génération moyenne &lt; 15&nbsp;s
              </p>
              <button
                type="button"
                class="inline-flex w-full items-center justify-center gap-2 rounded-xl px-6 py-2.5 text-sm font-semibold transition focus:ring-4 disabled:cursor-not-allowed"
                :class="
                  canGenerate
                    ? 'bg-blue-700 text-white hover:bg-blue-600 focus:ring-blue-300 dark:bg-blue-600 dark:hover:bg-blue-500'
                    : 'border border-gray-300 bg-gray-200 text-gray-500 focus:ring-gray-200 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-400'
                "
                :disabled="!canGenerate"
                @click="generatePresentation"
              >
                <svg
                  v-if="isLoading"
                  class="h-4 w-4 animate-spin"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4l3.5-3.5L12 1v4a7 7 0 00-7 7h-1z" />
                </svg>
                {{ isLoading ? 'Génération en cours…' : 'Générer la présentation' }}
              </button>
            </div>

            <div v-if="errorMessage" class="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700 dark:border-red-900/40 dark:bg-red-900/20 dark:text-red-100" role="alert">
              {{ errorMessage }}
            </div>

            <div v-if="downloadUrl" class="space-y-3 rounded-2xl border border-emerald-200 bg-emerald-50 p-5 text-emerald-900 dark:border-emerald-900/40 dark:bg-emerald-900/20 dark:text-emerald-100">
              <div class="flex items-center gap-3">
                <svg class="h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 16V4m0 12 4-4m-4 4-4-4m-2 8h12" />
                </svg>
                <div>
                  <p class="font-semibold">Votre présentation est prête 🎉</p>
                  <p class="text-sm text-emerald-700 dark:text-emerald-200">Téléchargez le PPTX généré automatiquement.</p>
                </div>
              </div>
              <a
                class="inline-flex items-center justify-center gap-2 rounded-xl bg-emerald-600 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-emerald-500"
                :href="downloadUrl"
                :download="downloadFileName"
              >
                Télécharger le PPT
              </a>
            </div>

            <div v-if="warnings.length" class="space-y-2 rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900 dark:border-amber-900/40 dark:bg-amber-900/20 dark:text-amber-100">
              <p class="font-semibold">Avertissements</p>
              <ul class="list-disc space-y-1 pl-5">
                <li v-for="warning in warnings" :key="warning">{{ warning }}</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Toast quota (free plan) -->
    <transition name="fade">
      <div
        v-if="quotaToast.visible"
        class="fixed top-4 right-4 z-50 w-full max-w-sm rounded-xl border border-blue-200 bg-white/95 p-4 shadow-xl backdrop-blur dark:border-blue-900/50 dark:bg-slate-900/95"
      >
        <div class="flex items-start gap-3">
          <span class="mt-0.5 inline-flex h-8 w-8 items-center justify-center rounded-full bg-blue-100 text-blue-700 dark:bg-blue-800 dark:text-blue-100">⚡</span>
          <div class="flex-1 space-y-1 text-sm text-gray-800 dark:text-gray-100">
            <p class="font-semibold">Limite gratuite</p>
            <p>{{ quotaToast.message }}</p>
            <div class="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-300">
              <a class="font-semibold text-blue-700 underline dark:text-blue-300" href="/inscription">Passer Pro</a>
              <span aria-hidden="true">·</span>
              <a class="font-semibold text-gray-700 underline dark:text-gray-200" href="/profil">Voir mon quota</a>
            </div>
          </div>
          <button class="text-gray-400 transition hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300" @click="hideQuotaToast" aria-label="Fermer la notification">
            ✕
          </button>
        </div>
      </div>
    </transition>

    <!-- Modal quota atteint -->
    <transition name="fade">
      <div v-if="showQuotaModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4 backdrop-blur-sm">
        <div class="w-full max-w-lg rounded-2xl bg-white p-6 shadow-2xl dark:bg-slate-900">
          <div class="mb-4 flex items-start gap-3">
            <div class="mt-1 inline-flex h-10 w-10 items-center justify-center rounded-full bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-100">🚫</div>
            <div class="space-y-1">
              <p class="text-lg font-semibold text-gray-900 dark:text-white">Quota atteint</p>
              <p class="text-sm text-gray-700 dark:text-gray-200">{{ quotaModalMessage }}</p>
              <p v-if="quotaCounts.limit" class="text-sm font-medium text-gray-900 dark:text-gray-100">
                {{ quotaCounts.used }} / {{ quotaCounts.limit }} conversions utilisées ce mois-ci.
              </p>
              <p class="text-sm text-gray-600 dark:text-gray-300">Passez au plan Pro pour continuer sans limite.</p>
            </div>
          </div>
          <div class="mb-4 grid gap-3 rounded-2xl border border-gray-200 bg-gray-50 p-4 text-sm text-gray-800 dark:border-gray-800 dark:bg-gray-800/60 dark:text-gray-100 sm:grid-cols-2">
            <div>
              <p class="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-300">🧠 IA Light (Free)</p>
              <ul class="mt-2 space-y-1">
                <li>Texte descriptif simple</li>
                <li>Résumés courts</li>
                <li>Pas d’analyse croisée</li>
                <li>Style neutre</li>
              </ul>
            </div>
            <div>
              <p class="text-xs font-semibold uppercase tracking-wide text-blue-700 dark:text-blue-200">🚀 IA Pro</p>
              <ul class="mt-2 space-y-1">
                <li>Analyses intelligentes</li>
                <li>Corrélations & insights</li>
                <li>Texte orienté décision</li>
                <li>Slides prêtes pour présentation client/comité</li>
                <li class="text-[13px] font-medium">IA optimisée pour un usage professionnel</li>
              </ul>
            </div>
          </div>
          <div class="flex flex-col gap-3 sm:flex-row sm:justify-end">
            <a
              href="/inscription"
              class="inline-flex w-full items-center justify-center rounded-xl bg-blue-700 px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-600 sm:w-auto"
            >
              Passer Pro
            </a>
            <a
              href="/profil"
              class="inline-flex w-full items-center justify-center rounded-xl border border-gray-300 px-4 py-2 text-sm font-semibold text-gray-800 transition hover:bg-gray-50 dark:border-gray-700 dark:text-gray-100 dark:hover:bg-gray-800 sm:w-auto"
              @click="showQuotaModal = false"
            >
              Voir mon quota
            </a>
          </div>
        </div>
      </div>
    </transition>
  </section>
</template>

<script setup>
import { computed, onBeforeUnmount, ref } from 'vue'
import FileUploader from './FileUploader.vue'

const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL
  || (typeof window !== 'undefined'
    && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
      ? 'http://127.0.0.1:8000'
      : '/api')
).replace(/\/$/, '')
const AUTH_TOKEN_KEY = 'access_token'
const PLAN_LIMITS = { free: 10 }
const SIZE_LIMITS = {
  csv: 15 * 1024 * 1024, // 15 Mo
  excel: 8 * 1024 * 1024, // 8 Mo
}

const selectedFile = ref(null)
const reportTitle = ref('Rapport - Présentation du jour')
const theme = ref('corporate')
const isLoading = ref(false)
const errorMessage = ref('')
const downloadUrl = ref('')
const downloadFileName = ref('rapport-presentation-du-jour.pptx')
const warnings = ref([])
const showQuotaModal = ref(false)
const quotaModalMessage = ref('Limite atteinte sur votre plan actuel.')
const quotaCounts = ref({ used: null, limit: null })
const quotaToast = ref({ visible: false, message: '' })
let quotaToastTimer = null

const canGenerate = computed(() => Boolean(selectedFile.value) && !isLoading.value)

const resetDownload = () => {
  if (downloadUrl.value) {
    URL.revokeObjectURL(downloadUrl.value)
    downloadUrl.value = ''
  }
}

const handleFileSelected = (file) => {
  if (!file) return

  const extension = file.name.split('.').pop()?.toLowerCase() || ''
  const isExcel = ['xlsx', 'xls'].includes(extension)
  const isCsvLike = ['csv', 'tsv', 'txt'].includes(extension)
  const limit = isExcel ? SIZE_LIMITS.excel : SIZE_LIMITS.csv

  if (!isExcel && !isCsvLike) {
    handleFileError('Seuls les fichiers CSV/TSV/TXT ou XLS/XLSX sont acceptés.')
    selectedFile.value = null
    return
  }

  if (file.size > limit) {
    showQuotaToast(
      "Le fichier est vraiment trop volumineux. Veuillez le segmenter ou choisir un autre fichier. Sinon contactez-nous : contact-csvtoppt@sassify.fr",
      { persistent: true }
    )
    selectedFile.value = null
    return
  }

  selectedFile.value = file
  errorMessage.value = ''
  warnings.value = []
  resetDownload()
}

const handleFileError = (message) => {
  showQuotaToast(message || 'Format non supporté. Choisissez un CSV/TSV/TXT ou un XLS/XLSX.', { persistent: true })
}

const sanitizeFileName = (value) =>
  value
    .toLowerCase()
    .normalize('NFD')
    .replace(/[^a-z0-9\s-]/g, '')
    .trim()
    .replace(/\s+/g, '-') || 'rapport-presentation-du-jour'

const generatePresentation = async () => {
  if (!selectedFile.value || isLoading.value) {
    return
  }

  const token = localStorage.getItem(AUTH_TOKEN_KEY)
  if (!token) {
    errorMessage.value = 'Connectez-vous pour générer une présentation.'
    return
  }

  isLoading.value = true
  errorMessage.value = ''
  warnings.value = []
  resetDownload()

  const formData = new FormData()
  formData.append('file', selectedFile.value)
  formData.append('title', reportTitle.value || 'Rapport - Présentation du jour')
  formData.append('theme', theme.value)
  formData.append('use_ai', 'true')

  try {
    const response = await fetch(`${API_BASE_URL}/convert`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: formData,
    })

    if (!response.ok) {
      const status = response.status
      let errorDetail = 'Impossible de générer la présentation.'
      try {
        const payload = await response.json()
        errorDetail = payload?.detail || errorDetail
      } catch (err) {
        console.error('Erreur parse JSON', err)
      }
      if (status === 403) {
        if (/limite du plan free/i.test(errorDetail) || /5\s*000/.test(errorDetail)) {
          showQuotaToast(errorDetail || 'Votre fichier dépasse la limite de lignes du plan Free.', { persistent: true })
          isLoading.value = false
          return
        }
        const parsed = parseQuotaDetail(errorDetail)
        quotaCounts.value = parsed
        quotaModalMessage.value = errorDetail || 'Limite atteinte sur votre plan actuel.'
        showQuotaModal.value = true
        isLoading.value = false
        return
      }
      if (status === 401) {
        window.localStorage.removeItem(AUTH_TOKEN_KEY)
        window.localStorage.removeItem('user')
        errorMessage.value = 'Session expirée, merci de vous reconnecter.'
        window.location.href = '/connexion'
        isLoading.value = false
        return
      }
      if (status === 400 || status === 413 || /trop volumineux/i.test(errorDetail)) {
        showQuotaToast(
          "Le fichier est vraiment trop volumineux. Veuillez le segmenter ou choisir un autre fichier. Sinon contactez-nous : contact-csvtoppt@sassify.fr",
          { persistent: true }
        )
        isLoading.value = false
        return
      }
      throw new Error(errorDetail)
    }

    const headerWarnings = response.headers.get('X-Report-Warnings')
    if (headerWarnings) {
      warnings.value = headerWarnings
        .split('|')
        .map((item) => item.trim())
        .filter(Boolean)
    }

    const blob = await response.blob()
    downloadFileName.value = `${sanitizeFileName(reportTitle.value)}.pptx`
    downloadUrl.value = URL.createObjectURL(blob)

    await refreshUsageSnapshotAndToast()
  } catch (error) {
    errorMessage.value = error?.message || 'Erreur inconnue lors de la génération.'
  } finally {
    isLoading.value = false
  }
}

onBeforeUnmount(() => {
  resetDownload()
  hideQuotaToast()
})

const parseQuotaDetail = (detail) => {
  const match = typeof detail === 'string' ? detail.match(/(\d+)\s*\/\s*(\d+)/) : null
  if (match) {
    const used = Number(match[1])
    const limit = Number(match[2])
    return { used, limit }
  }
  return { used: null, limit: null }
}

const showQuotaToast = (message, options = {}) => {
  const persistent = Boolean(options.persistent)
  quotaToast.value = { visible: true, message, persistent }
  if (quotaToastTimer) {
    clearTimeout(quotaToastTimer)
    quotaToastTimer = null
  }
  if (!persistent) {
    quotaToastTimer = setTimeout(() => {
      quotaToast.value.visible = false
    }, 6000)
  }
}

const hideQuotaToast = () => {
  quotaToast.value.visible = false
  if (quotaToastTimer) {
    clearTimeout(quotaToastTimer)
    quotaToastTimer = null
  }
}

const refreshUsageSnapshotAndToast = async () => {
  const token = localStorage.getItem(AUTH_TOKEN_KEY)
  if (!token) return

  try {
    const res = await fetch(`${API_BASE_URL}/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
    })
    if (!res.ok) return
    const data = await res.json()
    if (data?.plan) {
      const plan = data.plan
      const limit = PLAN_LIMITS[plan]
      if (plan === 'free' && Number.isFinite(limit)) {
        const used = Number(data.conversions_this_month ?? 0)
        const remaining = Math.max(0, limit - used)
        const msg = remaining > 0
          ? `Il vous reste ${remaining} conversion${remaining > 1 ? 's' : ''} sur ${limit} ce mois-ci.`
          : `Vous avez atteint ${used}/${limit} conversions ce mois-ci. Passez en Pro pour continuer.`
        showQuotaToast(msg)
      }
    }
    try {
      localStorage.setItem('user', JSON.stringify(data))
    } catch (err) {
      console.warn('Impossible de stocker le snapshot utilisateur', err)
    }
  } catch (err) {
    console.warn('Snapshot usage échoué', err)
  }
}
</script>
