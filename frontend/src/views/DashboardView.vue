<template>
  <section class="panel">
    <SectionToolbar eyebrow="Dashboard" title="运营看板">
      <button type="button" class="ghost-button" @click="load">刷新</button>
    </SectionToolbar>

    <p v-if="error" class="error">{{ error }}</p>
    <div v-if="stats" class="stats-grid">
      <button type="button" class="stat-card" @click="$emit('navigate', 'workstations')">
        <span>总工位</span>
        <strong>{{ stats.total_workstations }}</strong>
      </button>
      <button type="button" class="stat-card" @click="$emit('navigate', 'workstations')">
        <span>可租工位</span>
        <strong>{{ stats.available_workstations }}</strong>
      </button>
      <button type="button" class="stat-card" @click="$emit('navigate', 'workstations')">
        <span>已租工位</span>
        <strong>{{ stats.leased_workstations }}</strong>
      </button>
      <button type="button" class="stat-card" @click="$emit('navigate', 'contracts')">
        <span>履行合同</span>
        <strong>{{ stats.active_contracts }}</strong>
      </button>
      <button type="button" class="stat-card warning" @click="$emit('navigate', 'payments')">
        <span>待收金额</span>
        <strong>{{ currency(stats.unpaid_amount) }}</strong>
      </button>
      <button type="button" class="stat-card danger" @click="$emit('navigate', 'reminders')">
        <span>逾期金额</span>
        <strong>{{ currency(stats.overdue_amount) }}</strong>
      </button>
      <button type="button" class="stat-card expiry-critical" @click="$emit('navigate', 'reminders')">
        <span>7天内到期</span>
        <strong>{{ stats.expiring_critical || 0 }}</strong>
      </button>
      <button type="button" class="stat-card expiry-warning" @click="$emit('navigate', 'reminders')">
        <span>15天内到期</span>
        <strong>{{ stats.expiring_warning || 0 }}</strong>
      </button>
      <button type="button" class="stat-card expiry-attention" @click="$emit('navigate', 'reminders')">
        <span>30天内到期</span>
        <strong>{{ stats.expiring_attention || 0 }}</strong>
      </button>
      <button type="button" class="stat-card" @click="$emit('navigate', 'reminders')">
        <span>到期总计</span>
        <strong>{{ stats.expiring_contracts }}</strong>
      </button>
    </div>
  </section>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { fetchDashboardStats } from '../api/dashboard'
import SectionToolbar from '../components/SectionToolbar.vue'
import { currency } from '../utils/formatters'

defineEmits(['navigate'])

const stats = ref(null)
const error = ref('')

async function load() {
  error.value = ''
  try {
    stats.value = await fetchDashboardStats()
  } catch (err) {
    error.value = err.message
  }
}

onMounted(load)

defineExpose({ load })
</script>
