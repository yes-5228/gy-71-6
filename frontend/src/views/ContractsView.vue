<template>
  <section class="panel">
    <SectionToolbar eyebrow="Contracts" title="租赁合同签订">
      <div style="display: flex; gap: 10px; align-items: center;">
        <select v-model="riskFilter" @change="applyFilter">
          <option value="">全部风险</option>
          <option value="critical">7天内到期</option>
          <option value="warning">15天内到期</option>
          <option value="attention">30天内到期</option>
        </select>
        <select v-model="statusFilter" @change="applyFilter">
          <option value="">全部合同</option>
          <option value="active">履行中</option>
          <option value="terminated">已终止</option>
          <option value="expired">已到期</option>
        </select>
      </div>
    </SectionToolbar>

    <form class="form-grid" @submit.prevent="submit">
      <input v-model="form.tenant_name" placeholder="租户名称" required />
      <input v-model="form.tenant_contact" placeholder="联系人/电话" />
      <select v-model.number="form.workstation_id" required>
        <option value="" disabled>选择可租工位</option>
        <option v-for="item in availableWorkstations" :key="item.id" :value="item.id">
          {{ item.code }} / {{ item.area }} / {{ currency(item.monthly_rent) }}
        </option>
      </select>
      <input v-model="form.start_date" type="date" required />
      <input v-model="form.end_date" type="date" required />
      <input v-model.number="form.monthly_rent" type="number" min="0" placeholder="月租金" required />
      <input v-model.number="form.deposit" type="number" min="0" placeholder="押金" />
      <button type="submit">签订合同</button>
    </form>

    <p v-if="error" class="error">{{ error }}</p>
    <p v-if="successMsg" class="success">{{ successMsg }}</p>

    <div v-if="statusFilter === '' || statusFilter === 'active'" class="risk-groups" style="margin-bottom: 20px;">
      <div v-for="risk in EXPIRY_RISK_ORDER" :key="risk" class="risk-group">
        <div class="risk-group-header" :class="risk">
          <h3>{{ EXPIRY_RISK_LABELS[risk] }}</h3>
          <span class="risk-group-count">{{ groupedCounts[risk] }} 份</span>
        </div>
        <div class="risk-group-body">
          <p v-if="!groupedContracts[risk].length" class="empty">暂无</p>
          <table v-else>
            <thead>
              <tr>
                <th>合同号</th>
                <th>租户</th>
                <th>工位</th>
                <th>到期日</th>
                <th>剩余天数</th>
                <th>风险</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="contract in groupedContracts[risk]" :key="contract.id" :class="`row-${risk}`">
                <td>{{ contract.contract_no }}</td>
                <td>{{ contract.tenant_name }}<small>{{ contract.tenant_contact }}</small></td>
                <td>{{ contract.workstation?.code || '-' }}</td>
                <td>{{ contract.end_date }}</td>
                <td>
                  <span class="days-tag" :class="risk">{{ contract.days_until_expiry }} 天</span>
                </td>
                <td>
                  <span class="risk-badge" :class="`risk-${risk}`">{{ EXPIRY_RISK_LABELS[risk] }}</span>
                </td>
                <td>
                  <div class="action-buttons">
                    <button type="button" class="small-button primary" @click="openRenewDialog(contract)">续租</button>
                    <button type="button" class="small-button danger" @click="terminateContract(contract.id)">终止</button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <div class="table-wrap">
      <h3 style="margin: 0 0 12px;">全部合同</h3>
      <table>
        <thead>
          <tr>
            <th>合同号</th>
            <th>租户</th>
            <th>工位</th>
            <th>租期</th>
            <th>月租金</th>
            <th>押金</th>
            <th>剩余天数</th>
            <th>风险</th>
            <th>状态</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="contract in filteredContracts" :key="contract.id" :class="contract.expiry_risk ? `row-${contract.expiry_risk}` : ''">
            <td>{{ contract.contract_no }}</td>
            <td>{{ contract.tenant_name }}<small>{{ contract.tenant_contact }}</small></td>
            <td>{{ contract.workstation?.code || '-' }}</td>
            <td>{{ contract.start_date }} 至 {{ contract.end_date }}</td>
            <td>{{ currency(contract.monthly_rent) }}</td>
            <td>{{ currency(contract.deposit) }}</td>
            <td>
              <span v-if="contract.days_until_expiry != null && contract.status === 'active'"
                class="days-tag"
                :class="contract.expiry_risk || ''">
                {{ contract.days_until_expiry }} 天
              </span>
              <span v-else class="empty">-</span>
            </td>
            <td>
              <span v-if="contract.expiry_risk" class="risk-badge" :class="`risk-${contract.expiry_risk}`">
                {{ EXPIRY_RISK_LABELS[contract.expiry_risk] }}
              </span>
              <span v-else class="empty">-</span>
            </td>
            <td><StatusBadge :value="contract.status" /></td>
            <td>
              <div v-if="contract.status === 'active'" class="action-buttons">
                <button type="button" class="small-button primary" @click="openRenewDialog(contract)">续租</button>
                <button type="button" class="small-button danger" @click="terminateContract(contract.id)">终止</button>
              </div>
              <span v-else class="empty">-</span>
            </td>
          </tr>
        </tbody>
      </table>
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
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { createContract, fetchContracts, updateContract } from '../api/contracts'
import { fetchWorkstations } from '../api/workstations'
import SectionToolbar from '../components/SectionToolbar.vue'
import StatusBadge from '../components/StatusBadge.vue'
import {
  EXPIRY_RISK_LABELS,
  EXPIRY_RISK_ORDER,
  currency,
  todayISO,
  groupContractsByRisk
} from '../utils/formatters'

