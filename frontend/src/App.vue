<template>
  <AppHeader />
  <main class="app-shell">
    <NavigationTabs v-model="activeView" :items="tabs" />
    <DashboardView ref="dashboardRef" v-if="activeView === 'dashboard'" @navigate="activeView = $event" />
    <WorkstationsView v-else-if="activeView === 'workstations'" />
    <ContractsView v-else-if="activeView === 'contracts'" @contract-changed="refreshAllViews" />
    <PaymentsView v-else-if="activeView === 'payments'" />
    <RemindersView ref="remindersRef" v-else @contract-changed="refreshAllViews" />
  </main>
</template>

<script setup>
import { nextTick, ref } from 'vue'
import AppHeader from './components/AppHeader.vue'
import NavigationTabs from './components/NavigationTabs.vue'
import ContractsView from './views/ContractsView.vue'
import DashboardView from './views/DashboardView.vue'
import PaymentsView from './views/PaymentsView.vue'
import RemindersView from './views/RemindersView.vue'
import WorkstationsView from './views/WorkstationsView.vue'

const activeView = ref('dashboard')
const dashboardRef = ref(null)
const remindersRef = ref(null)

const tabs = [
  { key: 'dashboard', label: '运营看板' },
  { key: 'workstations', label: '工位管理' },
  { key: 'contracts', label: '合同签订' },
  { key: 'payments', label: '费用收缴' },
  { key: 'reminders', label: '到期提醒' }
]

async function refreshAllViews() {
  await nextTick()
  if (dashboardRef.value && typeof dashboardRef.value.load === 'function') {
    dashboardRef.value.load()
  }
  if (remindersRef.value && typeof remindersRef.value.load === 'function') {
    remindersRef.value.load()
  }
}
</script>
