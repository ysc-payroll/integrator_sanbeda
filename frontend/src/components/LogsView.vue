<template>
  <div class="p-6 space-y-6">
    <div class="flex items-center justify-between">
      <h1 class="text-3xl font-bold text-gray-900">Sync Logs</h1>
      <button @click="loadLogs" class="btn btn-secondary">
        <svg class="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
        Refresh
      </button>
    </div>

    <!-- Filters -->
    <div class="card">
      <div class="flex gap-4">
        <select v-model="filterType" class="input w-48">
          <option value="all">All Types</option>
          <option value="pull">Pull</option>
          <option value="push">Push</option>
        </select>
        <select v-model="filterStatus" class="input w-48">
          <option value="all">All Status</option>
          <option value="success">Success</option>
          <option value="error">Error</option>
          <option value="started">In Progress</option>
        </select>
      </div>
    </div>

    <!-- Logs Table -->
    <div class="card overflow-hidden">
      <div v-if="loading" class="text-center py-8 text-gray-500">
        Loading logs...
      </div>
      <div v-else-if="filteredLogs.length === 0" class="text-center py-8 text-gray-500">
        No sync logs found
      </div>
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Type
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Records
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Started At
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Duration
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Message
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="log in filteredLogs" :key="log.id">
              <td class="px-6 py-4 whitespace-nowrap">
                <span
                  :class="[
                    'badge',
                    log.sync_type === 'pull' ? 'badge-info' : 'badge-success'
                  ]"
                >
                  {{ log.sync_type.toUpperCase() }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span
                  :class="[
                    'badge',
                    log.status === 'success' ? 'badge-success' :
                    log.status === 'error' ? 'badge-error' :
                    'badge-warning'
                  ]"
                >
                  {{ log.status }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                <div class="flex flex-col">
                  <span class="text-green-600">✓ {{ log.records_success || 0 }} success</span>
                  <span v-if="log.records_failed > 0" class="text-red-600">✗ {{ log.records_failed }} failed</span>
                  <span class="text-gray-500">Total: {{ log.records_processed || 0 }}</span>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {{ formatDateTime(log.started_at) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {{ getDuration(log.started_at, log.completed_at) }}
              </td>
              <td class="px-6 py-4 text-sm text-gray-900">
                <div v-if="log.error_message" class="text-red-600">
                  {{ log.error_message }}
                </div>
                <div v-else-if="log.status === 'success'" class="text-green-600">
                  Completed successfully
                </div>
                <div v-else-if="log.status === 'started'" class="text-yellow-600">
                  In progress...
                </div>
                <div v-else class="text-gray-500">
                  -
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import bridgeService from '../services/bridge'
import { useToast } from '../composables/useToast'

const { error } = useToast()

const logs = ref([])
const loading = ref(false)
const filterType = ref('all')
const filterStatus = ref('all')

const filteredLogs = computed(() => {
  let filtered = logs.value

  if (filterType.value !== 'all') {
    filtered = filtered.filter(log => log.sync_type === filterType.value)
  }

  if (filterStatus.value !== 'all') {
    filtered = filtered.filter(log => log.status === filterStatus.value)
  }

  return filtered
})

const loadLogs = async () => {
  loading.value = true
  try {
    const result = await bridgeService.getSyncLogs()
    logs.value = result.data
  } catch (err) {
    console.error('Error loading logs:', err)
    error('Failed to load sync logs')
  } finally {
    loading.value = false
  }
}

const formatDateTime = (dateTime) => {
  if (!dateTime) return '-'
  const date = new Date(dateTime)
  return date.toLocaleString()
}

const getDuration = (startTime, endTime) => {
  if (!startTime || !endTime) return '-'

  const start = new Date(startTime)
  const end = new Date(endTime)
  const duration = end - start

  if (duration < 1000) {
    return `${duration}ms`
  } else if (duration < 60000) {
    return `${(duration / 1000).toFixed(1)}s`
  } else {
    const minutes = Math.floor(duration / 60000)
    const seconds = Math.floor((duration % 60000) / 1000)
    return `${minutes}m ${seconds}s`
  }
}

onMounted(async () => {
  await bridgeService.whenReady()
  await loadLogs()

  // Listen for sync completion to refresh logs
  window.addEventListener('syncCompleted', async () => {
    await loadLogs()
  })
})
</script>