const emit = defineEmits(['contract-changed'])

const contracts = ref([])
const availableWorkstations = ref([])
const statusFilter = ref('')
const riskFilter = ref('')
const error = ref('')
const successMsg = ref('')

const renewOpen = ref(false)
const renewTarget = ref(null)
const renewEndDate = ref('')

const form = reactive({
  tenant_name: '',
  tenant_contact: '',
  workstation_id: '',
  start_date: todayISO(),
  end_date: '',
  monthly_rent: 0,
  deposit: 0
})

watch(
  () => form.workstation_id,
  (id) => {
    const item = availableWorkstations.value.find((workstation) => workstation.id === Number(id))
    if (item) {
      form.monthly_rent = Number(item.monthly_rent)
      form.deposit = Number(item.monthly_rent) * 2
    }
  }
)

const filteredContracts = computed(() => {
  let list = contracts.value
  if (statusFilter.value) {
    list = list.filter((c) => c.status === statusFilter.value)
  }
  if (riskFilter.value) {
    list = list.filter((c) => c.expiry_risk === riskFilter.value)
  }
  return list
})

const groupedContracts = computed(() => {
  const active = contracts.value.filter((c) => c.status === 'active')
  return groupContractsByRisk(active)
})

const groupedCounts = computed(() => ({
  critical: groupedContracts.value.critical.length,
  warning: groupedContracts.value.warning.length,
  attention: groupedContracts.value.attention.length
}))

function applyFilter() {
}

function clearMessages() {
  error.value = ''
  successMsg.value = ''
}

function showSuccess(msg) {
  successMsg.value = msg
  setTimeout(() => { successMsg.value = '' }, 3000)
}

async function loadContracts() {
  clearMessages()
  try {
    contracts.value = await fetchContracts(statusFilter.value)
  } catch (err) {
    error.value = err.message
  }
}

async function loadWorkstations() {
  availableWorkstations.value = await fetchWorkstations('available')
}

async function load() {
  clearMessages()
  try {
    await Promise.all([loadContracts(), loadWorkstations()])
  } catch (err) {
    error.value = err.message
  }
}

async function submit() {
  clearMessages()
  try {
    await createContract({ ...form, workstation_id: Number(form.workstation_id) })
    Object.assign(form, {
      tenant_name: '',
      tenant_contact: '',
      workstation_id: '',
      start_date: todayISO(),
      end_date: '',
      monthly_rent: 0,
      deposit: 0
    })
    showSuccess('合同签订成功')
    await load()
    emit('contract-changed')
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
    showSuccess('续租成功')
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
    showSuccess('合同已终止')
    await load()
    emit('contract-changed')
  } catch (err) {
    error.value = err.message
  }
}

onMounted(load)
</script>
