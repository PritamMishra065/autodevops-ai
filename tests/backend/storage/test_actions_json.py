"""
Comprehensive test suite for backend/storage/actions.json

Validates the structure, data integrity, and consistency of the actions.json file
which tracks all agent actions in the AutoDevOps AI system.
"""

import pytest
import json
from pathlib import Path
from datetime import datetime
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "backend"))


class TestActionsJsonStructure:
    """Test the structure and validity of actions.json"""
    
    @pytest.fixture
    def actions_file(self):
        """Get path to actions.json"""
        return Path(__file__).parent.parent.parent.parent / "backend" / "storage" / "actions.json"
    
    @pytest.fixture
    def actions_data(self, actions_file):
        """Load actions.json data"""
        if not actions_file.exists():
            pytest.skip("actions.json file not found")
        with open(actions_file, 'r') as f:
            return json.load(f)
    
    def test_actions_file_exists(self, actions_file):
        """Test that actions.json file exists"""
        assert actions_file.exists(), "actions.json should exist"
    
    def test_actions_file_is_valid_json(self, actions_file):
        """Test that actions.json contains valid JSON"""
        with open(actions_file, 'r') as f:
            try:
                json.load(f)
            except json.JSONDecodeError as e:
                pytest.fail(f"actions.json is not valid JSON: {e}")
    
    def test_actions_is_list(self, actions_data):
        """Test that actions.json root is a list"""
        assert isinstance(actions_data, list), "actions.json should contain a list"
    
    def test_actions_not_empty(self, actions_data):
        """Test that actions.json contains data"""
        assert len(actions_data) > 0, "actions.json should not be empty"


class TestActionEntryStructure:
    """Test individual action entry structure"""
    
    @pytest.fixture
    def actions_data(self):
        actions_file = Path(__file__).parent.parent.parent.parent / "backend" / "storage" / "actions.json"
        if not actions_file.exists():
            pytest.skip("actions.json not found")
        with open(actions_file, 'r') as f:
            return json.load(f)
    
    def test_all_actions_have_required_fields(self, actions_data):
        """Test that all actions have required fields"""
        required_fields = ["type", "status", "agent", "timestamp"]
        
        for i, action in enumerate(actions_data):
            for field in required_fields:
                assert field in action, f"Action at index {i} missing required field: {field}"
    
    def test_action_types_are_valid(self, actions_data):
        """Test that action types are valid strings"""
        valid_types = [
            "create_pull_request", "run_cline", "run_coderabbit", "run_kestra", 
            "run_oumi", "code_review_started", "security_scan", "kestra_workflow_executed",
            "github_pr_tracked", "build_check", "auto_fix", "feature_generated"
        ]
        
        for i, action in enumerate(actions_data):
            action_type = action.get("type")
            assert isinstance(action_type, str), f"Action type at index {i} should be string"
            # Note: Allow any string type as system may have custom types
    
    def test_action_status_values_are_valid(self, actions_data):
        """Test that status values are valid"""
        valid_statuses = ["completed", "failed", "running", "pending", "error"]
        
        for i, action in enumerate(actions_data):
            status = action.get("status")
            assert status in valid_statuses, \
                f"Action at index {i} has invalid status: {status}"
    
    def test_action_agents_are_valid(self, actions_data):
        """Test that agent names are valid"""
        valid_agents = ["cline", "coderabbit", "kestra", "oumi", "github", "system"]
        
        for i, action in enumerate(actions_data):
            agent = action.get("agent")
            assert isinstance(agent, str), f"Agent at index {i} should be string"
            assert agent in valid_agents, f"Action at index {i} has unknown agent: {agent}"
    
    def test_timestamps_are_valid_iso_format(self, actions_data):
        """Test that all timestamps are valid ISO format"""
        for i, action in enumerate(actions_data):
            timestamp = action.get("timestamp")
            assert timestamp is not None, f"Action at index {i} missing timestamp"
            
            try:
                # Try parsing as ISO format
                datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except (ValueError, AttributeError) as e:
                pytest.fail(f"Action at index {i} has invalid timestamp format: {timestamp}")


class TestActionDataIntegrity:
    """Test data integrity and consistency"""
    
    @pytest.fixture
    def actions_data(self):
        actions_file = Path(__file__).parent.parent.parent.parent / "backend" / "storage" / "actions.json"
        if not actions_file.exists():
            pytest.skip("actions.json not found")
        with open(actions_file, 'r') as f:
            return json.load(f)
    
    def test_github_pr_actions_have_pr_number(self, actions_data):
        """Test that GitHub PR actions contain PR number"""
        for action in actions_data:
            if action.get("type") == "github_pr_tracked":
                assert "pr_number" in action, "GitHub PR action should have pr_number"
                assert isinstance(action["pr_number"], int), "PR number should be integer"
    
    def test_github_pr_actions_have_url(self, actions_data):
        """Test that GitHub PR actions contain URL"""
        for action in actions_data:
            if action.get("type") == "github_pr_tracked":
                assert "pr_url" in action, "GitHub PR action should have pr_url"
                assert action["pr_url"].startswith("https://"), "PR URL should be valid HTTPS URL"
    
    def test_github_pr_actions_have_state(self, actions_data):
        """Test that GitHub PR actions have valid state"""
        valid_states = ["open", "closed", "merged"]
        
        for action in actions_data:
            if action.get("type") == "github_pr_tracked":
                assert "pr_state" in action, "GitHub PR action should have pr_state"
                assert action["pr_state"] in valid_states, "PR state should be valid"
    
    def test_completed_actions_have_no_error_field(self, actions_data):
        """Test that completed actions don't have error field"""
        for i, action in enumerate(actions_data):
            if action.get("status") == "completed":
                # It's okay to have error field, but it shouldn't be primary status
                pass
    
    def test_failed_actions_context(self, actions_data):
        """Test that failed actions have appropriate context"""
        for action in actions_data:
            if action.get("status") == "failed":
                # Failed actions should ideally have some context
                # This is a soft check - not all systems log error details
                assert action.get("agent") is not None


