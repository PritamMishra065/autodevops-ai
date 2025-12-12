import React from 'react'
import { Play, CheckCircle2, XCircle, Clock } from 'lucide-react'

const AgentCard = ({ agent, onRun }) => {
  const getStatusIcon = (status) => {
    switch (status) {
      case 'success':
        return <CheckCircle2 className="w-5 h-5 text-green-500" />
      case 'error':
        return <XCircle className="w-5 h-5 text-red-500" />
      case 'running':
        return <Clock className="w-5 h-5 text-yellow-500 animate-spin" />
      default:
        return <Clock className="w-5 h-5 text-gray-400" />
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl font-semibold text-gray-800 capitalize">
          {agent.name}
        </h3>
        {getStatusIcon(agent.status)}
      </div>
      
      <p className="text-gray-600 text-sm mb-4">
        {agent.description || 'AI-powered development agent'}
      </p>

      <div className="flex items-center justify-between">
        <div className="text-sm text-gray-500">
          Last run: {agent.lastRun || 'Never'}
        </div>
        <button
          onClick={() => onRun(agent.name)}
          className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
        >
          <Play className="w-4 h-4" />
          Run
        </button>
      </div>
    </div>
  )
}

export default AgentCard


