/**
 * Comprehensive test suite for frontend/components/IssueCreator.jsx
 * 
 * Tests cover:
 * - Component rendering
 * - Form validation
 * - User interactions
 * - API calls and error handling
 * - State management
 * - Edge cases
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import IssueCreator from '../../../frontend/components/IssueCreator'
import { apiService } from '../../../frontend/services/api'

// Mock the API service
vi.mock('../../../frontend/services/api', () => ({
  apiService: {
    createIssue: vi.fn()
  }
}))

describe('IssueCreator Component', () => {
  beforeEach(() => {
    // Clear all mocks before each test
    vi.clearAllMocks()
    localStorage.clear()
  })

  describe('Initial Rendering', () => {
    it('should render create button when closed', () => {
      render(<IssueCreator />)
      
      const button = screen.getByRole('button', { name: /create issue/i })
      expect(button).toBeInTheDocument()
      expect(button).toHaveTextContent('Create Issue')
    })

    it('should show form when create button is clicked', async () => {
      const user = userEvent.setup()
      render(<IssueCreator />)
      
      const button = screen.getByRole('button', { name: /create issue/i })
      await user.click(button)
      
      expect(screen.getByRole('heading', { name: /create github issue/i })).toBeInTheDocument()
      expect(screen.getByLabelText(/repository/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/github token/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/title/i)).toBeInTheDocument()
    })

    it('should have default repository value', async () => {
      const user = userEvent.setup()
      render(<IssueCreator />)
      
      await user.click(screen.getByRole('button', { name: /create issue/i }))
      
      const repoInput = screen.getByLabelText(/repository/i)
      expect(repoInput).toHaveValue('PritamMishra065/autodevops-ai')
    })

    it('should load token from localStorage on mount', async () => {
      const savedToken = 'ghp_saved_token_123'
      localStorage.setItem('github_token', savedToken)
      
      const user = userEvent.setup()
      render(<IssueCreator />)
      
      await user.click(screen.getByRole('button', { name: /create issue/i }))
      
      const tokenInput = screen.getByLabelText(/github token/i)
      expect(tokenInput).toHaveValue(savedToken)
    })
  })

  describe('Form Fields', () => {
    beforeEach(async () => {
      const user = userEvent.setup()
      render(<IssueCreator />)
      await user.click(screen.getByRole('button', { name: /create issue/i }))
    })

    it('should render all required form fields', () => {
      expect(screen.getByLabelText(/repository/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/github token/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/title/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/description/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/labels/i)).toBeInTheDocument()
    })

    it('should allow typing in repository field', async () => {
      const user = userEvent.setup()
      const repoInput = screen.getByLabelText(/repository/i)
      
      await user.clear(repoInput)
      await user.type(repoInput, 'test/repo')
      
      expect(repoInput).toHaveValue('test/repo')
    })

    it('should allow typing in token field', async () => {
      const user = userEvent.setup()
      const tokenInput = screen.getByLabelText(/github token/i)
      
      await user.type(tokenInput, 'ghp_test123')
      
      expect(tokenInput).toHaveValue('ghp_test123')
    })

    it('should allow typing in title field', async () => {
      const user = userEvent.setup()
      const titleInput = screen.getByLabelText(/title/i)
      
      await user.type(titleInput, 'Test Issue Title')
      
      expect(titleInput).toHaveValue('Test Issue Title')
    })

    it('should allow typing in description textarea', async () => {
      const user = userEvent.setup()
      const descriptionInput = screen.getByLabelText(/description/i)
      
      await user.type(descriptionInput, 'This is a test description')
      
      expect(descriptionInput).toHaveValue('This is a test description')
    })

    it('should allow typing in labels field', async () => {
      const user = userEvent.setup()
      const labelsInput = screen.getByLabelText(/labels/i)
      
      await user.type(labelsInput, 'bug, enhancement')
      
      expect(labelsInput).toHaveValue('bug, enhancement')
    })

    it('should show token input as password type', () => {
      const tokenInput = screen.getByLabelText(/github token/i)
      expect(tokenInput).toHaveAttribute('type', 'password')
    })

    it('should show placeholder text for all fields', () => {
      expect(screen.getByPlaceholderText('owner/repo')).toBeInTheDocument()
      expect(screen.getByPlaceholderText(/ghp_/)).toBeInTheDocument()
      expect(screen.getByPlaceholderText('Issue title')).toBeInTheDocument()
      expect(screen.getByPlaceholderText(/supports Markdown/i)).toBeInTheDocument()
      expect(screen.getByPlaceholderText(/bug, enhancement/i)).toBeInTheDocument()
    })
  })

  describe('Form Validation', () => {
    it('should show error when submitting without title', async () => {
      const user = userEvent.setup()
      render(<IssueCreator />)
      
      await user.click(screen.getByRole('button', { name: /create issue/i }))
      
      const tokenInput = screen.getByLabelText(/github token/i)
      await user.type(tokenInput, 'ghp_test')
      
      const submitButton = screen.getByRole('button', { name: /^create issue$/i })
      await user.click(submitButton)
      
      await waitFor(() => {
        expect(screen.getByText(/title is required/i)).toBeInTheDocument()
      })
    })

    it('should show error when submitting without token', async () => {
      const user = userEvent.setup()
      render(<IssueCreator />)
      
      await user.click(screen.getByRole('button', { name: /create issue/i }))
      
      const titleInput = screen.getByLabelText(/title/i)
      await user.type(titleInput, 'Test Title')
      
      const submitButton = screen.getByRole('button', { name: /^create issue$/i })
      await user.click(submitButton)
      
      await waitFor(() => {
        expect(screen.getByText(/github token is required/i)).toBeInTheDocument()
      })
    })

    it('should not show error when title has only whitespace', async () => {
      const user = userEvent.setup()
      render(<IssueCreator />)
      
      await user.click(screen.getByRole('button', { name: /create issue/i }))
      
      const titleInput = screen.getByLabelText(/title/i)
      const tokenInput = screen.getByLabelText(/github token/i)
      
      await user.type(titleInput, '   ')
      await user.type(tokenInput, 'ghp_test')
      
      const submitButton = screen.getByRole('button', { name: /^create issue$/i })
      await user.click(submitButton)
      
      await waitFor(() => {
        expect(screen.getByText(/title is required/i)).toBeInTheDocument()
      })
    })
  })

  describe('Issue Creation - Success', () => {
    it('should successfully create issue with valid data', async () => {
      const user = userEvent.setup()
      const mockResponse = {
        data: {
          success: true,
          issue: {
            number: 42,
            title: 'Test Issue',
            url: 'https://github.com/test/repo/issues/42'
          }
        }
      }
      apiService.createIssue.mockResolvedValue(mockResponse)
      
      render(<IssueCreator />)
      await user.click(screen.getByRole('button', { name: /create issue/i }))
      
      await user.type(screen.getByLabelText(/title/i), 'Test Issue')
      await user.type(screen.getByLabelText(/github token/i), 'ghp_test')
      
      const submitButton = screen.getByRole('button', { name: /^create issue$/i })
      await user.click(submitButton)
      
      await waitFor(() => {
        expect(screen.getByText(/issue #42 created successfully/i)).toBeInTheDocument()
      })
      
      expect(apiService.createIssue).toHaveBeenCalledWith(
        'PritamMishra065/autodevops-ai',
        'Test Issue',
        '',
        'ghp_test',
        []
      )
    })

    it('should create issue with all fields populated', async () => {
      const user = userEvent.setup()
      const mockResponse = {
        data: {
          success: true,
          issue: { number: 1 }
        }
      }
      apiService.createIssue.mockResolvedValue(mockResponse)
      
      render(<IssueCreator />)
      await user.click(screen.getByRole('button', { name: /create issue/i }))
      
      await user.clear(screen.getByLabelText(/repository/i))
      await user.type(screen.getByLabelText(/repository/i), 'owner/repo')
      await user.type(screen.getByLabelText(/github token/i), 'ghp_token')
      await user.type(screen.getByLabelText(/title/i), 'Bug Report')
      await user.type(screen.getByLabelText(/description/i), 'Bug description')
      await user.type(screen.getByLabelText(/labels/i), 'bug, critical')
      
      const submitButton = screen.getByRole('button', { name: /^create issue$/i })
      await user.click(submitButton)
      
      await waitFor(() => {
        expect(apiService.createIssue).toHaveBeenCalledWith(
          'owner/repo',
          'Bug Report',
          'Bug description',
          'ghp_token',
          ['bug', 'critical']
        )
      })
    })

    it('should clear form after successful creation', async () => {
      const user = userEvent.setup()
      const mockResponse = {
        data: {
          success: true,
          issue: { number: 1 }
        }
      }
      apiService.createIssue.mockResolvedValue(mockResponse)
      
      render(<IssueCreator />)
      await user.click(screen.getByRole('button', { name: /create issue/i }))
      
      await user.type(screen.getByLabelText(/title/i), 'Test')
      await user.type(screen.getByLabelText(/description/i), 'Description')
      await user.type(screen.getByLabelText(/labels/i), 'test')
      await user.type(screen.getByLabelText(/github token/i), 'ghp_test')
      
      await user.click(screen.getByRole('button', { name: /^create issue$/i }))
      
      await waitFor(() => {
        expect(screen.getByLabelText(/title/i)).toHaveValue('')
        expect(screen.getByLabelText(/description/i)).toHaveValue('')
        expect(screen.getByLabelText(/labels/i)).toHaveValue('')
      })
    })

    it('should close modal after successful creation', async () => {
      const user = userEvent.setup()
      vi.useFakeTimers()
      
      const mockResponse = {
        data: {
          success: true,
          issue: { number: 1 }
        }
      }
      apiService.createIssue.mockResolvedValue(mockResponse)
      
      render(<IssueCreator />)
      await user.click(screen.getByRole('button', { name: /create issue/i }))
      
      await user.type(screen.getByLabelText(/title/i), 'Test')
      await user.type(screen.getByLabelText(/github token/i), 'ghp_test')
      await user.click(screen.getByRole('button', { name: /^create issue$/i }))
      
      await waitFor(() => {
        expect(screen.getByText(/created successfully/i)).toBeInTheDocument()
      })
      
      // Fast-forward time to trigger modal close
      vi.advanceTimersByTime(2000)
      
      await waitFor(() => {
        expect(screen.queryByRole('heading', { name: /create github issue/i })).not.toBeInTheDocument()
      })
      
      vi.useRealTimers()
    })

    it('should call onIssueCreated callback when provided', async () => {
      const user = userEvent.setup()
      const onIssueCreated = vi.fn()
      const mockIssue = { number: 42, title: 'Test' }
      const mockResponse = {
        data: {
          success: true,
          issue: mockIssue
        }
      }
      apiService.createIssue.mockResolvedValue(mockResponse)
      
      render(<IssueCreator onIssueCreated={onIssueCreated} />)
      await user.click(screen.getByRole('button', { name: /create issue/i }))
      
      await user.type(screen.getByLabelText(/title/i), 'Test')
      await user.type(screen.getByLabelText(/github token/i), 'ghp_test')
      await user.click(screen.getByRole('button', { name: /^create issue$/i }))
      
      await waitFor(() => {
        expect(onIssueCreated).toHaveBeenCalledWith(mockIssue)
      })
    })
  })

  describe('Issue Creation - Errors', () => {
    it('should show error message when API call fails', async () => {
      const user = userEvent.setup()
      const errorMessage = 'Failed to create issue'
      apiService.createIssue.mockResolvedValue({
        data: {
          success: false,
          error: errorMessage
        }
      })
      
      render(<IssueCreator />)
      await user.click(screen.getByRole('button', { name: /create issue/i }))
      
      await user.type(screen.getByLabelText(/title/i), 'Test')
      await user.type(screen.getByLabelText(/github token/i), 'ghp_test')
      await user.click(screen.getByRole('button', { name: /^create issue$/i }))
      
      await waitFor(() => {
        expect(screen.getByText(errorMessage)).toBeInTheDocument()
      })
    })

    it('should show error message from response data', async () => {
      const user = userEvent.setup()
      const error = { response: { data: { error: 'Invalid token' } } }
      apiService.createIssue.mockRejectedValue(error)
      
      render(<IssueCreator />)
      await user.click(screen.getByRole('button', { name: /create issue/i }))
      
      await user.type(screen.getByLabelText(/title/i), 'Test')
      await user.type(screen.getByLabelText(/github token/i), 'ghp_invalid')
      await user.click(screen.getByRole('button', { name: /^create issue$/i }))
      
      await waitFor(() => {
        expect(screen.getByText('Invalid token')).toBeInTheDocument()
      })
    })

    it('should show generic error when no specific error message', async () => {
      const user = userEvent.setup()
      apiService.createIssue.mockRejectedValue(new Error('Network error'))
      
      render(<IssueCreator />)
      await user.click(screen.getByRole('button', { name: /create issue/i }))
      
      await user.type(screen.getByLabelText(/title/i), 'Test')
      await user.type(screen.getByLabelText(/github token/i), 'ghp_test')
      await user.click(screen.getByRole('button', { name: /^create issue$/i }))
      
      await waitFor(() => {
        expect(screen.getByText(/failed to create issue/i)).toBeInTheDocument()
      })
    })
  })

  describe('Labels Processing', () => {
    it('should parse comma-separated labels correctly', async () => {
      const user = userEvent.setup()
      const mockResponse = {
        data: { success: true, issue: { number: 1 } }
      }
      apiService.createIssue.mockResolvedValue(mockResponse)
      
      render(<IssueCreator />)
      await user.click(screen.getByRole('button', { name: /create issue/i }))
      
      await user.type(screen.getByLabelText(/title/i), 'Test')
      await user.type(screen.getByLabelText(/github token/i), 'ghp_test')
      await user.type(screen.getByLabelText(/labels/i), 'bug, enhancement, documentation')
      await user.click(screen.getByRole('button', { name: /^create issue$/i }))
      
      await waitFor(() => {
        expect(apiService.createIssue).toHaveBeenCalledWith(
          expect.any(String),
          expect.any(String),
          expect.any(String),
          expect.any(String),
          ['bug', 'enhancement', 'documentation']
        )
      })
    })

    it('should trim whitespace from labels', async () => {
      const user = userEvent.setup()
      const mockResponse = {
        data: { success: true, issue: { number: 1 } }
      }
      apiService.createIssue.mockResolvedValue(mockResponse)
      
      render(<IssueCreator />)
      await user.click(screen.getByRole('button', { name: /create issue/i }))
      
      await user.type(screen.getByLabelText(/title/i), 'Test')
      await user.type(screen.getByLabelText(/github token/i), 'ghp_test')
      await user.type(screen.getByLabelText(/labels/i), '  bug  ,  test  ')
      await user.click(screen.getByRole('button', { name: /^create issue$/i }))
      
      await waitFor(() => {
        const call = apiService.createIssue.mock.calls[0]
        expect(call[4]).toEqual(['bug', 'test'])
      })
    })

    it('should filter out empty labels', async () => {
      const user = userEvent.setup()
      const mockResponse = {
        data: { success: true, issue: { number: 1 } }
      }
      apiService.createIssue.mockResolvedValue(mockResponse)
      
      render(<IssueCreator />)
      await user.click(screen.getByRole('button', { name: /create issue/i }))
      
      await user.type(screen.getByLabelText(/title/i), 'Test')
      await user.type(screen.getByLabelText(/github token/i), 'ghp_test')
      await user.type(screen.getByLabelText(/labels/i), 'bug, , test, ')
      await user.click(screen.getByRole('button', { name: /^create issue$/i }))
      
      await waitFor(() => {
        const call = apiService.createIssue.mock.calls[0]
        expect(call[4]).toEqual(['bug', 'test'])
      })
    })

    it('should handle empty labels string', async () => {
      const user = userEvent.setup()
      const mockResponse = {
        data: { success: true, issue: { number: 1 } }
      }
      apiService.createIssue.mockResolvedValue(mockResponse)
      
      render(<IssueCreator />)
      await user.click(screen.getByRole('button', { name: /create issue/i }))
      
      await user.type(screen.getByLabelText(/title/i), 'Test')
      await user.type(screen.getByLabelText(/github token/i), 'ghp_test')
      await user.click(screen.getByRole('button', { name: /^create issue$/i }))
      
      await waitFor(() => {
        const call = apiService.createIssue.mock.calls[0]
        expect(call[4]).toEqual([])
      })
    })
  })

  describe('UI State Management', () => {
    it('should show loading state during submission', async () => {
      const user = userEvent.setup()
      let resolvePromise
      const promise = new Promise((resolve) => {
        resolvePromise = resolve
      })
      apiService.createIssue.mockReturnValue(promise)
      
      render(<IssueCreator />)
      await user.click(screen.getByRole('button', { name: /create issue/i }))
      
      await user.type(screen.getByLabelText(/title/i), 'Test')
      await user.type(screen.getByLabelText(/github token/i), 'ghp_test')
      await user.click(screen.getByRole('button', { name: /^create issue$/i }))
      
      await waitFor(() => {
        expect(screen.getByText('Creating...')).toBeInTheDocument()
      })
      
      resolvePromise({ data: { success: true, issue: { number: 1 } } })
    })

    it('should disable submit button during submission', async () => {
      const user = userEvent.setup()
      let resolvePromise
      const promise = new Promise((resolve) => {
        resolvePromise = resolve
      })
      apiService.createIssue.mockReturnValue(promise)
      
      render(<IssueCreator />)
      await user.click(screen.getByRole('button', { name: /create issue/i }))
      
      await user.type(screen.getByLabelText(/title/i), 'Test')
      await user.type(screen.getByLabelText(/github token/i), 'ghp_test')
      
      const submitButton = screen.getByRole('button', { name: /^create issue$/i })
      await user.click(submitButton)
      
      await waitFor(() => {
        expect(submitButton).toBeDisabled()
      })
      
      resolvePromise({ data: { success: true, issue: { number: 1 } } })
    })
  })

  describe('Modal Close Functionality', () => {
    it('should close modal when X button is clicked', async () => {
      const user = userEvent.setup()
      render(<IssueCreator />)
      
      await user.click(screen.getByRole('button', { name: /create issue/i }))
      expect(screen.getByRole('heading', { name: /create github issue/i })).toBeInTheDocument()
      
      const closeButton = screen.getAllByRole('button').find(btn => btn.querySelector('svg'))
      await user.click(closeButton)
      
      expect(screen.queryByRole('heading', { name: /create github issue/i })).not.toBeInTheDocument()
    })

    it('should close modal when Cancel button is clicked', async () => {
      const user = userEvent.setup()
      render(<IssueCreator />)
      
      await user.click(screen.getByRole('button', { name: /create issue/i }))
      
      const cancelButton = screen.getByRole('button', { name: /cancel/i })
      await user.click(cancelButton)
      
      expect(screen.queryByRole('heading', { name: /create github issue/i })).not.toBeInTheDocument()
    })

    it('should clear error message when closing modal', async () => {
      const user = userEvent.setup()
      render(<IssueCreator />)
      
      await user.click(screen.getByRole('button', { name: /create issue/i }))
      
      // Trigger validation error
      await user.click(screen.getByRole('button', { name: /^create issue$/i }))
      await waitFor(() => {
        expect(screen.getByText(/title is required/i)).toBeInTheDocument()
      })
      
      // Close and reopen
      const closeButton = screen.getAllByRole('button').find(btn => btn.querySelector('svg'))
      await user.click(closeButton)
      await user.click(screen.getByRole('button', { name: /create issue/i }))
      
      expect(screen.queryByText(/title is required/i)).not.toBeInTheDocument()
    })
  })

  describe('Edge Cases', () => {
    it('should handle very long title', async () => {
      const user = userEvent.setup()
      const longTitle = 'A'.repeat(500)
      const mockResponse = {
        data: { success: true, issue: { number: 1 } }
      }
      apiService.createIssue.mockResolvedValue(mockResponse)
      
      render(<IssueCreator />)
      await user.click(screen.getByRole('button', { name: /create issue/i }))
      
      await user.type(screen.getByLabelText(/title/i), longTitle)
      await user.type(screen.getByLabelText(/github token/i), 'ghp_test')
      await user.click(screen.getByRole('button', { name: /^create issue$/i }))
      
      await waitFor(() => {
        expect(apiService.createIssue).toHaveBeenCalled()
      })
    })

    it('should handle special characters in title', async () => {
      const user = userEvent.setup()
      const specialTitle = 'Bug: [Feature] Test & Validation <component>'
      const mockResponse = {
        data: { success: true, issue: { number: 1 } }
      }
      apiService.createIssue.mockResolvedValue(mockResponse)
      
      render(<IssueCreator />)
      await user.click(screen.getByRole('button', { name: /create issue/i }))
      
      await user.type(screen.getByLabelText(/title/i), specialTitle)
      await user.type(screen.getByLabelText(/github token/i), 'ghp_test')
      await user.click(screen.getByRole('button', { name: /^create issue$/i }))
      
      await waitFor(() => {
        const call = apiService.createIssue.mock.calls[0]
        expect(call[1]).toBe(specialTitle)
      })
    })

    it('should handle markdown in description', async () => {
      const user = userEvent.setup()
      const markdown = '# Heading\n\n- List item\n- Another item\n\n```code```'
      const mockResponse = {
        data: { success: true, issue: { number: 1 } }
      }
      apiService.createIssue.mockResolvedValue(mockResponse)
      
      render(<IssueCreator />)
      await user.click(screen.getByRole('button', { name: /create issue/i }))
      
      await user.type(screen.getByLabelText(/title/i), 'Test')
      await user.type(screen.getByLabelText(/description/i), markdown)
      await user.type(screen.getByLabelText(/github token/i), 'ghp_test')
      await user.click(screen.getByRole('button', { name: /^create issue$/i }))
      
      await waitFor(() => {
        const call = apiService.createIssue.mock.calls[0]
        expect(call[2]).toBe(markdown)
      })
    })

    it('should handle unicode characters', async () => {
      const user = userEvent.setup()
      const unicodeTitle = '测试 Issue with émoji 🎉'
      const mockResponse = {
        data: { success: true, issue: { number: 1 } }
      }
      apiService.createIssue.mockResolvedValue(mockResponse)
      
      render(<IssueCreator />)
      await user.click(screen.getByRole('button', { name: /create issue/i }))
      
      await user.type(screen.getByLabelText(/title/i), unicodeTitle)
      await user.type(screen.getByLabelText(/github token/i), 'ghp_test')
      await user.click(screen.getByRole('button', { name: /^create issue$/i }))
      
      await waitFor(() => {
        expect(apiService.createIssue).toHaveBeenCalled()
      })
    })
  })

  describe('Accessibility', () => {
    it('should have required attribute on title field', async () => {
      const user = userEvent.setup()
      render(<IssueCreator />)
      
      await user.click(screen.getByRole('button', { name: /create issue/i }))
      
      const titleInput = screen.getByLabelText(/title/i)
      expect(titleInput).toHaveAttribute('required')
    })

    it('should have required attribute on token field', async () => {
      const user = userEvent.setup()
      render(<IssueCreator />)
      
      await user.click(screen.getByRole('button', { name: /create issue/i }))
      
      const tokenInput = screen.getByLabelText(/github token/i)
      expect(tokenInput).toHaveAttribute('required')
    })

    it('should have descriptive labels for all inputs', async () => {
      const user = userEvent.setup()
      render(<IssueCreator />)
      
      await user.click(screen.getByRole('button', { name: /create issue/i }))
      
      expect(screen.getByLabelText(/repository/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/github token/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/title/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/description/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/labels/i)).toBeInTheDocument()
    })
  })
})