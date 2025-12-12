import React, { useState, useEffect } from 'react'
import { RefreshCw, Search, Trash2 } from 'lucide-react'
import { apiService } from '../services/api'

const LogViewer = () => {
  const [logs, setLogs] = useState([])
  const [filteredLogs, setFilteredLogs] = useState([])
  const [searchTerm, setSearchTerm] = useState('')
  const [loading, setLoading] = useState(false)

  const fetchLogs = async () => {
    setLoading(true)
    try {
      const response = await apiService.getLogs()
      const logData = response.data || []
      setLogs(logData)
      setFilteredLogs(logData)
    } catch (error) {
      console.error('Error fetching logs:', error)
      setLogs([])
      setFilteredLogs([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchLogs()
    const interval = setInterval(fetchLogs, 5000) // Refresh every 5 seconds
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    if (searchTerm) {
      const filtered = logs.filter(log =>
        JSON.stringify(log).toLowerCase().includes(searchTerm.toLowerCase())
      )
      setFilteredLogs(filtered)
    } else {
      setFilteredLogs(logs)
    }
  }, [searchTerm, logs])

  const getLogLevelColor = (level) => {
    switch (level?.toLowerCase()) {
      case 'error':
        return 'bg-red-100 text-red-800 border-red-300'
      case 'warning':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300'
      case 'info':
        return 'bg-blue-100 text-blue-800 border-blue-300'
      case 'success':
        return 'bg-green-100 text-green-800 border-green-300'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300'
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold text-gray-800">Logs</h2>
        <div className="flex items-center gap-2">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search logs..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <button
            onClick={fetchLogs}
            disabled={loading}
            className="p-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      <div className="space-y-2 max-h-96 overflow-y-auto">
        {filteredLogs.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            {loading ? 'Loading logs...' : 'No logs available'}
          </div>
        ) : (
          filteredLogs.map((log, index) => (
            <div
              key={index}
              className={`p-3 rounded-lg border ${getLogLevelColor(log.level)}`}
            >
              <div className="flex items-center justify-between mb-1">
                <span className="font-semibold text-sm">
                  {log.level || 'INFO'}
                </span>
                <span className="text-xs opacity-75">
                  {log.timestamp || new Date().toLocaleString()}
                </span>
              </div>
              <pre className="text-xs whitespace-pre-wrap font-mono">
                {typeof log === 'object' ? JSON.stringify(log, null, 2) : log}
              </pre>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

export default LogViewer


