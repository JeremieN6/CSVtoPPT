<template>
  <div class="space-y-3">
    <label
      for="file-upload"
      class="flex w-full cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed border-gray-300 bg-gray-50 p-8 text-center transition hover:border-primary-500 hover:bg-white dark:border-gray-600 dark:bg-gray-800"
      :class="{
        'border-primary-500 bg-white shadow-lg dark:bg-gray-700': isDragging,
        'pointer-events-none opacity-60': disabled,
      }"
      @dragover.prevent="handleDragOver"
      @dragleave.prevent="handleDragLeave"
      @drop.prevent="handleDrop"
    >
      <div class="flex max-w-sm flex-col items-center gap-4">
        <span class="inline-flex h-14 w-14 items-center justify-center rounded-full bg-primary-50 text-primary-600 dark:bg-gray-700 dark:text-primary-300">
          <svg class="h-8 w-8" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
              d="M12 16V8m0 0-3 3m3-3 3 3M6 20h12a2 2 0 0 0 2-2V9.414a2 2 0 0 0-.586-1.414l-5.414-5.414A2 2 0 0 0 12.586 2H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2Z" />
          </svg>
        </span>
        <div class="space-y-1">
          <p class="text-lg font-semibold text-gray-900 dark:text-white">Glissez votre fichier ici</p>
          <p class="text-sm text-gray-500 dark:text-gray-300">
            <span class="font-semibold">Cliquez pour sélectionner</span> ou faites glisser votre fichier.
          </p>
          <p class="text-xs text-gray-500 dark:text-gray-400">Formats acceptés : CSV ou XLSX (max 10&nbsp;Mo).</p>
        </div>
        <button
          type="button"
          class="rounded-lg border border-gray-300 bg-white px-5 py-2 text-sm font-medium text-gray-700 transition hover:bg-gray-100 hover:text-gray-900 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100"
          @click.stop.prevent="openFileDialog"
          :disabled="disabled"
        >
          Parcourir vos fichiers
        </button>
        <input
          ref="fileInput"
          id="file-upload"
          type="file"
          class="hidden"
          accept=".csv,.xlsx"
          :disabled="disabled"
          @change="handleFileChange"
        />
      </div>

      <div v-if="props.selectedFileName" class="mt-4 flex items-center gap-2 text-sm text-primary-600 dark:text-primary-300">
        <svg class="h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M5 12h14m-7-7v14" />
        </svg>
        <span class="truncate">{{ props.selectedFileName }}</span>
      </div>
    </label>

    <div v-if="localError" class="flex items-center gap-2 rounded-lg border border-red-200 bg-red-50 px-4 py-2 text-sm text-red-700 dark:border-red-900/50 dark:bg-red-900/20 dark:text-red-200">
      <svg class="h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
          d="M12 9v4m0 4h.01m-7.938-1a9 9 0 1115.856 0 9 9 0 01-15.856 0z" />
      </svg>
      <span>{{ localError }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  disabled: {
    type: Boolean,
    default: false,
  },
  selectedFileName: {
    type: String,
    default: '',
  },
})

const emit = defineEmits(['file-selected'])

const fileInput = ref(null)
const isDragging = ref(false)
const localError = ref('')

const allowedExtensions = ['csv', 'xlsx']

const validateFile = (file) => {
  if (!file) return false
  const extension = file.name.split('.').pop().toLowerCase()
  return allowedExtensions.includes(extension)
}

const handleFile = (fileList) => {
  if (!fileList?.length) return
  const file = fileList[0]

  if (!validateFile(file)) {
    localError.value = 'Format non supporté. Choisissez un CSV ou un XLSX.'
    return
  }

  localError.value = ''
  emit('file-selected', file)
}

const handleDragOver = () => {
  if (props.disabled) return
  isDragging.value = true
}

const handleDragLeave = () => {
  isDragging.value = false
}

const handleDrop = (event) => {
  if (props.disabled) return
  isDragging.value = false
  handleFile(event.dataTransfer?.files)
}

const handleFileChange = (event) => {
  handleFile(event.target.files)
  event.target.value = ''
}

const openFileDialog = () => {
  if (props.disabled) return
  fileInput.value?.click()
}
</script>
