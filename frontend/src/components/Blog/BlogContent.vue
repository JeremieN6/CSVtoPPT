<template>
    <!-- 
Install the "flowbite-typography" NPM package to apply styles and format the article content: 

URL: https://flowbite.com/docs/components/typography/ 
-->

    <main class="pt-8 pb-16 lg:pt-16 lg:pb-24 bg-white dark:bg-gray-900 antialiased">
        <div class="flex justify-between px-4 mx-auto max-w-screen-xl ">
            <article v-if="article"
                class="mx-auto w-full max-w-2xl format format-sm sm:format-base lg:format-lg format-blue dark:format-invert">
                <header class="mb-4 lg:mb-6 not-format">
                    <address class="flex items-center mb-6 not-italic">
                        <div class="inline-flex items-center mr-3 text-sm text-gray-900 dark:text-white">
                            <img class="mr-4 w-16 h-16 rounded-full object-cover" src="https://agence.jeremiecode.fr/assets/images/testimonials/img-4.jpg"
                                alt="aMANDINE C.">
                            <div>
                                <a href="#" rel="author" class="text-xl font-bold text-gray-900 dark:text-white">Amandine C.</a>
                                <p class="text-base text-gray-500 dark:text-gray-400">Auxiliaire petite enfance</p>
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
            <div v-else>
                <p>Article introuvable.</p>
            </div>
        </div>
    </main>

</template>

<script setup>
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'
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
