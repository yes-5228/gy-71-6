export function currency(value) {
  return new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency: 'CNY',
    maximumFractionDigits: 0
  }).format(Number(value || 0))
}

export function statusText(value) {
  const map = {
    available: '可租',
    leased: '已租',
    maintenance: '维护',
    reserved: '预留',
    active: '履行中',
    terminated: '已终止',
    expired: '已到期',
    unpaid: '待收',
    paid: '已收',
    overdue: '逾期'
  }
  return map[value] || value
}

export function todayISO() {
  return new Date().toISOString().slice(0, 10)
}

export const EXPIRY_RISK_ORDER = ['critical', 'warning', 'attention']

export const EXPIRY_RISK_LABELS = {
  critical: '7天内到期',
  warning: '15天内到期',
  attention: '30天内到期'
}

export const EXPIRY_RISK_THRESHOLDS = {
  critical: 7,
  warning: 15,
  attention: 30
}

export function expiryRiskLabel(risk) {
  return EXPIRY_RISK_LABELS[risk] || ''
}

export function getExpiryRisk(endDate, status) {
  if (status !== 'active') return null
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const end = new Date(endDate)
  end.setHours(0, 0, 0, 0)
  const days = Math.ceil((end - today) / (1000 * 60 * 60 * 24))
  if (days < 0) return null
  if (days <= 7) return 'critical'
  if (days <= 15) return 'warning'
  if (days <= 30) return 'attention'
  return null
}

export function daysUntilExpiry(endDate) {
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  const end = new Date(endDate)
  end.setHours(0, 0, 0, 0)
  return Math.ceil((end - today) / (1000 * 60 * 60 * 24))
}

export function groupContractsByRisk(contracts) {
  const groups = { critical: [], warning: [], attention: [] }
  for (const c of contracts) {
    const risk = c.expiry_risk || getExpiryRisk(c.end_date, c.status)
    if (risk && groups[risk]) {
      groups[risk].push(c)
    }
  }
  return groups
}
