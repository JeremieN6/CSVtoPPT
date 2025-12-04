<template>
  <section id="benefits" class="bg-white dark:bg-gray-900">
    <div class="mx-auto max-w-screen-xl px-4 py-16 sm:py-24 lg:px-8">
      <div class="mx-auto max-w-3xl text-center">
        <p class="inline-flex items-center gap-2 rounded-full border border-blue-200 bg-blue-50 px-4 py-1 text-xs font-semibold uppercase tracking-[0.3em] text-blue-700 dark:border-blue-500/30 dark:bg-blue-900/20 dark:text-blue-200">
          Bénéfices clés
        </p>
        <h2 class="mt-4 text-3xl font-extrabold leading-tight text-gray-900 dark:text-white sm:text-4xl">
          Pourquoi les équipes passent de leurs tableaux bruts à un PPT prêt à livrer en quelques secondes
        </h2>
        <p class="mt-4 text-base text-gray-600 dark:text-gray-400">
          Chaque point ci-dessous provient d'un besoin terrain : moins de copier-coller, des slides propres et un process enfin automatisé.
        </p>
      </div>

      <div class="mt-12 grid gap-8 md:grid-cols-2">
        <article
          v-for="benefit in benefits"
          :key="benefit.id"
          class="flex h-full flex-col rounded-2xl border border-gray-200 bg-white/80 p-8 shadow-sm backdrop-blur dark:border-gray-800 dark:bg-gray-800/60"
        >
          <div class="flex items-center gap-3 text-blue-600 dark:text-blue-300">
            <span class="text-2xl">{{ benefit.emoji }}</span>
            <p class="text-sm font-semibold uppercase tracking-wide">{{ benefit.badge }}</p>
          </div>
          <h3 class="mt-4 text-2xl font-semibold text-gray-900 dark:text-white">
            {{ benefit.title }}
          </h3>
          <p class="mt-3 text-gray-600 dark:text-gray-300">
            {{ benefit.description }}
          </p>
          <p v-if="benefit.detail" class="mt-3 text-sm font-medium text-gray-500 dark:text-gray-400">
            {{ benefit.detail }}
          </p>
          <ol v-if="benefit.steps" class="mt-5 space-y-3 text-gray-600 dark:text-gray-300">
            <li v-for="(step, index) in benefit.steps" :key="step" class="flex items-start gap-3">
              <span class="mt-0.5 inline-flex h-6 w-6 items-center justify-center rounded-full bg-blue-600 text-xs font-bold text-white">
                {{ index + 1 }}
              </span>
              <span>{{ step }}</span>
            </li>
          </ol>
        </article>
      </div>
    </div>
  </section>
</template>

<script setup>
const benefits = [
  {
    id: 1,
    emoji: '⚡',
    badge: 'Gain de temps massif',
    title: 'De 2 heures à 30 secondes',
    description:
      'Fini les copier-coller interminables, les ajustements de colonnes et la mise en forme à répétition. Le convertisseur transforme vos CSV ou Excel en présentation complète en quelques secondes.',
    detail:
      'Concrètement : jusqu’à 10 heures récupérées par mois pour vous concentrer sur l’analyse, la stratégie et la prise de décision — pas sur la mise en page.',
  },
  {
    id: 2,
    emoji: '🎨',
    badge: 'Qualité professionnelle',
    title: 'Slides propres, cohérentes, prêtes à presenter',
    description:
      'Titres clairs, tableaux lisibles, mise en page harmonisée : l’outil génère automatiquement des slides prêtes pour vos réunions ou vos clients.',
    detail:
      'Le résultat : une image professionnelle et soignée, même si vous partez de données brutes. Aucune compétence en design n’est requise.',
  },
  {
    id: 3,
    emoji: '🔄',
    badge: 'Automatisation des reporting',
    title: 'Des livrables constants et fiables',
    description:
      'Pour les rapports hebdos, dashboards mensuels ou présentations clients répétitives, le convertisseur supprime les tâches manuelles récurrentes.',
    detail:
      'L’avantage : un flux de travail automatisé qui produit la même qualité de slides à chaque export.',
  },
  {
    id: 4,
    emoji: '🚀',
    badge: 'Simplicité radicale',
    title: 'Productivité maximale dès la première utilisation',
    description:
      'Pas de tutoriel de 20 minutes, pas de logiciel lourd. Trois étapes suffisent pour obtenir un PPT prêt à l’emploi.',
    detail: 'En clair : aucune friction, aucune perte de temps — juste des résultats immédiats.',
    steps: [
      'Uploadez votre fichier CSV ou Excel',
      'L’outil génère automatiquement votre PowerPoint',
      'Téléchargez votre présentation prête à l’emploi',
    ],
  },
]
</script>
