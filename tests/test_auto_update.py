"""
Test suite for auto-update logic (Issue #33).

Tests the version comparison, GitHub API parsing, ZIP validation, and file operation
logic that will be embedded in update.sh and update.ps1 scripts.

Written by: Mylo
Coverage: Version comparison, API parsing, ZIP validation, deployment operations
"""

import pytest
import json
import tempfile
import zipfile
import os
from pathlib import Path
from unittest.mock import Mock, patch
import shutil
import importlib.util


# ============================================================================
# Helper Functions (Logic to be embedded in update scripts)
# ============================================================================

def parse_version(version_str):
    """Parse version string to tuple of integers (major, minor, patch).
    
    Handles 'v' prefix and whitespace: 'v0.5.4' or ' 0.5.4\n' -> (0, 5, 4)
    """
    version_str = version_str.strip().lstrip('v')
    parts = version_str.split('.')
    if len(parts) != 3:
        raise ValueError(f"Invalid version format: {version_str}")
    return tuple(int(p) for p in parts)


def should_update(local_version, remote_version):
    """Return True if remote_version > local_version (semantic versioning).
    
    Handles 'v' prefix and whitespace automatically.
    """
    local = parse_version(local_version)
    remote = parse_version(remote_version)
    return remote > local


def extract_tag_from_release_json(json_str):
    """Extract and clean version tag from GitHub release JSON response.
    
    Returns version without 'v' prefix: {"tag_name": "v0.6.0"} -> "0.6.0"
    """
    data = json.loads(json_str)
    if 'tag_name' not in data:
        raise ValueError("Missing 'tag_name' in release JSON")
    tag = data['tag_name'].strip().lstrip('v')
    return tag


def validate_zip(zip_path):
    """Validate ZIP file contains required Mr. Pumpkin files.
    
    Required files: pumpkin_face.py, VERSION, requirements.txt
    Returns True if valid, False otherwise.
    """
    required_files = {'pumpkin_face.py', 'VERSION', 'requirements.txt'}
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            # Get all file names (excluding directories)
            file_names = {os.path.basename(name) for name in zf.namelist() if not name.endswith('/')}
            return required_files.issubset(file_names)
    except (zipfile.BadZipFile, FileNotFoundError):
        return False


def create_temp_dir():
    """Create temporary directory for update operations.
    
    Returns path to created directory.
    """
    return tempfile.mkdtemp(prefix='mr-pumpkin-update-')


def deploy_files(source_dir, dest_dir, preserve_configs=True):
    """Deploy files from extracted ZIP to installation directory.
    
    Args:
        source_dir: Path to extracted ZIP contents
        dest_dir: Installation directory
        preserve_configs: If True, skip timeline files (user data)
    
    Returns list of copied files.
    """
    copied_files = []
    
    for item in os.listdir(source_dir):
        source_path = os.path.join(source_dir, item)
        dest_path = os.path.join(dest_dir, item)
        
        # Skip timeline files if preservation enabled
        if preserve_configs and item.startswith('timeline_') and item.endswith('.json'):
            continue
        
        if os.path.isfile(source_path):
            shutil.copy2(source_path, dest_path)
            copied_files.append(item)
    
    return copied_files


# ============================================================================
# Test Classes
# ============================================================================

class TestVersionComparison:
    """Test semantic version comparison logic."""
    
    def test_older_minor_triggers_update(self):
        """0.5.4 vs 0.6.0 → True (minor version increase)"""
        assert should_update("0.5.4", "0.6.0") is True
    
    def test_older_patch_triggers_update(self):
        """0.5.3 vs 0.5.4 → True (patch version increase)"""
        assert should_update("0.5.3", "0.5.4") is True
    
    def test_same_version_no_update(self):
        """0.5.4 vs 0.5.4 → False (identical versions)"""
        assert should_update("0.5.4", "0.5.4") is False
    
    def test_newer_local_no_update(self):
        """0.5.5 vs 0.5.4 → False (local is newer)"""
        assert should_update("0.5.5", "0.5.4") is False
    
    def test_older_major_triggers_update(self):
        """0.5.4 vs 1.0.0 → True (major version increase)"""
        assert should_update("0.5.4", "1.0.0") is True
    
    def test_newer_major_no_update(self):
        """1.0.0 vs 0.9.9 → False (local major is newer)"""
        assert should_update("1.0.0", "0.9.9") is False
    
    def test_patch_boundary(self):
        """0.5.9 vs 0.5.10 → True (handles multi-digit patch numbers)"""
        assert should_update("0.5.9", "0.5.10") is True
    
    def test_strips_v_prefix(self):
        """v0.5.4 vs v0.6.0 → True (handles 'v' prefix in both versions)"""
        assert should_update("v0.5.4", "v0.6.0") is True
    
    def test_handles_whitespace(self):
        """ 0.5.4\n vs 0.6.0 → True (strips leading/trailing whitespace)"""
        assert should_update(" 0.5.4\n", "0.6.0") is True
    
    def test_mixed_prefix_formats(self):
        """v0.5.4 vs 0.6.0 → True (one version has 'v', other doesn't)"""
        assert should_update("v0.5.4", "0.6.0") is True
        assert should_update("0.5.4", "v0.6.0") is True
    
    def test_parse_version_invalid_format(self):
        """Invalid version format raises ValueError"""
        with pytest.raises(ValueError):
            parse_version("0.5")  # Missing patch
        with pytest.raises(ValueError):
            parse_version("1.2.3.4")  # Too many parts
        with pytest.raises(ValueError):
            parse_version("abc.def.ghi")  # Non-numeric


