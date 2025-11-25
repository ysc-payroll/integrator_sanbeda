<template>
  <div class="p-6 space-y-6">
    <h1 class="text-3xl font-bold text-gray-900">Configuration</h1>

    <!-- Pull Configuration -->
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
            placeholder="Enter password"
            class="input"
          />
          <p class="text-sm text-gray-500 mt-1">
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

        <button
          @click="testConnection('pull')"
          :disabled="!form.pull_host || testingPull"
          class="btn btn-secondary"
        >
          <span v-if="!testingPull">Test Connection</span>
          <span v-else>Testing...</span>
        </button>
      </div>
    </div>

    <!-- Push Configuration -->
    <div class="card">
      <h2 class="text-xl font-semibold mb-4 flex items-center gap-2">
        <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
        </svg>
        Push Configuration (Cloud Payroll)
      </h2>

      <div class="space-y-4">
        <div>
          <label class="label">API Endpoint URL</label>
          <input
            v-model="form.push_url"
            type="text"
            placeholder="https://api.theabbapayroll.com/timesheets"
            class="input"
          />
        </div>

        <div>
          <label class="label">Authentication Type</label>
          <select v-model="form.push_auth_type" class="input">
            <option value="">None</option>
            <option value="bearer">Bearer Token</option>
            <option value="api_key">API Key</option>
            <option value="basic">Basic Auth</option>
          </select>
        </div>

        <div v-if="form.push_auth_type">
          <label class="label">Credentials</label>
          <input
            v-model="form.push_credentials"
            type="password"
            :placeholder="getCredentialsPlaceholder(form.push_auth_type)"
            class="input"
          />
          <p class="text-sm text-gray-500 mt-1">
            {{ getCredentialsHint(form.push_auth_type) }}
          </p>
        </div>

        <div>
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
          @click="testConnection('push')"
          :disabled="!form.push_url || testingPush"
          class="btn btn-secondary"
        >
          <span v-if="!testingPush">Test Connection</span>
          <span v-else>Testing...</span>
        </button>
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
  push_url: '',
  push_auth_type: '',
  push_credentials: '',
  push_interval_minutes: 15
})

const saving = ref(false)
const testingPull = ref(false)
const testingPush = ref(false)

const loadConfig = async () => {
  try {
    const result = await bridgeService.getApiConfig()
    if (result.data) {
      form.value = {
        pull_host: result.data.pull_host || '',
        pull_username: result.data.pull_username || '',
        pull_password: result.data.pull_password === '***' ? '' : result.data.pull_password || '',
        pull_interval_minutes: result.data.pull_interval_minutes || 30,
        push_url: result.data.push_url || '',
        push_auth_type: result.data.push_auth_type || '',
        push_credentials: result.data.push_credentials === '***' ? '' : result.data.push_credentials || '',
        push_interval_minutes: result.data.push_interval_minutes || 15
      }
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

const getCredentialsPlaceholder = (authType) => {
  switch (authType) {
    case 'bearer':
      return 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
    case 'api_key':
      return 'your-api-key-here'
    case 'basic':
      return 'base64-encoded-username:password'
    default:
      return ''
  }
}

const getCredentialsHint = (authType) => {
  switch (authType) {
    case 'bearer':
      return 'Enter your Bearer token (JWT)'
    case 'api_key':
      return 'Enter your API key'
    case 'basic':
      return 'Enter base64-encoded username:password'
    default:
      return ''
  }
}

onMounted(async () => {
  await bridgeService.whenReady()
  await loadConfig()
})
</script>
