import React, { useState, useEffect } from 'react'
import { RefreshCw, AlertCircle, CheckCircle2, ExternalLink, MessageSquare } from 'lucide-react'
import { apiService } from '../services/api'

const IssuesList = () => {
  const [issues, setIssues] = useState([])
  const [loading, setLoading] = useState(false)
  const [repo, setRepo] = useState('PritamMishra065/autodevops-ai')
  const [token, setToken] = useState('')
  const [filter, setFilter] = useState('all')

  const fetchIssues = async () => {
    setLoading(true)
    try {
      const response = await apiService.getIssues(repo, token, filter)
      if (response.data && response.data.issues) {
        setIssues(response.data.issues)
      } else {
        setIssues([])
      }
    } catch (error) {
      console.error('Error fetching issues:', error)
      setIssues([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    const savedToken = localStorage.getItem('github_token')
    if (savedToken) {
      setToken(savedToken)
    }
  }, [])

  useEffect(() => {
    if (token) {
      fetchIssues()
      const interval = setInterval(fetchIssues, 30000)
      return () => clearInterval(interval)
    }
  }, [repo, token, filter])

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A'
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <AlertCircle className="w-6 h-6 text-primary-600" />
          <h2 className="text-2xl font-bold text-gray-800">Issues</h2>
        </div>
        <button
          onClick={fetchIssues}
          disabled={loading || !token}
          className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {/* Configuration */}
      <div className="mb-4 p-4 bg-gray-50 rounded-lg space-y-3">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Repository
          </label>
          <input
            type="text"
            value={repo}
            onChange={(e) => setRepo(e.target.value)}
            placeholder="owner/repo"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Filter
          </label>
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="all">All</option>
            <option value="open">Open</option>
            <option value="closed">Closed</option>
          </select>
        </div>
      </div>

      {/* Issues List */}
      <div className="space-y-3">
        {!token ? (
          <div className="text-center py-8 text-gray-500">
            Please configure your GitHub token in Pull Requests tab
          </div>
        ) : loading && issues.length === 0 ? (
          <div className="text-center py-8 text-gray-500">Loading issues...</div>
        ) : issues.length === 0 ? (
          <div className="text-center py-8 text-gray-500">No issues found</div>
        ) : (
          issues.map((issue) => (
            <div
              key={issue.number}
              className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-3 flex-1">
                  {issue.state === 'open' ? (
                    <AlertCircle className="w-5 h-5 text-green-500" />
                  ) : (
                    <CheckCircle2 className="w-5 h-5 text-gray-400" />
                  )}
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="font-semibold text-gray-800">
                        #{issue.number}: {issue.title}
                      </h3>
                      <span
                        className={`px-2 py-1 text-xs rounded ${
                          issue.state === 'open'
                            ? 'bg-green-100 text-green-800 border border-green-300'
                            : 'bg-gray-100 text-gray-800 border border-gray-300'
                        }`}
                      >
                        {issue.state}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">
                      by {issue.author} • {formatDate(issue.created_at)}
                    </p>
                    {issue.body && (
                      <p className="text-sm text-gray-500 line-clamp-2">
                        {issue.body.substring(0, 150)}...
                      </p>
                    )}
                  </div>
                </div>
                <a
                  href={issue.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="ml-4 p-2 text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
                >
                  <ExternalLink className="w-5 h-5" />
                </a>
              </div>
              
              <div className="flex items-center gap-4 mt-3 text-sm text-gray-600">
                <div className="flex items-center gap-1">
                  <MessageSquare className="w-4 h-4" />
                  {issue.comments} comments
                </div>
                {issue.labels && issue.labels.length > 0 && (
                  <div className="flex gap-1">
                    {issue.labels.map((label, idx) => (
                      <span
                        key={idx}
                        className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded"
                      >
                        {label}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

export default IssuesList


