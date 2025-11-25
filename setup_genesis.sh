#!/bin/bash

echo "🤖 Setting up Cintessa Agent - Local AI Coding IDE"

# Create main directory
mkdir -p cintessa_agent
cd cintessa_agent

echo "📁 Creating project structure..."
mkdir -p agent

# Create requirements.txt
cat > requirements.txt << 'EOL'
streamlit>=1.28.0
requests>=2.31.0
pyyaml>=6.0
gitpython>=3.1.0
EOL

echo "✅ Created requirements.txt"

# Create config.yaml
cat > config.yaml << 'EOL'
ollama:
  base_url: "http://localhost:11434"
  model: "qwen2:7b"
  temperature: 0.1

workspace:
  default_path: "./workspace"

agent:
  system_prompt: |
    You are Cintessa, an AI coding assistant. Help users with:
    - Code understanding and editing
    - Project scaffolding
    - Running commands and tests
    - File operations
    Be concise and helpful.
EOL

echo "✅ Created config.yaml"

# Create agent/__init__.py
cat > agent/__init__.py << 'EOL'
# Cintessa Agent Package
from .core import CintessaAgent
from .tools import Tools

__all__ = ["CintessaAgent", "Tools"]
EOL

echo "✅ Created agent/__init__.py"

# Create agent/tools.py
cat > agent/tools.py << 'EOL'
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
            return full_path.read_text(encoding='utf-8')
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
EOL

echo "✅ Created agent/tools.py"

# Create agent/core.py
cat > agent/core.py << 'EOL'
import yaml
import requests
import json
import re
from typing import Tuple, Dict, Any
from .tools import Tools

class CintessaAgent:
    def __init__(self, config_path: str = "config.yaml"):
        self.config = self._load_config(config_path)
        self.tools = None
        self.ollama_client = OllamaClient(
            self.config['ollama']['base_url'],
            self.config['ollama']['model']
        )
        self.memory = []
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except:
            # Default config if file not found
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
        self.tools = Tools(workspace_path)
    
    def parse_command(self, user_input: str) -> Tuple[str, Dict[str, Any]]:
        """Parse natural language command using LLM"""
        if not self.tools:
            return "error", {"message": "Workspace not set. Please select a workspace first."}
        
        prompt = f"""
        Analyze this user command and return ONLY a JSON response with action and params.
        
        Available actions:
        - read_file: {{"file_path": "path/to/file"}}
        - write_file: {{"file_path": "path/to/file", "content": "file content"}}
        - run_command: {{"command": "shell command"}}
        - list_files: {{"path": "optional/subpath"}}
        - create_project: {{"project_name": "name", "project_type": "basic|python"}}
        - ask_question: {{"question": "user question"}}
        
        User command: "{user_input}"
        
        Respond with JSON only:
        {{"action": "action_name", "params": {{...}}}}
        """
        
        try:
            response = self.ollama_client.generate(prompt, system_prompt="You are a command parser. Return only valid JSON.")
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                return result.get("action", "ask_question"), result.get("params", {})
            else:
                return "ask_question", {"question": user_input}
                
        except Exception as e:
            return "error", {"message": f"Failed to parse command: {e}"}
    
    def execute_action(self, action: str, params: Dict[str, Any]) -> str:
        """Execute the parsed action"""
        if not self.tools:
            return "Error: Workspace not set. Please select a workspace first."
        
        try:
            if action == "read_file":
                return self.tools.read_file(params.get("file_path", ""))
            
            elif action == "write_file":
                return self.tools.write_file(
                    params.get("file_path", ""), 
                    params.get("content", "")
                )
            
            elif action == "run_command":
                code, out, err = self.tools.run_shell(params.get("command", ""))
                result = f"Exit code: {code}\n"
                if out:
                    result += f"Output:\n{out}\n"
                if err:
                    result += f"Error:\n{err}\n"
                return result
            
            elif action == "list_files":
                files = self.tools.list_workspace(params.get("path"))
                return "\n".join(files) if files else "No files found"
            
            elif action == "create_project":
                return self.tools.create_project_scaffold(
                    params.get("project_name", "new_project"),
                    params.get("project_type", "basic")
                )
            
            elif action == "ask_question":
                # Use LLM to answer general questions
                return self.ollama_client.generate(
                    params.get("question", ""),
                    system_prompt=self.config.get('agent', {}).get('system_prompt', 'You are a helpful assistant.')
                )
            
            elif action == "error":
                return params.get("message", "Unknown error")
            
            else:
                return f"Unknown action: {action}"
                
        except Exception as e:
            return f"Error executing action: {e}"
    
    def chat(self, message: str) -> str:
        """High-level chat interface"""
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
            return f"Error connecting to Ollama: {e}. Make sure Ollama is running and the model is installed."
EOL

echo "✅ Created agent/core.py"

# Create main.py
cat > main.py << 'EOL'
import streamlit as st
import os
from pathlib import Path
from agent.core import CintessaAgent

