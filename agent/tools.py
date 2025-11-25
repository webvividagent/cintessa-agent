import os
import subprocess
import shutil
from pathlib import Path
from typing import List, Tuple

class Tools:
    def __init__(self, workspace_path: str = "./workspace"):
        self.workspace_path = Path(workspace_path)
        self.workspace_path.mkdir(exist_ok=True)
    
    def list_workspace(self, path: str = None) -> List[str]:
        """List all files and folders in workspace"""
        target_path = self.workspace_path / path if path else self.workspace_path
        files = []
        try:
            for item in target_path.rglob("*"):
                if item.is_file():
                    files.append(str(item.relative_to(self.workspace_path)))
        except Exception as e:
            files = [f"Error: {e}"]
        return files
    
    def read_file(self, file_path: str) -> str:
        """Read file content"""
        try:
            full_path = self.workspace_path / file_path
            if full_path.exists():
                return full_path.read_text(encoding='utf-8')
            else:
                # Try to find the file case-insensitively
                for actual_file in self.workspace_path.rglob("*"):
                    if actual_file.is_file() and actual_file.name.lower() == file_path.lower():
                        return actual_file.read_text(encoding='utf-8')
                return f"Error: File '{file_path}' not found in workspace"
        except Exception as e:
            return f"Error reading file: {e}"
    
    def write_file(self, file_path: str, content: str) -> str:
        """Write content to file"""
        try:
            full_path = self.workspace_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content, encoding='utf-8')
            return f"Successfully wrote to {file_path}"
        except Exception as e:
            return f"Error writing file: {e}"
    
    def run_shell(self, command: str) -> Tuple[int, str, str]:
        """Execute shell command in workspace"""
        try:
            process = subprocess.run(
                command,
                shell=True,
                cwd=self.workspace_path,
                capture_output=True,
                text=True
            )
            return process.returncode, process.stdout, process.stderr
        except Exception as e:
            return 1, "", f"Error executing command: {e}"
    
    def create_project_scaffold(self, project_name: str, project_type: str = "basic") -> str:
        """Create basic project structure"""
        try:
            project_path = self.workspace_path / project_name
            project_path.mkdir(exist_ok=True)
            
            # Create basic structure
            (project_path / "src").mkdir(exist_ok=True)
            (project_path / "tests").mkdir(exist_ok=True)
            
            # Create README
            readme_content = f"# {project_name}\n\nProject created by Cintessa Agent"
            (project_path / "README.md").write_text(readme_content)
            
            # Create basic Python files for Python projects
            if project_type == "python":
                (project_path / "src" / "__init__.py").write_text("")
                (project_path / "requirements.txt").write_text("")
                
            return f"Created project '{project_name}' at {project_path}"
        except Exception as e:
            return f"Error creating project: {e}"
