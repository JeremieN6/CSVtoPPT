<template>
    <section id="faq" class="bg-white dark:bg-gray-900">
        <div class="mx-auto max-w-screen-xl px-4 py-12 sm:py-20 lg:px-6">
            <div class="max-w-3xl">
                <p class="inline-flex items-center gap-2 rounded-full border border-blue-200 bg-blue-50 px-4 py-1 text-xs font-semibold uppercase tracking-[0.25em] text-blue-700 dark:border-blue-500/30 dark:bg-blue-900/20 dark:text-blue-200">FAQ</p>
                <h2 class="mt-3 text-4xl font-extrabold tracking-tight text-gray-900 dark:text-white">Questions fréquentes</h2>
                <p class="mt-4 text-base text-gray-600 dark:text-gray-400">Tout ce qu’il faut savoir sur la conversion de vos données en slides prêtes à présenter.</p>
            </div>
            <div class="mt-12 grid gap-10 border-t border-gray-200 pt-10 text-left md:grid-cols-2 md:gap-16 dark:border-gray-800">
                <article
                    v-for="faq in visibleFaqItems"
                    :key="faq.question"
                    class="space-y-4"
                >
                    <h3 class="flex items-start gap-3 text-lg font-semibold text-gray-900 dark:text-white">
                        <span class="text-2xl" aria-hidden="true">{{ faq.icon }}</span>
                        <span>{{ faq.question }}</span>
                    </h3>
                    <p class="text-gray-600 dark:text-gray-400">{{ faq.answer }}</p>
                </article>
            </div>
        </div>
    </section>
</template>

<script setup>
import { computed } from 'vue'

const faqItems = [
    {
        icon: '💰',
        question: 'Combien ça coûte ?',
        answer:
            'Nous proposons plusieurs formules adaptées à vos besoins. Un essai gratuit est disponible pour tester l’outil sans engagement. Les plans payants démarrent à partir de 14,90 €/mois et incluent des conversions illimitées, le support prioritaire et l’accès aux templates personnalisés.'
    },
    {
        icon: '📊',
        question: 'Quels types de fichiers sont acceptés ?',
        answer:
                'L’outil accepte les formats CSV et Excel (.xlsx, .xls). Vos fichiers peuvent contenir des tableaux simples ou complexes, des données numériques, du texte, des dates, etc. Nous gérons également les gros fichiers (jusqu’à 50 000 lignes).'
    },
    {
        icon: '⏱️',
        question: 'Combien de temps prend réellement la conversion ?',
        answer:
            'La plupart des conversions se font entre 10 et 30 secondes, selon la taille du fichier. Un fichier de quelques centaines de lignes ? Moins de 20 secondes. Un fichier plus volumineux ? Rarement plus d’une minute. Dans tous les cas, c’est bien plus rapide qu’une création manuelle.'
    },
    {
        icon: '🎨',
        question: 'Puis-je personnaliser le design des slides ?',
        answer:
            'Oui. Vous pouvez uploader votre propre template PowerPoint (charte graphique, couleurs corporate, logo) et l’outil l’utilisera automatiquement pour générer vos présentations. Idéal pour conserver une identité visuelle homogène.'
    },
    {
        icon: '🔒',
        question: 'Mes données sont-elles sécurisées ?',
        answer:
            'Absolument. Vos fichiers sont traités de manière sécurisée et supprimés automatiquement de nos serveurs après la génération du PowerPoint. Nous ne conservons aucune donnée, et vos informations ne sont jamais partagées avec des tiers. Conformité RGPD garantie.'
    },
    {
        icon: '📈',
        question: 'L’outil génère-t-il aussi des graphiques ?',
        answer:
            'Oui. L’outil détecte automatiquement les données numériques et peut générer des graphiques adaptés (histogrammes, courbes, diagrammes circulaires, etc.). Vous pouvez également choisir de produire uniquement des tableaux si vous préférez.'
    },
    {
        icon: '🔄',
        question: 'Est-ce que je peux convertir plusieurs fichiers en une seule présentation ?',
        answer:
            'Pour l’instant, l’outil convertit un fichier à la fois. Cependant, si votre fichier Excel contient plusieurs onglets, chaque onglet peut devenir une slide distincte. Une fonctionnalité de fusion multi-fichiers est prévue très bientôt.'
    },
    {
        icon: '💼',
        question: 'C’est adapté pour des présentations clients ou en comité de direction ?',
        answer:
            'Tout à fait. Les slides générées sont professionnelles, cohérentes et présentables immédiatement. Consultantes, analystes et managers utilisent déjà l’outil pour préparer leurs présentations stratégiques, leurs reportings ou leurs pitchs clients.'
    },
    {
        icon: '🖥️',
        question: 'Est-ce que je dois installer un logiciel ?',
        answer:
            'Non, aucune installation n’est nécessaire. L’outil fonctionne 100 % en ligne depuis votre navigateur (Chrome, Firefox, Safari, Edge, etc.). Vous pouvez l’utiliser depuis n’importe quel ordinateur, où que vous soyez.'
    },
    {
        icon: '📱',
        question: 'Ça marche sur mobile ?',
        answer:
            'L’outil est optimisé pour desktop, mais vous pouvez uploader un fichier depuis mobile. Pour visualiser et télécharger confortablement les slides, nous recommandons tout de même un ordinateur.'
    },
    {
        icon: '🔁',
        question: 'Que se passe-t-il si le résultat ne me convient pas ?',
        answer:
            'Vous pouvez régénérer votre présentation autant de fois que nécessaire en modifiant vos données ou en ajustant les paramètres. Si un problème persiste, notre support est là pour vous aider à obtenir exactement le rendu souhaité.'
    },
    {
        icon: '🤝',
        question: 'Y a-t-il une API pour intégrer l’outil dans nos systèmes ?',
        answer:
            'Oui, une API est disponible pour les entreprises qui souhaitent automatiser la génération de PowerPoint depuis leur CRM, ERP ou tout autre outil interne. Contactez-nous pour discuter des modalités techniques et tarifaires.'
    },
    {
        icon: '🎓',
        question: 'Est-ce adapté pour les étudiants ou enseignants ?',
        answer:
            'Absolument. L’outil est idéal pour transformer rapidement des données de recherche, des résultats d’enquêtes ou des statistiques en présentations claires pour des soutenances ou des cours. Des tarifs spéciaux sont proposés pour l’éducation.'
    },
    {
        icon: '❓',
        question: 'Une autre question ?',
        answer:
            'Notre équipe est là pour vous aider. Contactez-nous via le chat intégré ou par email à support@csvtoppt.com et nous vous répondrons rapidement.'
    }
]

const visibleFaqItems = computed(() => faqItems.slice(0, 8))
</script>