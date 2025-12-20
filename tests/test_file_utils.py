"""
Comprehensive unit tests for backend/services/file_utils.py

Tests cover:
- JSON file reading and writing
- Path handling and validation
- Error conditions (missing files, invalid JSON, permissions)
- Edge cases (empty files, nested directories, unicode)
"""
import pytest
import json
from pathlib import Path
from services.file_utils import read_json, write_json


class TestReadJson:
    """Test suite for read_json function."""
    
    def test_read_json_existing_file(self, tmp_path):
        """Test reading a valid JSON file."""
        test_file = tmp_path / "test.json"
        test_data = {"key": "value", "number": 42}
        test_file.write_text(json.dumps(test_data))
        
        result = read_json(test_file)
        assert result == test_data
    
    def test_read_json_nonexistent_file(self, tmp_path):
        """Test reading a file that doesn't exist returns empty dict."""
        test_file = tmp_path / "nonexistent.json"
        result = read_json(test_file)
        assert result == {}
    
    def test_read_json_empty_file(self, tmp_path):
        """Test reading an empty file."""
        test_file = tmp_path / "empty.json"
        test_file.write_text("")
        
        with pytest.raises(json.JSONDecodeError):
            read_json(test_file)
    
    def test_read_json_invalid_json(self, tmp_path):
        """Test reading a file with invalid JSON."""
        test_file = tmp_path / "invalid.json"
        test_file.write_text("not valid json {]")
        
        with pytest.raises(json.JSONDecodeError):
            read_json(test_file)
    
    def test_read_json_with_unicode(self, tmp_path):
        """Test reading JSON with unicode characters."""
        test_file = tmp_path / "unicode.json"
        test_data = {"message": "Hello 世界 🌍", "emoji": "🚀"}
        test_file.write_text(json.dumps(test_data), encoding="utf-8")
        
        result = read_json(test_file)
        assert result == test_data
    
    def test_read_json_nested_data(self, tmp_path):
        """Test reading JSON with nested structures."""
        test_file = tmp_path / "nested.json"
        test_data = {
            "level1": {
                "level2": {
                    "level3": ["a", "b", "c"]
                }
            }
        }
        test_file.write_text(json.dumps(test_data))
        
        result = read_json(test_file)
        assert result == test_data
    
    def test_read_json_array(self, tmp_path):
        """Test reading JSON array."""
        test_file = tmp_path / "array.json"
        test_data = [1, 2, 3, {"key": "value"}]
        test_file.write_text(json.dumps(test_data))
        
        result = read_json(test_file)
        assert result == test_data
    
    def test_read_json_with_pathlib(self, tmp_path):
        """Test reading with pathlib.Path object."""
        test_file = tmp_path / "test.json"
        test_data = {"test": True}
        test_file.write_text(json.dumps(test_data))
        
        result = read_json(Path(test_file))
        assert result == test_data
    
    def test_read_json_with_string_path(self, tmp_path):
        """Test reading with string path."""
        test_file = tmp_path / "test.json"
        test_data = {"test": True}
        test_file.write_text(json.dumps(test_data))
        
        result = read_json(str(test_file))
        assert result == test_data