st.set_page_config(
    page_title="Cintessa Agent - Local AI Coding IDE",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .file-tree {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
        max-height: 400px;
        overflow-y: auto;
    }
    .terminal {
        background-color: #000;
        color: #00ff00;
        padding: 10px;
        border-radius: 5px;
        font-family: monospace;
        max-height: 300px;
        overflow-y: auto;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.markdown('<div class="main-header">🤖 Cintessa Agent - Local AI Coding IDE</div>', unsafe_allow_html=True)
    
    # Initialize session state
    if "agent" not in st.session_state:
        st.session_state.agent = CintessaAgent()
    
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    if "workspace_path" not in st.session_state:
        st.session_state.workspace_path = None
    
    if "terminal_output" not in st.session_state:
        st.session_state.terminal_output = "Welcome to Cintessa Terminal!\\n"
    
    # Sidebar for workspace management
    with st.sidebar:
        st.header("Workspace Settings")
        
        # Workspace selection
        st.subheader("Select Workspace")
        workspace_input = st.text_input("Workspace Path:", value="./workspace")
        
        if st.button("Set Workspace") or not st.session_state.workspace_path:
            if os.path.exists(workspace_input):
                st.session_state.workspace_path = workspace_input
                st.session_state.agent.set_workspace(workspace_input)
                st.success(f"Workspace set to: {workspace_input}")
            else:
                st.error("Path does not exist!")
        
        # Quick actions
        st.subheader("Quick Actions")
        if st.button("List Files"):
            if st.session_state.workspace_path:
                result = st.session_state.agent.execute_action("list_files", {})
                st.session_state.terminal_output += f"\\n$ ls\\n{result}\\n"
        
        if st.button("Create Python Project"):
            project_name = st.text_input("Project Name:", value="my_project")
            if st.button("Create"):
                result = st.session_state.agent.execute_action("create_project", {
                    "project_name": project_name,
                    "project_type": "python"
                })
                st.session_state.terminal_output += f"\\n$ create project {project_name}\\n{result}\\n"
    
    # Main content area with tabs
    tab1, tab2, tab3 = st.tabs(["📁 Workspace Explorer", "💬 Chat with Cintessa", "🖥️ Terminal"])
    
    # Tab 1: Workspace Explorer
    with tab1:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("File Explorer")
            if st.session_state.workspace_path:
                st.markdown(f"**Workspace:** `{st.session_state.workspace_path}`")
                
                # File tree
                files = st.session_state.agent.tools.list_workspace() if st.session_state.agent.tools else []
                if files:
                    st.markdown('<div class="file-tree">', unsafe_allow_html=True)
                    for file in sorted(files):
                        st.text(f"📄 {file}")
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.info("No files in workspace or workspace not set")
            else:
                st.warning("Please set a workspace path in the sidebar")
        
        with col2:
            st.subheader("File Operations")
            if st.session_state.workspace_path:
                op_type = st.selectbox("Operation", ["Read File", "Write File"])
                
                if op_type == "Read File":
                    file_path = st.text_input("File path to read:")
                    if st.button("Read File") and file_path:
                        content = st.session_state.agent.tools.read_file(file_path)
                        st.text_area("File Content:", content, height=300)
                
                elif op_type == "Write File":
                    file_path = st.text_input("File path to write:")
                    content = st.text_area("Content:", height=250)
                    if st.button("Write File") and file_path and content:
                        result = st.session_state.agent.tools.write_file(file_path, content)
                        st.success(result)
    
    # Tab 2: Chat Interface
    with tab2:
        st.subheader("Chat with Cintessa Agent")
        
        # Display chat history
        for msg in st.session_state.chat_history:
            with st.chat_message("user"):
                st.write(msg["question"])
            with st.chat_message("assistant"):
                st.write(msg["answer"])
        
        # Chat input
        if prompt := st.chat_input("Ask Cintessa to code, run commands, or explain..."):
            # Add user message to history
            with st.chat_message("user"):
                st.write(prompt)
            
            # Get agent response
            if st.session_state.workspace_path:
                with st.chat_message("assistant"):
                    with st.spinner("Cintessa is thinking..."):
                        response = st.session_state.agent.chat(prompt)
                        st.write(response)
                
                # Store in history
                st.session_state.chat_history.append({
                    "question": prompt,
                    "answer": response
                })
            else:
                st.error("Please set a workspace path first!")
    
    # Tab 3: Terminal
    with tab3:
        st.subheader("Integrated Terminal")
        
        # Terminal output
        st.markdown('<div class="terminal">', unsafe_allow_html=True)
        st.text(st.session_state.terminal_output)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Terminal input
        col1, col2 = st.columns([4, 1])
        with col1:
            terminal_cmd = st.text_input("Enter command:", key="term_cmd", label_visibility="collapsed")
        with col2:
            if st.button("Run", use_container_width=True) and terminal_cmd:
                if st.session_state.workspace_path:
                    code, out, err = st.session_state.agent.tools.run_shell(terminal_cmd)
                    st.session_state.terminal_output += f"\\n$ {terminal_cmd}\\n"
                    if out:
                        st.session_state.terminal_output += f"{out}\\n"
                    if err:
                        st.session_state.terminal_output += f"Error: {err}\\n"
                    st.session_state.terminal_output += f"[Exit code: {code}]\\n"
                    
                    # Refresh to show new output
                    st.rerun()
                else:
                    st.error("Set workspace first!")

if __name__ == "__main__":
    main()
EOL

echo "✅ Created main.py"

# Create README.md
cat > README.md << 'EOL'
# Cintessa Agent - Local AI Coding IDE

A local AI-powered coding assistant with Ollama integration.

## Quick Start

1. Create virtual environment and install:
\`\`\`bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
\`\`\`

2. Run the app:
\`\`\`bash
streamlit run main.py
\`\`\`

3. Open http://localhost:8501 in your browser
EOL

echo "✅ Created README.md"

echo ""
echo "🎉 Cintessa Agent setup complete!"
echo ""
echo "Next steps:"
echo "1. cd cintessa_agent"
echo "2. python3 -m venv venv"
echo "3. source venv/bin/activate"
echo "4. pip install -r requirements.txt"
echo "5. streamlit run main.py"
echo ""
echo "Enjoy! 🚀"
EOL

echo "🤖 Setup script created! Now run it:"
echo "chmod +x setup_cintessa.sh"
echo "./setup_cintessa.sh"
