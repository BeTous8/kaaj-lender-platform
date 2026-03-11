import axios from 'axios'
import type { LoanApplication, UnderwriteResponse, Lender, PolicyRule } from '../types'

const api = axios.create({
  baseURL: 'http://localhost:8000',
})

export interface ApplicationPayload {
  business_name: string
  industry?: string
  state?: string
  years_in_business?: number
  annual_revenue?: number
  is_startup?: boolean
  fico_score?: number
  paynet_score?: number
  transunion_score?: number
  loan_amount?: number
  equipment_type?: string
  equipment_year?: number
  equipment_mileage?: number
  has_bankruptcy?: boolean
  has_judgments?: boolean
  has_repossessions?: boolean
  has_tax_liens?: boolean
  is_us_citizen?: boolean
}

export interface RulePayload {
  field_name?: string
  operator?: string
  value?: string
  is_hard_stop?: boolean
  description?: string | null
}

export async function createApplication(data: ApplicationPayload): Promise<LoanApplication> {
  const res = await api.post<LoanApplication>('/api/applications', data)
  return res.data
}

export async function triggerUnderwrite(appId: number): Promise<UnderwriteResponse> {
  const res = await api.post<UnderwriteResponse>(`/api/underwrite/${appId}`)
  return res.data
}

export async function getApplicationResults(appId: number): Promise<UnderwriteResponse> {
  const res = await api.get<UnderwriteResponse>(`/api/applications/${appId}/results`)
  return res.data
}

export async function getLenders(): Promise<Lender[]> {
  const res = await api.get<Lender[]>('/api/lenders')
  return res.data
}

export async function getLender(id: number): Promise<Lender> {
  const res = await api.get<Lender>(`/api/lenders/${id}`)
  return res.data
}

export async function updateRule(ruleId: number, data: RulePayload): Promise<PolicyRule> {
  const res = await api.put<PolicyRule>(`/api/rules/${ruleId}`, data)
  return res.data
}

export async function deleteRule(ruleId: number): Promise<void> {
  await api.delete(`/api/rules/${ruleId}`)
}

export async function addRule(programId: number, data: RulePayload): Promise<PolicyRule> {
  const res = await api.post<PolicyRule>(`/api/programs/${programId}/rules`, data)
  return res.data
}