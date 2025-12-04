<template>
  <section id="generator" class="bg-gray-50 py-16 dark:bg-gray-900">
    <div class="mx-auto grid max-w-screen-xl gap-10 px-4 lg:grid-cols-2 lg:items-center lg:px-8">
      <div class="space-y-5">
        <p class="inline-flex items-center gap-2 rounded-full bg-blue-100 px-4 py-1 text-xs font-semibold uppercase tracking-[0.3em] text-blue-700 dark:bg-blue-900/30 dark:text-blue-300">
          Convertisseur CSV → PPT
        </p>
        <h2 class="text-3xl font-extrabold text-gray-900 dark:text-white">
          Convertissez vos CSV en présentations prêtes à présenter
        </h2>
        <p class="text-base text-gray-500 dark:text-gray-300">
          Téléversez vos données (CSV ou XLSX) puis laissez notre pipeline générer automatiquement une présentation PowerPoint
          structurée : analyses, graphiques et slides propres sont produits côté backend FastAPI.
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
      <ReportGenerator />
    </div>
  </section>
</template>

<script setup>
import ReportGenerator from '../convertisseur/ReportGenerator.vue'
</script>
