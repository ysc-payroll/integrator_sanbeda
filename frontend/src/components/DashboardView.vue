<template>
  <div class="p-6 space-y-6">
    <h1 class="text-3xl font-bold text-gray-900">Dashboard</h1>

    <!-- Sync Controls -->
    <div class="grid grid-cols-2 gap-6">
      <!-- Pull Sync Card -->
      <div class="card">
        <h2 class="text-xl font-semibold mb-4 flex items-center gap-2">
          <svg class="w-6 h-6 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          Pull from San Beda
        </h2>
        <p class="text-gray-600 mb-4">
          Pull timesheet data from on-premise system
        </p>
        <div v-if="config" class="text-sm text-gray-500 mb-4">
          Last pull: {{ formatDateTime(config.last_pull_at) || 'Never' }}
        </div>
        <button
          @click="handlePullSync"
          :disabled="pullLoading"
          class="btn btn-primary w-full"
        >
          <span v-if="!pullLoading">Pull Data Now</span>
          <span v-else class="flex items-center justify-center gap-2">
            <svg class="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Pulling...
          </span>
        </button>
      </div>

      <!-- Push Sync Card -->
      <div class="card">
        <h2 class="text-xl font-semibold mb-4 flex items-center gap-2">
          <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
          </svg>
          Push to Cloud Payroll
        </h2>
        <p class="text-gray-600 mb-4">
          Sync timesheet data to cloud payroll system
        </p>
        <div v-if="config" class="text-sm text-gray-500 mb-4">
          Last push: {{ formatDateTime(config.last_push_at) || 'Never' }}
        </div>
        <button
          @click="handlePushSync"
          :disabled="pushLoading || stats.pending === 0"
          class="btn btn-success w-full"
        >
          <span v-if="!pushLoading">Push Data Now</span>
          <span v-else class="flex items-center justify-center gap-2">
            <svg class="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Pushing...
          </span>
        </button>
      </div>
    </div>

    <!-- Statistics -->
    <div class="grid grid-cols-4 gap-4">
      <div class="card">
        <div class="text-sm text-gray-600 mb-1">Total Records</div>
        <div class="text-3xl font-bold text-gray-900">{{ stats.total || 0 }}</div>
      </div>
      <div class="card">
        <div class="text-sm text-gray-600 mb-1">Synced</div>
        <div class="text-3xl font-bold text-green-600">{{ stats.synced || 0 }}</div>
      </div>
      <div class="card">
        <div class="text-sm text-gray-600 mb-1">Pending</div>
        <div class="text-3xl font-bold text-yellow-600">{{ stats.pending || 0 }}</div>
      </div>
      <div class="card">
        <div class="text-sm text-gray-600 mb-1">Errors</div>
        <div class="text-3xl font-bold text-red-600">{{ stats.errors || 0 }}</div>
      </div>
    </div>

    <!-- Recent Sync Activity -->
    <div class="card">
      <h2 class="text-xl font-semibold mb-4">Recent Sync Activity</h2>
      <div v-if="loadingLogs" class="text-center py-8 text-gray-500">
        Loading...
      </div>
      <div v-else-if="recentLogs.length === 0" class="text-center py-8 text-gray-500">
        No sync activity yet
      </div>
      <div v-else class="space-y-2">
        <div
          v-for="log in recentLogs"
          :key="log.id"
          class="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
        >
          <div class="flex items-center gap-3">
            <span
              :class="[
                'badge',
                log.sync_type === 'pull' ? 'badge-info' : 'badge-success'
              ]"
            >
              {{ log.sync_type.toUpperCase() }}
            </span>
            <span class="text-sm text-gray-700">
              {{ log.records_success || 0 }} records processed
            </span>
            <span
              v-if="log.status === 'error'"
              class="badge badge-error"
            >
              Error
            </span>
          </div>
          <div class="text-sm text-gray-500">
            {{ formatDateTime(log.started_at) }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import bridgeService from '../services/bridge'
import { useToast } from '../composables/useToast'

const { success, error } = useToast()

const stats = ref({
  total: 0,
  synced: 0,
  pending: 0,
  errors: 0
})

const config = ref(null)
const recentLogs = ref([])
const pullLoading = ref(false)
const pushLoading = ref(false)
const loadingLogs = ref(false)

const loadData = async () => {
  try {
    // Load stats
    const statsResult = await bridgeService.getTimesheetStats()
    stats.value = statsResult.data

    // Load config
    const configResult = await bridgeService.getApiConfig()
    config.value = configResult.data

    // Load recent logs
    loadingLogs.value = true
    const logsResult = await bridgeService.getSyncLogs()
    recentLogs.value = logsResult.data.slice(0, 10)
  } catch (err) {
    console.error('Error loading dashboard data:', err)
    error('Failed to load dashboard data')
  } finally {
    loadingLogs.value = false
  }
}

const handlePullSync = async () => {
  pullLoading.value = true
  try {
    const result = await bridgeService.startPullSync()
    success(result.message)
    await loadData()
  } catch (err) {
    error(`Pull sync failed: ${err.message}`)
  } finally {
    pullLoading.value = false
  }
}

const handlePushSync = async () => {
  pushLoading.value = true
  try {
    const result = await bridgeService.startPushSync()
    success(result.message)
    await loadData()
  } catch (err) {
    error(`Push sync failed: ${err.message}`)
  } finally {
    pushLoading.value = false
  }
}

const formatDateTime = (dateTime) => {
  if (!dateTime) return 'Never'
  const date = new Date(dateTime)
  return date.toLocaleString()
}

// Listen for sync completion events
onMounted(async () => {
  await bridgeService.whenReady()
  await loadData()

  // Listen for sync completion
  window.addEventListener('syncCompleted', async (event) => {
    await loadData()
  })
})
</script>
