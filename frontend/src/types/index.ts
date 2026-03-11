export interface RuleEvaluation {
  rule_id: number
  passed: boolean
  actual_value: string | null
  required_value: string
  explanation: string
}

export interface MatchResult {
  lender_id: number
  lender_name: string
  program_id: number
  program_name: string
  is_eligible: boolean
  fit_score: number
  rule_evaluations: RuleEvaluation[]
}

export interface UnderwriteResponse {
  application_id: number
  status: string
  match_count: number
  results: MatchResult[]
}

export interface LoanApplication {
  id: number
  business_name: string
  status: 'pending' | 'processing' | 'complete'
  created_at: string
}

export interface PolicyRule {
  id: number
  field_name: string
  operator: string
  value: string
  is_hard_stop: boolean
  description: string | null
}

export interface Program {
  id: number
  name: string
  priority: number
  is_active: boolean
  policy_rules: PolicyRule[]
}

export interface Lender {
  id: number
  name: string
  slug: string
  is_active: boolean
  notes: string | null
  programs: Program[]
}

export interface ApplicationFormData {
  business_name: string
  industry: string
  state: string
  years_in_business: number | ''
  annual_revenue: number | ''
  is_startup: boolean
  fico_score: number | ''
  paynet_score: number | ''
  transunion_score: number | ''
  loan_amount: number | ''
  equipment_type: string
  equipment_year: number | ''
  equipment_mileage: number | ''
  has_bankruptcy: boolean
  has_judgments: boolean
  has_repossessions: boolean
  has_tax_liens: boolean
  is_us_citizen: boolean
}