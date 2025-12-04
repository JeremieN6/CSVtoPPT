<template>
    <section id="pricing" class="bg-white dark:bg-gray-900">
        <div class="mx-auto max-w-screen-xl px-4 py-16 lg:px-6 lg:py-24">
            <div class="mx-auto max-w-3xl text-center">
                <p class="inline-flex items-center gap-2 rounded-full border border-blue-200 bg-blue-50 px-4 py-1 text-xs font-semibold uppercase tracking-[0.3em] text-blue-700 dark:border-blue-500/30 dark:bg-blue-900/20 dark:text-blue-200">
                    Tarifs
                </p>
                <h2 class="mt-4 text-4xl font-extrabold tracking-tight text-gray-900 dark:text-white">Deux plans, un même objectif&nbsp;: produire des slides impeccables en un clic</h2>
                <p class="mt-3 text-base text-gray-600 dark:text-gray-400">Choisissez la formule qui correspond à votre rythme de production. Passez au Pro quand vous avez besoin d’automatiser vos reportings récurrents et d’activer les capacités avancées.</p>
            </div>

            <div class="mt-12 grid gap-8 lg:grid-cols-2">
                <!-- Plan Starter -->
                <article class="flex flex-col rounded-3xl border border-gray-200 bg-white p-8 shadow-lg transition hover:-translate-y-1 hover:border-blue-200 dark:border-gray-800 dark:bg-gray-900">
                    <div class="flex flex-col items-start justify-between">
                        <div>
                            <p class="text-sm font-semibold uppercase tracking-wide text-blue-600 dark:text-blue-300">Plan Starter</p>
                            <h3 class="mt-1 text-3xl font-bold text-gray-900 dark:text-white">Starter</h3>
                        </div>
                        <p class="text-right text-sm text-gray-500 dark:text-gray-400">Idéal pour tester ou produire des slides ponctuelles.</p>
                    </div>
                    <div class="mt-8 flex items-baseline gap-2 text-gray-900 dark:text-white">
                        <span class="text-4xl font-extrabold">Gratuit</span>
                        <span class="text-sm text-gray-500 dark:text-gray-400">/ mois</span>
                    </div>
                                <ul class="mt-8 space-y-4 text-sm text-gray-700 dark:text-gray-300">
                                                <li class="flex items-start gap-3">
                                                    <svg class="mt-0.5 h-5 w-5 flex-shrink-0 text-green-500" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                                                        <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                                                    </svg>
                                        <span>3 conversions / mois</span>
                                    </li>
                                    <li class="flex items-start gap-3">
                                                    <svg class="mt-0.5 h-5 w-5 flex-shrink-0 text-green-500" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                                                        <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                                                    </svg>
                                        <span>3 slides maximum par export</span>
                                    </li>
                                    <li class="flex items-start gap-3">
                                                    <svg class="mt-0.5 h-5 w-5 flex-shrink-0 text-green-500" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                                                        <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                                                    </svg>
                                        <span>1 template unique</span>
                                    </li>
                                    <li class="flex items-start gap-3">
                                                    <svg class="mt-0.5 h-5 w-5 flex-shrink-0 text-green-500" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                                                        <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                                                    </svg>
                                        <span>Template basique</span>
                                    </li>
                                    <li class="flex items-start gap-3">
                                                    <svg class="mt-0.5 h-5 w-5 flex-shrink-0 text-green-500" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                                                        <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                                                    </svg>
                                        <span>Mise en forme automatique basique</span>
                                    </li>
                                    <li class="flex items-start gap-3">
                                                    <svg class="mt-0.5 h-5 w-5 flex-shrink-0 text-red-500" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true">
                                                        <path stroke-linecap="round" stroke-linejoin="round" d="M6 6l8 8M6 14L14 6" />
                                                    </svg>
                                        <span>Pas de modification dans les slides</span>
                                    </li>
                                    <li class="flex items-start gap-3">
                                                    <svg class="mt-0.5 h-5 w-5 flex-shrink-0 text-red-500" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true">
                                                        <path stroke-linecap="round" stroke-linejoin="round" d="M6 6l8 8M6 14L14 6" />
                                                    </svg>
                                        <span>Watermark sur chaque page</span>
                                    </li>
                                </ul>
                    <button class="mt-8 w-full rounded-xl border border-gray-300 px-5 py-3 text-sm font-semibold text-gray-900 transition hover:border-blue-500 hover:text-blue-600 dark:border-gray-700 dark:text-white dark:hover:border-blue-500">Commencer gratuitement</button>
                </article>

                <!-- Plan Pro -->
                <article class="relative flex flex-col rounded-3xl border border-blue-300 bg-gradient-to-b from-blue-50 to-white p-8 shadow-2xl transition hover:-translate-y-1 dark:border-blue-700/50 dark:from-blue-900/40 dark:to-gray-900">
                    <span class="absolute right-6 top-6 inline-flex items-center rounded-full bg-blue-600 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-white">Le plus populaire</span>
                    <div class="flex flex-col items-start justify-between">
                        <div>
                            <p class="text-sm font-semibold uppercase tracking-wide text-blue-700 dark:text-blue-200">Plan Pro</p>
                            <h3 class="mt-1 text-3xl font-bold text-gray-900 dark:text-white">Pro</h3>
                        </div>
                        <p class="text-right text-sm text-gray-600 dark:text-gray-300">Pensé pour les équipes qui publient des rapports chaque semaine.</p>
                    </div>
                    <div class="mt-8 flex items-baseline gap-2 text-gray-900 dark:text-white">
                        <span class="text-4xl font-extrabold">14,90€</span>
                        <span class="text-sm text-gray-500 dark:text-gray-300">/ mois</span>
                    </div>
                                <ul class="mt-8 space-y-4 text-sm text-gray-800 dark:text-gray-200">
                                                <li class="flex items-start gap-3">
                                                    <svg class="mt-0.5 h-5 w-5 flex-shrink-0 text-green-500" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                                                        <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                                                    </svg>
                                        <span>Conversions illimitées</span>
                                    </li>
                                    <li class="flex items-start gap-3">
                                                    <svg class="mt-0.5 h-5 w-5 flex-shrink-0 text-green-500" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                                                        <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                                                    </svg>
                                        <span>Multi-slides automatique</span>
                                    </li>
                                    <li class="flex items-start gap-3">
                                                    <svg class="mt-0.5 h-5 w-5 flex-shrink-0 text-green-500" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                                                        <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                                                    </svg>
                                        <span>Analyse et mise en forme intelligente des données (IA)</span>
                                    </li>
                                    <li class="flex items-start gap-3">
                                                    <svg class="mt-0.5 h-5 w-5 flex-shrink-0 text-green-500" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                                                        <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                                                    </svg>
                                        <span>
                                            Import avancé (Sheets, URL, batch)
                                            <span class="ml-2 inline-flex items-center rounded-full bg-blue-100 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider text-blue-700 dark:bg-blue-900/50 dark:text-blue-200">Bientôt</span>
                                        </span>
                                    </li>
                                                                        <li class="flex items-start gap-3">
                                                    <svg class="mt-0.5 h-5 w-5 flex-shrink-0 text-green-500" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                                                        <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                                                    </svg>
                                        <span>
                                            Templates personnalisables
                                            <span class="ml-2 inline-flex items-center rounded-full bg-blue-100 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider text-blue-700 dark:bg-blue-900/50 dark:text-blue-200">Bientôt</span>
                                        </span>
                                    </li>
                                    <li class="flex items-start gap-3">
                                                    <svg class="mt-0.5 h-5 w-5 flex-shrink-0 text-green-500" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                                                        <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                                                    </svg>
                                        <span>Mode sécurisé</span>
                                    </li>
                                    <li class="flex items-start gap-3">
                                                    <svg class="mt-0.5 h-5 w-5 flex-shrink-0 text-green-500" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                                                        <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                                                    </svg>
                                        <span>Priorité de traitement</span>
                                    </li>
                                    <li class="flex items-start gap-3">
                                                    <svg class="mt-0.5 h-5 w-5 flex-shrink-0 text-green-500" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                                                        <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                                                    </svg>
                                        <span>Support prioritaire</span>
                                    </li>
                                </ul>
                    <button class="mt-8 w-full rounded-xl bg-blue-700 px-5 py-3 text-sm font-semibold text-white shadow-lg transition hover:bg-blue-600">Passer au plan Pro</button>
                </article>
            </div>
        </div>
    </section>
</template>

<script setup>
</script>

<script setup>
// async function redirectToCheckout() {
//   try {
//     const response = await fetch('/.netlify/functions/create-checkout-session', {
//       method: 'POST'
//     })
//     const data = await response.json()
//     console.log('Stripe response:', data)

//     if (data.url) {
//       window.location.href = data.url
//     } else {
//       alert("Erreur : pas de redirection reçue")
//     }
//   } catch (err) {
//     console.error('Erreur de requête :', err)
//     alert("Erreur lors de la tentative de redirection.")
//   }
// }
</script>