class TestGitHubApiParsing:
    """Test GitHub API JSON response parsing."""
    
    def test_extracts_tag_from_release_json(self):
        """Extract version from standard GitHub release JSON"""
        json_response = '{"tag_name": "v0.6.0", "name": "Release 0.6.0"}'
        assert extract_tag_from_release_json(json_response) == "0.6.0"
    
    def test_strips_v_prefix_from_tag(self):
        """v0.6.0 → 0.6.0 (removes 'v' prefix)"""
        json_response = '{"tag_name": "v0.6.0"}'
        assert extract_tag_from_release_json(json_response) == "0.6.0"
    
    def test_handles_tag_without_v_prefix(self):
        """0.6.0 → 0.6.0 (already clean, no 'v' to strip)"""
        json_response = '{"tag_name": "0.6.0"}'
        assert extract_tag_from_release_json(json_response) == "0.6.0"
    
    def test_handles_missing_tag_name(self):
        """{} → raises ValueError (missing required field)"""
        json_response = '{"name": "Some Release"}'
        with pytest.raises(ValueError, match="Missing 'tag_name'"):
            extract_tag_from_release_json(json_response)
    
    def test_handles_malformed_json(self):
        """not json → raises ValueError (JSON parsing error)"""
        with pytest.raises(json.JSONDecodeError):
            extract_tag_from_release_json("not valid json")
    
    def test_handles_whitespace_in_tag(self):
        """ v0.6.0\n → 0.6.0 (strips whitespace from tag)"""
        json_response = '{"tag_name": " v0.6.0\\n"}'
        assert extract_tag_from_release_json(json_response) == "0.6.0"


class TestZipValidation:
    """Test ZIP file validation logic."""
    
    def test_valid_zip_with_required_files_passes(self):
        """ZIP with pumpkin_face.py, VERSION, requirements.txt → valid"""
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp:
            zip_path = tmp.name
        
        try:
            with zipfile.ZipFile(zip_path, 'w') as zf:
                zf.writestr('pumpkin_face.py', '# Main file')
                zf.writestr('VERSION', '0.6.0')
                zf.writestr('requirements.txt', 'pygame>=2.0.0')
            
            assert validate_zip(zip_path) is True
        finally:
            os.unlink(zip_path)
    
    def test_zip_missing_pumpkin_face_fails(self):
        """ZIP without pumpkin_face.py → invalid"""
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp:
            zip_path = tmp.name
        
        try:
            with zipfile.ZipFile(zip_path, 'w') as zf:
                zf.writestr('VERSION', '0.6.0')
                zf.writestr('requirements.txt', 'pygame>=2.0.0')
            
            assert validate_zip(zip_path) is False
        finally:
            os.unlink(zip_path)
    
    def test_zip_missing_version_file_fails(self):
        """ZIP without VERSION → invalid"""
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp:
            zip_path = tmp.name
        
        try:
            with zipfile.ZipFile(zip_path, 'w') as zf:
                zf.writestr('pumpkin_face.py', '# Main file')
                zf.writestr('requirements.txt', 'pygame>=2.0.0')
            
            assert validate_zip(zip_path) is False
        finally:
            os.unlink(zip_path)
    
    def test_zip_missing_requirements_fails(self):
        """ZIP without requirements.txt → invalid"""
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp:
            zip_path = tmp.name
        
        try:
            with zipfile.ZipFile(zip_path, 'w') as zf:
                zf.writestr('pumpkin_face.py', '# Main file')
                zf.writestr('VERSION', '0.6.0')
            
            assert validate_zip(zip_path) is False
        finally:
            os.unlink(zip_path)
    
    def test_empty_zip_fails(self):
        """Empty ZIP → invalid"""
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp:
            zip_path = tmp.name
        
        try:
            with zipfile.ZipFile(zip_path, 'w') as zf:
                pass  # Empty ZIP
            
            assert validate_zip(zip_path) is False
        finally:
            os.unlink(zip_path)
    
    def test_corrupted_zip_fails(self):
        """Corrupted ZIP file → invalid"""
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp:
            tmp.write(b'This is not a ZIP file')
            zip_path = tmp.name
        
        try:
            assert validate_zip(zip_path) is False
        finally:
            os.unlink(zip_path)
    
    def test_nonexistent_zip_fails(self):
        """Non-existent file path → invalid"""
        assert validate_zip('/nonexistent/path/to/file.zip') is False
    
    def test_zip_with_subdirectory_structure(self):
        """ZIP with files in subdirectories → valid (extracts basenames)"""
        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp:
            zip_path = tmp.name
        
        try:
            with zipfile.ZipFile(zip_path, 'w') as zf:
                zf.writestr('mr-pumpkin/pumpkin_face.py', '# Main file')
                zf.writestr('mr-pumpkin/VERSION', '0.6.0')
                zf.writestr('mr-pumpkin/requirements.txt', 'pygame>=2.0.0')
            
            assert validate_zip(zip_path) is True
        finally:
            os.unlink(zip_path)


