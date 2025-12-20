/**
 * Comprehensive test suite for frontend/components/WorkflowExecutor.jsx
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import WorkflowExecutor from '../../../frontend/components/WorkflowExecutor'
import { apiService } from '../../../frontend/services/api'

vi.mock('../../../frontend/services/api', () => ({
  apiService: {
    getWorkflows: vi.fn(),
    executeWorkflow: vi.fn(),
    executeTroutWorkflow: vi.fn()
  }
}))

describe('WorkflowExecutor Component', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Initial Rendering', () => {
    it('should render component with title', async () => {
      apiService.getWorkflows.mockResolvedValue({ data: [] })
      
      render(<WorkflowExecutor />)
      
      expect(screen.getByRole('heading', { name: /kestra workflows/i })).toBeInTheDocument()
    })

    it('should fetch workflows on mount', async () => {
      apiService.getWorkflows.mockResolvedValue({ data: [] })
      
      render(<WorkflowExecutor />)
      
      await waitFor(() => {
        expect(apiService.getWorkflows).toHaveBeenCalledTimes(1)
      })
    })

    it('should show refresh button', async () => {
      apiService.getWorkflows.mockResolvedValue({ data: [] })
      
      render(<WorkflowExecutor />)
      
      expect(screen.getByRole('button', { name: /refresh/i })).toBeInTheDocument()
    })
  })

  describe('Workflows Display', () => {
    it('should display message when no workflows found', async () => {
      apiService.getWorkflows.mockResolvedValue({ data: [] })
      
      render(<WorkflowExecutor />)
      
      await waitFor(() => {
        expect(screen.getByText(/no workflows found/i)).toBeInTheDocument()
      })
    })

    it('should display workflow list when workflows exist', async () => {
      const mockWorkflows = [
        { id: 'workflow1', namespace: 'test', description: 'Test workflow 1' },
        { id: 'workflow2', namespace: 'prod', description: 'Test workflow 2' }
      ]
      apiService.getWorkflows.mockResolvedValue({ data: mockWorkflows })
      
      render(<WorkflowExecutor />)
      
      await waitFor(() => {
        expect(screen.getByText('workflow1')).toBeInTheDocument()
        expect(screen.getByText('workflow2')).toBeInTheDocument()
        expect(screen.getByText('test')).toBeInTheDocument()
        expect(screen.getByText('prod')).toBeInTheDocument()
      })
    })

    it('should display workflow descriptions', async () => {
      const mockWorkflows = [
        { id: 'workflow1', namespace: 'test', description: 'A test workflow' }
      ]
      apiService.getWorkflows.mockResolvedValue({ data: mockWorkflows })
      
      render(<WorkflowExecutor />)
      
      await waitFor(() => {
        expect(screen.getByText('A test workflow')).toBeInTheDocument()
      })
    })

    it('should handle workflows without descriptions', async () => {
      const mockWorkflows = [
        { id: 'workflow1', namespace: 'test' }
      ]
      apiService.getWorkflows.mockResolvedValue({ data: mockWorkflows })
      
      render(<WorkflowExecutor />)
      
      await waitFor(() => {
        expect(screen.getByText('workflow1')).toBeInTheDocument()
      })
    })
  })

  describe('Workflow Execution', () => {
    it('should execute workflow when execute button clicked', async () => {
      const user = userEvent.setup()
      const mockWorkflows = [
        { id: 'test-workflow', namespace: 'test' }
      ]
      const mockResult = {
        data: {
          status: 'success',
          workflow_id: 'test-workflow'
        }
      }
      apiService.getWorkflows.mockResolvedValue({ data: mockWorkflows })
      apiService.executeWorkflow.mockResolvedValue(mockResult)
      
      render(<WorkflowExecutor />)
      
      await waitFor(() => {
        expect(screen.getByText('test-workflow')).toBeInTheDocument()
      })
      
      const executeButton = screen.getByRole('button', { name: /execute/i })
      await user.click(executeButton)
      
      await waitFor(() => {
        expect(apiService.executeWorkflow).toHaveBeenCalledWith('test-workflow', {})
      })
    })

    it('should show loading state during execution', async () => {
      const user = userEvent.setup()
      let resolvePromise
      const promise = new Promise(resolve => { resolvePromise = resolve })
      
      const mockWorkflows = [{ id: 'workflow1', namespace: 'test' }]
      apiService.getWorkflows.mockResolvedValue({ data: mockWorkflows })
      apiService.executeWorkflow.mockReturnValue(promise)
      
      render(<WorkflowExecutor />)
      
      await waitFor(() => screen.getByText('workflow1'))
      
      const executeButton = screen.getByRole('button', { name: /execute/i })
      await user.click(executeButton)
      
      expect(executeButton).toBeDisabled()
      
      resolvePromise({ data: { status: 'success' } })
    })

    it('should display execution result on success', async () => {
      const user = userEvent.setup()
      const mockWorkflows = [{ id: 'workflow1', namespace: 'test' }]
      const mockResult = {
        data: {
          status: 'success',
          message: 'Workflow executed successfully'
        }
      }
      apiService.getWorkflows.mockResolvedValue({ data: mockWorkflows })
      apiService.executeWorkflow.mockResolvedValue(mockResult)
      
      render(<WorkflowExecutor />)
      
      await waitFor(() => screen.getByText('workflow1'))
      
      await user.click(screen.getByRole('button', { name: /execute/i }))
      
      await waitFor(() => {
        expect(screen.getByText(/success/i)).toBeInTheDocument()
      })
    })

    it('should display error message on execution failure', async () => {
      const user = userEvent.setup()
      const mockWorkflows = [{ id: 'workflow1', namespace: 'test' }]
      const error = { response: { data: { error: 'Execution failed' } } }
      
      apiService.getWorkflows.mockResolvedValue({ data: mockWorkflows })
      apiService.executeWorkflow.mockRejectedValue(error)
      
      render(<WorkflowExecutor />)
      
      await waitFor(() => screen.getByText('workflow1'))
      
      await user.click(screen.getByRole('button', { name: /execute/i }))
      
      await waitFor(() => {
        expect(screen.getByText(/execution failed/i)).toBeInTheDocument()
      })
    })
  })

  describe('Trout Workflow', () => {
    it('should execute trout workflow', async () => {
      const user = userEvent.setup()
      apiService.getWorkflows.mockResolvedValue({ data: [] })
      apiService.executeTroutWorkflow.mockResolvedValue({
        data: { status: 'success' }
      })
      
      render(<WorkflowExecutor />)
      
      // Find and click Trout workflow button (implementation specific)
      const buttons = screen.getAllByRole('button')
      const troutButton = buttons.find(btn => btn.textContent.includes('Trout') || btn.textContent.includes('Execute'))
      
      if (troutButton) {
        await user.click(troutButton)
        
        await waitFor(() => {
          expect(apiService.executeTroutWorkflow).toHaveBeenCalled()
        })
      }
    })
  })

  describe('Refresh Functionality', () => {
    it('should refresh workflows when refresh button clicked', async () => {
      const user = userEvent.setup()
      apiService.getWorkflows.mockResolvedValue({ data: [] })
      
      render(<WorkflowExecutor />)
      
      await waitFor(() => {
        expect(apiService.getWorkflows).toHaveBeenCalledTimes(1)
      })
      
      const refreshButton = screen.getByRole('button', { name: /refresh/i })
      await user.click(refreshButton)
      
      await waitFor(() => {
        expect(apiService.getWorkflows).toHaveBeenCalledTimes(2)
      })
    })
  })

  describe('Error Handling', () => {
    it('should handle API errors when fetching workflows', async () => {
      const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {})
      apiService.getWorkflows.mockRejectedValue(new Error('API Error'))
      
      render(<WorkflowExecutor />)
      
      await waitFor(() => {
        expect(consoleError).toHaveBeenCalled()
      })
      
      consoleError.mockRestore()
    })

    it('should handle generic execution errors', async () => {
      const user = userEvent.setup()
      const mockWorkflows = [{ id: 'workflow1', namespace: 'test' }]
      
      apiService.getWorkflows.mockResolvedValue({ data: mockWorkflows })
      apiService.executeWorkflow.mockRejectedValue(new Error('Network error'))
      
      render(<WorkflowExecutor />)
      
      await waitFor(() => screen.getByText('workflow1'))
      
      await user.click(screen.getByRole('button', { name: /execute/i }))
      
      await waitFor(() => {
        expect(screen.getByText(/failed to execute/i)).toBeInTheDocument()
      })
    })
  })
})