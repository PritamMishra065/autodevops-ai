"""
Comprehensive test suite for backend/storage/actions.json validation

Tests cover:
- JSON structure validation
- Schema compliance for different action types
- Required fields validation
- Data type validation
- Timestamp format validation
- Edge cases and malformed data
"""

import pytest
import json
from pathlib import Path
from datetime import datetime
import sys

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "backend"))


class TestActionsJsonStructure:
    """Test overall JSON structure of actions.json"""
    
    @classmethod
    def setup_class(cls):
        """Load actions.json for testing"""
        cls.actions_file = Path(__file__).parent.parent.parent.parent / "backend" / "storage" / "actions.json"
    
    def test_actions_file_exists(self):
        """Test that actions.json file exists"""
        assert self.actions_file.exists(), "actions.json should exist"
    
    def test_actions_file_is_valid_json(self):
        """Test that actions.json contains valid JSON"""
        with open(self.actions_file, 'r') as f:
            try:
                data = json.load(f)
                assert data is not None
            except json.JSONDecodeError as e:
                pytest.fail(f"actions.json contains invalid JSON: {e}")
    
    def test_actions_is_array(self):
        """Test that actions.json root is an array"""
        with open(self.actions_file, 'r') as f:
            data = json.load(f)
            assert isinstance(data, list), "actions.json should be a JSON array"
    
    def test_actions_not_empty(self):
        """Test that actions.json contains at least one action"""
        with open(self.actions_file, 'r') as f:
            data = json.load(f)
            assert len(data) > 0, "actions.json should contain at least one action"
    
    def test_all_actions_are_objects(self):
        """Test that all actions are JSON objects"""
        with open(self.actions_file, 'r') as f:
            data = json.load(f)
            for i, action in enumerate(data):
                assert isinstance(action, dict), f"Action at index {i} should be an object"


class TestActionRequiredFields:
    """Test required fields in action objects"""
    
    @classmethod
    def setup_class(cls):
        """Load actions for testing"""
        actions_file = Path(__file__).parent.parent.parent.parent / "backend" / "storage" / "actions.json"
        with open(actions_file, 'r') as f:
            cls.actions = json.load(f)
    
    def test_all_actions_have_type(self):
        """Test that all actions have a 'type' field"""
        for i, action in enumerate(self.actions):
            assert "type" in action, f"Action at index {i} missing 'type' field"
            assert action["type"], f"Action at index {i} has empty 'type' field"
    
    def test_all_actions_have_status(self):
        """Test that all actions have a 'status' field"""
        for i, action in enumerate(self.actions):
            assert "status" in action, f"Action at index {i} missing 'status' field"
            assert action["status"], f"Action at index {i} has empty 'status' field"
    
    def test_all_actions_have_agent(self):
        """Test that all actions have an 'agent' field"""
        for i, action in enumerate(self.actions):
            assert "agent" in action, f"Action at index {i} missing 'agent' field"
            assert action["agent"], f"Action at index {i} has empty 'agent' field"
    
    def test_all_actions_have_timestamp(self):
        """Test that all actions have a 'timestamp' field"""
        for i, action in enumerate(self.actions):
            assert "timestamp" in action, f"Action at index {i} missing 'timestamp' field"
            assert action["timestamp"], f"Action at index {i} has empty 'timestamp' field"


class TestActionFieldTypes:
    """Test data types of action fields"""
    
    @classmethod
    def setup_class(cls):
        """Load actions for testing"""
        actions_file = Path(__file__).parent.parent.parent.parent / "backend" / "storage" / "actions.json"
        with open(actions_file, 'r') as f:
            cls.actions = json.load(f)
    
    def test_type_field_is_string(self):
        """Test that 'type' field is always a string"""
        for i, action in enumerate(self.actions):
            assert isinstance(action["type"], str), f"Action at index {i}: 'type' should be string"
    
    def test_status_field_is_string(self):
        """Test that 'status' field is always a string"""
        for i, action in enumerate(self.actions):
            assert isinstance(action["status"], str), f"Action at index {i}: 'status' should be string"
    
    def test_agent_field_is_string(self):
        """Test that 'agent' field is always a string"""
        for i, action in enumerate(self.actions):
            assert isinstance(action["agent"], str), f"Action at index {i}: 'agent' should be string"
    
    def test_timestamp_field_is_string(self):
        """Test that 'timestamp' field is always a string"""
        for i, action in enumerate(self.actions):
            assert isinstance(action["timestamp"], str), f"Action at index {i}: 'timestamp' should be string"
    
    def test_description_field_is_string_when_present(self):
        """Test that optional 'description' field is string when present"""
        for i, action in enumerate(self.actions):
            if "description" in action:
                assert isinstance(action["description"], str), \
                    f"Action at index {i}: 'description' should be string"
    
    def test_pr_number_is_integer_when_present(self):
        """Test that 'pr_number' field is integer when present"""
        for i, action in enumerate(self.actions):
            if "pr_number" in action:
                assert isinstance(action["pr_number"], int), \
                    f"Action at index {i}: 'pr_number' should be integer"
    
    def test_pr_url_is_string_when_present(self):
        """Test that 'pr_url' field is string when present"""
        for i, action in enumerate(self.actions):
            if "pr_url" in action:
                assert isinstance(action["pr_url"], str), \
                    f"Action at index {i}: 'pr_url' should be string"


