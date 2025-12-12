import React, { useState } from 'react'
import { Sparkles, Loader, CheckCircle2, AlertCircle } from 'lucide-react'
import { apiService } from '../services/api'

const FeatureGenerator = () => {
  const [feature, setFeature] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const handleGenerate = async (e) => {
    e.preventDefault()
    
    if (!feature.trim()) {
      setError('Please enter a feature description')
      return
    }

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const response = await apiService.generateFeature(feature)
      
      if (response.data && response.data.status === 'success') {
        setResult(response.data)
        setFeature('') // Clear input on success
      } else {
        setError(response.data?.error || 'Failed to generate feature')
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to generate feature')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center gap-2 mb-4">
        <Sparkles className="w-6 h-6 text-primary-600" />
        <h2 className="text-2xl font-bold text-gray-800">Generate Feature with Cline</h2>
      </div>

      <form onSubmit={handleGenerate} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Feature Description
          </label>
          <textarea
            value={feature}
            onChange={(e) => setFeature(e.target.value)}
            placeholder="e.g., Add login with GitHub OAuth"
            rows={4}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            disabled={loading}
          />
          <p className="text-xs text-gray-500 mt-1">
            Describe the feature you want Cline to build. Cline will create the code, tests, and documentation.
          </p>
        </div>

        <button
          type="submit"
          disabled={loading || !feature.trim()}
          className="w-full px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <Loader className="w-4 h-4 animate-spin" />
              Generating...
            </>
          ) : (
            <>
              <Sparkles className="w-4 h-4" />
              Generate Feature
            </>
          )}
        </button>
      </form>

      {error && (
        <div className="mt-4 p-3 bg-red-100 text-red-800 rounded-lg flex items-center gap-2">
          <AlertCircle className="w-5 h-5" />
          <span>{error}</span>
        </div>
      )}

      {result && (
        <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
          <div className="flex items-center gap-2 mb-3">
            <CheckCircle2 className="w-5 h-5 text-green-600" />
            <h3 className="font-semibold text-green-800">Feature Generated Successfully!</h3>
          </div>
          
          <div className="space-y-2 text-sm">
            <div>
              <span className="font-semibold">Feature:</span> {result.feature}
            </div>
            {result.files_created && (
              <div>
                <span className="font-semibold">Files Created:</span>
                <ul className="list-disc list-inside ml-2">
                  {result.files_created.map((file, idx) => (
                    <li key={idx}>{file}</li>
                  ))}
                </ul>
              </div>
            )}
            {result.branch && (
              <div>
                <span className="font-semibold">Branch:</span> {result.branch}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default FeatureGenerator

