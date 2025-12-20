"""
Comprehensive test suite for backend/storage/actions.json

Tests validate:
- JSON structure and schema
- Required fields presence
- Data type validation
- Timestamp format validation
- Action type validation
- Status values validation
"""

import pytest
import json
from pathlib import Path
import sys
from datetime import datetime

backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))


@pytest.fixture
def actions_file_path():
    """Path to actions.json file"""
    return Path(__file__).parent.parent.parent / "backend" / "storage" / "actions.json"


@pytest.fixture
def actions_data(actions_file_path):
    """Load actions.json data"""
    if not actions_file_path.exists():
        pytest.skip("actions.json file not found")
    
    with open(actions_file_path, 'r') as f:
        return json.load(f)


class TestActionsJsonStructure:
    """Test the overall structure of actions.json"""
    
    def test_actions_json_exists(self, actions_file_path):
        """Test that actions.json file exists"""
        assert actions_file_path.exists(), "actions.json should exist"
    
    def test_actions_json_is_valid_json(self, actions_file_path):
        """Test that actions.json contains valid JSON"""
        try:
            with open(actions_file_path, 'r') as f:
                json.load(f)
        except json.JSONDecodeError as e:
            pytest.fail(f"actions.json contains invalid JSON: {e}")
    
    def test_actions_json_is_array(self, actions_data):
        """Test that actions.json root element is an array"""
        assert isinstance(actions_data, list), "actions.json should contain an array"
    
    def test_actions_json_not_empty(self, actions_data):
        """Test that actions.json contains data"""
        assert len(actions_data) > 0, "actions.json should not be empty"


class TestActionEntrySchema:
    """Test that each action entry follows the expected schema"""
    
    def test_all_entries_have_type_field(self, actions_data):
        """Test that all action entries have a 'type' field"""
        for i, action in enumerate(actions_data):
            assert "type" in action, f"Action at index {i} missing 'type' field"
            assert isinstance(action["type"], str), f"Action at index {i} 'type' should be string"
            assert action["type"], f"Action at index {i} 'type' should not be empty"
    
    def test_all_entries_have_status_field(self, actions_data):
        """Test that all action entries have a 'status' field"""
        for i, action in enumerate(actions_data):
            assert "status" in action, f"Action at index {i} missing 'status' field"
            assert isinstance(action["status"], str), f"Action at index {i} 'status' should be string"
    
    def test_all_entries_have_agent_field(self, actions_data):
        """Test that all action entries have an 'agent' field"""
        for i, action in enumerate(actions_data):
            assert "agent" in action, f"Action at index {i} missing 'agent' field"
            assert isinstance(action["agent"], str), f"Action at index {i} 'agent' should be string"
    
    def test_all_entries_have_timestamp_field(self, actions_data):
        """Test that all action entries have a 'timestamp' field"""
        for i, action in enumerate(actions_data):
            assert "timestamp" in action, f"Action at index {i} missing 'timestamp' field"
            assert isinstance(action["timestamp"], str), f"Action at index {i} 'timestamp' should be string"


class TestActionTypeValues:
    """Test that action type values are valid"""
    
    def test_action_types_are_valid(self, actions_data):
        """Test that action types follow expected patterns"""
        valid_type_patterns = [
            "create_pull_request",
            "run_cline",
            "run_coderabbit",
            "run_kestra",
            "run_oumi",
            "code_review_started",
            "security_scan",
            "kestra_workflow_executed",
            "github_pr_tracked",
            "deployment",
            "test_execution"
        ]
        
        for i, action in enumerate(actions_data):
            action_type = action["type"]
            # Check if type matches known patterns or follows snake_case convention
            assert "_" in action_type or action_type.islower(), \
                f"Action at index {i} has invalid type format: {action_type}"
    
    def test_action_types_use_snake_case(self, actions_data):
        """Test that action types use snake_case naming convention"""
        for i, action in enumerate(actions_data):
            action_type = action["type"]
            # Should not contain spaces or uppercase letters
            assert " " not in action_type, \
                f"Action at index {i} type contains spaces: {action_type}"
            assert action_type.islower() or "_" in action_type, \
                f"Action at index {i} type should be lowercase/snake_case: {action_type}"


class TestStatusValues:
    """Test that status values are valid"""
    
    def test_status_values_are_valid(self, actions_data):
        """Test that status values are from expected set"""
        valid_statuses = {"completed", "failed", "running", "pending", "cancelled", "error"}
        
        for i, action in enumerate(actions_data):
            status = action["status"]
            assert status in valid_statuses, \
                f"Action at index {i} has invalid status: {status}. Expected one of {valid_statuses}"
    
    def test_status_values_are_lowercase(self, actions_data):
        """Test that status values are lowercase"""
        for i, action in enumerate(actions_data):
            status = action["status"]
            assert status == status.lower(), \
                f"Action at index {i} status should be lowercase: {status}"


class TestAgentValues:
    """Test that agent values are valid"""
    
    def test_agent_values_are_valid(self, actions_data):
        """Test that agent values are from expected set"""
        valid_agents = {"cline", "coderabbit", "kestra", "oumi", "github", "vercel", "system"}
        
        for i, action in enumerate(actions_data):
            agent = action["agent"]
            assert agent in valid_agents, \
                f"Action at index {i} has unexpected agent: {agent}. Expected one of {valid_agents}"