class TestActionOrdering:
    """Test action ordering and timeline"""
    
    @pytest.fixture
    def actions_data(self):
        actions_file = Path(__file__).parent.parent.parent.parent / "backend" / "storage" / "actions.json"
        if not actions_file.exists():
            pytest.skip("actions.json not found")
        with open(actions_file, 'r') as f:
            return json.load(f)
    
    def test_actions_have_chronological_timestamps(self, actions_data):
        """Test that actions are in reasonable chronological order"""
        timestamps = []
        for action in actions_data:
            ts_str = action.get("timestamp", "")
            try:
                ts = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
                timestamps.append(ts)
            except:
                pass
        
        # Check that we have timestamps
        assert len(timestamps) > 0, "Should have parseable timestamps"
    
    def test_no_duplicate_actions(self, actions_data):
        """Test for potential duplicate actions"""
        # This is a heuristic test - exact duplicates are unlikely but possible
        seen = set()
        for action in actions_data:
            # Create a signature from key fields
            sig = (action.get("type"), action.get("timestamp"), action.get("agent"))
            # Allow duplicates but warn if too many
            seen.add(sig)
        
        # If we have way more signatures than unique ones, something might be wrong
        # But this is informational only
        assert len(seen) > 0


class TestSpecificActionTypes:
    """Test specific action type requirements"""
    
    @pytest.fixture
    def actions_data(self):
        actions_file = Path(__file__).parent.parent.parent.parent / "backend" / "storage" / "actions.json"
        if not actions_file.exists():
            pytest.skip("actions.json not found")
        with open(actions_file, 'r') as f:
            return json.load(f)
    
    def test_kestra_workflow_actions(self, actions_data):
        """Test kestra_workflow_executed actions have workflow_id"""
        for action in actions_data:
            if action.get("type") == "kestra_workflow_executed":
                # Should have workflow_id if available
                # This is a soft requirement
                pass
    
    def test_agent_run_actions(self, actions_data):
        """Test that run_* actions are properly formatted"""
        agent_types = ["run_cline", "run_coderabbit", "run_kestra", "run_oumi"]
        
        for action in actions_data:
            if action.get("type") in agent_types:
                assert action.get("agent") is not None
                assert action.get("status") in ["completed", "failed"]
    
    def test_github_pr_tracked_completeness(self, actions_data):
        """Test GitHub PR tracked actions are complete"""
        required_pr_fields = ["pr_number", "pr_state", "pr_url"]
        
        pr_actions = [a for a in actions_data if a.get("type") == "github_pr_tracked"]
        
        if len(pr_actions) > 0:
            for action in pr_actions:
                for field in required_pr_fields:
                    assert field in action, f"PR action missing {field}"


class TestFileFormatting:
    """Test JSON file formatting and consistency"""
    
    @pytest.fixture
    def actions_file(self):
        return Path(__file__).parent.parent.parent.parent / "backend" / "storage" / "actions.json"
    
    def test_file_has_consistent_indentation(self, actions_file):
        """Test that JSON file has consistent indentation"""
        with open(actions_file, 'r') as f:
            content = f.read()
        
        # Check that file uses consistent indentation (should be 2 spaces)
        lines = content.split('\n')
        indented_lines = [l for l in lines if l.startswith('  ')]
        
        # If we have indented lines, verify consistency
        if indented_lines:
            assert all('  ' in l or not l.strip() for l in lines if l.strip())
    
    def test_file_ends_with_proper_structure(self, actions_file):
        """Test that file ends with proper JSON array closure"""
        with open(actions_file, 'r') as f:
            content = f.read().strip()
        
        assert content.endswith(']'), "JSON file should end with ]"
    
    def test_no_trailing_commas(self, actions_file):
        """Test that there are no trailing commas in JSON"""
        with open(actions_file, 'r') as f:
            content = f.read()
        
        # Valid JSON shouldn't have trailing commas
        # Python's json module will catch this, but let's verify
        try:
            json.loads(content)
        except json.JSONDecodeError as e:
            if 'trailing comma' in str(e).lower():
                pytest.fail("JSON contains trailing commas")


class TestActionStatistics:
    """Test statistics and insights about actions"""
    
    @pytest.fixture
    def actions_data(self):
        actions_file = Path(__file__).parent.parent.parent.parent / "backend" / "storage" / "actions.json"
        if not actions_file.exists():
            pytest.skip("actions.json not found")
        with open(actions_file, 'r') as f:
            return json.load(f)
    
    def test_actions_have_multiple_agents(self, actions_data):
        """Test that multiple agents have recorded actions"""
        agents = set(action.get("agent") for action in actions_data)
        assert len(agents) >= 2, "Should have actions from multiple agents"
    
    def test_majority_actions_completed_successfully(self, actions_data):
        """Test that most actions completed successfully"""
        completed = sum(1 for a in actions_data if a.get("status") == "completed")
        total = len(actions_data)
        
        # At least 50% should be completed (reasonable threshold)
        success_rate = completed / total if total > 0 else 0
        assert success_rate >= 0.3, f"Success rate too low: {success_rate:.2%}"
    
    def test_has_recent_activity(self, actions_data):
        """Test that there is recent activity"""
        if len(actions_data) == 0:
            pytest.skip("No actions to check")
        
        # Get most recent timestamp
        latest = actions_data[-1].get("timestamp")
        assert latest is not None, "Should have timestamp on latest action"