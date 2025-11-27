<template>
  <div class="p-6 space-y-6">
    <!-- Clear Timesheets Modal -->
    <div v-if="showClearModal" class="fixed inset-0 z-50 flex items-center justify-center">
      <div class="absolute inset-0 bg-black bg-opacity-50" @click="closeClearModal"></div>
      <div class="relative bg-white rounded-lg shadow-xl w-full max-w-md mx-4">
        <!-- Modal Header -->
        <div class="flex items-center justify-between p-4 border-b">
          <h3 class="text-lg font-semibold text-red-600">Clear Timesheet Records</h3>
          <button @click="closeClearModal" class="text-gray-500 hover:text-gray-700">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Modal Body -->
        <div class="p-4 space-y-4">
          <div class="bg-red-50 border border-red-200 rounded-lg p-3">
            <p class="text-sm text-red-700">
              <strong>Warning:</strong> This will permanently delete timesheet records within the selected date range. This action cannot be undone.
            </p>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">From</label>
            <input
              v-model="clearDateFrom"
              type="date"
              class="input w-full"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">To</label>
            <input
              v-model="clearDateTo"
              type="date"
              class="input w-full"
            />
          </div>
        </div>

        <!-- Modal Footer -->
        <div class="flex justify-end gap-2 p-4 border-t">
          <button @click="closeClearModal" class="btn btn-secondary">Cancel</button>
          <button @click="executeClear" :disabled="clearing" class="btn bg-red-600 text-white hover:bg-red-700">
            <span v-if="!clearing">Delete Records</span>
            <span v-else>Deleting...</span>
          </button>
        </div>
      </div>
    </div>

    <div class="flex items-center justify-between">
      <h1 class="text-3xl font-bold text-gray-900">Timesheet Records</h1>
      <div class="flex gap-2">
        <button @click="openClearModal" class="btn bg-red-100 text-red-700 hover:bg-red-200">
          <svg class="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
          Clear Records
        </button>
        <button @click="loadData" class="btn btn-secondary">
          <svg class="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Refresh
        </button>
      </div>
    </div>

    <!-- Filters -->
    <div class="card">
      <div class="flex gap-4 items-center">
        <div class="flex-1">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search by employee name or ID..."
            class="input"
          />
        </div>
        <select v-model="filterStatus" class="input w-48">
          <option value="all">All Records</option>
          <option value="synced">Synced</option>
          <option value="pending">Pending</option>
          <option value="error">Errors</option>
        </select>
      </div>
    </div>

    <!-- Table -->
    <div class="card overflow-hidden">
      <div v-if="loading" class="text-center py-8 text-gray-500">
        Loading timesheets...
      </div>
      <div v-else-if="filteredTimesheets.length === 0" class="text-center py-8 text-gray-500">
        No timesheet records found
      </div>
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Date & Time
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Employee
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Type
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Sync ID
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="entry in paginatedTimesheets" :key="entry.id">
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {{ entry.date }} {{ entry.time }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">{{ entry.employee_name }}</div>
                <div class="text-sm text-gray-500">{{ entry.employee_code || 'N/A' }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span
                  :class="[
                    'badge',
                    entry.log_type === 'in' ? 'badge-success' : 'badge-warning'
                  ]"
                >
                  {{ entry.log_type.toUpperCase() }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span
                  v-if="entry.backend_timesheet_id"
                  class="badge badge-success"
                  :title="`Backend ID: ${entry.backend_timesheet_id}`"
                >
                  Synced
                </span>
                <span
                  v-else-if="entry.sync_error_message"
                  class="badge badge-error"
                  :title="entry.sync_error_message"
                >
                  Error
                </span>
                <span v-else class="badge badge-warning">
                  Pending
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 font-mono">
                {{ entry.sync_id }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm">
                <button
                  v-if="entry.sync_error_message"
                  @click="retrySync(entry.id)"
                  class="text-primary-600 hover:text-primary-900"
                  title="Retry sync"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="bg-gray-50 px-6 py-4 flex items-center justify-between border-t">
        <div class="text-sm text-gray-700">
          Showing {{ (currentPage - 1) * pageSize + 1 }} to {{ Math.min(currentPage * pageSize, filteredTimesheets.length) }}
          of {{ filteredTimesheets.length }} results
        </div>
        <div class="flex gap-2">
          <button
            @click="currentPage--"
            :disabled="currentPage === 1"
            class="btn btn-secondary"
          >
            Previous
          </button>
          <button
            @click="currentPage++"
            :disabled="currentPage === totalPages"
            class="btn btn-secondary"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import bridgeService from '../services/bridge'
import { useToast } from '../composables/useToast'

const { success, error } = useToast()

const timesheets = ref([])
const loading = ref(false)
const searchQuery = ref('')
const filterStatus = ref('all')
const currentPage = ref(1)
const pageSize = 50

// Clear modal state
const showClearModal = ref(false)
const clearDateFrom = ref('')
const clearDateTo = ref('')
const clearing = ref(false)

// Helper to get date in YYYY-MM-DD format
const getDateString = (date) => {
  return date.toISOString().split('T')[0]
}

const openClearModal = () => {
  // Default: last 7 days
  const today = new Date()
  const weekAgo = new Date(today)
  weekAgo.setDate(weekAgo.getDate() - 7)

  clearDateFrom.value = getDateString(weekAgo)
  clearDateTo.value = getDateString(today)
  showClearModal.value = true
}

const closeClearModal = () => {
  showClearModal.value = false
}

const executeClear = async () => {
  clearing.value = true
  try {
    const result = await bridgeService.clearTimesheets(clearDateFrom.value, clearDateTo.value)
    success(result.message)
    showClearModal.value = false
    await loadData()
  } catch (err) {
    error(`Failed to clear records: ${err.message}`)
  } finally {
    clearing.value = false
  }
}

const filteredTimesheets = computed(() => {
  let filtered = timesheets.value

  // Filter by status
  if (filterStatus.value === 'synced') {
    filtered = filtered.filter(t => t.backend_timesheet_id !== null)
  } else if (filterStatus.value === 'pending') {
    filtered = filtered.filter(t => t.backend_timesheet_id === null && !t.sync_error_message)
  } else if (filterStatus.value === 'error') {
    filtered = filtered.filter(t => t.sync_error_message !== null)
  }

  // Filter by search query
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(t =>
      t.employee_name?.toLowerCase().includes(query) ||
      t.employee_code?.toLowerCase().includes(query) ||
      t.sync_id?.toLowerCase().includes(query)
    )
  }

  return filtered
})

const totalPages = computed(() => {
  return Math.ceil(filteredTimesheets.value.length / pageSize)
})

const paginatedTimesheets = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  const end = start + pageSize
  return filteredTimesheets.value.slice(start, end)
})

const loadData = async () => {
  loading.value = true
  try {
    const result = await bridgeService.getAllTimesheets(5000, 0)
    timesheets.value = result.data
  } catch (err) {
    console.error('Error loading timesheets:', err)
    error('Failed to load timesheets')
  } finally {
    loading.value = false
  }
}

const retrySync = async (timesheetId) => {
  try {
    await bridgeService.retryFailedTimesheet(timesheetId)
    success('Timesheet marked for retry. It will sync on next push.')
    await loadData()
  } catch (err) {
    error('Failed to retry timesheet sync')
  }
}

onMounted(async () => {
  await bridgeService.whenReady()
  await loadData()

  // Listen for sync completion to refresh data
  window.addEventListener('syncCompleted', async () => {
    await loadData()
  })
})
</script>
