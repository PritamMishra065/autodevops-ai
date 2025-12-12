import React, { useState, useEffect } from 'react'
import { RefreshCw, Database, Settings } from 'lucide-react'
import { apiService } from '../services/api'

const ModelsList = () => {
  const [models, setModels] = useState([])
  const [loading, setLoading] = useState(false)

  const fetchModels = async () => {
    setLoading(true)
    try {
      const response = await apiService.getModels()
      const modelData = response.data || []
      setModels(modelData)
    } catch (error) {
      console.error('Error fetching models:', error)
      setModels([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchModels()
  }, [])

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Database className="w-6 h-6 text-primary-600" />
          <h2 className="text-2xl font-bold text-gray-800">AI Models</h2>
        </div>
        <button
          onClick={fetchModels}
          disabled={loading}
          className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {models.length === 0 ? (
          <div className="col-span-full text-center py-8 text-gray-500">
            {loading ? 'Loading models...' : 'No models configured'}
          </div>
        ) : (
          models.map((model, index) => (
            <div
              key={index}
              className="p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow"
            >
              <div className="flex items-center gap-2 mb-2">
                <Settings className="w-5 h-5 text-primary-600" />
                <h3 className="font-semibold text-gray-800">
                  {model.name || model.model || 'Unnamed Model'}
                </h3>
              </div>
              {model.provider && (
                <div className="text-sm text-gray-600 mb-1">
                  Provider: <span className="font-medium">{model.provider}</span>
                </div>
              )}
              {model.version && (
                <div className="text-sm text-gray-600 mb-1">
                  Version: <span className="font-medium">{model.version}</span>
                </div>
              )}
              {model.status && (
                <div className="mt-2">
                  <span
                    className={`px-2 py-1 text-xs rounded ${
                      model.status === 'active'
                        ? 'bg-green-100 text-green-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    {model.status}
                  </span>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  )
}

export default ModelsList