class TestFileOperations:
    """Test file path and directory operations."""
    
    def test_temp_dir_creation(self):
        """Temp dir is created, path returned, exists on disk"""
        temp_dir = create_temp_dir()
        
        try:
            assert temp_dir is not None
            assert os.path.exists(temp_dir)
            assert os.path.isdir(temp_dir)
            assert 'mr-pumpkin-update-' in temp_dir
        finally:
            if os.path.exists(temp_dir):
                os.rmdir(temp_dir)
    
    def test_deploy_copies_required_files(self):
        """Files from extracted ZIP end up in install dir"""
        source_dir = tempfile.mkdtemp()
        dest_dir = tempfile.mkdtemp()
        
        try:
            # Create source files
            Path(source_dir, 'pumpkin_face.py').write_text('# Main file')
            Path(source_dir, 'VERSION').write_text('0.6.0')
            Path(source_dir, 'requirements.txt').write_text('pygame>=2.0.0')
            
            # Deploy files
            copied = deploy_files(source_dir, dest_dir)
            
            # Verify files copied
            assert 'pumpkin_face.py' in copied
            assert 'VERSION' in copied
            assert 'requirements.txt' in copied
            assert os.path.exists(os.path.join(dest_dir, 'pumpkin_face.py'))
            assert os.path.exists(os.path.join(dest_dir, 'VERSION'))
            assert os.path.exists(os.path.join(dest_dir, 'requirements.txt'))
        finally:
            shutil.rmtree(source_dir, ignore_errors=True)
            shutil.rmtree(dest_dir, ignore_errors=True)
    
    def test_deploy_preserves_existing_config(self):
        """Doesn't overwrite local timeline files (user data)"""
        source_dir = tempfile.mkdtemp()
        dest_dir = tempfile.mkdtemp()
        
        try:
            # Create source files (including a timeline)
            Path(source_dir, 'pumpkin_face.py').write_text('# Main file')
            Path(source_dir, 'VERSION').write_text('0.6.0')
            Path(source_dir, 'timeline_example.json').write_text('{"commands": []}')
            
            # Create existing timeline in dest (user data to preserve)
            user_timeline_path = Path(dest_dir, 'timeline_custom.json')
            user_timeline_path.write_text('{"commands": ["user data"]}')
            
            # Deploy files with preservation enabled
            copied = deploy_files(source_dir, dest_dir, preserve_configs=True)
            
            # Verify timeline not in copied list
            assert 'timeline_example.json' not in copied
            
            # Verify user timeline unchanged
            assert user_timeline_path.exists()
            assert 'user data' in user_timeline_path.read_text()
        finally:
            shutil.rmtree(source_dir, ignore_errors=True)
            shutil.rmtree(dest_dir, ignore_errors=True)
    
    def test_deploy_without_preservation_copies_all(self):
        """When preserve_configs=False, all files copied including timelines"""
        source_dir = tempfile.mkdtemp()
        dest_dir = tempfile.mkdtemp()
        
        try:
            # Create source files including timeline
            Path(source_dir, 'pumpkin_face.py').write_text('# Main file')
            Path(source_dir, 'timeline_example.json').write_text('{"commands": []}')
            
            # Deploy without preservation
            copied = deploy_files(source_dir, dest_dir, preserve_configs=False)
            
            # Verify timeline WAS copied
            assert 'timeline_example.json' in copied
            assert os.path.exists(os.path.join(dest_dir, 'timeline_example.json'))
        finally:
            shutil.rmtree(source_dir, ignore_errors=True)
            shutil.rmtree(dest_dir, ignore_errors=True)


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_version_with_prerelease_suffix(self):
        """0.5.4 vs 0.6.0-beta.1 → comparison on base version only"""
        # For v1, we'll treat pre-release as part of patch number (will fail)
        # This documents the limitation - proper handling is v2 feature
        with pytest.raises(ValueError):
            should_update("0.5.4", "0.6.0-beta.1")
    
    def test_very_large_version_numbers(self):
        """Handles large version numbers (e.g., 99.99.99)"""
        assert should_update("99.99.98", "99.99.99") is True
        assert should_update("1.0.0", "99.99.99") is True
    
    def test_deploy_to_nonexistent_destination(self):
        """Deploy to non-existent directory → should fail gracefully"""
        source_dir = tempfile.mkdtemp()
        dest_dir = os.path.join(tempfile.gettempdir(), 'nonexistent_dir_xyz')
        
        try:
            Path(source_dir, 'pumpkin_face.py').write_text('# Main file')
            
            # Should raise error (directory doesn't exist)
            with pytest.raises(FileNotFoundError):
                deploy_files(source_dir, dest_dir)
        finally:
            shutil.rmtree(source_dir, ignore_errors=True)


