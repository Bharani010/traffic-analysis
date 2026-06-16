import { useEffect, useState } from 'react'
import { api, type HealthResponse } from '../../services/api'

export function Dashboard() {
  const [health, setHealth] = useState<HealthResponse | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api
      .getHealth()
      .then(setHealth)
      .catch(() => setHealth(null))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="min-h-screen bg-surface-900">
      {/* ── Header ── */}
      <header className="border-b border-surface-700/50 bg-surface-800/30 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-brand-500 to-brand-700 flex items-center justify-center shadow-lg shadow-brand-500/20">
              <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <div>
              <h1 className="text-lg font-bold text-white">Traffic Analysis</h1>
              <p className="text-xs text-surface-200/50">Anomaly Detection Platform</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            {health && (
              <span className={`badge ${health.status === 'healthy' ? 'badge-success' : 'badge-danger'}`}>
                ● {health.status}
              </span>
            )}
          </div>
        </div>
      </header>

      {/* ── Main Content ── */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8 animate-fade-in">
          <StatCard
            label="Total Events"
            value="—"
            change="+0%"
            trend="neutral"
            icon={
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z" />
              </svg>
            }
          />
          <StatCard
            label="Anomalies"
            value="—"
            change="+0%"
            trend="neutral"
            icon={
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
              </svg>
            }
          />
          <StatCard
            label="Open Incidents"
            value="—"
            change="+0%"
            trend="neutral"
            icon={
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 12h16.5m-16.5 3.75h16.5M3.75 19.5h16.5M5.625 4.5h12.75a1.875 1.875 0 010 3.75H5.625a1.875 1.875 0 010-3.75z" />
              </svg>
            }
          />
          <StatCard
            label="Uptime"
            value={health ? `${health.uptime_seconds}s` : '—'}
            change="99.9%"
            trend="up"
            icon={
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            }
          />
        </div>

        {/* Placeholder Panels */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 card animate-fade-in">
            <h2 className="text-lg font-semibold text-white mb-4">Traffic Overview</h2>
            <div className="h-64 flex items-center justify-center text-surface-200/30 border border-dashed border-surface-700 rounded-xl">
              <p className="text-sm">Traffic chart — coming in Phase 2</p>
            </div>
          </div>
          <div className="card animate-fade-in">
            <h2 className="text-lg font-semibold text-white mb-4">Recent Anomalies</h2>
            <div className="h-64 flex items-center justify-center text-surface-200/30 border border-dashed border-surface-700 rounded-xl">
              <p className="text-sm">Anomaly feed — coming in Phase 2</p>
            </div>
          </div>
        </div>

        {/* System Info */}
        {loading ? (
          <div className="mt-8 card animate-pulse">
            <div className="h-4 bg-surface-700/50 rounded w-1/3"></div>
          </div>
        ) : health ? (
          <div className="mt-8 card animate-fade-in">
            <h2 className="text-lg font-semibold text-white mb-3">System Status</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <span className="text-surface-200/50">Service</span>
                <p className="font-mono text-brand-400">{health.service}</p>
              </div>
              <div>
                <span className="text-surface-200/50">Version</span>
                <p className="font-mono text-brand-400">{health.version}</p>
              </div>
              <div>
                <span className="text-surface-200/50">Status</span>
                <p className={`font-mono ${health.status === 'healthy' ? 'text-success-400' : 'text-danger-400'}`}>
                  {health.status}
                </p>
              </div>
              <div>
                <span className="text-surface-200/50">Uptime</span>
                <p className="font-mono text-brand-400">{health.uptime_seconds}s</p>
              </div>
            </div>
          </div>
        ) : (
          <div className="mt-8 card border-danger-500/30 animate-fade-in">
            <p className="text-danger-400 text-sm">
              ⚠ Unable to connect to backend. Make sure the API is running.
            </p>
          </div>
        )}
      </main>
    </div>
  )
}

// ── Stat Card Component ──

interface StatCardProps {
  label: string
  value: string
  change: string
  trend: 'up' | 'down' | 'neutral'
  icon: React.ReactNode
}

function StatCard({ label, value, change, trend, icon }: StatCardProps) {
  const trendColor =
    trend === 'up' ? 'text-success-400' : trend === 'down' ? 'text-danger-400' : 'text-surface-200/40'

  return (
    <div className="stat-card group">
      <div className="flex items-center justify-between">
        <div className="w-10 h-10 rounded-xl bg-brand-500/10 text-brand-400 flex items-center justify-center group-hover:bg-brand-500/20 transition-colors">
          {icon}
        </div>
        <span className={`text-xs font-medium ${trendColor}`}>{change}</span>
      </div>
      <div className="mt-3">
        <p className="stat-value text-white">{value}</p>
        <p className="stat-label">{label}</p>
      </div>
    </div>
  )
}

export default Dashboard
