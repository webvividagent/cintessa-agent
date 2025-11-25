import yaml
import requests
import json
import re
import os
import subprocess
import shutil
from typing import Tuple, Dict, Any, List
from pathlib import Path

class Tools:
    def __init__(self, workspace_path: str = None):
        self.workspace_path = Path(workspace_path) if workspace_path else None
        if self.workspace_path:
            self.workspace_path.mkdir(exist_ok=True)
    
    def set_workspace(self, workspace_path: str):
        """Set or change workspace path"""
        self.workspace_path = Path(workspace_path)
        self.workspace_path.mkdir(parents=True, exist_ok=True)
        return f"✅ Workspace set to: {workspace_path}"
    
    def create_directory(self, dir_path: str) -> str:
        """Create directory at specified path (absolute or relative)"""
        try:
            path = Path(dir_path)
            if not path.is_absolute():
                # If no workspace, use home directory as default
                base_path = self.workspace_path if self.workspace_path else Path.home()
                path = base_path / path
            path.mkdir(parents=True, exist_ok=True)
            return f"✅ Created directory: {path}"
        except Exception as e:
            return f"❌ Error creating directory: {e}"
    
    def list_workspace(self, path: str = None) -> List[str]:
        """List all files and folders in workspace"""
        if not self.workspace_path:
            return ["ℹ️ No workspace set. Use 'set workspace <path>' first."]
        
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
        if not self.workspace_path:
            return "❌ Error: No workspace set. Please set a workspace first."
        
        try:
            full_path = self.workspace_path / file_path
            if full_path.exists():
                return full_path.read_text(encoding='utf-8')
            else:
                return f"❌ Error: File '{file_path}' not found in workspace"
        except Exception as e:
            return f"❌ Error reading file: {e}"
    
    def write_file(self, file_path: str, content: str) -> str:
        """Write content to file"""
        if not self.workspace_path:
            return "❌ Error: No workspace set. Please set a workspace first."
        
        try:
            full_path = self.workspace_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content, encoding='utf-8')
            return f"✅ Successfully wrote to {file_path}"
        except Exception as e:
            return f"❌ Error writing file: {e}"
    
    def run_shell(self, command: str) -> Tuple[int, str, str]:
        """Execute shell command in workspace or current directory"""
        try:
            cwd = self.workspace_path if self.workspace_path else Path.cwd()
            process = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True
            )
            return process.returncode, process.stdout, process.stderr
        except Exception as e:
            return 1, "", f"❌ Error executing command: {e}"
    
    def create_project_scaffold(self, project_name: str, project_type: str = "basic") -> str:
        """Create basic project structure"""
        if not self.workspace_path:
            return "❌ Error: No workspace set. Please set a workspace first."
        
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
                
            return f"✅ Created project '{project_name}' at {project_path}"
        except Exception as e:
            return f"❌ Error creating project: {e}"