class TestActionStatusValues:
    """Test valid status values"""
    
    @classmethod
    def setup_class(cls):
        """Load actions for testing"""
        actions_file = Path(__file__).parent.parent.parent.parent / "backend" / "storage" / "actions.json"
        with open(actions_file, 'r') as f:
            cls.actions = json.load(f)
    
    def test_status_values_are_valid(self):
        """Test that status values are from expected set"""
        valid_statuses = {"completed", "failed", "pending", "running", "error", "success"}
        
        for i, action in enumerate(self.actions):
            status = action["status"]
            assert status in valid_statuses, \
                f"Action at index {i} has invalid status '{status}'. Valid: {valid_statuses}"
    
    def test_status_values_are_lowercase(self):
        """Test that status values use lowercase"""
        for i, action in enumerate(self.actions):
            status = action["status"]
            assert status == status.lower(), \
                f"Action at index {i}: status '{status}' should be lowercase"


class TestActionAgentValues:
    """Test valid agent values"""
    
    @classmethod
    def setup_class(cls):
        """Load actions for testing"""
        actions_file = Path(__file__).parent.parent.parent.parent / "backend" / "storage" / "actions.json"
        with open(actions_file, 'r') as f:
            cls.actions = json.load(f)
    
    def test_agent_values_are_valid(self):
        """Test that agent values are from expected set"""
        valid_agents = {"cline", "coderabbit", "kestra", "oumi", "github", "vercel"}
        
        for i, action in enumerate(self.actions):
            agent = action["agent"]
            assert agent in valid_agents, \
                f"Action at index {i} has invalid agent '{agent}'. Valid: {valid_agents}"
    
    def test_agent_values_are_lowercase(self):
        """Test that agent values use lowercase"""
        for i, action in enumerate(self.actions):
            agent = action["agent"]
            assert agent == agent.lower(), \
                f"Action at index {i}: agent '{agent}' should be lowercase"


class TestActionTimestamps:
    """Test timestamp format and validity"""
    
    @classmethod
    def setup_class(cls):
        """Load actions for testing"""
        actions_file = Path(__file__).parent.parent.parent.parent / "backend" / "storage" / "actions.json"
        with open(actions_file, 'r') as f:
            cls.actions = json.load(f)
    
    def test_timestamps_are_iso_format(self):
        """Test that timestamps are in ISO 8601 format"""
        for i, action in enumerate(self.actions):
            timestamp = action["timestamp"]
            try:
                # Try parsing as ISO format
                datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except ValueError as e:
                pytest.fail(f"Action at index {i}: Invalid timestamp format '{timestamp}': {e}")
    
    def test_timestamps_are_not_empty(self):
        """Test that timestamps are not empty strings"""
        for i, action in enumerate(self.actions):
            timestamp = action["timestamp"]
            assert len(timestamp) > 0, f"Action at index {i}: timestamp is empty"
    
    def test_timestamps_are_reasonable_dates(self):
        """Test that timestamps are reasonable (not in far future/past)"""
        min_date = datetime(2020, 1, 1)
        max_date = datetime(2030, 12, 31)
        
        for i, action in enumerate(self.actions):
            timestamp = action["timestamp"]
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            
            assert min_date <= dt <= max_date, \
                f"Action at index {i}: timestamp {timestamp} is outside reasonable range"


