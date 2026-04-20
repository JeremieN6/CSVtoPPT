<template>
    <!-- 
Install the "flowbite-typography" NPM package to apply styles and format the article content: 

URL: https://flowbite.com/docs/components/typography/ 
-->

    <main class="pt-8 pb-16 lg:pt-16 lg:pb-24 bg-white dark:bg-gray-900 antialiased">
        <div class="px-4 mx-auto max-w-screen-xl">
            <div v-if="article" class="mx-auto w-full max-w-2xl">
                <nav class="mb-6" aria-label="Fil d'ariane"><ol class="inline-flex flex-wrap items-center text-sm text-gray-600 gap-1 md:gap-2 dark:text-gray-300"><li class="inline-flex items-center"><RouterLink to="/" class="inline-flex items-center font-medium text-gray-700 transition hover:text-blue-600 dark:text-gray-300 dark:hover:text-blue-400"><svg class="mr-2 h-4 w-4" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true"><path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z"></path></svg> Accueil </RouterLink></li><li class="flex items-center"><svg class="h-5 w-5 text-gray-400" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true"><path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd"></path></svg><RouterLink to="/blog" class="ml-1 font-medium text-gray-700 transition hover:text-blue-600 dark:text-gray-300 dark:hover:text-blue-400">Blog</RouterLink></li><li class="flex items-center" aria-current="page"><svg class="h-5 w-5 text-gray-400" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true"><path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd"></path></svg><span class="ml-1 font-medium text-gray-500 dark:text-gray-400 line-clamp-1">{{ article.title }}</span></li></ol></nav>
            <article
                class="w-full format format-sm sm:format-base lg:format-lg format-blue dark:format-invert">
                <header class="mb-4 lg:mb-6 not-format">
                    <address class="flex items-center mb-6 not-italic">
                        <div class="inline-flex items-center mr-3 text-sm text-gray-900 dark:text-white">
                            <img class="mr-4 w-16 h-16 rounded-full object-cover" src="../../assets/images/moi.webp"
                                alt="Jérémie N.">
                            <div>
                                <a href="#" rel="author" class="text-xl font-bold text-gray-900 dark:text-white">Jérémie N.</a>
                                <p class="text-base text-gray-500 dark:text-gray-400">Développeur, & CEO de CSVtoPPT™ & SnapCode™ Agency</p>
                                <p class="text-base text-gray-500 dark:text-gray-400"><time pubdate
                                        datetime="2025-27-05" title="February 8th, 2022">{{ article.date }}</time></p>
                            </div>
                        </div>
                    </address>
                    <h1 v-if="article"
                        class="mb-4 text-3xl font-extrabold leading-tight text-gray-900 lg:mb-6 lg:text-4xl dark:text-white">
                        {{ article.title }}</h1>
                </header>
                <p class="lead mb-6 text-lg text-gray-700 dark:text-gray-300">{{ article.intro }}.</p>

                <section v-for="(section, index) in article.sections" :key="index">
                    <h2 class="mt-12 mb-6 text-2xl font-semibold text-gray-900 dark:text-white">{{ section.subtitle }}
                    </h2>
                    <p class="mb-6 text-gray-700 dark:text-gray-300">{{ section.content }}</p>
                </section>
            </article>
            </div>
            <div v-else class="mx-auto w-full max-w-2xl">
                <p>Article introuvable.</p>
            </div>
        </div>
    </main>

</template>

<script setup>
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { RouterLink } from 'vue-router'
import articlesData from '../../assets/data/articles.json'

const route = useRoute()
const article = ref(null)

const loadArticle = (slug) => {
  if (!slug) return
  const found = articlesData.find(a => a.slug === slug)
  if (found) {
    article.value = found
  } else {
    article.value = null
    console.warn('Aucun article trouvé pour le slug:', slug)
  }
}

// Initialisation
loadArticle(route.params.slug)

// Mise à jour dynamique si la route change
watch(() => route.params.slug, (newSlug) => {
    loadArticle(newSlug)
})
</script>
