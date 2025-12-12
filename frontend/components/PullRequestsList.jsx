import React, { useState, useEffect } from 'react'
import { RefreshCw, GitPullRequest, CheckCircle2, XCircle, Clock, ExternalLink, GitBranch } from 'lucide-react'
import { apiService } from '../services/api'

const PullRequestsList = () => {
  const [prs, setPrs] = useState([])
  const [loading, setLoading] = useState(false)
  const [repo, setRepo] = useState('PritamMishra065/autodevops-ai')
  const [token, setToken] = useState('')
  const [filter, setFilter] = useState('all')

  const fetchPRs = async () => {
    setLoading(true)
    try {
      const response = await apiService.getPullRequests(repo, token, filter)
      if (response.data && response.data.pull_requests) {
        setPrs(response.data.pull_requests)
      } else {
        setPrs([])
      }
    } catch (error) {
      console.error('Error fetching PRs:', error)
      setPrs([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    // Try to get token from localStorage
    const savedToken = localStorage.getItem('github_token')
    if (savedToken) {
      setToken(savedToken)
    }
  }, [])

  useEffect(() => {
    if (token) {
      fetchPRs()
      const interval = setInterval(fetchPRs, 30000) // Refresh every 30 seconds
      return () => clearInterval(interval)
    }
  }, [repo, token, filter])

  const getStateIcon = (state) => {
    switch (state) {
      case 'open':
        return <GitPullRequest className="w-5 h-5 text-green-500" />
      case 'closed':
        return <CheckCircle2 className="w-5 h-5 text-purple-500" />
      case 'merged':
        return <GitBranch className="w-5 h-5 text-blue-500" />
      default:
        return <Clock className="w-5 h-5 text-gray-400" />
    }
  }

  const getStateColor = (state) => {
    switch (state) {
      case 'open':
        return 'bg-green-100 text-green-800 border-green-300'
      case 'closed':
        return 'bg-gray-100 text-gray-800 border-gray-300'
      case 'merged':
        return 'bg-purple-100 text-purple-800 border-purple-300'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300'
    }
  }

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

  const handleTokenSave = () => {
    if (token) {
      localStorage.setItem('github_token', token)
      fetchPRs()
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <GitPullRequest className="w-6 h-6 text-primary-600" />
          <h2 className="text-2xl font-bold text-gray-800">Pull Requests</h2>
        </div>
        <button
          onClick={fetchPRs}
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
            GitHub Token (stored locally)
          </label>
          <div className="flex gap-2">
            <input
              type="password"
              value={token}
              onChange={(e) => setToken(e.target.value)}
              placeholder="ghp_..."
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
            <button
              onClick={handleTokenSave}
              className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
            >
              Save
            </button>
          </div>
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

      {/* PR List */}
      <div className="space-y-3">
        {!token ? (
          <div className="text-center py-8 text-gray-500">
            Please enter your GitHub token to track pull requests
          </div>
        ) : loading && prs.length === 0 ? (
          <div className="text-center py-8 text-gray-500">Loading PRs...</div>
        ) : prs.length === 0 ? (
          <div className="text-center py-8 text-gray-500">No pull requests found</div>
        ) : (
          prs.map((pr) => (
            <div
              key={pr.number}
              className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-3 flex-1">
                  {getStateIcon(pr.state)}
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="font-semibold text-gray-800">
                        #{pr.number}: {pr.title}
                      </h3>
                      <span
                        className={`px-2 py-1 text-xs rounded border ${getStateColor(pr.state)}`}
                      >
                        {pr.state}
                      </span>
                      {pr.draft && (
                        <span className="px-2 py-1 text-xs rounded bg-gray-100 text-gray-800 border border-gray-300">
                          Draft
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-gray-600 mb-2">
                      by {pr.author} • {formatDate(pr.created_at)}
                    </p>
                    {pr.body && (
                      <p className="text-sm text-gray-500 line-clamp-2">
                        {pr.body.substring(0, 150)}...
                      </p>
                    )}
                  </div>
                </div>
                <a
                  href={pr.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="ml-4 p-2 text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
                >
                  <ExternalLink className="w-5 h-5" />
                </a>
              </div>
              
              <div className="flex items-center gap-4 mt-3 text-sm text-gray-600">
                <div className="flex items-center gap-1">
                  <span className="text-green-600">+{pr.additions}</span>
                  <span className="text-red-600">-{pr.deletions}</span>
                </div>
                <div>{pr.changed_files} files changed</div>
                <div className="flex items-center gap-1">
                  <GitBranch className="w-4 h-4" />
                  {pr.head?.ref} → {pr.base?.ref}
                </div>
                {pr.labels && pr.labels.length > 0 && (
                  <div className="flex gap-1">
                    {pr.labels.map((label, idx) => (
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

export default PullRequestsList