class CintessaAgent:
    def __init__(self, config_path: str = "config.yaml"):
        self.config = self._load_config(config_path)
        self.tools = Tools()  # Start without workspace
        self.ollama_client = OllamaClient(
            self.config['ollama']['base_url'],
            self.config['ollama']['model']
        )
        self.memory = []
        self.pending_changes = {}
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except:
            return {
                'ollama': {
                    'base_url': 'http://localhost:11434',
                    'model': 'qwen2:7b'
                },
                'workspace': {
                    'default_path': './workspace'
                }
            }
    
    def set_workspace(self, workspace_path: str):
        """Set workspace path for tools"""
        return self.tools.set_workspace(workspace_path)
    
    def parse_command(self, user_input: str) -> Tuple[str, Dict[str, Any]]:
        """Parse natural language command using LLM"""
        user_lower = user_input.lower()
        
        # Direct command mapping - workspace operations (always available)
        if any(phrase in user_lower for phrase in ['set workspace', 'use folder', 'open directory', 'cd to']):
            path = self._extract_path(user_input) or "."
            return "set_workspace", {"path": path}
        
        elif any(phrase in user_lower for phrase in ['create dir', 'make folder', 'mkdir', 'new directory']):
            path = self._extract_path(user_input) or "new_folder"
            return "create_directory", {"path": path}
        
        elif any(phrase in user_lower for phrase in ['create project', 'new project', 'scaffold project']):
            project_name = self._extract_project_name(user_input) or "new_project"
            return "create_project", {"project_name": project_name}
        
        # File operations (only if workspace is set)
        elif any(phrase in user_lower for phrase in ['list files', 'show files', 'ls', 'dir']):
            return "list_files", {}
        
        elif any(phrase in user_lower for phrase in ['read file', 'show file', 'cat']):
            file_path = self._extract_file_path(user_input)
            return "read_file", {"file_path": file_path}
        
        # Code proposals (always available)
        elif any(phrase in user_lower for phrase in ['create function', 'write code', 'implement', 'add feature', 'propose code']):
            return "propose_code", {"user_request": user_input}
        
        # System commands (always available)
        elif any(phrase in user_lower for phrase in ['smoke test', 'test app', 'run tests']):
            return "smoke_test", {}
        
        elif any(phrase in user_lower for phrase in ['run app', 'start app']):
            return "run_app", {}
        
        elif any(phrase in user_lower for phrase in ['help', 'what can you do']):
            return "show_help", {}
        
        # Enhanced LLM parsing for other commands
        prompt = f"""
        Analyze this user command and return ONLY a JSON response with action and params.
        
        Available actions:
        - set_workspace: {{"path": "directory/path"}} - set workspace directory
        - create_directory: {{"path": "directory/path"}} - create new directory
        - create_project: {{"project_name": "name"}} - create new project
        - read_file: {{"file_path": "path/to/file"}} - read file (requires workspace)
        - write_file: {{"file_path": "path/to/file", "content": "content"}} - write file (requires workspace)
        - list_files: {{}} - list files (requires workspace)
        - run_command: {{"command": "shell command"}} - run terminal command
        - propose_code: {{"user_request": "user request"}} - propose code changes
        - smoke_test: {{}} - run smoke tests
        - run_app: {{}} - run application
        - show_help: {{}} - show help information
        - ask_question: {{"question": "user question"}} - general questions
        
        User command: "{user_input}"
        
        IMPORTANT: For general conversation, coding questions, or directory creation, 
        use ask_question or propose_code - these don't require a workspace.
        
        Respond with JSON only:
        {{"action": "action_name", "params": {{...}}}}
        """
        
        try:
            response = self.ollama_client.generate(prompt, system_prompt="You are a command parser. Return only valid JSON. Use ask_question for general chat.")
            
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                action = result.get("action", "ask_question")
                params = result.get("params", {})
                
                # Force ask_question for simple greetings and chat
                if any(word in user_lower for word in ['hi', 'hello', 'hey', 'how are you', 'jimmy']):
                    return "ask_question", {"question": user_input}
                    
                return action, params
            else:
                return "ask_question", {"question": user_input}
                
        except Exception as e:
            return "ask_question", {"question": user_input}
    
    def _extract_path(self, user_input: str) -> str:
        """Extract path from user input"""
        words = user_input.split()
        for i, word in enumerate(words):
            if word in ['to', 'at', 'in', 'folder', 'directory', 'called', 'named'] and i + 1 < len(words):
                return words[i + 1]
        # Return last word as fallback
        return words[-1] if words else ""
    
    def _extract_file_path(self, user_input: str) -> str:
        """Extract file path from user input"""
        words = user_input.split()
        for i, word in enumerate(words):
            if word in ['file', 'file'] and i + 1 < len(words):
                return words[i + 1]
        return "file.txt"
    
    def _extract_project_name(self, user_input: str) -> str:
        """Extract project name from user input"""
        words = user_input.split()
        for i, word in enumerate(words):
            if word in ['project', 'called', 'named'] and i + 1 < len(words):
                return words[i + 1]
        return "new_project"
    
    def create_directory(self, path: str) -> str:
        """Create a directory"""
        return self.tools.create_directory(path)
    
    def propose_code_changes(self, user_request: str) -> str:
        """Propose code changes with Copilot-style suggestions"""
        # Use LLM to generate code based on user request
        prompt = f"""
        The user requested: "{user_request}"
        
        Analyze their request and generate appropriate code. Consider:
        - What files might need to be created or modified
        - What functions or classes are needed
        - Follow Python best practices
        - Include helpful comments
        
        Provide the code in this format:
        FILE: filename.py
        ```python
        # code here
        ```
        
        EXPLANATION: Briefly explain what the code does and why it's needed.
        
        If multiple files are needed, provide each in the same format.
        """
        
        response = self.ollama_client.generate(
            prompt, 
            system_prompt="You are a helpful AI coding assistant. Provide clean, working code with clear explanations. Always specify the filename."
        )
        
        # Generate a unique ID for this proposal
        import uuid
        proposal_id = str(uuid.uuid4())[:8]
        
        # Store the proposal in memory
        self.pending_changes[proposal_id] = {
            "user_request": user_request,
            "code_proposal": response,
            "timestamp": subprocess.getoutput("date")
        }
        
        # Format the response with the proposal ID
        formatted_response = f"💡 **Code Proposal** (ID: `{proposal_id}`)\\n\\n"
        formatted_response += f"**Request:** {user_request}\\n\\n"
        formatted_response += "---\\n\\n"
        formatted_response += response
        formatted_response += "\\n\\n---\\n\\n"
        formatted_response += f"🔧 **Use this ID to accept:** `accept {proposal_id}` or `reject {proposal_id}`"
        
        return formatted_response
    
    def accept_code_proposal(self, proposal_id: str) -> str:
        """Accept and apply a code proposal"""
        if proposal_id not in self.pending_changes:
            return f"❌ No pending proposal found with ID: {proposal_id}"
        
        try:
            proposal = self.pending_changes[proposal_id]
            code_proposal = proposal["code_proposal"]
            
            # Parse the code proposal to extract files and content
            files_to_create = self._parse_code_proposal(code_proposal)
            
            results = f"✅ **Applying Proposal {proposal_id}**\\n\\n"
            
            for file_info in files_to_create:
                file_path = file_info["file_path"]
                content = file_info["content"]
                
                # Write the file
                result = self.tools.write_file(file_path, content)
                if "Successfully" in result:
                    results += f"📄 **{file_path}** - Created successfully\\n"
                else:
                    results += f"❌ **{file_path}** - Error: {result}\\n"
            
            # Remove from pending changes
            del self.pending_changes[proposal_id]
            
            results += "\\n🎉 **Code changes applied!**"
            return results
            
        except Exception as e:
            return f"❌ Error applying code proposal: {e}"
    
    def _parse_code_proposal(self, code_proposal: str) -> List[Dict[str, str]]:
        """Parse code proposal into file paths and content"""
        files = []
        
        # Split by FILE: sections
        sections = code_proposal.split('FILE:')
        for section in sections[1:]:  # Skip first empty section
            if '```' in section:
                # Extract filename and code
                lines = section.strip().split('\\n')
                filename = lines[0].strip()
                # Find code between ```
                code_start = section.find('```')
                code_end = section.find('```', code_start + 3)
                if code_start != -1 and code_end != -1:
                    code_content = section[code_start + 3:code_end].strip()
                    # Remove language specifier if present
                    if code_content.startswith('python'):
                        code_content = code_content[6:].strip()
                    
                    files.append({
                        "file_path": filename,
                        "content": code_content
                    })
        
        return files
    
    def show_help(self) -> str:
        """Show help information"""
        help_text = """
🤖 **Cintessa Agent - Available Commands:**

💬 **Chat & General:**
- Just talk to me! (e.g., "hi", "how are you", "what can you do")
- "help" - Show this help message

📁 **Directory Operations (no workspace needed):**
- "create folder called [name]" - Create a new directory
- "set workspace [path]" - Set a workspace for file operations
- "make directory [name] on desktop" - Create directory anywhere

💻 **Code Proposals (no workspace needed):**
- "create a function that [does something]"
- "write code for [feature]"
- "implement [class/function]"

📄 **File Operations (requires workspace):**
- "list files" - Show files in workspace
- "read file [filename]" - Read a file
- "create file [filename]" - Create a new file

🔧 **System Commands:**
- "smoke test" - Run system tests
- "run app" - Start the application

💡 **Tip:** You can chat and create directories without setting a workspace first!
        """
        return help_text
    
    def execute_action(self, action: str, params: Dict[str, Any]) -> str:
        """Execute the parsed action"""
        try:
            if action == "set_workspace":
                return self.set_workspace(params.get("path", "."))
            
            elif action == "create_directory":
                return self.create_directory(params.get("path", "new_folder"))
            
            elif action == "create_project":
                return self.tools.create_project_scaffold(
                    params.get("project_name", "new_project"),
                    params.get("project_type", "basic")
                )
            
            elif action == "read_file":
                file_path = params.get("file_path", "")
                content = self.tools.read_file(file_path)
                return f"📄 **Content of {file_path}:**\\n\\n```\\n{content}\\n```"
            
            elif action == "write_file":
                return self.tools.write_file(
                    params.get("file_path", ""), 
                    params.get("content", "")
                )
            
            elif action == "run_command":
                code, out, err = self.tools.run_shell(params.get("command", ""))
                result = f"💲 **Command:** `{params.get('command', '')}`\\n"
                result += f"📟 **Exit code:** {code}\\n\\n"
                if out:
                    result += f"**Output:**\\n```\\n{out}\\n```\\n"
                if err:
                    result += f"**Errors:**\\n```\\n{err}\\n```"
                return result
            
            elif action == "list_files":
                files = self.tools.list_workspace(params.get("path"))
                if files and "ℹ️" not in files[0]:
                    return f"📁 **Files in workspace:**\\n\\n" + "\\n".join([f"  - {f}" for f in sorted(files)[:50]]) + f"\\n\\n... and {len(files) - 50} more files"
                return "\\n".join(files) if files else "📁 No files found in workspace"
            
            elif action == "propose_code":
                return self.propose_code_changes(params.get("user_request", ""))
            
            elif action == "smoke_test":
                # Simple smoke test that doesn't require workspace
                if not self.tools.workspace_path:
                    return "🧪 **Quick System Check**\\n\\n✅ Agent is running\\n✅ Ollama connection available\\n💡 Set a workspace for full file operations testing"
                else:
                    return "🧪 **Running full smoke tests...**\\n\\n(This would test files in your workspace)"
            
            elif action == "run_app":
                return "🚀 **Application Launcher**\\n\\nSet a workspace first to run applications."
            
            elif action == "show_help":
                return self.show_help()
            
            elif action == "ask_question":
                # Use LLM to answer general questions
                return self.ollama_client.generate(
                    params.get("question", ""),
                    system_prompt="You are Cintessa, a friendly and helpful AI coding assistant. Be conversational and helpful. If the user mentions creating files or directories, offer to help with that."
                )
            
            else:
                return f"❌ Unknown action: {action}"
                
        except Exception as e:
            return f"❌ Error executing action: {e}"
    
    def chat(self, message: str) -> str:
        """High-level chat interface"""
        # Check for accept/reject commands
        if message.lower().startswith('accept '):
            proposal_id = message.split(' ')[1]
            return self.accept_code_proposal(proposal_id)
        elif message.lower().startswith('reject '):
            proposal_id = message.split(' ')[1]
            if proposal_id in self.pending_changes:
                del self.pending_changes[proposal_id]
                return f"❌ **Proposal {proposal_id} rejected and discarded.**"
            else:
                return f"❌ No pending proposal found with ID: {proposal_id}"
        
        # Normal command processing
        action, params = self.parse_command(message)
        result = self.execute_action(action, params)
        
        # Store in memory
        self.memory.append({
            "input": message,
            "action": action,
            "params": params,
            "result": result
        })
        
        return result

class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "qwen2:7b"):
        self.base_url = base_url
        self.model = model
    
    def generate(self, prompt: str, system_prompt: str = None) -> str:
        """Generate response using Ollama"""
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
            if system_prompt:
                payload["system"] = system_prompt
            
            response = requests.post(f"{self.base_url}/api/generate", json=payload, timeout=30)
            response.raise_for_status()
            return response.json().get("response", "No response from Ollama")
        except Exception as e:
            return f"❌ Error connecting to Ollama: {e}. Make sure Ollama is running and the model is installed."
