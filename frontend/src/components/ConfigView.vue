<template>
  <div class="p-6 space-y-6">
    <h1 class="text-3xl font-bold text-gray-900">Configuration</h1>

    <!-- Push Configuration (YAHSHUA Payroll) - First -->
    <div class="card">
      <h2 class="text-xl font-semibold mb-4 flex items-center gap-2">
        <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
        </svg>
        Push Configuration (YAHSHUA Payroll)
      </h2>

      <div class="space-y-4">
        <!-- Logged In State -->
        <div v-if="pushLoggedIn">
          <div class="bg-green-50 border border-green-200 rounded-lg p-4">
            <div class="flex items-center gap-2 mb-2">
              <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span class="font-semibold text-green-800">Connected to YAHSHUA Payroll</span>
            </div>
            <p class="text-green-800">
              Logged in as <strong>{{ pushUserLogged }}</strong><br/>
              <span class="text-sm">({{ form.push_username }})</span>
            </p>
            <p class="text-sm text-green-600 mt-2">
              Last login: {{ pushTokenCreatedAt }}
            </p>
          </div>

          <div class="mt-4">
            <label class="label">Sync Interval (minutes)</label>
            <input
              v-model.number="form.push_interval_minutes"
              type="number"
              min="1"
              max="1440"
              class="input"
            />
            <p class="text-sm text-gray-500 mt-1">
              How often to automatically push data (0 to disable automatic sync)
            </p>
          </div>

          <button
            @click="logoutPush"
            :disabled="loggingOut"
            class="btn btn-secondary mt-4"
          >
            <span v-if="!loggingOut">Logout</span>
            <span v-else>Logging out...</span>
          </button>
        </div>

        <!-- Logged Out State -->
        <div v-else>
          <div class="bg-gray-50 border border-gray-200 rounded-lg p-4 mb-4">
            <p class="text-sm text-gray-600">
              <strong>YAHSHUA Payroll API</strong><br/>
              Login to connect and sync timesheet data.
            </p>
          </div>

          <div>
            <label class="label">Email / Username</label>
            <input
              v-model="form.push_username"
              type="email"
              placeholder="timekeeping@sanbeda.com"
              class="input"
            />
          </div>

          <div>
            <label class="label">Password</label>
            <input
              v-model="form.push_password"
              type="password"
              placeholder="Enter password"
              class="input"
            />
          </div>

          <button
            @click="loginPush"
            :disabled="!form.push_username || !form.push_password || loggingIn"
            class="btn btn-primary mt-4"
          >
            <span v-if="!loggingIn">Login</span>
            <span v-else>Logging in...</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Pull Configuration (San Beda On-Premise) - Second -->
    <div class="card">
      <h2 class="text-xl font-semibold mb-4 flex items-center gap-2">
        <svg class="w-6 h-6 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
        </svg>
        Pull Configuration (San Beda On-Premise)
      </h2>

      <div class="space-y-4">
        <div>
          <label class="label">Host / IP Address</label>
          <input
            v-model="form.pull_host"
            type="text"
            placeholder="192.168.9.125"
            class="input"
          />
          <p class="text-sm text-gray-500 mt-1">
            San Beda server IP address or hostname (e.g., 192.168.9.125)
          </p>
        </div>

        <div>
          <label class="label">Username</label>
          <input
            v-model="form.pull_username"
            type="text"
            placeholder="system"
            class="input"
          />
          <p class="text-sm text-gray-500 mt-1">
            San Beda system username
          </p>
        </div>

        <div>
          <label class="label">Password</label>
          <input
            v-model="form.pull_password"
            type="password"
            :placeholder="pullPasswordSet ? '••••••••' : 'Enter password'"
            class="input"
          />
          <p v-if="pullPasswordSet && !form.pull_password" class="text-sm text-green-600 mt-1">
            Password is configured. Leave blank to keep current password.
          </p>
          <p v-else class="text-sm text-gray-500 mt-1">
            San Beda system password
          </p>
        </div>

        <div>
          <label class="label">Sync Interval (minutes)</label>
          <input
            v-model.number="form.pull_interval_minutes"
            type="number"
            min="1"
            max="1440"
            class="input"
          />
          <p class="text-sm text-gray-500 mt-1">
            How often to automatically pull data (0 to disable automatic sync)
          </p>
        </div>

        <div class="flex gap-2">
          <button
            v-if="pullConnected"
            @click="testConnection('pull')"
            :disabled="!form.pull_host || testingPull"
            class="btn btn-secondary"
          >
            <span v-if="!testingPull">Test Connection</span>
            <span v-else>Testing...</span>
          </button>
          <button
            @click="reconnectPull"
            :disabled="!form.pull_host || reconnectingPull"
            class="btn btn-primary"
          >
            <span v-if="!reconnectingPull">{{ pullConnected ? 'Reconnect' : 'Connect' }}</span>
            <span v-else>{{ pullConnected ? 'Reconnecting...' : 'Connecting...' }}</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Save Button -->
    <div class="flex justify-end gap-4">
      <button @click="loadConfig" class="btn btn-secondary">
        Reset
      </button>
      <button
        @click="saveConfig"
        :disabled="saving"
        class="btn btn-primary"
      >
        <span v-if="!saving">Save Configuration</span>
        <span v-else>Saving...</span>
      </button>
    </div>

    <!-- System Logs Section -->
    <div class="card">
      <h2 class="text-xl font-semibold mb-4 flex items-center gap-2">
        <svg class="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        System Logs
      </h2>
      <p class="text-sm text-gray-500 mb-4">View application logs for debugging and troubleshooting.</p>
      <button @click="openLogModal" class="btn btn-secondary">
        View System Logs
      </button>
    </div>

    <!-- Log Modal -->
    <div v-if="showLogModal" class="fixed inset-0 z-50 flex items-center justify-center">
      <div class="absolute inset-0 bg-black bg-opacity-50" @click="closeLogModal"></div>
      <div class="relative bg-white rounded-lg shadow-xl w-full max-w-4xl mx-4 max-h-[80vh] flex flex-col">
        <!-- Modal Header -->
        <div class="flex items-center justify-between p-4 border-b">
          <h3 class="text-lg font-semibold">System Logs</h3>
          <button @click="closeLogModal" class="text-gray-500 hover:text-gray-700">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Modal Body -->
        <div class="p-4 flex-1 overflow-hidden flex flex-col">
          <!-- Log File Selector -->
          <div class="flex items-center gap-4 mb-4">
            <select v-model="selectedLogFile" @change="loadLogContent" class="input w-64">
              <option value="">Select a log file...</option>
              <option v-for="file in logFiles" :key="file.filename" :value="file.filename">
                {{ formatLogDate(file.date) }} ({{ formatFileSize(file.size) }})
              </option>
            </select>
            <button @click="loadLogContent" :disabled="!selectedLogFile || loadingLog" class="btn btn-secondary">
              <span v-if="!loadingLog">Refresh</span>
              <span v-else>Loading...</span>
            </button>
            <button @click="downloadLog" :disabled="!selectedLogFile || !logContent" class="btn btn-secondary">
              Download
            </button>
            <span v-if="logInfo" class="text-sm text-gray-500">
              Showing {{ logInfo.showing_lines }} of {{ logInfo.total_lines }} lines
            </span>
          </div>

          <!-- Log Content -->
          <div class="flex-1 overflow-auto bg-gray-900 rounded-lg p-4">
            <pre v-if="logContent" class="text-green-400 text-xs font-mono whitespace-pre-wrap">{{ logContent }}</pre>
            <p v-else class="text-gray-500 text-center py-8">Select a log file to view its contents</p>
          </div>
        </div>

        <!-- Modal Footer -->
        <div class="flex justify-end p-4 border-t">
          <button @click="closeLogModal" class="btn btn-secondary">Close</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import bridgeService from '../services/bridge'
