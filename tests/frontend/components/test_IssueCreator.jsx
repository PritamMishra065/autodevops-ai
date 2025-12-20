/**
 * Comprehensive test suite for frontend/components/IssueCreator.jsx
 * 
 * Tests cover:
 * - Component rendering (collapsed and expanded states)
 * - Form input handling and validation
 * - LocalStorage integration for token
 * - Form submission (success and error cases)
 * - Issue creation API integration
 * - Loading states and disabled states
 * - Label parsing (comma-separated)
 * - Callback invocation on success
 * - Auto-close behavior
 * - Edge cases
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import IssueCreator from '../../../frontend/components/IssueCreator';
import { apiService } from '../../../frontend/services/api';

// Mock the API service
vi.mock('../../../frontend/services/api', () => ({
  apiService: {
    createIssue: vi.fn(),
  },
}));

// Mock lucide-react icons
vi.mock('lucide-react', () => ({
  Plus: () => <div data-testid="plus-icon">Plus</div>,
  AlertCircle: () => <div data-testid="alert-icon">Alert</div>,
  CheckCircle2: () => <div data-testid="check-icon">Check</div>,
  X: () => <div data-testid="x-icon">X</div>,
}));

describe('IssueCreator Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  describe('Initial Rendering - Collapsed State', () => {
    it('should render Create Issue button when collapsed', () => {
      render(<IssueCreator />);
      expect(screen.getByRole('button', { name: /Create Issue/i })).toBeInTheDocument();
    });

    it('should not show form when collapsed', () => {
      render(<IssueCreator />);
      expect(screen.queryByText('Create GitHub Issue')).not.toBeInTheDocument();
    });

    it('should expand form when Create Issue button is clicked', async () => {
      const user = userEvent.setup();
      render(<IssueCreator />);
      
      const button = screen.getByRole('button', { name: /Create Issue/i });
      await user.click(button);
      
      expect(screen.getByText('Create GitHub Issue')).toBeInTheDocument();
    });
  });

  describe('Initial Rendering - Expanded State', () => {
    beforeEach(async () => {
      const user = userEvent.setup();
      render(<IssueCreator />);
      const button = screen.getByRole('button', { name: /Create Issue/i });
      await user.click(button);
    });

    it('should render all form fields', () => {
      expect(screen.getByLabelText(/Repository/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/GitHub Token/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/Title/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/Description/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/Labels/i)).toBeInTheDocument();
    });

    it('should have default repository value', () => {
      const repoInput = screen.getByPlaceholderText('owner/repo');
      expect(repoInput).toHaveValue('PritamMishra065/autodevops-ai');
    });

    it('should render submit and cancel buttons', () => {
      expect(screen.getByRole('button', { name: /Create Issue/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /Cancel/i })).toBeInTheDocument();
    });

    it('should render close button', () => {
      expect(screen.getByTestId('x-icon')).toBeInTheDocument();
    });
  });

  describe('LocalStorage Token Integration', () => {
    it('should load token from localStorage on mount', async () => {
      localStorage.setItem('github_token', 'saved_token_123');
      
      const user = userEvent.setup();
      render(<IssueCreator />);
      
      const button = screen.getByRole('button', { name: /Create Issue/i });
      await user.click(button);
      
      const tokenInput = screen.getByPlaceholderText('ghp_...');
      expect(tokenInput).toHaveValue('saved_token_123');
    });

    it('should have empty token when localStorage is empty', async () => {
      const user = userEvent.setup();
      render(<IssueCreator />);
      
      const button = screen.getByRole('button', { name: /Create Issue/i });
      await user.click(button);
      
      const tokenInput = screen.getByPlaceholderText('ghp_...');
      expect(tokenInput).toHaveValue('');
    });
  });

  describe('Form Input Handling', () => {
    beforeEach(async () => {
      const user = userEvent.setup();
      render(<IssueCreator />);
      const button = screen.getByRole('button', { name: /Create Issue/i });
      await user.click(button);
    });

    it('should update repository field', async () => {
      const user = userEvent.setup();
      const repoInput = screen.getByPlaceholderText('owner/repo');
      
      await user.clear(repoInput);
      await user.type(repoInput, 'newowner/newrepo');
      
      expect(repoInput).toHaveValue('newowner/newrepo');
    });

    it('should update token field', async () => {
      const user = userEvent.setup();
      const tokenInput = screen.getByPlaceholderText('ghp_...');
      
      await user.type(tokenInput, 'ghp_mytoken');
      
      expect(tokenInput).toHaveValue('ghp_mytoken');
    });

    it('should update title field', async () => {
      const user = userEvent.setup();
      const titleInput = screen.getByPlaceholderText('Issue title');
      
      await user.type(titleInput, 'Bug Report');
      
      expect(titleInput).toHaveValue('Bug Report');
    });

    it('should update description field', async () => {
      const user = userEvent.setup();
      const descInput = screen.getByPlaceholderText(/supports Markdown/i);
      
      await user.type(descInput, 'This is a bug description');
      
      expect(descInput).toHaveValue('This is a bug description');
    });

    it('should update labels field', async () => {
      const user = userEvent.setup();
      const labelsInput = screen.getByPlaceholderText('bug, enhancement, documentation');
      
      await user.type(labelsInput, 'bug, urgent');
      
      expect(labelsInput).toHaveValue('bug, urgent');
    });

    it('should handle multiline description', async () => {
      const user = userEvent.setup();
      const descInput = screen.getByPlaceholderText(/supports Markdown/i);
      
      await user.type(descInput, 'Line 1{Enter}Line 2{Enter}Line 3');
      
      expect(descInput.value).toContain('Line 1');
      expect(descInput.value).toContain('Line 2');
    });
  });

  describe('Form Validation', () => {
    beforeEach(async () => {
      const user = userEvent.setup();
      render(<IssueCreator />);
      const button = screen.getByRole('button', { name: /Create Issue/i });
      await user.click(button);
    });

    it('should show error when title is empty', async () => {
      const user = userEvent.setup();
      
      const tokenInput = screen.getByPlaceholderText('ghp_...');
      await user.type(tokenInput, 'token');
      
      const submitButton = screen.getByRole('button', { name: /Create Issue/i });
      await user.click(submitButton);
      
      await waitFor(() => {
        expect(screen.getByText('Title is required')).toBeInTheDocument();
      });
    });

    it('should show error when token is missing', async () => {
      const user = userEvent.setup();
      
      const titleInput = screen.getByPlaceholderText('Issue title');
      await user.type(titleInput, 'Test Issue');
      
      const submitButton = screen.getByRole('button', { name: /Create Issue/i });
      await user.click(submitButton);
      
      await waitFor(() => {
        expect(screen.getByText('GitHub token is required')).toBeInTheDocument();
      });
    });

    it('should show error for whitespace-only title', async () => {
      const user = userEvent.setup();
      
      const tokenInput = screen.getByPlaceholderText('ghp_...');
      await user.type(tokenInput, 'token');
      
      const titleInput = screen.getByPlaceholderText('Issue title');
      await user.type(titleInput, '   ');
      
      const submitButton = screen.getByRole('button', { name: /Create Issue/i });
      await user.click(submitButton);
      
      await waitFor(() => {
        expect(screen.getByText('Title is required')).toBeInTheDocument();
      });
    });
  });

  describe('Form Submission - Success Cases', () => {
    beforeEach(async () => {
      const user = userEvent.setup();
      render(<IssueCreator />);
      const button = screen.getByRole('button', { name: /Create Issue/i });
      await user.click(button);
    });

    it('should call API with correct parameters', async () => {
      const user = userEvent.setup();
      apiService.createIssue.mockResolvedValue({
        data: {
          success: true,
          issue: { number: 42, title: 'Test Issue' },
        },
      });
      
      const tokenInput = screen.getByPlaceholderText('ghp_...');
      await user.type(tokenInput, 'test_token');
      
      const titleInput = screen.getByPlaceholderText('Issue title');
      await user.type(titleInput, 'Test Issue');
      
      const descInput = screen.getByPlaceholderText(/supports Markdown/i);
      await user.type(descInput, 'Issue description');
      
      const labelsInput = screen.getByPlaceholderText('bug, enhancement, documentation');
      await user.type(labelsInput, 'bug, urgent');
      
      const submitButton = screen.getByRole('button', { name: /Create Issue/i });
      await user.click(submitButton);
      
      await waitFor(() => {
        expect(apiService.createIssue).toHaveBeenCalledWith(
          'PritamMishra065/autodevops-ai',
          'Test Issue',
          'Issue description',
          'test_token',
          ['bug', 'urgent']
        );
      });
    });

    it('should parse comma-separated labels correctly', async () => {
      const user = userEvent.setup();
      apiService.createIssue.mockResolvedValue({
        data: { success: true, issue: { number: 1 } },
      });
      
      const tokenInput = screen.getByPlaceholderText('ghp_...');
      await user.type(tokenInput, 'token');
      
      const titleInput = screen.getByPlaceholderText('Issue title');
      await user.type(titleInput, 'Test');
      
      const labelsInput = screen.getByPlaceholderText('bug, enhancement, documentation');
      await user.type(labelsInput, 'bug,  enhancement  , documentation');
      
      const submitButton = screen.getByRole('button', { name: /Create Issue/i });
      await user.click(submitButton);
      
      await waitFor(() => {
        const callArgs = apiService.createIssue.mock.calls[0];
        expect(callArgs[4]).toEqual(['bug', 'enhancement', 'documentation']);
      });
    });

    it('should handle empty labels', async () => {
      const user = userEvent.setup();
      apiService.createIssue.mockResolvedValue({
        data: { success: true, issue: { number: 1 } },
      });
      
      const tokenInput = screen.getByPlaceholderText('ghp_...');
      await user.type(tokenInput, 'token');
      
      const titleInput = screen.getByPlaceholderText('Issue title');
      await user.type(titleInput, 'Test');
      
      const submitButton = screen.getByRole('button', { name: /Create Issue/i });
      await user.click(submitButton);
      
      await waitFor(() => {
        const callArgs = apiService.createIssue.mock.calls[0];
        expect(callArgs[4]).toEqual([]);
      });
    });

    it('should display success message', async () => {
      const user = userEvent.setup();
      apiService.createIssue.mockResolvedValue({
        data: {
          success: true,
          issue: { number: 42, title: 'Test Issue' },
        },
      });
      
      const tokenInput = screen.getByPlaceholderText('ghp_...');
      await user.type(tokenInput, 'token');
      
      const titleInput = screen.getByPlaceholderText('Issue title');
      await user.type(titleInput, 'Test');
      
      const submitButton = screen.getByRole('button', { name: /Create Issue/i });
      await user.click(submitButton);
      
      await waitFor(() => {
        expect(screen.getByText(/Issue #42 created successfully!/i)).toBeInTheDocument();
      });
    });

    it('should clear form after successful submission', async () => {
      const user = userEvent.setup();
      apiService.createIssue.mockResolvedValue({
        data: {
          success: true,
          issue: { number: 1 },
        },
      });
      
      const tokenInput = screen.getByPlaceholderText('ghp_...');
      await user.type(tokenInput, 'token');
      
      const titleInput = screen.getByPlaceholderText('Issue title');
      await user.type(titleInput, 'Test');
      
      const descInput = screen.getByPlaceholderText(/supports Markdown/i);
      await user.type(descInput, 'Description');
      
      const labelsInput = screen.getByPlaceholderText('bug, enhancement, documentation');
      await user.type(labelsInput, 'bug');
      
      const submitButton = screen.getByRole('button', { name: /Create Issue/i });
      await user.click(submitButton);
      
      await waitFor(() => {
        expect(titleInput).toHaveValue('');
        expect(descInput).toHaveValue('');
        expect(labelsInput).toHaveValue('');
      });
    });

    it('should auto-close after 2 seconds on success', async () => {
      vi.useFakeTimers();
      const user = userEvent.setup();
      
      apiService.createIssue.mockResolvedValue({
        data: {
          success: true,
          issue: { number: 1 },
        },
      });
      
      const tokenInput = screen.getByPlaceholderText('ghp_...');
      await user.type(tokenInput, 'token');
      
      const titleInput = screen.getByPlaceholderText('Issue title');
      await user.type(titleInput, 'Test');
      
      const submitButton = screen.getByRole('button', { name: /Create Issue/i });
      await user.click(submitButton);
      
      await waitFor(() => {
        expect(screen.getByText(/created successfully/i)).toBeInTheDocument();
      });
      
      // Fast-forward 2 seconds
      vi.advanceTimersByTime(2000);
      
      await waitFor(() => {
        expect(screen.queryByText('Create GitHub Issue')).not.toBeInTheDocument();
      });
      
      vi.useRealTimers();
    });

    it('should call onIssueCreated callback when provided', async () => {
      const mockCallback = vi.fn();
      const user = userEvent.setup();
      
      const { rerender } = render(<IssueCreator />);
      const button = screen.getByRole('button', { name: /Create Issue/i });
      await user.click(button);
      
      // Rerender with callback
      rerender(<IssueCreator onIssueCreated={mockCallback} />);
      
      apiService.createIssue.mockResolvedValue({
        data: {
          success: true,
          issue: { number: 42, title: 'Test' },
        },
      });
      
      const tokenInput = screen.getByPlaceholderText('ghp_...');
      await user.type(tokenInput, 'token');
      
      const titleInput = screen.getByPlaceholderText('Issue title');
      await user.type(titleInput, 'Test');
      
      const submitButton = screen.getByRole('button', { name: /Create Issue/i });
      await user.click(submitButton);
      
      await waitFor(() => {
        expect(mockCallback).toHaveBeenCalledWith({
          number: 42,
          title: 'Test',
        });
      });
    });
  });

  describe('Form Submission - Error Cases', () => {
    beforeEach(async () => {
      const user = userEvent.setup();
      render(<IssueCreator />);
      const button = screen.getByRole('button', { name: /Create Issue/i });
      await user.click(button);
    });

    it('should display API error message', async () => {
      const user = userEvent.setup();
      apiService.createIssue.mockRejectedValue({
        response: {
          data: {
            error: 'Invalid token',
          },
        },
      });
      
      const tokenInput = screen.getByPlaceholderText('ghp_...');
      await user.type(tokenInput, 'bad_token');
      
      const titleInput = screen.getByPlaceholderText('Issue title');
      await user.type(titleInput, 'Test');
      
      const submitButton = screen.getByRole('button', { name: /Create Issue/i });
      await user.click(submitButton);
      
      await waitFor(() => {
        expect(screen.getByText('Invalid token')).toBeInTheDocument();
      });
    });

    it('should display generic error when API returns no specific message', async () => {
      const user = userEvent.setup();
      apiService.createIssue.mockRejectedValue({
        response: { data: {} },
      });
      
      const tokenInput = screen.getByPlaceholderText('ghp_...');
      await user.type(tokenInput, 'token');
      
      const titleInput = screen.getByPlaceholderText('Issue title');
      await user.type(titleInput, 'Test');
      
      const submitButton = screen.getByRole('button', { name: /Create Issue/i });
      await user.click(submitButton);
      
      await waitFor(() => {
        expect(screen.getByText('Failed to create issue')).toBeInTheDocument();
      });
    });

    it('should display error for non-success response', async () => {
      const user = userEvent.setup();
      apiService.createIssue.mockResolvedValue({
        data: {
          success: false,
          error: 'Repository not found',
        },
      });
      
      const tokenInput = screen.getByPlaceholderText('ghp_...');
      await user.type(tokenInput, 'token');
      
      const titleInput = screen.getByPlaceholderText('Issue title');
      await user.type(titleInput, 'Test');
      
      const submitButton = screen.getByRole('button', { name: /Create Issue/i });
      await user.click(submitButton);
      
      await waitFor(() => {
        expect(screen.getByText('Repository not found')).toBeInTheDocument();
      });
    });

    it('should not clear form on error', async () => {
      const user = userEvent.setup();
      apiService.createIssue.mockRejectedValue({
        response: { data: { error: 'Error' } },
      });
      
      const tokenInput = screen.getByPlaceholderText('ghp_...');
      await user.type(tokenInput, 'token');
      
      const titleInput = screen.getByPlaceholderText('Issue title');
      await user.type(titleInput, 'Test Issue');
      
      const submitButton = screen.getByRole('button', { name: /Create Issue/i });
      await user.click(submitButton);
      
      await waitFor(() => {
        expect(screen.getByText('Error')).toBeInTheDocument();
      });
      
      // Form should still have values
      expect(titleInput).toHaveValue('Test Issue');
      expect(tokenInput).toHaveValue('token');
    });
  });

  describe('Loading State', () => {
    beforeEach(async () => {
      const user = userEvent.setup();
      render(<IssueCreator />);
      const button = screen.getByRole('button', { name: /Create Issue/i });
      await user.click(button);
    });

    it('should show loading text during submission', async () => {
      const user = userEvent.setup();
      apiService.createIssue.mockImplementation(() => 
        new Promise(resolve => setTimeout(() => resolve({ data: { success: true, issue: {} } }), 100))
      );
      
      const tokenInput = screen.getByPlaceholderText('ghp_...');
      await user.type(tokenInput, 'token');
      
      const titleInput = screen.getByPlaceholderText('Issue title');
      await user.type(titleInput, 'Test');
      
      const submitButton = screen.getByRole('button', { name: /Create Issue/i });
      await user.click(submitButton);
      
      expect(screen.getByText('Creating...')).toBeInTheDocument();
    });

    it('should disable submit button during loading', async () => {
      const user = userEvent.setup();
      apiService.createIssue.mockImplementation(() => 
        new Promise(resolve => setTimeout(() => resolve({ data: { success: true, issue: {} } }), 100))
      );
      
      const tokenInput = screen.getByPlaceholderText('ghp_...');
      await user.type(tokenInput, 'token');
      
      const titleInput = screen.getByPlaceholderText('Issue title');
      await user.type(titleInput, 'Test');
      
      const submitButton = screen.getByRole('button', { name: /Create Issue/i });
      await user.click(submitButton);
      
      expect(submitButton).toBeDisabled();
    });
  });

  describe('Close and Cancel Functionality', () => {
    it('should close form when X button is clicked', async () => {
      const user = userEvent.setup();
      render(<IssueCreator />);
      
      const openButton = screen.getByRole('button', { name: /Create Issue/i });
      await user.click(openButton);
      
      expect(screen.getByText('Create GitHub Issue')).toBeInTheDocument();
      
      const closeButton = screen.getByTestId('x-icon').closest('button');
      await user.click(closeButton);
      
      expect(screen.queryByText('Create GitHub Issue')).not.toBeInTheDocument();
    });

    it('should close form when Cancel button is clicked', async () => {
      const user = userEvent.setup();
      render(<IssueCreator />);
      
      const openButton = screen.getByRole('button', { name: /Create Issue/i });
      await user.click(openButton);
      
      const cancelButton = screen.getByRole('button', { name: /Cancel/i });
      await user.click(cancelButton);
      
      expect(screen.queryByText('Create GitHub Issue')).not.toBeInTheDocument();
    });

    it('should clear error message when closing form', async () => {
      const user = userEvent.setup();
      render(<IssueCreator />);
      
      const openButton = screen.getByRole('button', { name: /Create Issue/i });
      await user.click(openButton);
      
      // Trigger an error
      const submitButton = screen.getByRole('button', { name: /Create Issue/i });
      await user.click(submitButton);
      
      await waitFor(() => {
        expect(screen.getByText('Title is required')).toBeInTheDocument();
      });
      
      // Close form
      const closeButton = screen.getByTestId('x-icon').closest('button');
      await user.click(closeButton);
      
      // Reopen
      await user.click(screen.getByRole('button', { name: /Create Issue/i }));
      
      // Error should be cleared
      expect(screen.queryByText('Title is required')).not.toBeInTheDocument();
    });
  });

  describe('Edge Cases', () => {
    it('should handle labels with only commas', async () => {
      const user = userEvent.setup();
      render(<IssueCreator />);
      const button = screen.getByRole('button', { name: /Create Issue/i });
      await user.click(button);
      
      apiService.createIssue.mockResolvedValue({
        data: { success: true, issue: { number: 1 } },
      });
      
      const tokenInput = screen.getByPlaceholderText('ghp_...');
      await user.type(tokenInput, 'token');
      
      const titleInput = screen.getByPlaceholderText('Issue title');
      await user.type(titleInput, 'Test');
      
      const labelsInput = screen.getByPlaceholderText('bug, enhancement, documentation');
      await user.type(labelsInput, ',,,');
      
      const submitButton = screen.getByRole('button', { name: /Create Issue/i });
      await user.click(submitButton);
      
      await waitFor(() => {
        const callArgs = apiService.createIssue.mock.calls[0];
        expect(callArgs[4]).toEqual([]);
      });
    });

    it('should handle special characters in title', async () => {
      const user = userEvent.setup();
      render(<IssueCreator />);
      const button = screen.getByRole('button', { name: /Create Issue/i });
      await user.click(button);
      
      apiService.createIssue.mockResolvedValue({
        data: { success: true, issue: { number: 1 } },
      });
      
      const tokenInput = screen.getByPlaceholderText('ghp_...');
      await user.type(tokenInput, 'token');
      
      const titleInput = screen.getByPlaceholderText('Issue title');
      await user.type(titleInput, 'Bug: <script>alert("xss")</script>');
      
      const submitButton = screen.getByRole('button', { name: /Create Issue/i });
      await user.click(submitButton);
      
      await waitFor(() => {
        expect(apiService.createIssue).toHaveBeenCalled();
      });
    });

    it('should handle very long descriptions', async () => {
      const user = userEvent.setup();
      render(<IssueCreator />);
      const button = screen.getByRole('button', { name: /Create Issue/i });
      await user.click(button);
      
      apiService.createIssue.mockResolvedValue({
        data: { success: true, issue: { number: 1 } },
      });
      
      const tokenInput = screen.getByPlaceholderText('ghp_...');
      await user.type(tokenInput, 'token');
      
      const titleInput = screen.getByPlaceholderText('Issue title');
      await user.type(titleInput, 'Test');
      
      const descInput = screen.getByPlaceholderText(/supports Markdown/i);
      const longDesc = 'A'.repeat(5000);
      await user.type(descInput, longDesc);
      
      const submitButton = screen.getByRole('button', { name: /Create Issue/i });
      await user.click(submitButton);
      
      await waitFor(() => {
        expect(apiService.createIssue).toHaveBeenCalled();
      });
    });
  });
});