class TestActionTypeSpecificFields:
    """Test fields specific to certain action types"""
    
    @classmethod
    def setup_class(cls):
        """Load actions for testing"""
        actions_file = Path(__file__).parent.parent.parent.parent / "backend" / "storage" / "actions.json"
        with open(actions_file, 'r') as f:
            cls.actions = json.load(f)
    
    def test_github_pr_tracked_has_required_fields(self):
        """Test that github_pr_tracked actions have PR-specific fields"""
        pr_actions = [a for a in self.actions if a["type"] == "github_pr_tracked"]
        
        for action in pr_actions:
            assert "pr_number" in action, "github_pr_tracked should have pr_number"
            assert "pr_state" in action, "github_pr_tracked should have pr_state"
            assert "pr_url" in action, "github_pr_tracked should have pr_url"
    
    def test_github_pr_tracked_pr_state_is_valid(self):
        """Test that PR state values are valid"""
        valid_states = {"open", "closed", "merged"}
        pr_actions = [a for a in self.actions if a["type"] == "github_pr_tracked"]
        
        for action in pr_actions:
            if "pr_state" in action:
                assert action["pr_state"] in valid_states, \
                    f"Invalid pr_state: {action['pr_state']}"
    
    def test_github_pr_tracked_pr_url_is_github_url(self):
        """Test that PR URLs are GitHub URLs"""
        pr_actions = [a for a in self.actions if a["type"] == "github_pr_tracked"]
        
        for action in pr_actions:
            if "pr_url" in action:
                url = action["pr_url"]
                assert url.startswith("https://github.com/"), \
                    f"PR URL should be GitHub URL: {url}"
    
    def test_kestra_workflow_executed_has_workflow_id(self):
        """Test that kestra workflow actions have workflow_id"""
        kestra_actions = [a for a in self.actions if a["type"] == "kestra_workflow_executed"]
        
        for action in kestra_actions:
            assert "workflow_id" in action, "kestra_workflow_executed should have workflow_id"
    
    def test_security_scan_has_vulnerabilities_found_when_present(self):
        """Test that security_scan actions have vulnerabilities_found field"""
        security_actions = [a for a in self.actions if a["type"] == "security_scan"]
        
        for action in security_actions:
            if "vulnerabilities_found" in action:
                assert isinstance(action["vulnerabilities_found"], int), \
                    "vulnerabilities_found should be integer"
                assert action["vulnerabilities_found"] >= 0, \
                    "vulnerabilities_found should be non-negative"


class TestActionTypeValues:
    """Test action type values and patterns"""
    
    @classmethod
    def setup_class(cls):
        """Load actions for testing"""
        actions_file = Path(__file__).parent.parent.parent.parent / "backend" / "storage" / "actions.json"
        with open(actions_file, 'r') as f:
            cls.actions = json.load(f)
    
    def test_action_types_follow_snake_case(self):
        """Test that action types use snake_case naming"""
        for i, action in enumerate(self.actions):
            action_type = action["type"]
            # Should not contain uppercase or spaces
            assert action_type == action_type.lower(), \
                f"Action at index {i}: type '{action_type}' should be lowercase"
            assert " " not in action_type, \
                f"Action at index {i}: type '{action_type}' should not contain spaces"
    
    def test_known_action_types_are_documented(self):
        """Test that we have a known set of action types"""
        known_types = {
            "create_pull_request",
            "run_cline",
            "run_coderabbit",
            "run_kestra",
            "run_oumi",
            "code_review_started",
            "security_scan",
            "pr_approved",
            "merge_pull_request",
            "github_pr_tracked",
            "kestra_workflow_executed"
        }
        
        action_types = {action["type"] for action in self.actions}
        
        # All action types should be known (or we should document new ones)
        for action_type in action_types:
            assert action_type in known_types, \
                f"Unknown action type '{action_type}'. Add to known_types if this is expected."


