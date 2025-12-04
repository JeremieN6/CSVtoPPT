<template>
  <!-- Default layout (visible) -->
  <section v-if="!useAltLayout" id="process" class="bg-gray-50 dark:bg-gray-900">
    <div class="mx-auto max-w-screen-xl px-4 py-16 lg:px-8">
      <div class="mx-auto max-w-2xl text-center">
        <p class="inline-flex items-center gap-2 rounded-full border border-blue-200 bg-blue-50 px-4 py-1 text-xs font-semibold uppercase tracking-[0.25em] text-blue-700 dark:border-blue-500/30 dark:bg-blue-900/20 dark:text-blue-200">
          Processus
        </p>
        <h2 class="mt-4 text-3xl font-extrabold tracking-tight text-gray-900 dark:text-white sm:text-4xl">
          Trois étapes pour un PowerPoint prêt à présenter
        </h2>
        <p class="mt-3 text-base text-gray-500 dark:text-gray-400">
          L’interface guide votre équipe depuis l’import du fichier jusqu’au téléchargement du PPTX final.
        </p>
      </div>

      <ol class="mt-12 items-center space-y-12 sm:flex sm:space-y-0 sm:space-x-0 sm:divide-x sm:divide-gray-200 dark:sm:divide-gray-700">
        <li
          v-for="(step, index) in steps"
          :key="step.id"
          class="relative flex-1 text-center sm:px-6"
        >
          <div class="flex items-center justify-center">
            <div class="z-10 flex h-16 w-16 items-center justify-center rounded-full border border-blue-200 bg-blue-50 text-2xl font-semibold text-blue-700 dark:border-blue-500/30 dark:bg-blue-900/30 dark:text-blue-200">
              {{ step.id }}
            </div>
          </div>
          <div class="mt-6 space-y-2">
            <p class="text-sm font-semibold uppercase tracking-wide text-blue-600 dark:text-blue-300">
              {{ step.label }}
            </p>
            <h3 class="text-xl font-semibold text-gray-900 dark:text-white">
              {{ step.title }}
            </h3>
            <p class="text-gray-600 dark:text-gray-400">
              {{ step.description }}
            </p>
          </div>
          <div
            aria-hidden="true"
            :class="[
              'hidden sm:absolute sm:inset-y-8 sm:-right-3 sm:flex sm:w-px sm:bg-gray-200 dark:sm:bg-gray-700',
              index === steps.length - 1 ? 'sm:hidden' : ''
            ]"
          ></div>
        </li>
      </ol>
    </div>
  </section>

  <!-- Alternative layout (toggle useAltLayout to true to display) -->
  <section v-else id="process" class="bg-gradient-to-b from-white via-blue-50/60 to-white dark:from-gray-900 dark:via-gray-900/40 dark:to-gray-900">
    <div class="mx-auto max-w-screen-xl px-4 py-16 lg:px-8">
      <div class="max-w-3xl">
        <p class="text-sm font-semibold uppercase tracking-[0.3em] text-blue-600 dark:text-blue-300">Processus</p>
        <h2 class="mt-3 text-4xl font-extrabold tracking-tight text-gray-900 dark:text-white">Un parcours fluide pour transformer vos données en slides</h2>
        <p class="mt-4 text-base text-gray-600 dark:text-gray-400">Importer, paramétrer, livrer&nbsp;: tout est pensé pour gagner du temps et garder la maîtrise sur chaque étape.</p>
      </div>

      <div class="mt-12 grid gap-6 md:grid-cols-3">
        <article
          v-for="(step, index) in steps"
          :key="step.id"
          class="rounded-2xl border border-gray-200 bg-white/80 p-6 text-left shadow-sm backdrop-blur dark:border-gray-800 dark:bg-gray-800/70"
        >
          <div class="mb-4 flex items-center gap-4">
            <span class="flex h-12 w-12 items-center justify-center rounded-full bg-blue-100 text-lg font-semibold text-blue-700 dark:bg-blue-900/40 dark:text-blue-200">
              {{ index + 1 }}
            </span>
            <div>
              <p class="text-xs font-semibold uppercase tracking-wide text-blue-600 dark:text-blue-300">{{ step.label }}</p>
              <h3 class="text-xl font-semibold text-gray-900 dark:text-white">{{ step.title }}</h3>
            </div>
          </div>
          <p class="text-gray-600 dark:text-gray-300">{{ step.description }}</p>
          <div class="mt-6 rounded-lg bg-gray-100 p-4 dark:bg-gray-900/60">
            <div class="flex items-center gap-3 text-gray-700 dark:text-gray-200">
              <span class="rounded-md bg-blue-600/10 p-2 text-blue-600 dark:text-blue-300">
                <svg class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
                  <path :d="step.iconPath" fill-rule="evenodd" clip-rule="evenodd"></path>
                </svg>
              </span>
              <p class="text-sm font-medium">{{ step.caption }}</p>
            </div>
          </div>
        </article>
      </div>
    </div>
  </section>
</template>

<script setup>
const useAltLayout = false

const steps = [
  {
    id: '01',
    label: 'Étape 1',
    title: 'Importez votre fichier',
    description: 'Glissez/déposez votre CSV ou Excel ou cliquez pour le sélectionner depuis votre ordinateur.',
    caption: 'Import CSV/Excel sécurisé en quelques secondes',
    iconPath: 'M3 4a1 1 0 011-1h12a1 1 0 011 1v12a1 1 0 01-1 1H4a1 1 0 01-1-1V4zm4 2a1 1 0 100 2h6a1 1 0 100-2H7zm0 4a1 1 0 100 2h6a1 1 0 100-2H7z'
  },
  {
    id: '02',
    label: 'Étape 2',
    title: 'Personnalisez la génération',
    description: 'Choisissez un titre, un template, une palette de couleurs puis lancez la génération automatique.',
    caption: 'Options de branding et IA de mise en page',
    iconPath: 'M4 3a1 1 0 00-1 1v12a1 1 0 001 1h5v-2H5V5h10v4h2V4a1 1 0 00-1-1H4zm7 8a1 1 0 10-2 0v2H7l3 3 3-3h-2v-2z'
  },
  {
    id: '03',
    label: 'Étape 3',
    title: 'Téléchargez le PPTX',
    description: 'Récupérez la présentation générée, enrichie d’avertissements éventuels pour vos données.',
    caption: 'Export PPTX structuré + commentaires qualité',
    iconPath: 'M10 3a1 1 0 011 1v9.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 111.414-1.414L9 13.586V4a1 1 0 011-1zm-6 12a1 1 0 011-1h10a1 1 0 110 2H5a1 1 0 01-1-1z'
  },
]
</script>
