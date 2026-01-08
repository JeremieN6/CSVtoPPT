<template>
  <section id="convertisseur" class="bg-gradient-to-b from-blue-900 via-blue-900/90 to-gray-900 text-white">
    <div class="mx-auto max-w-screen-xl px-4 py-16 lg:px-8">
      <div class="grid gap-10 lg:grid-cols-2 lg:items-center">
        <div class="space-y-6">
          <p class="inline-flex items-center gap-2 rounded-full bg-white/10 px-4 py-1 text-xs font-semibold uppercase tracking-[0.4em] text-blue-100">
            Démo guidée
          </p>
          <h2 class="text-4xl font-extrabold leading-tight">Montrez votre CSV qui travaille pour vous</h2>
          <p class="text-base text-blue-100">
            Plutôt que de proposer l’upload complet directement sur la landing, on vous glisse un rappel léger.
            Cliquez pour ouvrir l’espace convertisseur, glissez votre fichier et laissez la génération automatique produire vos slides.
          </p>
          <ul class="space-y-4">
            <li v-for="item in teaserPoints" :key="item.title" class="flex gap-3 rounded-2xl bg-white/5 p-4">
              <span class="mt-1 text-lg font-semibold text-blue-200">{{ item.id }}</span>
              <div>
                <p class="font-semibold">{{ item.title }}</p>
                <p class="text-sm text-blue-100">{{ item.description }}</p>
              </div>
            </li>
          </ul>
          <div class="flex flex-wrap gap-4">
            <RouterLink
              to="/convertisseur"
              class="inline-flex items-center justify-center rounded-xl bg-white px-6 py-3 text-sm font-semibold text-blue-900 shadow-lg transition hover:-translate-y-0.5"
            >
              Accéder au convertisseur
              <svg class="ml-2 h-4 w-4" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                <path fill-rule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l5 5a1 1 0 010 1.414l-5 5a1 1 0 01-1.414-1.414L13.586 11H4a1 1 0 110-2h9.586l-3.293-3.293a1 1 0 010-1.414z" clip-rule="evenodd" />
              </svg>
            </RouterLink>
            <a href="#pricing" class="inline-flex items-center justify-center rounded-xl border border-white/20 px-6 py-3 text-sm font-semibold text-white transition hover:bg-white/10">
              Voir les tarifs
            </a>
          </div>
        </div>
        <div class="relative">
          <div class="rounded-3xl bg-white/5 p-6 shadow-2xl backdrop-blur">
            <div class="flex items-center justify-between text-xs uppercase tracking-[0.3em] text-blue-200">
              <span>Prévisualisation</span>
              <span>Module G</span>
            </div>
            <div class="mt-4 space-y-4">
              <div class="rounded-2xl border border-white/10 bg-white/5 p-4">
                <p class="text-sm font-semibold text-white">Upload</p>
                <p class="text-xs text-blue-100">fiche_contrats_q4.csv</p>
                <div class="mt-3 h-2 rounded-full bg-white/10">
                  <div class="h-2 rounded-full bg-emerald-400" style="width: 65%"></div>
                </div>
              </div>
              <div class="rounded-2xl border border-white/10 bg-white/5 p-4">
                <p class="text-sm font-semibold text-white">AI formatting</p>
                <p class="text-xs text-blue-100">Palette « Corporate » + slides thématiques</p>
                <div class="mt-3 h-2 rounded-full bg-white/10">
                  <div class="h-2 rounded-full bg-blue-400" style="width: 45%"></div>
                </div>
              </div>
              <div class="rounded-2xl border border-white/10 bg-white/5 p-4">
                <p class="text-sm font-semibold text-white">Export PPTX</p>
                <p class="text-xs text-blue-100">Commentaires qualité + téléchargement</p>
                <div class="mt-3 h-2 rounded-full bg-white/10">
                  <div class="h-2 rounded-full bg-violet-400" style="width: 90%"></div>
                </div>
              </div>
            </div>
            <p class="mt-6 text-center text-xs text-blue-200">Envie de tester ? direction la page convertisseur.</p>
          </div>
          <div class="pointer-events-none absolute -left-6 -top-6 hidden h-16 w-16 rounded-2xl border border-dashed border-white/20 lg:block"></div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { RouterLink } from 'vue-router'

const teaserPoints = [
  {
    id: '01',
    title: 'Glissez votre CSV/XLSX',
    description: 'Aucun envoi visible ici : la zone de drop se trouve sur la page convertisseur, avec les mêmes contrôles.'
  },
  {
    id: '02',
    title: 'Personnalisez le rendu',
    description: 'Choisissez le titre, la palette, et laissez l’IA structurer la présentation en slides compréhensibles.'
  },
  {
    id: '03',
    title: 'Téléchargez et partagez',
    description: 'Exports PPTX propres, avertissements sur la data et support prioritaire selon le plan choisi.'
  }
]
</script>