import { useToast } from '../composables/useToast'

const { success, error, info } = useToast()

const form = ref({
  pull_host: '',
  pull_username: '',
  pull_password: '',
  pull_interval_minutes: 30,
  push_username: '',
  push_password: '',
  push_interval_minutes: 15
})

const saving = ref(false)
const testingPull = ref(false)
const testingPush = ref(false)

// YAHSHUA login state
const pushLoggedIn = ref(false)
const pushUserLogged = ref('')
const pushTokenCreatedAt = ref('')
const loggingIn = ref(false)
const loggingOut = ref(false)

// Pull config state
const pullPasswordSet = ref(false)
const pullConnected = ref(false)
const reconnectingPull = ref(false)

// System logs state
const showLogModal = ref(false)
const logFiles = ref([])
const selectedLogFile = ref('')
const logContent = ref('')
const logInfo = ref(null)
const loadingLog = ref(false)

const loadConfig = async () => {
  try {
    const result = await bridgeService.getApiConfig()
    if (result.data) {
      form.value = {
        pull_host: result.data.pull_host || '',
        pull_username: result.data.pull_username || '',
        pull_password: result.data.pull_password === '***' ? '' : result.data.pull_password || '',
        pull_interval_minutes: result.data.pull_interval_minutes || 30,
        push_username: result.data.push_username || '',
        push_password: '',  // Never prefill password
        push_interval_minutes: result.data.push_interval_minutes || 15
      }

      // Set YAHSHUA login state
      pushLoggedIn.value = result.data.push_token_exists || false
      pushUserLogged.value = result.data.push_user_logged || ''
      pushTokenCreatedAt.value = result.data.push_token_created_at || ''

      // Set pull password state
      pullPasswordSet.value = result.data.pull_password === '***'

      // Set pull connected state
      pullConnected.value = result.data.login_token_exists || false
    }
  } catch (err) {
    console.error('Error loading config:', err)
    error('Failed to load configuration')
  }
}

