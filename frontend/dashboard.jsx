import React, { useState, useEffect } from 'react'
import { 
  Activity, 
  FileText, 
  Database, 
  Star, 
  Settings,
  Zap,
  TrendingUp,
  GitPullRequest,
  AlertCircle
} from 'lucide-react'
import AgentCard from './components/AgentCard'
import LogViewer from './components/LogViewer'
import ActionsList from './components/ActionsList'
import ModelsList from './components/ModelsList'
import ReviewsList from './components/ReviewsList'
import PullRequestsList from './components/PullRequestsList'
import IssueCreator from './components/IssueCreator'
import IssuesList from './components/IssuesList'
import KestraMonitor from './components/KestraMonitor'
import FeatureGenerator from './components/FeatureGenerator'
import WorkflowExecutor from './components/WorkflowExecutor'
import { apiService } from './services/api'

const agents = [
  {
    name: 'Cline',
    description: 'AI coding assistant for development tasks',
    status: 'idle',
    lastRun: null,
  },
  {
    name: 'CodeRabbit',
    description: 'Automated code review and quality analysis',
    status: 'idle',
    lastRun: null,
  },
  {
    name: 'Kestra',
    description: 'Workflow orchestration and automation',
    status: 'idle',
    lastRun: null,
  },
  {
    name: 'Oumi',
    description: 'Multi-agent coordination and management',
    status: 'idle',
    lastRun: null,
  },
]

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState('overview')
  const [healthStatus, setHealthStatus] = useState('checking')
  const [stats, setStats] = useState({
    totalActions: 0,
    totalLogs: 0,
    totalReviews: 0,
    activeAgents: 0,
  })

  useEffect(() => {
    checkHealth()
    fetchStats()
    const interval = setInterval(() => {
      fetchStats()
    }, 10000)
    return () => clearInterval(interval)
  }, [])

  const checkHealth = async () => {
    try {
      const response = await apiService.getHealth()
      setHealthStatus(response.data?.status === 'ok' ? 'healthy' : 'unhealthy')
    } catch (error) {
      setHealthStatus('unhealthy')
    }
  }

  const fetchStats = async () => {
    try {
      const [actionsRes, logsRes, reviewsRes] = await Promise.all([
        apiService.getActions().catch(() => ({ data: [] })),
        apiService.getLogs().catch(() => ({ data: [] })),
        apiService.getReviews().catch(() => ({ data: [] })),
      ])

      setStats({
        totalActions: actionsRes.data?.length || 0,
        totalLogs: logsRes.data?.length || 0,
        totalReviews: reviewsRes.data?.length || 0,
        activeAgents: agents.filter(a => a.status === 'running').length,
      })
    } catch (error) {
      console.error('Error fetching stats:', error)
    }
  }

  const handleRunAgent = async (agentName) => {
    try {
      const agent = agents.find(a => a.name.toLowerCase() === agentName.toLowerCase())
      if (agent) {
        agent.status = 'running'
        setActiveTab('agents')
        
        await apiService.runAgent(agentName.toLowerCase(), {})
        
        agent.status = 'success'
        agent.lastRun = new Date().toLocaleString()
        fetchStats()
      }
    } catch (error) {
      console.error(`Error running agent ${agentName}:`, error)
      const agent = agents.find(a => a.name.toLowerCase() === agentName.toLowerCase())
      if (agent) {
        agent.status = 'error'
      }
    }
  }

  const tabs = [
    { id: 'overview', label: 'Overview', icon: Activity },
    { id: 'kestra', label: 'Kestra Monitor', icon: Settings },
    { id: 'workflows', label: 'Workflows', icon: FileText },
    { id: 'agents', label: 'Agents', icon: Zap },
    { id: 'pull-requests', label: 'Pull Requests', icon: GitPullRequest },
    { id: 'issues', label: 'Issues', icon: AlertCircle },
    { id: 'logs', label: 'Logs', icon: FileText },
    { id: 'actions', label: 'Actions', icon: TrendingUp },
    { id: 'reviews', label: 'Reviews', icon: Star },
    { id: 'models', label: 'Models', icon: Database },
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-700 rounded-lg flex items-center justify-center">
                <Settings className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  AutoDevOps AI
                </h1>
                <p className="text-sm text-gray-500">
                  Intelligent Development Automation Platform
                </p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <div
                  className={`w-3 h-3 rounded-full ${
                    healthStatus === 'healthy'
                      ? 'bg-green-500'
                      : healthStatus === 'checking'
                      ? 'bg-yellow-500 animate-pulse'
                      : 'bg-red-500'
                  }`}
                />
                <span className="text-sm text-gray-600 capitalize">
                  {healthStatus}
                </span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-1 overflow-x-auto">
            {tabs.map((tab) => {
              const Icon = tab.icon
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
                    activeTab === tab.id
                      ? 'border-primary-600 text-primary-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {tab.label}
                </button>
              )
            })}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="bg-white rounded-lg shadow-md p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">
                      Total Actions
                    </p>
                    <p className="text-3xl font-bold text-gray-900 mt-2">
                      {stats.totalActions}
                    </p>
                  </div>
                  <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
                    <TrendingUp className="w-6 h-6 text-primary-600" />
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow-md p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">
                      Total Logs
                    </p>
                    <p className="text-3xl font-bold text-gray-900 mt-2">
                      {stats.totalLogs}
                    </p>
                  </div>
                  <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                    <FileText className="w-6 h-6 text-blue-600" />
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow-md p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">
                      Code Reviews
                    </p>
                    <p className="text-3xl font-bold text-gray-900 mt-2">
                      {stats.totalReviews}
                    </p>
                  </div>
                  <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center">
                    <Star className="w-6 h-6 text-yellow-600" />
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow-md p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">
                      Active Agents
                    </p>
                    <p className="text-3xl font-bold text-gray-900 mt-2">
                      {stats.activeAgents}
                    </p>
                  </div>
                  <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                    <Zap className="w-6 h-6 text-green-600" />
                  </div>
                </div>
              </div>
            </div>

            {/* Feature Generator */}
            <div className="mb-6">
              <FeatureGenerator />
            </div>

            {/* Agents Preview */}
            <div>
              <h2 className="text-xl font-bold text-gray-800 mb-4">Agents</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {agents.map((agent) => (
                  <AgentCard
                    key={agent.name}
                    agent={agent}
                    onRun={handleRunAgent}
                  />
                ))}
              </div>
            </div>

            {/* Recent Activity */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-xl font-bold text-gray-800 mb-4">
                  Recent Actions
                </h2>
                <ActionsList />
              </div>
              <div className="bg-white rounded-lg shadow-md p-6">
                <h2 className="text-xl font-bold text-gray-800 mb-4">
                  Recent Logs
                </h2>
                <LogViewer />
              </div>
            </div>
          </div>
        )}

        {activeTab === 'kestra' && <KestraMonitor />}

        {activeTab === 'workflows' && <WorkflowExecutor />}

        {activeTab === 'agents' && (
          <div>
            <h2 className="text-2xl font-bold text-gray-800 mb-6">AI Agents</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {agents.map((agent) => (
                <AgentCard
                  key={agent.name}
                  agent={agent}
                  onRun={handleRunAgent}
                />
              ))}
            </div>
          </div>
        )}

        {activeTab === 'pull-requests' && <PullRequestsList />}
        {activeTab === 'issues' && (
          <div className="space-y-6">
            <IssueCreator onIssueCreated={(issue) => {
              console.log('Issue created:', issue)
              // Refresh issues list
              setTimeout(() => {
                window.location.reload()
              }, 1000)
            }} />
            <IssuesList />
          </div>
        )}
        {activeTab === 'logs' && <LogViewer />}
        {activeTab === 'actions' && <ActionsList />}
        {activeTab === 'reviews' && <ReviewsList />}
        {activeTab === 'models' && <ModelsList />}
      </main>
    </div>
  )
}