class TestReleasePackaging:
    """Test release package contents that support installation and updates."""

    @staticmethod
    def load_package_release_module():
        """Load the release packaging script as a module for testing."""
        repo_root = Path(__file__).resolve().parent.parent
        module_path = repo_root / "scripts" / "package_release.py"
        spec = importlib.util.spec_from_file_location("package_release", module_path)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        return module

    def test_release_package_includes_update_scripts(self, monkeypatch):
        """Generated release ZIP contains both cross-platform update scripts."""
        repo_root = Path(__file__).resolve().parent.parent
        module = self.load_package_release_module()
        version = module.read_version()
        archive_name = f"mr-pumpkin-v{version}.zip"
        folder_name = f"mr-pumpkin-v{version}"
        archive_path = repo_root / archive_name

        if archive_path.exists():
            archive_path.unlink()

        monkeypatch.chdir(repo_root)

        try:
            created_archive = module.create_release_package()
            assert Path(created_archive) == Path(archive_name)
            assert archive_path.exists()

            with zipfile.ZipFile(archive_path, "r") as zf:
                file_names = set(zf.namelist())

            assert f"{folder_name}/update.sh" in file_names
            assert f"{folder_name}/update.ps1" in file_names
            assert f"{folder_name}/scripts/unix_dependency_plan.py" in file_names
        finally:
            if archive_path.exists():
                archive_path.unlink()


class TestUnixDependencyPlan:
    """Test the Raspberry Pi dependency planning helper used by shell scripts."""

    @staticmethod
    def load_dependency_plan_module():
        repo_root = Path(__file__).resolve().parent.parent
        module_path = repo_root / "scripts" / "unix_dependency_plan.py"
        spec = importlib.util.spec_from_file_location("unix_dependency_plan", module_path)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        return module

    def test_raspberry_pi_plan_prefers_supported_apt_packages(self, tmp_path):
        module = self.load_dependency_plan_module()
        requirements = tmp_path / "requirements.txt"
        requirements.write_text(
            "\n".join(
                [
                    "pygame>=2.0.0,<3.0.0",
                    "websockets>=13.0,<15.1",
                    "google-genai>=1.0.0",
                    "mutagen>=1.45.0",
                    "openai>=1.0.0",
                ]
            )
        )

        plan = module.build_install_plan([requirements], raspberry_pi=True)

        assert plan.apt_packages == [
            "python3-mutagen",
            "python3-pygame",
            "python3-websockets",
        ]
        assert plan.pip_requirements == [
            "google-genai>=1.0.0",
            "openai>=1.0.0",
        ]

    def test_non_pi_plan_leaves_requirements_with_pip(self, tmp_path):
        module = self.load_dependency_plan_module()
        requirements = tmp_path / "requirements.txt"
        requirements.write_text("pygame>=2.0.0,<3.0.0\nwebsockets>=13.0,<15.1\n")

        plan = module.build_install_plan([requirements], raspberry_pi=False)

        assert plan.apt_packages == []
        assert plan.pip_requirements == [
            "pygame>=2.0.0,<3.0.0",
            "websockets>=13.0,<15.1",
        ]

    def test_nested_requirement_files_are_expanded_once(self, tmp_path):
        module = self.load_dependency_plan_module()
        child = tmp_path / "child.txt"
        child.write_text("websockets>=13.0,<15.1\n")
        parent = tmp_path / "requirements.txt"
        parent.write_text("-r child.txt\n-r child.txt\npygame>=2.0.0,<3.0.0\n")

        plan = module.build_install_plan([parent], raspberry_pi=True)

        assert plan.apt_packages == [
            "python3-pygame",
            "python3-websockets",
        ]
        assert plan.pip_requirements == []
