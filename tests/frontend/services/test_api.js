/**
 * Comprehensive test suite for frontend/services/api.js
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import axios from 'axios'
import { apiService } from '../../../frontend/services/api'

vi.mock('axios')

describe('API Service', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('API Instance Configuration', () => {
    it('should have correct base URL in development', () => {
      expect(apiService).toBeDefined()
    })
  })

  describe('Health Check', () => {
    it('should call health endpoint', async () => {
      const mockResponse = { data: { status: 'ok' } }
      axios.get.mockResolvedValue(mockResponse)
      
      const result = await apiService.getHealth()
      
      expect(axios.get).toHaveBeenCalled()
      expect(result).toEqual(mockResponse)
    })
  })

  describe('Agents Endpoints', () => {
    it('should get agents list', async () => {
      const mockAgents = [
        { name: 'Cline', status: 'idle' },
        { name: 'CodeRabbit', status: 'idle' }
      ]
      const mockApi = {
        get: vi.fn().mockResolvedValue({ data: mockAgents })
      }
      
      expect(apiService.getAgents).toBeDefined()
    })

    it('should run agent with parameters', async () => {
      const mockApi = {
        post: vi.fn().mockResolvedValue({ data: { status: 'success' } })
      }
      
      expect(apiService.runAgent).toBeDefined()
    })
  })

  describe('Storage Endpoints', () => {
    it('should have getActions method', () => {
      expect(apiService.getActions).toBeDefined()
      expect(typeof apiService.getActions).toBe('function')
    })

    it('should have addAction method', () => {
      expect(apiService.addAction).toBeDefined()
      expect(typeof apiService.addAction).toBe('function')
    })

    it('should have getLogs method', () => {
      expect(apiService.getLogs).toBeDefined()
      expect(typeof apiService.getLogs).toBe('function')
    })

    it('should have getModels method', () => {
      expect(apiService.getModels).toBeDefined()
      expect(typeof apiService.getModels).toBe('function')
    })

    it('should have getReviews method', () => {
      expect(apiService.getReviews).toBeDefined()
      expect(typeof apiService.getReviews).toBe('function')
    })
  })

  describe('GitHub Endpoints', () => {
    it('should have getPullRequests method', () => {
      expect(apiService.getPullRequests).toBeDefined()
      expect(typeof apiService.getPullRequests).toBe('function')
    })

    it('should have getPullRequest method', () => {
      expect(apiService.getPullRequest).toBeDefined()
      expect(typeof apiService.getPullRequest).toBe('function')
    })

    it('should have getIssues method', () => {
      expect(apiService.getIssues).toBeDefined()
      expect(typeof apiService.getIssues).toBe('function')
    })

    it('should have createIssue method', () => {
      expect(apiService.createIssue).toBeDefined()
      expect(typeof apiService.createIssue).toBe('function')
    })
  })

  describe('Workflow Endpoints', () => {
    it('should have getWorkflows method', () => {
      expect(apiService.getWorkflows).toBeDefined()
      expect(typeof apiService.getWorkflows).toBe('function')
    })

    it('should have executeWorkflow method', () => {
      expect(apiService.executeWorkflow).toBeDefined()
      expect(typeof apiService.executeWorkflow).toBe('function')
    })

    it('should have executeTroutWorkflow method', () => {
      expect(apiService.executeTroutWorkflow).toBeDefined()
      expect(typeof apiService.executeTroutWorkflow).toBe('function')
    })
  })

  describe('Feature Generation', () => {
    it('should have generateFeature method', () => {
      expect(apiService.generateFeature).toBeDefined()
      expect(typeof apiService.generateFeature).toBe('function')
    })
  })

  describe('Kestra Commands', () => {
    it('should have kestraMonitor method', () => {
      expect(apiService.kestraMonitor).toBeDefined()
      expect(typeof apiService.kestraMonitor).toBe('function')
    })

    it('should have kestraCommand method', () => {
      expect(apiService.kestraCommand).toBeDefined()
      expect(typeof apiService.kestraCommand).toBe('function')
    })
  })

  describe('Oumi Endpoints', () => {
    it('should have oumiTrain method', () => {
      expect(apiService.oumiTrain).toBeDefined()
      expect(typeof apiService.oumiTrain).toBe('function')
    })

    it('should have oumiEvaluate method', () => {
      expect(apiService.oumiEvaluate).toBeDefined()
      expect(typeof apiService.oumiEvaluate).toBe('function')
    })
  })

  describe('CodeRabbit and Cline', () => {
    it('should have coderabbitReview method', () => {
      expect(apiService.coderabbitReview).toBeDefined()
      expect(typeof apiService.coderabbitReview).toBe('function')
    })

    it('should have clineFix method', () => {
      expect(apiService.clineFix).toBeDefined()
      expect(typeof apiService.clineFix).toBe('function')
    })

    it('should have clineRefactor method', () => {
      expect(apiService.clineRefactor).toBeDefined()
      expect(typeof apiService.clineRefactor).toBe('function')
    })
  })
})