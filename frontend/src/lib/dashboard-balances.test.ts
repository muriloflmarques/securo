import { describe, expect, it } from 'vitest'

import { getDashboardBalances } from './dashboard-balances'
import type { DashboardSummary } from '@/types'

function summary(overrides: Partial<DashboardSummary>): DashboardSummary {
  return {
    total_balance: {},
    total_balance_primary: 0,
    projected_balance: {},
    projected_balance_primary: 0,
    available_balance_primary: 1000,
    projected_available_balance_primary: 970,
    projected_available_delta_primary: -30,
    balance_date: '2026-10-05',
    monthly_income: 0,
    monthly_expenses: 0,
    monthly_income_primary: 0,
    monthly_expenses_primary: 0,
    accounts_count: 0,
    pending_categorization: 0,
    pending_categorization_amount: 0,
    assets_value: {},
    assets_value_primary: 0,
    primary_currency: 'EUR',
    pending_shares_net: 0,
    ...overrides,
  }
}

describe('getDashboardBalances', () => {
  it('uses projected available fields returned by the summary API', () => {
    expect(getDashboardBalances(summary({}), 123)).toEqual({
      availableBalance: 1000,
      projectedAvailableBalance: 970,
      projectedAvailableDelta: -30,
      hasProjectedAvailableBalance: true,
    })
  })

  it('falls back to the current available balance when the summary is missing', () => {
    expect(getDashboardBalances(undefined, 250)).toEqual({
      availableBalance: 250,
      projectedAvailableBalance: 250,
      projectedAvailableDelta: 0,
      hasProjectedAvailableBalance: false,
    })
  })
})
