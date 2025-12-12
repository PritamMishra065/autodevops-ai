import React, { useState, useEffect } from 'react'
import { RefreshCw, Plus, CheckCircle2, XCircle, Clock } from 'lucide-react'
import { apiService } from '../services/api'

const ActionsList = () => {
  const [actions, setActions] = useState([])
  const [loading, setLoading] = useState(false)

  const fetchActions = async () => {
    setLoading(true)
    try {
      const response = await apiService.getActions()
      const actionData = response.data || []
      setActions(actionData)
    } catch (error) {
      console.error('Error fetching actions:', error)
      setActions([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchActions()
    const interval = setInterval(fetchActions, 5000)
    return () => clearInterval(interval)
  }, [])

  const getStatusIcon = (status) => {
    switch (status?.toLowerCase()) {
      case 'completed':
      case 'success':
        return <CheckCircle2 className="w-5 h-5 text-green-500" />
      case 'failed':
      case 'error':
        return <XCircle className="w-5 h-5 text-red-500" />
      case 'running':
      case 'pending':
        return <Clock className="w-5 h-5 text-yellow-500 animate-spin" />
      default:
        return <Clock className="w-5 h-5 text-gray-400" />
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold text-gray-800">Actions</h2>
        <button
          onClick={fetchActions}
          disabled={loading}
          className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      <div className="space-y-3">
        {actions.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            {loading ? 'Loading actions...' : 'No actions recorded'}
          </div>
        ) : (
          actions.map((action, index) => (
            <div
              key={index}
              className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  {getStatusIcon(action.status)}
                  <div>
                    <h3 className="font-semibold text-gray-800">
                      {action.type || action.name || 'Action'}
                    </h3>
                    <p className="text-sm text-gray-600">
                      {action.description || action.message || 'No description'}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-xs text-gray-500">
                    {action.timestamp || action.created_at || 'Unknown time'}
                  </div>
                  {action.agent && (
                    <div className="text-xs text-primary-600 mt-1">
                      Agent: {action.agent}
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

export default ActionsList