const saveConfig = async () => {
  saving.value = true
  try {
    await bridgeService.updateApiConfig(form.value)
    success('Configuration saved successfully')
  } catch (err) {
    console.error('Error saving config:', err)
    error('Failed to save configuration')
  } finally {
    saving.value = false
  }
}

const testConnection = async (type) => {
  if (type === 'pull') {
    testingPull.value = true
  } else {
    testingPush.value = true
  }

  try {
    // Save config first
    await bridgeService.updateApiConfig(form.value)

    // Test connection
    const result = await bridgeService.testConnection(type)
    if (result.success) {
      success(result.message)
    } else {
      error(result.message)
    }
  } catch (err) {
    error(`Connection test failed: ${err.message}`)
  } finally {
    if (type === 'pull') {
      testingPull.value = false
    } else {
      testingPush.value = false
    }
  }
}

const loginPush = async () => {
  loggingIn.value = true
  try {
    const result = await bridgeService.loginPush(form.value.push_username, form.value.push_password)
    if (result.success) {
      pushLoggedIn.value = true
      pushUserLogged.value = result.user_logged
      pushTokenCreatedAt.value = new Date().toLocaleString()
      form.value.push_password = ''  // Clear password from form
      success(result.message)
    } else {
      error(result.error || 'Login failed')
    }
  } catch (err) {
    error(`Login failed: ${err.message}`)
  } finally {
    loggingIn.value = false
  }
}

const logoutPush = async () => {
  loggingOut.value = true
  try {
    const result = await bridgeService.logoutPush()
    if (result.success) {
      pushLoggedIn.value = false
      pushUserLogged.value = ''
      pushTokenCreatedAt.value = ''
      success('Logged out successfully')
    }
  } catch (err) {
    error(`Logout failed: ${err.message}`)
  } finally {
    loggingOut.value = false
  }
}

const reconnectPull = async () => {
  const wasConnected = pullConnected.value
  reconnectingPull.value = true
  try {
    // Save config first to ensure credentials are updated
    await bridgeService.updateApiConfig(form.value)

    // Test connection (this will re-authenticate and get new token)
    const result = await bridgeService.testConnection('pull')
    if (result.success) {
      pullConnected.value = true
      success(wasConnected ? 'Reconnected to San Beda successfully' : 'Connected to San Beda successfully')
    } else {
      error(result.message || 'Connection failed')
    }
  } catch (err) {
    error(`Connection failed: ${err.message}`)
  } finally {
    reconnectingPull.value = false
  }
}

// System log functions
const openLogModal = async () => {
  showLogModal.value = true
  selectedLogFile.value = ''
  logContent.value = ''
  logInfo.value = null

  try {
    const result = await bridgeService.getSystemLogFiles()
    if (result.success) {
      logFiles.value = result.data
      // Auto-select first (most recent) file
      if (logFiles.value.length > 0) {
        selectedLogFile.value = logFiles.value[0].filename
        await loadLogContent()
      }
    }
  } catch (err) {
    console.error('Error loading log files:', err)
    error('Failed to load log files')
  }
}

const closeLogModal = () => {
  showLogModal.value = false
}

const loadLogContent = async () => {
  if (!selectedLogFile.value) return

  loadingLog.value = true
  try {
    const result = await bridgeService.getSystemLogContent(selectedLogFile.value)
    if (result.success) {
      logContent.value = result.data.content
      logInfo.value = result.data
    } else {
      error(result.error || 'Failed to load log content')
    }
  } catch (err) {
    console.error('Error loading log content:', err)
    error('Failed to load log content')
  } finally {
    loadingLog.value = false
  }
}

const formatLogDate = (dateStr) => {
  // Convert YYYYMMDD to readable format
  if (!dateStr || dateStr.length !== 8) return dateStr
  const year = dateStr.substring(0, 4)
  const month = dateStr.substring(4, 6)
  const day = dateStr.substring(6, 8)
  return `${year}-${month}-${day}`
}

const formatFileSize = (bytes) => {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

const downloadLog = () => {
  if (!logContent.value || !selectedLogFile.value) return

  const blob = new Blob([logContent.value], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = selectedLogFile.value
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

onMounted(async () => {
  await bridgeService.whenReady()
  await loadConfig()
})
</script>
