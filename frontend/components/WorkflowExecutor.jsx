import React, { useState, useEffect } from 'react'
import { Play, RefreshCw, CheckCircle2, XCircle, FileText } from 'lucide-react'
import { apiService } from '../services/api'

const WorkflowExecutor = () => {
  const [workflows, setWorkflows] = useState([])
  const [selectedWorkflow, setSelectedWorkflow] = useState(null)
  const [executionResult, setExecutionResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [inputs, setInputs] = useState({})

  useEffect(() => {
    fetchWorkflows()
  }, [])

  const fetchWorkflows = async () => {
    try {
      const response = await apiService.getWorkflows()
      if (response.data) {
        setWorkflows(response.data)
      }
    } catch (error) {
      console.error('Error fetching workflows:', error)
    }
  }

  const executeWorkflow = async (workflowId) => {
    setLoading(true)
    setExecutionResult(null)

    try {
      const response = await apiService.executeWorkflow(workflowId, inputs)
      setExecutionResult(response.data)
    } catch (error) {
      setExecutionResult({
        status: 'error',
        error: error.response?.data?.error || 'Failed to execute workflow'
      })
    } finally {
      setLoading(false)
    }
  }

  const executeTrout = async () => {
    setLoading(true)
    setExecutionResult(null)

    try {
      const response = await apiService.executeTroutWorkflow(inputs)
      setExecutionResult(response.data)
    } catch (error) {
      setExecutionResult({
        status: 'error',
        error: error.response?.data?.error || 'Failed to execute workflow'
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <FileText className="w-6 h-6 text-primary-600" />
            <h2 className="text-2xl font-bold text-gray-800">Kestra Workflows</h2>
          </div>
          <button
            onClick={fetchWorkflows}
            className="flex items-center gap-2 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
          >
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
        </div>

        <div className="space-y-3">
          {workflows.length === 0 ? (
            <div className="text-center py-8 text-gray-500">No workflows found</div>
          ) : (
            workflows.map((workflow) => (
              <div
                key={workflow.id}
                className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-semibold text-gray-800">{workflow.id}</h3>
                    <p className="text-sm text-gray-600">{workflow.namespace}</p>
                    {workflow.description && (
                      <p className="text-sm text-gray-500 mt-1">{workflow.description}</p>
                    )}
                  </div>
                  <button
                    onClick={() => executeWorkflow(workflow.id)}
                    disabled={loading}
                    className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
                  >
                    <Play className="w-4 h-4" />
                    Execute
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Trout Workflow Quick Execute */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-xl font-bold text-gray-800 mb-4">Trout Workflow (Email → Issue)</h3>
        <p className="text-sm text-gray-600 mb-4">
          Execute the trout workflow: Read email → Process with Ollama → Create GitHub issue → Send notification
        </p>
        
        <div className="space-y-3 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Issue Title (optional)
            </label>
            <input
              type="text"
              value={inputs.title || ''}
              onChange={(e) => setInputs({ ...inputs, title: e.target.value })}
              placeholder="Auto-generated from email"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Issue Body (optional)
            </label>
            <textarea
              value={inputs.body || ''}
              onChange={(e) => setInputs({ ...inputs, body: e.target.value })}
              placeholder="Issue description"
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg"
            />
          </div>
        </div>

        <button
          onClick={executeTrout}
          disabled={loading}
          className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
        >
          {loading ? (
            <>
              <RefreshCw className="w-4 h-4 animate-spin" />
              Executing...
            </>
          ) : (
            <>
              <Play className="w-4 h-4" />
              Execute Trout Workflow
            </>
          )}
        </button>
      </div>

      {/* Execution Result */}
      {executionResult && (
        <div className={`bg-white rounded-lg shadow-md p-6 ${
          executionResult.status === 'success' ? 'border-green-300' : 'border-red-300'
        } border-2`}>
          <div className="flex items-center gap-2 mb-4">
            {executionResult.status === 'success' ? (
              <CheckCircle2 className="w-6 h-6 text-green-500" />
            ) : (
              <XCircle className="w-6 h-6 text-red-500" />
            )}
            <h3 className="text-xl font-bold text-gray-800">
              Execution Result: {executionResult.status}
            </h3>
          </div>

          {executionResult.error && (
            <div className="mb-4 p-3 bg-red-100 text-red-800 rounded-lg">
              {executionResult.error}
            </div>
          )}

          {executionResult.results && (
            <div className="space-y-2">
              <h4 className="font-semibold">Task Results:</h4>
              {executionResult.results.map((result, idx) => (
                <div key={idx} className="p-3 bg-gray-50 rounded-lg">
                  <div className="font-medium">{result.task_id}</div>
                  <div className="text-sm text-gray-600">{result.type}</div>
                  <pre className="text-xs mt-2 bg-white p-2 rounded overflow-auto">
                    {JSON.stringify(result.result, null, 2)}
                  </pre>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default WorkflowExecutor


