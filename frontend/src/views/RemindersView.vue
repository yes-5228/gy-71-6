<template>
  <section class="panel">
    <SectionToolbar eyebrow="Reminders" title="到期与逾期提醒">
      <button type="button" class="ghost-button" @click="load">刷新</button>
    </SectionToolbar>

    <p v-if="error" class="error">{{ error }}</p>
    <p v-if="successMsg" class="success">{{ successMsg }}</p>

    <div class="split-grid">
      <div>
        <h3>到期合同风险分级（共 {{ grouped.total_count || 0 }} 份）</h3>
        <div class="risk-groups">
          <div v-for="risk in EXPIRY_RISK_ORDER" :key="risk" class="risk-group">
            <div class="risk-group-header" :class="risk">
              <h3>{{ EXPIRY_RISK_LABELS[risk] }}</h3>
              <span class="risk-group-count">{{ grouped[risk]?.count || 0 }} 份</span>
            </div>
            <div class="risk-group-body">
              <div class="list">
                <article
                  v-for="contract in grouped[risk]?.contracts || []"
                  :key="contract.id"
                  class="list-item"
                  :class="`${risk}-line`"
                >
                  <div style="display: flex; justify-content: space-between; align-items: center;">
                    <strong>{{ contract.tenant_name }}</strong>
                    <span class="days-tag" :class="risk">{{ contract.days_until_expiry }} 天后到期</span>
                  </div>
                  <span>{{ contract.contract_no }} / {{ contract.workstation?.code || '-' }}</span>
                  <span>到期日：{{ contract.end_date }} / 月租金：{{ currency(contract.monthly_rent) }}</span>
                  <div class="action-buttons">
                    <button type="button" class="small-button primary" @click="openRenewDialog(contract)">续租</button>
                    <button type="button" class="small-button danger" @click="terminateContract(contract.id)">终止</button>
                  </div>
                </article>
                <p v-if="!grouped[risk]?.contracts?.length" class="empty">暂无{{ EXPIRY_RISK_LABELS[risk] }}合同</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div>
        <h3>逾期未收账单</h3>
        <div class="list">
          <article v-for="payment in payments" :key="payment.id" class="list-item danger-line">
            <strong>{{ payment.tenant_name }}</strong>
            <span>{{ payment.contract_no }} / {{ payment.period }}</span>
            <span>{{ currency(payment.amount) }}，应收日 {{ payment.due_date }}</span>
          </article>
          <p v-if="!payments.length" class="empty">暂无逾期账单</p>
        </div>
      </div>
    </div>

    <div v-if="renewOpen" class="renew-dialog">
      <h4>续租合同：{{ renewTarget?.contract_no }}</h4>
      <p>当前租户：{{ renewTarget?.tenant_name }}，当前到期日：{{ renewTarget?.end_date }}</p>
      <div class="form-grid" style="margin-bottom: 0;">
        <label>
          <small>新的到期日</small>
          <input v-model="renewEndDate" type="date" required />
        </label>
      </div>
      <div class="renew-actions">
        <button type="button" class="small-button" @click="cancelRenew">取消</button>
        <button type="button" class="small-button primary" @click="confirmRenew">确认续租</button>
      </div>
    </div>
  </section>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { fetchExpiringContractsGrouped, fetchOverduePayments } from '../api/reminders'
import { updateContract } from '../api/contracts'
import SectionToolbar from '../components/SectionToolbar.vue'
import {
  EXPIRY_RISK_LABELS,
  EXPIRY_RISK_ORDER,
  currency,
  todayISO
} from '../utils/formatters'

const emit = defineEmits(['contract-changed'])

const grouped = ref({ critical: { count: 0, contracts: [] }, warning: { count: 0, contracts: [] }, attention: { count: 0, contracts: [] }, total_count: 0 })
const payments = ref([])
const error = ref('')
const successMsg = ref('')

const renewOpen = ref(false)
const renewTarget = ref(null)
const renewEndDate = ref('')

function clearMessages() {
  error.value = ''
  successMsg.value = ''
}

function showSuccess(msg) {
  successMsg.value = msg
  setTimeout(() => { successMsg.value = '' }, 3000)
}

async function load() {
  clearMessages()
  try {
    const [expiringGrouped, overdue] = await Promise.all([
      fetchExpiringContractsGrouped(),
      fetchOverduePayments()
    ])
    grouped.value = expiringGrouped
    payments.value = overdue
  } catch (err) {
    error.value = err.message
  }
}

function openRenewDialog(contract) {
  renewTarget.value = contract
  const currentEnd = new Date(contract.end_date)
  const defaultEnd = new Date(currentEnd)
  defaultEnd.setMonth(defaultEnd.getMonth() + 12)
  renewEndDate.value = defaultEnd.toISOString().slice(0, 10)
  renewOpen.value = true
}

function cancelRenew() {
  renewOpen.value = false
  renewTarget.value = null
  renewEndDate.value = ''
}

async function confirmRenew() {
  if (!renewTarget.value || !renewEndDate.value) return
  clearMessages()
  try {
    await updateContract(renewTarget.value.id, { end_date: renewEndDate.value })
    showSuccess('续租成功，提醒已更新')
    cancelRenew()
    await load()
    emit('contract-changed')
  } catch (err) {
    error.value = err.message
  }
}

async function terminateContract(id) {
  if (!confirm('确认终止该合同吗？终止后工位将变为可租状态。')) return
  clearMessages()
  try {
    await updateContract(id, { status: 'terminated' })
    showSuccess('合同已终止，提醒已更新')
    await load()
    emit('contract-changed')
  } catch (err) {
    error.value = err.message
  }
}

onMounted(load)
</script>
