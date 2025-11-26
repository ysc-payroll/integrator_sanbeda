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

onMounted(async () => {
  await bridgeService.whenReady()
  await loadConfig()
})
</script>