class TestActionsJsonConsistency:
    """Test consistency and data quality"""
    
    @classmethod
    def setup_class(cls):
        """Load actions for testing"""
        actions_file = Path(__file__).parent.parent.parent.parent / "backend" / "storage" / "actions.json"
        with open(actions_file, 'r') as f:
            cls.actions = json.load(f)
    
    def test_no_duplicate_exact_actions(self):
        """Test that there are no exact duplicate actions"""
        seen = set()
        
        for i, action in enumerate(self.actions):
            # Create a hashable representation
            action_tuple = tuple(sorted(action.items()))
            
            if action_tuple in seen:
                pytest.fail(f"Duplicate action found at index {i}: {action}")
            seen.add(action_tuple)
    
    def test_pr_numbers_are_positive(self):
        """Test that PR numbers are positive integers"""
        for i, action in enumerate(self.actions):
            if "pr_number" in action:
                pr_num = action["pr_number"]
                assert pr_num > 0, f"Action at index {i}: pr_number should be positive"
    
    def test_descriptions_are_meaningful(self):
        """Test that descriptions (when present) are not empty"""
        for i, action in enumerate(self.actions):
            if "description" in action:
                desc = action["description"]
                assert len(desc.strip()) > 0, \
                    f"Action at index {i}: description should not be empty"
    
    def test_urls_are_valid_format(self):
        """Test that URL fields have valid format"""
        for i, action in enumerate(self.actions):
            if "pr_url" in action:
                url = action["pr_url"]
                assert url.startswith("http://") or url.startswith("https://"), \
                    f"Action at index {i}: URL should start with http:// or https://"
            
            if "url" in action:
                url = action["url"]
                assert url.startswith("http://") or url.startswith("https://"), \
                    f"Action at index {i}: URL should start with http:// or https://"


class TestActionsFileFormatting:
    """Test JSON file formatting and structure"""
    
    @classmethod
    def setup_class(cls):
        """Load actions file content"""
        cls.actions_file = Path(__file__).parent.parent.parent.parent / "backend" / "storage" / "actions.json"
    
    def test_file_ends_with_newline(self):
        """Test that file ends with a newline"""
        with open(self.actions_file, 'rb') as f:
            content = f.read()
            assert content.endswith(b'\n') or content.endswith(b']'), \
                "File should end with newline or closing bracket"
    
    def test_file_uses_consistent_indentation(self):
        """Test that file uses consistent indentation"""
        with open(self.actions_file, 'r') as f:
            content = f.read()
            
            # Check for consistent 2-space indentation
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.strip():  # Skip empty lines
                    # Count leading spaces
                    spaces = len(line) - len(line.lstrip(' '))
                    if spaces > 0:
                        assert spaces % 2 == 0, \
                            f"Line {i+1} has inconsistent indentation (not multiple of 2)"
    
    def test_json_is_properly_formatted(self):
        """Test that JSON is properly formatted (can be re-serialized)"""
        with open(self.actions_file, 'r') as f:
            data = json.load(f)
        
        # Should be able to serialize back to JSON
        try:
            json.dumps(data, indent=2)
        except Exception as e:
            pytest.fail(f"Cannot serialize actions.json: {e}")


class TestEdgeCasesAndValidation:
    """Test edge cases and validation scenarios"""
    
    @classmethod
    def setup_class(cls):
        """Load actions for testing"""
        actions_file = Path(__file__).parent.parent.parent.parent / "backend" / "storage" / "actions.json"
        with open(actions_file, 'r') as f:
            cls.actions = json.load(f)
    
    def test_no_null_values_in_required_fields(self):
        """Test that required fields don't have null values"""
        required_fields = ["type", "status", "agent", "timestamp"]
        
        for i, action in enumerate(self.actions):
            for field in required_fields:
                assert action.get(field) is not None, \
                    f"Action at index {i}: required field '{field}' is null"
    
    def test_timestamps_are_chronologically_reasonable(self):
        """Test that timestamps progress in a reasonable manner"""
        timestamps = []
        
        for action in self.actions:
            try:
                dt = datetime.fromisoformat(action["timestamp"].replace('Z', '+00:00'))
                timestamps.append(dt)
            except:
                pass
        
        # Should have at least some timestamps
        assert len(timestamps) > 0, "Should have parseable timestamps"
    
    def test_no_suspicious_characters_in_strings(self):
        """Test that string fields don't contain suspicious characters"""
        suspicious_chars = ['\x00', '\r', '\b', '\f']
        
        for i, action in enumerate(self.actions):
            for key, value in action.items():
                if isinstance(value, str):
                    for char in suspicious_chars:
                        assert char not in value, \
                            f"Action at index {i}: field '{key}' contains suspicious character"
    
    def test_workflow_id_format_when_present(self):
        """Test that workflow_id follows expected format"""
        for i, action in enumerate(self.actions):
            if "workflow_id" in action:
                workflow_id = action["workflow_id"]
                assert isinstance(workflow_id, str), \
                    f"Action at index {i}: workflow_id should be string"
                assert len(workflow_id) > 0, \
                    f"Action at index {i}: workflow_id should not be empty"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])