class TestWriteJson:
    """Test suite for write_json function."""
    
    def test_write_json_basic(self, tmp_path):
        """Test writing basic JSON data."""
        test_file = tmp_path / "output.json"
        test_data = {"key": "value", "number": 42}
        
        write_json(test_file, test_data)
        
        assert test_file.exists()
        content = json.loads(test_file.read_text())
        assert content == test_data
    
    def test_write_json_creates_parent_dirs(self, tmp_path):
        """Test that write_json creates parent directories."""
        test_file = tmp_path / "nested" / "deep" / "file.json"
        test_data = {"created": True}
        
        write_json(test_file, test_data)
        
        assert test_file.exists()
        content = json.loads(test_file.read_text())
        assert content == test_data
    
    def test_write_json_overwrites_existing(self, tmp_path):
        """Test that write_json overwrites existing files."""
        test_file = tmp_path / "overwrite.json"
        old_data = {"old": "data"}
        new_data = {"new": "data"}
        
        test_file.write_text(json.dumps(old_data))
        write_json(test_file, new_data)
        
        content = json.loads(test_file.read_text())
        assert content == new_data
        assert content != old_data
    
    def test_write_json_with_unicode(self, tmp_path):
        """Test writing JSON with unicode characters."""
        test_file = tmp_path / "unicode.json"
        test_data = {"message": "Hello 世界 🌍", "emoji": "🚀"}
        
        write_json(test_file, test_data)
        
        content = json.loads(test_file.read_text(encoding="utf-8"))
        assert content == test_data
    
    def test_write_json_formatted(self, tmp_path):
        """Test that JSON is written with indentation."""
        test_file = tmp_path / "formatted.json"
        test_data = {"key": "value"}
        
        write_json(test_file, test_data)
        
        content = test_file.read_text()
        assert "\n" in content  # Check for formatting
        assert "  " in content  # Check for indentation
    
    def test_write_json_array(self, tmp_path):
        """Test writing JSON array."""
        test_file = tmp_path / "array.json"
        test_data = [1, 2, 3, {"key": "value"}]
        
        write_json(test_file, test_data)
        
        content = json.loads(test_file.read_text())
        assert content == test_data
    
    def test_write_json_empty_dict(self, tmp_path):
        """Test writing empty dictionary."""
        test_file = tmp_path / "empty.json"
        test_data = {}
        
        write_json(test_file, test_data)
        
        assert test_file.exists()
        content = json.loads(test_file.read_text())
        assert content == {}
    
    def test_write_json_empty_list(self, tmp_path):
        """Test writing empty list."""
        test_file = tmp_path / "empty_list.json"
        test_data = []
        
        write_json(test_file, test_data)
        
        content = json.loads(test_file.read_text())
        assert content == []


class TestFileUtilsIntegration:
    """Integration tests for file_utils functions."""
    
    def test_read_write_round_trip(self, tmp_path):
        """Test reading data that was just written."""
        test_file = tmp_path / "roundtrip.json"
        test_data = {
            "string": "value",
            "number": 42,
            "float": 3.14,
            "bool": True,
            "null": None,
            "array": [1, 2, 3],
            "nested": {"key": "value"}
        }
        
        write_json(test_file, test_data)
        result = read_json(test_file)
        
        assert result == test_data
    
    def test_multiple_writes(self, tmp_path):
        """Test multiple successive writes."""
        test_file = tmp_path / "multiple.json"
        
        for i in range(5):
            data = {"iteration": i}
            write_json(test_file, data)
            result = read_json(test_file)
            assert result == data
    
    def test_concurrent_operations(self, tmp_path):
        """Test reading and writing to different files."""
        file1 = tmp_path / "file1.json"
        file2 = tmp_path / "file2.json"
        data1 = {"file": 1}
        data2 = {"file": 2}
        
        write_json(file1, data1)
        write_json(file2, data2)
        
        assert read_json(file1) == data1
        assert read_json(file2) == data2


class TestFileUtilsEdgeCases:
    """Edge case tests for file_utils."""
    
    def test_very_large_json(self, tmp_path):
        """Test handling of large JSON files."""
        test_file = tmp_path / "large.json"
        large_data = {f"key_{i}": f"value_{i}" for i in range(1000)}
        
        write_json(test_file, large_data)
        result = read_json(test_file)
        
        assert len(result) == 1000
        assert result == large_data
    
    def test_special_characters_in_path(self, tmp_path):
        """Test paths with special characters."""
        test_file = tmp_path / "test-file_123.json"
        test_data = {"test": True}
        
        write_json(test_file, test_data)
        result = read_json(test_file)
        
        assert result == test_data
    
    def test_deeply_nested_structure(self, tmp_path):
        """Test deeply nested JSON structure."""
        test_file = tmp_path / "deep.json"
        test_data = {"level": 1}
        current = test_data
        for i in range(2, 20):
            current["nested"] = {"level": i}
            current = current["nested"]
        
        write_json(test_file, test_data)
        result = read_json(test_file)
        
        assert result == test_data