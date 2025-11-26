<template>
  <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center">
    <!-- Backdrop -->
    <div class="absolute inset-0 bg-black bg-opacity-50"></div>

    <!-- Modal -->
    <div class="relative bg-white rounded-lg shadow-xl p-6 w-full max-w-md mx-4">
      <h2 class="text-xl font-semibold mb-4 flex items-center gap-2">
        <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
        </svg>
        Syncing to YAHSHUA Payroll
      </h2>

      <!-- Progress Info -->
      <div class="mb-4">
        <div class="text-lg font-medium text-gray-700 mb-2">
          Processing batch {{ progress.batch_current }} / {{ progress.batch_total }}
        </div>

        <!-- Progress Bar -->
        <div class="w-full bg-gray-200 rounded-full h-4 mb-2">
          <div
            class="bg-green-500 h-4 rounded-full transition-all duration-300"
            :style="{ width: progressPercent + '%' }"
          ></div>
        </div>

        <div class="text-sm text-gray-500 text-right">
          {{ progressPercent }}%
        </div>
      </div>

      <!-- Stats -->
      <div class="flex items-center justify-center gap-6 text-sm">
        <div class="flex items-center gap-1">
          <svg class="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
          </svg>
          <span class="text-green-600 font-medium">{{ progress.success.toLocaleString() }} synced</span>
        </div>
        <div class="text-gray-300">|</div>
        <div class="flex items-center gap-1">
          <svg class="w-4 h-4 text-red-500" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
          </svg>
          <span class="text-red-600 font-medium">{{ progress.failed.toLocaleString() }} failed</span>
        </div>
      </div>

      <!-- Spinner -->
      <div class="flex justify-center mt-4">
        <svg class="animate-spin h-6 w-6 text-green-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  progress: {
    type: Object,
    default: () => ({
      batch_current: 0,
      batch_total: 0,
      batch_size: 0,
      success: 0,
      failed: 0
    })
  }
})

const progressPercent = computed(() => {
  if (props.progress.batch_total === 0) return 0
  return Math.round((props.progress.batch_current / props.progress.batch_total) * 100)
})
</script>
