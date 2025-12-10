<template>
  <div class="bg-gray-100 dark:bg-gray-900 min-h-screen">
    <LP_Header />

    <div class="py-8 px-4 mx-auto max-w-screen-lg sm:py-16 lg:px-6" id="convertisseur">
      <div class="title">
        <h1
          class="mb-4 text-3xl font-extrabold text-center tracking-tight leading-none text-gray-900 md:text-4xl lg:text-5xl dark:text-white">
          Convertisseur de csv vers ppt
        </h1>
        <p
          class="mb-8 text-lg font-normal text-center text-gray-500 lg:text-xl sm:px-16 xl:px-28 dark:text-gray-400">
          Avec CSVtoPPT™, uploadez votre fichier CSV ou Excel, et laissez l'outil générer automatiquement une présentation professionnelle avec graphiques, insights IA et layouts adaptatifs.
        </p>
      </div>
    </div>
    <ReportGenerator />
    <LP_Testimonials />
    <LP_Footer />
  </div>
</template>

<script setup>
import LP_Header from '../components/Landing/LP_Header.vue'
import ReportGenerator from '../components/convertisseur/ReportGenerator.vue'
import LP_Testimonials from '../components/Landing/LP_Testimonials.vue'
import LP_Footer from '../components/Landing/LP_Footer.vue'
</script>
