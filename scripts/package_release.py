#!/usr/bin/env python3
"""
Release package builder for Mr. Pumpkin.
Creates a ZIP archive with all necessary files for distribution.
"""
import os
import zipfile
from pathlib import Path

def read_version():
    """Read version from VERSION file."""
    version_file = Path(__file__).parent.parent / "VERSION"
    with open(version_file, 'r') as f:
        return f.read().strip()

def create_release_package():
    """Build ZIP archive for release distribution."""
    version = read_version()
    archive_name = f"mr-pumpkin-v{version}.zip"
    folder_name = f"mr-pumpkin-v{version}"
    
    # Files to include in release
    include_files = [
        "pumpkin_face.py",
        "client_example.py",
        "requirements.txt",
        "README.md",
        "VERSION",
        "LICENSE",
        "test_projection_mapping.py",
        "install.sh",
        "install.ps1"
    ]
    
    # Directories to include
    include_dirs = ["docs"]
    
    repo_root = Path(__file__).parent.parent
    
    print(f"📦 Building release package: {archive_name}")
    
    with zipfile.ZipFile(archive_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add individual files
        for filename in include_files:
            file_path = repo_root / filename
            if file_path.exists():
                arcname = f"{folder_name}/{filename}"
                zipf.write(file_path, arcname)
                print(f"  ✓ {filename}")
            else:
                print(f"  ⚠ Skipping {filename} (not found)")
        
        # Add directories recursively
        for dirname in include_dirs:
            dir_path = repo_root / dirname
            if dir_path.exists() and dir_path.is_dir():
                for root, dirs, files in os.walk(dir_path):
                    # Skip hidden directories
                    dirs[:] = [d for d in dirs if not d.startswith('.')]
                    
                    for file in files:
                        if not file.startswith('.'):
                            file_path = Path(root) / file
                            arcname = f"{folder_name}/{file_path.relative_to(repo_root)}"
                            zipf.write(file_path, arcname)
                            print(f"  ✓ {file_path.relative_to(repo_root)}")
    
    print(f"✅ Release package created: {archive_name}")
    return archive_name

if __name__ == "__main__":
    create_release_package()
