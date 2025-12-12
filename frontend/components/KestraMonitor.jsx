import React, { useState, useEffect } from 'react'
import { RefreshCw, Brain, CheckCircle2, XCircle, AlertTriangle, Zap } from 'lucide-react'
import { apiService } from '../services/api'

const KestraMonitor = () => {
  const [decisions, setDecisions] = useState([])
  const [loading, setLoading] = useState(false)
  const [autoRefresh, setAutoRefresh] = useState(true)

  const fetchDecisions = async () => {
    setLoading(true)
    try {
      const response = await apiService.kestraMonitor()
      if (response.data && response.data.decisions) {
        setDecisions(response.data.decisions)
      }
    } catch (error) {
      console.error('Error fetching Kestra decisions:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (autoRefresh) {
      fetchDecisions()
      const interval = setInterval(fetchDecisions, 10000) // Every 10 seconds
      return () => clearInterval(interval)
    }
  }, [autoRefresh])

  const getDecisionIcon = (type) => {
    switch (type) {
      case 'BUILD_FAILURE':
        return <XCircle className="w-5 h-5 text-red-500" />
      case 'LOW_CODE_QUALITY':
        return <AlertTriangle className="w-5 h-5 text-yellow-500" />
      case 'DEPLOYMENT_FAILURE':
        return <XCircle className="w-5 h-5 text-red-500" />
      case 'STALE_PR':
        return <AlertTriangle className="w-5 h-5 text-yellow-500" />
      default:
        return <Zap className="w-5 h-5 text-blue-500" />
    }
  }

  const getDecisionColor = (type) => {
    switch (type) {
      case 'BUILD_FAILURE':
      case 'DEPLOYMENT_FAILURE':
        return 'bg-red-100 text-red-800 border-red-300'
      case 'LOW_CODE_QUALITY':
      case 'STALE_PR':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300'
      default:
        return 'bg-blue-100 text-blue-800 border-blue-300'
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Brain className="w-6 h-6 text-primary-600" />
          <h2 className="text-2xl font-bold text-gray-800">Kestra Decision Engine</h2>
        </div>
        <div className="flex items-center gap-2">
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
              className="rounded"
            />
            Auto-refresh
          </label>
          <button
            onClick={fetchDecisions}
            disabled={loading}
            className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            Monitor
          </button>
        </div>
      </div>

      <div className="space-y-3">
        {decisions.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            {loading ? 'Monitoring system...' : 'No decisions made. System is healthy.'}
          </div>
        ) : (
          decisions.map((decision, index) => (
            <div
              key={index}
              className={`p-4 rounded-lg border ${getDecisionColor(decision.type)}`}
            >
              <div className="flex items-start gap-3">
                {getDecisionIcon(decision.type)}
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-1">
                    <h3 className="font-semibold">{decision.type}</h3>
                    {decision.action_required && (
                      <span className="px-2 py-1 text-xs bg-red-500 text-white rounded">
                        Action Required
                      </span>
                    )}
                  </div>
                  <p className="text-sm opacity-90">{decision.reason}</p>
                  {decision.action && (
                    <div className="mt-2 text-xs">
                      <span className="font-semibold">Action:</span> {decision.action}
                    </div>
                  )}
                  {decision.pr_number && (
                    <div className="mt-1 text-xs">
                      <span className="font-semibold">PR:</span> #{decision.pr_number}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

export default KestraMonitor

