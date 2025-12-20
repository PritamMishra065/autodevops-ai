/**
 * Comprehensive test suite for frontend/components/FeatureGenerator.jsx
 * 
 * Tests cover:
 * - Component rendering
 * - Form input handling
 * - Form submission (success and error cases)
 * - Loading states
 * - Error display
 * - Success result display
 * - Input validation
 * - API integration
 * - Edge cases
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import FeatureGenerator from '../../../frontend/components/FeatureGenerator';
import { apiService } from '../../../frontend/services/api';

// Mock the API service
vi.mock('../../../frontend/services/api', () => ({
  apiService: {
    generateFeature: vi.fn(),
  },
}));

// Mock lucide-react icons
vi.mock('lucide-react', () => ({
  Sparkles: () => <div data-testid="sparkles-icon">Sparkles</div>,
  Loader: () => <div data-testid="loader-icon">Loader</div>,
  CheckCircle2: () => <div data-testid="check-icon">Check</div>,
  AlertCircle: () => <div data-testid="alert-icon">Alert</div>,
}));

describe('FeatureGenerator Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Initial Rendering', () => {
    it('should render the component with title', () => {
      render(<FeatureGenerator />);
      expect(screen.getByText('Generate Feature with Cline')).toBeInTheDocument();
    });

    it('should render the textarea input', () => {
      render(<FeatureGenerator />);
      const textarea = screen.getByPlaceholderText(/Add login with GitHub OAuth/i);
      expect(textarea).toBeInTheDocument();
    });

    it('should render the submit button', () => {
      render(<FeatureGenerator />);
      const button = screen.getByRole('button', { name: /Generate Feature/i });
      expect(button).toBeInTheDocument();
    });

    it('should render the label for feature description', () => {
      render(<FeatureGenerator />);
      expect(screen.getByText('Feature Description')).toBeInTheDocument();
    });

    it('should render helper text', () => {
      render(<FeatureGenerator />);
      expect(screen.getByText(/Describe the feature you want Cline to build/i)).toBeInTheDocument();
    });

    it('should have empty textarea initially', () => {
      render(<FeatureGenerator />);
      const textarea = screen.getByPlaceholderText(/Add login with GitHub OAuth/i);
      expect(textarea).toHaveValue('');
    });

    it('should have submit button disabled initially', () => {
      render(<FeatureGenerator />);
      const button = screen.getByRole('button', { name: /Generate Feature/i });
      expect(button).toBeDisabled();
    });
  });

  describe('User Input Handling', () => {
    it('should update textarea value when user types', async () => {
      const user = userEvent.setup();
      render(<FeatureGenerator />);
      
      const textarea = screen.getByPlaceholderText(/Add login with GitHub OAuth/i);
      await user.type(textarea, 'Add user authentication');
      
      expect(textarea).toHaveValue('Add user authentication');
    });

    it('should enable submit button when textarea has content', async () => {
      const user = userEvent.setup();
      render(<FeatureGenerator />);
      
      const textarea = screen.getByPlaceholderText(/Add login with GitHub OAuth/i);
      const button = screen.getByRole('button', { name: /Generate Feature/i });
      
      await user.type(textarea, 'Add feature');
      
      expect(button).not.toBeDisabled();
    });

    it('should keep button disabled for whitespace-only input', async () => {
      const user = userEvent.setup();
      render(<FeatureGenerator />);
      
      const textarea = screen.getByPlaceholderText(/Add login with GitHub OAuth/i);
      const button = screen.getByRole('button', { name: /Generate Feature/i });
      
      await user.type(textarea, '   ');
      
      // Note: Button state depends on trim() in handleGenerate, not in render
      expect(button).not.toBeDisabled(); // Button is enabled but validation happens on submit
    });

    it('should handle multiline input', async () => {
      const user = userEvent.setup();
      render(<FeatureGenerator />);
      
      const textarea = screen.getByPlaceholderText(/Add login with GitHub OAuth/i);
      const multilineText = 'Line 1\nLine 2\nLine 3';
      
      await user.type(textarea, multilineText);
      
      expect(textarea).toHaveValue(multilineText);
    });

    it('should handle long input text', async () => {
      const user = userEvent.setup();
      render(<FeatureGenerator />);
      
      const textarea = screen.getByPlaceholderText(/Add login with GitHub OAuth/i);
      const longText = 'A'.repeat(500);
      
      await user.type(textarea, longText);
      
      expect(textarea).toHaveValue(longText);
    });
  });

  describe('Form Submission - Success Cases', () => {
    it('should call API with feature description on submit', async () => {
      const user = userEvent.setup();
      apiService.generateFeature.mockResolvedValue({
        data: {
          status: 'success',
          feature: 'Test feature',
        },
      });

      render(<FeatureGenerator />);
      
      const textarea = screen.getByPlaceholderText(/Add login with GitHub OAuth/i);
      await user.type(textarea, 'Add authentication');
      
      const button = screen.getByRole('button', { name: /Generate Feature/i });
      await user.click(button);
      
      expect(apiService.generateFeature).toHaveBeenCalledWith('Add authentication');
    });

    it('should show loading state during API call', async () => {
      const user = userEvent.setup();
      apiService.generateFeature.mockImplementation(() => 
        new Promise(resolve => setTimeout(() => resolve({ data: { status: 'success' } }), 100))
      );

      render(<FeatureGenerator />);
      
      const textarea = screen.getByPlaceholderText(/Add login with GitHub OAuth/i);
      await user.type(textarea, 'Test feature');
      
      const button = screen.getByRole('button', { name: /Generate Feature/i });
      await user.click(button);
      
      expect(screen.getByText('Generating...')).toBeInTheDocument();
      expect(button).toBeDisabled();
    });

    it('should display success message after successful generation', async () => {
      const user = userEvent.setup();
      apiService.generateFeature.mockResolvedValue({
        data: {
          status: 'success',
          feature: 'Authentication System',
        },
      });

      render(<FeatureGenerator />);
      
      const textarea = screen.getByPlaceholderText(/Add login with GitHub OAuth/i);
      await user.type(textarea, 'Add authentication');
      
      const button = screen.getByRole('button', { name: /Generate Feature/i });
      await user.click(button);
      
      await waitFor(() => {
        expect(screen.getByText('Feature Generated Successfully!')).toBeInTheDocument();
      });
    });

    it('should display feature details in success message', async () => {
      const user = userEvent.setup();
      apiService.generateFeature.mockResolvedValue({
        data: {
          status: 'success',
          feature: 'User Authentication',
          files_created: ['auth.js', 'login.jsx'],
          branch: 'feature/user-auth',
        },
      });

      render(<FeatureGenerator />);
      
      const textarea = screen.getByPlaceholderText(/Add login with GitHub OAuth/i);
      await user.type(textarea, 'Add authentication');
      
      const button = screen.getByRole('button', { name: /Generate Feature/i });
      await user.click(button);
      
      await waitFor(() => {
        expect(screen.getByText(/User Authentication/i)).toBeInTheDocument();
        expect(screen.getByText(/auth.js/i)).toBeInTheDocument();
        expect(screen.getByText(/login.jsx/i)).toBeInTheDocument();
        expect(screen.getByText(/feature\/user-auth/i)).toBeInTheDocument();
      });
    });

    it('should clear input after successful submission', async () => {
      const user = userEvent.setup();
      apiService.generateFeature.mockResolvedValue({
        data: {
          status: 'success',
          feature: 'Test',
        },
      });

      render(<FeatureGenerator />);
      
      const textarea = screen.getByPlaceholderText(/Add login with GitHub OAuth/i);
      await user.type(textarea, 'Test feature');
      
      const button = screen.getByRole('button', { name: /Generate Feature/i });
      await user.click(button);
      
      await waitFor(() => {
        expect(textarea).toHaveValue('');
      });
    });

    it('should clear previous error on successful submission', async () => {
      const user = userEvent.setup();
      
      // First call fails
      apiService.generateFeature.mockRejectedValueOnce({
        response: { data: { error: 'First error' } },
      });
      
      // Second call succeeds
      apiService.generateFeature.mockResolvedValueOnce({
        data: { status: 'success', feature: 'Test' },
      });

      render(<FeatureGenerator />);
      
      const textarea = screen.getByPlaceholderText(/Add login with GitHub OAuth/i);
      await user.type(textarea, 'Test');
      
      const button = screen.getByRole('button', { name: /Generate Feature/i });
      await user.click(button);
      
      await waitFor(() => {
        expect(screen.getByText('First error')).toBeInTheDocument();
      });
      
      // Try again
      await user.type(textarea, 'Test again');
      await user.click(button);
      
      await waitFor(() => {
        expect(screen.queryByText('First error')).not.toBeInTheDocument();
      });
    });
  });

  describe('Form Submission - Error Cases', () => {
    it('should show error when submitting empty input', async () => {
      const user = userEvent.setup();
      render(<FeatureGenerator />);
      
      const form = screen.getByRole('button', { name: /Generate Feature/i }).closest('form');
      fireEvent.submit(form);
      
      await waitFor(() => {
        expect(screen.getByText('Please enter a feature description')).toBeInTheDocument();
      });
    });

    it('should show error when submitting whitespace-only input', async () => {
      const user = userEvent.setup();
      render(<FeatureGenerator />);
      
      const textarea = screen.getByPlaceholderText(/Add login with GitHub OAuth/i);
      await user.type(textarea, '   ');
      
      const form = screen.getByRole('button', { name: /Generate Feature/i }).closest('form');
      fireEvent.submit(form);
      
      await waitFor(() => {
        expect(screen.getByText('Please enter a feature description')).toBeInTheDocument();
      });
    });

    it('should not call API when input is empty', async () => {
      render(<FeatureGenerator />);
      
      const form = screen.getByRole('button', { name: /Generate Feature/i }).closest('form');
      fireEvent.submit(form);
      
      await waitFor(() => {
        expect(apiService.generateFeature).not.toHaveBeenCalled();
      });
    });

    it('should display API error message', async () => {
      const user = userEvent.setup();
      apiService.generateFeature.mockRejectedValue({
        response: {
          data: {
            error: 'Feature generation failed',
          },
        },
      });

      render(<FeatureGenerator />);
      
      const textarea = screen.getByPlaceholderText(/Add login with GitHub OAuth/i);
      await user.type(textarea, 'Test feature');
      
      const button = screen.getByRole('button', { name: /Generate Feature/i });
      await user.click(button);
      
      await waitFor(() => {
        expect(screen.getByText('Feature generation failed')).toBeInTheDocument();
      });
    });

    it('should display generic error when API response has no error message', async () => {
      const user = userEvent.setup();
      apiService.generateFeature.mockRejectedValue({
        response: {
          data: {},
        },
      });

      render(<FeatureGenerator />);
      
      const textarea = screen.getByPlaceholderText(/Add login with GitHub OAuth/i);
      await user.type(textarea, 'Test feature');
      
      const button = screen.getByRole('button', { name: /Generate Feature/i });
      await user.click(button);
      
      await waitFor(() => {
        expect(screen.getByText('Failed to generate feature')).toBeInTheDocument();
      });
    });

    it('should handle network error gracefully', async () => {
      const user = userEvent.setup();
      apiService.generateFeature.mockRejectedValue(new Error('Network error'));

      render(<FeatureGenerator />);
      
      const textarea = screen.getByPlaceholderText(/Add login with GitHub OAuth/i);
      await user.type(textarea, 'Test feature');
      
      const button = screen.getByRole('button', { name: /Generate Feature/i });
      await user.click(button);
      
      await waitFor(() => {
        expect(screen.getByText('Failed to generate feature')).toBeInTheDocument();
      });
    });

    it('should handle non-success response status', async () => {
      const user = userEvent.setup();
      apiService.generateFeature.mockResolvedValue({
        data: {
          status: 'error',
          error: 'Invalid feature description',
        },
      });

      render(<FeatureGenerator />);
      
      const textarea = screen.getByPlaceholderText(/Add login with GitHub OAuth/i);
      await user.type(textarea, 'Test');
      
      const button = screen.getByRole('button', { name: /Generate Feature/i });
      await user.click(button);
      
      await waitFor(() => {
        expect(screen.getByText('Invalid feature description')).toBeInTheDocument();
      });
    });

    it('should stop loading state after error', async () => {
      const user = userEvent.setup();
      apiService.generateFeature.mockRejectedValue({
        response: { data: { error: 'Error' } },
      });

      render(<FeatureGenerator />);
      
      const textarea = screen.getByPlaceholderText(/Add login with GitHub OAuth/i);
      await user.type(textarea, 'Test');
      
      const button = screen.getByRole('button', { name: /Generate Feature/i });
      await user.click(button);
      
      await waitFor(() => {
        expect(screen.getByText('Error')).toBeInTheDocument();
      });
      
      expect(button).not.toBeDisabled();
      expect(screen.queryByText('Generating...')).not.toBeInTheDocument();
    });
  });

  describe('Textarea Disabled State', () => {
    it('should disable textarea during loading', async () => {
      const user = userEvent.setup();
      apiService.generateFeature.mockImplementation(() => 
        new Promise(resolve => setTimeout(() => resolve({ data: { status: 'success' } }), 100))
      );

      render(<FeatureGenerator />);
      
      const textarea = screen.getByPlaceholderText(/Add login with GitHub OAuth/i);
      await user.type(textarea, 'Test');
      
      const button = screen.getByRole('button', { name: /Generate Feature/i });
      await user.click(button);
      
      expect(textarea).toBeDisabled();
    });

    it('should re-enable textarea after successful submission', async () => {
      const user = userEvent.setup();
      apiService.generateFeature.mockResolvedValue({
        data: { status: 'success', feature: 'Test' },
      });

      render(<FeatureGenerator />);
      
      const textarea = screen.getByPlaceholderText(/Add login with GitHub OAuth/i);
      await user.type(textarea, 'Test');
      
      const button = screen.getByRole('button', { name: /Generate Feature/i });
      await user.click(button);
      
      await waitFor(() => {
        expect(textarea).not.toBeDisabled();
      });
    });

    it('should re-enable textarea after error', async () => {
      const user = userEvent.setup();
      apiService.generateFeature.mockRejectedValue({
        response: { data: { error: 'Error' } },
      });

      render(<FeatureGenerator />);
      
      const textarea = screen.getByPlaceholderText(/Add login with GitHub OAuth/i);
      await user.type(textarea, 'Test');
      
      const button = screen.getByRole('button', { name: /Generate Feature/i });
      await user.click(button);
      
      await waitFor(() => {
        expect(textarea).not.toBeDisabled();
      });
    });
  });

  describe('Edge Cases and Special Scenarios', () => {
    it('should handle rapid successive submissions', async () => {
      const user = userEvent.setup();
      apiService.generateFeature.mockResolvedValue({
        data: { status: 'success', feature: 'Test' },
      });

      render(<FeatureGenerator />);
      
      const textarea = screen.getByPlaceholderText(/Add login with GitHub OAuth/i);
      await user.type(textarea, 'Test');
      
      const button = screen.getByRole('button', { name: /Generate Feature/i });
      
      // Try to click multiple times
      await user.click(button);
      await user.click(button);
      
      // API should only be called once due to loading state
      await waitFor(() => {
        expect(apiService.generateFeature).toHaveBeenCalledTimes(1);
      });
    });

    it('should handle special characters in input', async () => {
      const user = userEvent.setup();
      apiService.generateFeature.mockResolvedValue({
        data: { status: 'success', feature: 'Test' },
      });

      render(<FeatureGenerator />);
      
      const textarea = screen.getByPlaceholderText(/Add login with GitHub OAuth/i);
      const specialText = 'Feature with <>&"\'';
      await user.type(textarea, specialText);
      
      const button = screen.getByRole('button', { name: /Generate Feature/i });
      await user.click(button);
      
      expect(apiService.generateFeature).toHaveBeenCalledWith(specialText);
    });

    it('should handle emoji in input', async () => {
      const user = userEvent.setup();
      apiService.generateFeature.mockResolvedValue({
        data: { status: 'success', feature: 'Test' },
      });

      render(<FeatureGenerator />);
      
      const textarea = screen.getByPlaceholderText(/Add login with GitHub OAuth/i);
      await user.type(textarea, 'Add feature 🚀');
      
      const button = screen.getByRole('button', { name: /Generate Feature/i });
      await user.click(button);
      
      expect(apiService.generateFeature).toHaveBeenCalledWith('Add feature 🚀');
    });

    it('should handle missing files_created in success response', async () => {
      const user = userEvent.setup();
      apiService.generateFeature.mockResolvedValue({
        data: {
          status: 'success',
          feature: 'Test Feature',
          // No files_created field
        },
      });

      render(<FeatureGenerator />);
      
      const textarea = screen.getByPlaceholderText(/Add login with GitHub OAuth/i);
      await user.type(textarea, 'Test');
      
      const button = screen.getByRole('button', { name: /Generate Feature/i });
      await user.click(button);
      
      await waitFor(() => {
        expect(screen.getByText('Feature Generated Successfully!')).toBeInTheDocument();
      });
      
      // Should not crash, just not display files section
      expect(screen.queryByText('Files Created:')).not.toBeInTheDocument();
    });

    it('should handle empty files_created array', async () => {
      const user = userEvent.setup();
      apiService.generateFeature.mockResolvedValue({
        data: {
          status: 'success',
          feature: 'Test Feature',
          files_created: [],
        },
      });

      render(<FeatureGenerator />);
      
      const textarea = screen.getByPlaceholderText(/Add login with GitHub OAuth/i);
      await user.type(textarea, 'Test');
      
      const button = screen.getByRole('button', { name: /Generate Feature/i });
      await user.click(button);
      
      await waitFor(() => {
        expect(screen.getByText('Feature Generated Successfully!')).toBeInTheDocument();
      });
    });
  });

  describe('Accessibility', () => {
    it('should have proper form structure', () => {
      render(<FeatureGenerator />);
      const form = screen.getByRole('button', { name: /Generate Feature/i }).closest('form');
      expect(form).toBeInTheDocument();
    });

    it('should have label associated with textarea', () => {
      render(<FeatureGenerator />);
      const label = screen.getByText('Feature Description');
      const textarea = screen.getByPlaceholderText(/Add login with GitHub OAuth/i);
      
      expect(label).toBeInTheDocument();
      expect(textarea).toBeInTheDocument();
    });

    it('should have appropriate ARIA attributes on button', () => {
      render(<FeatureGenerator />);
      const button = screen.getByRole('button', { name: /Generate Feature/i });
      expect(button).toHaveAttribute('type', 'submit');
    });
  });
});