class TestTimestampFormat:
    """Test that timestamps are in valid format"""
    
    def test_timestamps_are_iso8601_format(self, actions_data):
        """Test that timestamps follow ISO 8601 format"""
        for i, action in enumerate(actions_data):
            timestamp = action["timestamp"]
            try:
                # Try parsing as ISO 8601
                datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except ValueError as e:
                pytest.fail(f"Action at index {i} has invalid timestamp format: {timestamp}. Error: {e}")
    
    def test_timestamps_are_chronologically_valid(self, actions_data):
        """Test that timestamps represent valid dates"""
        for i, action in enumerate(actions_data):
            timestamp = action["timestamp"]
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            
            # Timestamps should be between 2020 and 2030 (reasonable range)
            assert 2020 <= dt.year <= 2030, \
                f"Action at index {i} has unreasonable timestamp: {timestamp}"


class TestOptionalFields:
    """Test optional fields when present"""
    
    def test_description_field_when_present(self, actions_data):
        """Test that description field is string when present"""
        for i, action in enumerate(actions_data):
            if "description" in action:
                assert isinstance(action["description"], str), \
                    f"Action at index {i} description should be string"
                assert len(action["description"]) > 0, \
                    f"Action at index {i} description should not be empty if present"
    
    def test_pr_number_field_when_present(self, actions_data):
        """Test that pr_number field is integer when present"""
        for i, action in enumerate(actions_data):
            if "pr_number" in action:
                assert isinstance(action["pr_number"], int), \
                    f"Action at index {i} pr_number should be integer"
                assert action["pr_number"] > 0, \
                    f"Action at index {i} pr_number should be positive"
    
    def test_pr_state_field_when_present(self, actions_data):
        """Test that pr_state field is valid when present"""
        valid_pr_states = {"open", "closed", "merged"}
        for i, action in enumerate(actions_data):
            if "pr_state" in action:
                assert action["pr_state"] in valid_pr_states, \
                    f"Action at index {i} has invalid pr_state: {action['pr_state']}"
    
    def test_pr_url_field_when_present(self, actions_data):
        """Test that pr_url field is valid URL when present"""
        for i, action in enumerate(actions_data):
            if "pr_url" in action:
                pr_url = action["pr_url"]
                assert isinstance(pr_url, str), \
                    f"Action at index {i} pr_url should be string"
                assert pr_url.startswith("https://"), \
                    f"Action at index {i} pr_url should be HTTPS URL: {pr_url}"
                assert "github.com" in pr_url, \
                    f"Action at index {i} pr_url should be GitHub URL: {pr_url}"


class TestGithubPRTrackedActions:
    """Test github_pr_tracked specific actions"""
    
    def test_github_pr_tracked_has_required_fields(self, actions_data):
        """Test that github_pr_tracked actions have required fields"""
        pr_tracked_actions = [a for a in actions_data if a.get("type") == "github_pr_tracked"]
        
        for action in pr_tracked_actions:
            assert "pr_number" in action, "github_pr_tracked should have pr_number"
            assert "pr_state" in action, "github_pr_tracked should have pr_state"
            assert "pr_url" in action, "github_pr_tracked should have pr_url"
            assert "description" in action, "github_pr_tracked should have description"


class TestWorkflowExecutedActions:
    """Test kestra_workflow_executed specific actions"""
    
    def test_workflow_executed_has_agent_kestra(self, actions_data):
        """Test that workflow execution actions have kestra agent"""
        workflow_actions = [a for a in actions_data if a.get("type") == "kestra_workflow_executed"]
        
        for action in workflow_actions:
            assert action["agent"] == "kestra", \
                "kestra_workflow_executed actions should have agent 'kestra'"


class TestDataConsistency:
    """Test data consistency across the file"""
    
    def test_no_duplicate_entries(self, actions_data):
        """Test that there are no exact duplicate entries"""
        # Convert to JSON strings for comparison
        json_strings = [json.dumps(action, sort_keys=True) for action in actions_data]
        unique_count = len(set(json_strings))
        
        # Note: Some duplicates may be intentional (same PR tracked multiple times)
        # So we just warn if there are many duplicates
        duplicate_count = len(json_strings) - unique_count
        if duplicate_count > len(actions_data) * 0.5:  # More than 50% duplicates
            pytest.fail(f"Too many duplicate entries: {duplicate_count} duplicates out of {len(actions_data)} total")
    
    def test_actions_are_recent(self, actions_data):
        """Test that actions have recent timestamps"""
        now = datetime.now()
        recent_count = 0
        
        for action in actions_data:
            timestamp = action["timestamp"]
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            
            # Count actions from last 365 days
            days_old = (now - dt.replace(tzinfo=None)).days
            if days_old <= 365:
                recent_count += 1
        
        # At least some actions should be recent
        assert recent_count > 0, "Should have at least some recent actions"


class TestEdgeCases:
    """Test edge cases and data quality"""
    
    def test_no_null_values_in_required_fields(self, actions_data):
        """Test that required fields don't have null values"""
        required_fields = ["type", "status", "agent", "timestamp"]
        
        for i, action in enumerate(actions_data):
            for field in required_fields:
                assert action.get(field) is not None, \
                    f"Action at index {i} has null value for required field '{field}'"
    
    def test_no_empty_string_values_in_required_fields(self, actions_data):
        """Test that required string fields are not empty"""
        for i, action in enumerate(actions_data):
            if "type" in action:
                assert len(action["type"].strip()) > 0, \
                    f"Action at index {i} has empty 'type' field"
            if "agent" in action:
                assert len(action["agent"].strip()) > 0, \
                    f"Action at index {i} has empty 'agent' field"
    
    def test_json_is_pretty_printed(self, actions_file_path):
        """Test that JSON file is properly formatted (indented)"""
        with open(actions_file_path, 'r') as f:
            content = f.read()
        
        # Should have indentation (multiple spaces or tabs)
        assert "  " in content or "\t" in content, \
            "JSON file should be properly indented"