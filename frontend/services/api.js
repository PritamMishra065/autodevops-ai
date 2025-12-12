import axios from 'axios'

// Use proxy in development, or full URL in production
const API_BASE_URL = import.meta.env.VITE_API_URL || (import.meta.env.DEV ? '/api' : 'http://127.0.0.1:8000/api')

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add error interceptor for debugging
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

export const apiService = {
  // Health check
  getHealth: () => {
    const baseUrl = import.meta.env.DEV ? '' : 'http://127.0.0.1:8000'
    return axios.get(`${baseUrl}/`)
  },

  // Agents
  getAgents: () => api.get('/agents'),
  runAgent: (agentName, params) => api.post(`/agents/${agentName}`, params),

  // Storage endpoints
  getActions: () => api.get('/actions'),
  addAction: (action) => api.post('/actions', action),

  getLogs: () => api.get('/logs'),
  addLog: (log) => api.post('/logs', log),

  getModels: () => api.get('/models'),
  addModel: (model) => api.post('/models', model),

  getReviews: () => api.get('/reviews'),
  addReview: (review) => api.post('/reviews', review),

  // Services
  getGithubInfo: (repo, token) => api.post('/github/info', { repo, token }),
  deployToVercel: (projectName, token) => api.post('/vercel/deploy', { projectName, token }),

  // GitHub PR and Issues
  getPullRequests: (repo, token, state) => api.post('/github/pull-requests', { repo, token, state }),
  getPullRequest: (repo, prNumber, token) => api.get(`/github/pull-request/${prNumber}?repo=${repo}&token=${token}`),
  getIssues: (repo, token, state) => api.post('/github/issues', { repo, token, state }),
  createIssue: (repo, title, body, token, labels) => api.post('/github/issues/create', { repo, title, body, token, labels }),

  // Autonomous DevOps Endpoints
  generateFeature: (feature) => api.post('/feature', { feature }),
  kestraMonitor: () => api.post('/agent/kestra', { command: 'monitor' }),
  kestraCommand: (action, data) => api.post('/agent/kestra', { action, ...data }),
  oumiTrain: (modelName) => api.post('/oumi/train', { model_name: modelName }),
  oumiEvaluate: (modelName) => api.post('/oumi/evaluate', { model_name: modelName }),
  coderabbitReview: (prNumber, repo) => api.post('/coderabbit/review', { pr_number: prNumber, repo }),
  clineFix: (context) => api.post('/cline/fix', { context }),
  clineRefactor: (context) => api.post('/cline/refactor', { context }),

  // Kestra Workflows
  getWorkflows: () => api.get('/workflows'),
  executeWorkflow: (workflowId, inputs) => api.post(`/workflows/${workflowId}/execute`, { inputs }),
  executeTroutWorkflow: (inputs) => api.post('/workflows/trout/execute', { inputs }),
}

export default api


