import type { DashboardSummary } from '@/types'

const MEANINGFUL_DELTA = 0.01

export function getDashboardBalances(
  summary: DashboardSummary | undefined,
  fallbackAvailableBalance: number,
) {
  const availableBalance = Number(
    summary?.available_balance_primary ?? fallbackAvailableBalance,
  )
  const projectedAvailableBalance = Number(
    summary?.projected_available_balance_primary ?? availableBalance,
  )
  const projectedAvailableDelta = Number(
    summary?.projected_available_delta_primary
      ?? projectedAvailableBalance - availableBalance,
  )

  return {
    availableBalance,
    projectedAvailableBalance,
    projectedAvailableDelta,
    hasProjectedAvailableBalance: Math.abs(projectedAvailableDelta) >= MEANINGFUL_DELTA,
  }
}
