import React, { useState } from 'react'
import { Plus, AlertCircle, CheckCircle2, X } from 'lucide-react'
import { apiService } from '../services/api'

const IssueCreator = ({ onIssueCreated }) => {
  const [isOpen, setIsOpen] = useState(false)
  const [repo, setRepo] = useState('PritamMishra065/autodevops-ai')
  const [token, setToken] = useState('')
  const [title, setTitle] = useState('')
  const [body, setBody] = useState('')
  const [labels, setLabels] = useState('')
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState(null)

  React.useEffect(() => {
    const savedToken = localStorage.getItem('github_token')
    if (savedToken) {
      setToken(savedToken)
    }
  }, [])

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!title.trim()) {
      setMessage({ type: 'error', text: 'Title is required' })
      return
    }

    if (!token) {
      setMessage({ type: 'error', text: 'GitHub token is required' })
      return
    }

    setLoading(true)
    setMessage(null)

    try {
      const labelsArray = labels
        ? labels.split(',').map(l => l.trim()).filter(l => l)
        : []

      const response = await apiService.createIssue(repo, title, body, token, labelsArray)
      
      if (response.data && response.data.success) {
        setMessage({
          type: 'success',
          text: `Issue #${response.data.issue.number} created successfully!`
        })
        setTitle('')
        setBody('')
        setLabels('')
        
        if (onIssueCreated) {
          onIssueCreated(response.data.issue)
        }
        
        setTimeout(() => {
          setIsOpen(false)
          setMessage(null)
        }, 2000)
      } else {
        setMessage({
          type: 'error',
          text: response.data?.error || 'Failed to create issue'
        })
      }
    } catch (error) {
      setMessage({
        type: 'error',
        text: error.response?.data?.error || 'Failed to create issue'
      })
    } finally {
      setLoading(false)
    }
  }

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
      >
        <Plus className="w-4 h-4" />
        Create Issue
      </button>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold text-gray-800">Create GitHub Issue</h2>
        <button
          onClick={() => {
            setIsOpen(false)
            setMessage(null)
          }}
          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {message && (
        <div
          className={`mb-4 p-3 rounded-lg flex items-center gap-2 ${
            message.type === 'success'
              ? 'bg-green-100 text-green-800'
              : 'bg-red-100 text-red-800'
          }`}
        >
          {message.type === 'success' ? (
            <CheckCircle2 className="w-5 h-5" />
          ) : (
            <AlertCircle className="w-5 h-5" />
          )}
          <span>{message.text}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
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
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            GitHub Token
          </label>
          <input
            type="password"
            value={token}
            onChange={(e) => setToken(e.target.value)}
            placeholder="ghp_..."
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            required
          />
          <p className="text-xs text-gray-500 mt-1">
            Token is stored locally in your browser
          </p>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Title <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Issue title"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Description
          </label>
          <textarea
            value={body}
            onChange={(e) => setBody(e.target.value)}
            placeholder="Issue description (supports Markdown)"
            rows={6}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Labels (comma-separated)
          </label>
          <input
            type="text"
            value={labels}
            onChange={(e) => setLabels(e.target.value)}
            placeholder="bug, enhancement, documentation"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>

        <div className="flex gap-2">
          <button
            type="submit"
            disabled={loading}
            className="flex-1 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50"
          >
            {loading ? 'Creating...' : 'Create Issue'}
          </button>
          <button
            type="button"
            onClick={() => {
              setIsOpen(false)
              setMessage(null)
            }}
            className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  )
}

export default IssueCreator


