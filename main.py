import streamlit as st
import os
import re
import time
from pathlib import Path
from agent.core import CintessaAgent

st.set_page_config(
    page_title="Cintessa Agent - Cyber AI IDE",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Black with Purple Cyberpunk Style CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        background: linear-gradient(45deg, #ff00ff, #8a2be2, #00ffff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
        text-shadow: 0 0 10px #ff00ff, 0 0 20px #8a2be2;
    }
    .stApp {
        background-color: #000000;
        color: #c77dff;
    }
    .cyber-container {
        background-color: #0a0a0a;
        border: 1px solid #ff00ff;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 0 15px #ff00ff;
        color: #c77dff;
    }
    .file-tree {
        background-color: #111111;
        padding: 10px;
        border-radius: 5px;
        max-height: 500px;
        overflow-y: auto;
        border: 1px solid #8a2be2;
        color: #c77dff;
        font-family: 'Courier New', monospace;
    }
    .terminal {
        background-color: #000000;
        color: #c77dff;
        padding: 15px;
        border-radius: 5px;
        font-family: 'Courier New', monospace;
        max-height: 400px;
        overflow-y: auto;
        border: 1px solid #c77dff;
        box-shadow: 0 0 10px #c77dff;
    }
    .chat-message-user {
        background: linear-gradient(45deg, #1a1a1a, #2a0a4a);
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 4px solid #ff00ff;
        color: #c77dff;
    }
    .chat-message-assistant {
        background: linear-gradient(45deg, #1a1a1a, #0a2a4a);
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 4px solid #c77dff;
        color: #c77dff;
    }
    .code-proposal {
        background: linear-gradient(45deg, #1a0a2a, #0a1a2a);
        padding: 20px;
        border-radius: 10px;
        border: 2px solid #00ff00;
        margin: 15px 0;
        box-shadow: 0 0 20px #00ff00;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { box-shadow: 0 0 20px #00ff00; }
        50% { box-shadow: 0 0 30px #00ff00; }
        100% { box-shadow: 0 0 20px #00ff00; }
    }
    .code-block {
        background-color: #111111;
        padding: 15px;
        border-radius: 5px;
        border: 1px solid #00ff00;
        margin: 10px 0;
        font-family: 'Courier New', monospace;
        color: #00ff00;
        max-height: 400px;
        overflow-y: auto;
    }
    .proposal-actions {
        background: linear-gradient(45deg, #2a2a2a, #1a2a2a);
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #00ff00;
        margin: 10px 0;
    }
    .stButton button {
        background: linear-gradient(45deg, #ff00ff, #8a2be2);
        color: white;
        border: none;
        border-radius: 5px;
        padding: 10px 20px;
        font-weight: bold;
    }
    .stButton button:hover {
        background: linear-gradient(45deg, #8a2be2, #ff00ff);
        box-shadow: 0 0 15px #ff00ff;
    }
    .accept-button {
        background: linear-gradient(45deg, #00ff00, #00b894) !important;
        color: white !important;
    }
    .accept-button:hover {
        background: linear-gradient(45deg, #00b894, #00ff00) !important;
        box-shadow: 0 0 15px #00ff00 !important;
    }
    .reject-button {
        background: linear-gradient(45deg, #ff6b6b, #ee5a24) !important;
        color: white !important;
    }
    .reject-button:hover {
        background: linear-gradient(45deg, #ee5a24, #ff6b6b) !important;
        box-shadow: 0 0 15px #ff6b6b !important;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #0a0a0a, #1a0a2a);
    }
    .stTab {
        background-color: #1a1a1a;
        color: #c77dff;
    }
    .stTab[aria-selected="true"] {
        background-color: #ff00ff !important;
        color: white !important;
    }
    .folder-browser {
        background: linear-gradient(45deg, #1a0a2a, #0a0a2a);
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #8a2be2;
        margin: 10px 0;
        color: #c77dff;
    }
    .no-workspace-banner {
        background: linear-gradient(45deg, #2a0a0a, #0a0a2a);
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #ff6b6b;
        margin: 10px 0;
        text-align: center;
    }
    /* Make all text purple */
    p, div, span, h1, h2, h3, h4, h5, h6 {
        color: #c77dff !important;
    }
    /* Input fields */
    .stTextInput input, .stTextArea textarea {
        background-color: #111111 !important;
        color: #c77dff !important;
        border: 1px solid #c77dff !important;
    }
    /* Select boxes */
    .stSelectbox select {
        background-color: #111111 !important;
        color: #c77dff !important;
        border: 1px solid #c77dff !important;
    }
    /* Code blocks */
    code {
        background-color: #111111 !important;
        color: #c77dff !important;
        border: 1px solid #c77dff !important;
    }
</style>
""", unsafe_allow_html=True)

def get_common_directories():
    """Get common directories like Desktop, Documents, Downloads, etc."""
    home = Path.home()
    common_dirs = {
        "🏠 Home": home,
        "🖥️ Desktop": home / "Desktop",
        "📁 Documents": home / "Documents", 
        "📥 Downloads": home / "Downloads",
        "🎵 Music": home / "Music",
        "🖼️ Pictures": home / "Pictures",
        "🎬 Videos": home / "Videos"
    }
    
    # Only include directories that actually exist
    return {name: path for name, path in common_dirs.items() if path.exists()}

def browse_folder_interactive():
    """Interactive folder browser using Streamlit components"""
    
    if "current_path" not in st.session_state:
        st.session_state.current_path = Path.home()
    
    if "folder_history" not in st.session_state:
        st.session_state.folder_history = [st.session_state.current_path]
    
    st.markdown('<div class="folder-browser">', unsafe_allow_html=True)
    st.subheader("📁 Browse Folders")
    
    # Quick access to common directories
    st.markdown("**🚀 Quick Access:**")
    common_dirs = get_common_directories()
    
    cols = st.columns(3)
    col_idx = 0
    for name, path in common_dirs.items():
        with cols[col_idx]:
            if st.button(name, use_container_width=True, key=f"quick_{name}"):
                st.session_state.current_path = path
                st.session_state.folder_history.append(path)
                st.rerun()
        col_idx = (col_idx + 1) % 3
    
    st.markdown("---")
    
    # Current path display and navigation
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"**📍 Current Path:** `{st.session_state.current_path}`")
    with col2:
        if st.button("⬆️ Up", use_container_width=True):
            parent = st.session_state.current_path.parent
            if parent != st.session_state.current_path:  # Not at root
                st.session_state.current_path = parent
                st.session_state.folder_history.append(parent)
                st.rerun()
    
    # Manual path input
    manual_path = st.text_input("Or enter custom path:", value=str(st.session_state.current_path))
    if st.button("📂 Go to Path", use_container_width=True):
        if os.path.exists(manual_path) and os.path.isdir(manual_path):
            st.session_state.current_path = Path(manual_path)
            st.session_state.folder_history.append(Path(manual_path))
            st.rerun()
        else:
            st.error("❌ Path does not exist or is not a directory!")
    
    st.markdown("---")
    
    # List folders and files in current directory
    try:
        items = list(st.session_state.current_path.iterdir())
        folders = [item for item in items if item.is_dir()]
        files = [item for item in items if item.is_file()]
        
        st.markdown(f"**📂 Folders ({len(folders)})**")
        if folders:
            for folder in sorted(folders):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"📁 {folder.name}")
                with col2:
                    if st.button("Open", key=f"open_{folder}", use_container_width=True):
                        st.session_state.current_path = folder
                        st.session_state.folder_history.append(folder)
                        st.rerun()
        else:
            st.info("No subfolders")
        
        st.markdown(f"**📄 Files ({len(files)})**")
        if files:
            for file in sorted(files):
                st.write(f"📄 {file.name}")
        else:
            st.info("No files")
            
    except PermissionError:
        st.error("❌ Permission denied to access this folder")
    except Exception as e:
        st.error(f"❌ Error reading folder: {e}")
    
    st.markdown("---")
    
    # Select current folder as workspace
    if st.button("✅ SELECT THIS FOLDER AS WORKSPACE", use_container_width=True, type="primary"):
        st.session_state.workspace_path = str(st.session_state.current_path)
        st.session_state.agent.set_workspace(st.session_state.workspace_path)
        st.session_state.file_tree = []
        st.success(f"🎯 Workspace set to: {st.session_state.current_path}")
        st.markdown('</div>', unsafe_allow_html=True)
        return True
    
    st.markdown('</div>', unsafe_allow_html=True)
    return False

def get_file_tree(startpath):
    """Generate a file tree structure"""
    if not startpath:
        return ["No workspace set"]
    
    tree = []
    try:
        for root, dirs, files in os.walk(startpath):
            # Limit depth to avoid too much recursion
            if root.count(os.sep) - startpath.count(os.sep) > 3:
                continue
                
            level = root.replace(str(startpath), '').count(os.sep)
            indent = ' ' * 2 * level
            tree.append(f"{indent}📁 {os.path.basename(root)}/")
            subindent = ' ' * 2 * (level + 1)
            for file in files[:50]:  # Limit files per directory
                tree.append(f"{subindent}📄 {file}")
    except Exception as e:
        tree.append(f"❌ Error reading directory: {e}")
    return tree

def display_code_proposal(proposal_content, proposal_id):
    """Display a code proposal with accept/reject buttons"""
    st.markdown('<div class="code-proposal">', unsafe_allow_html=True)
    st.markdown(f"### 💡 **Code Proposal** `{proposal_id}`")
    
    # Extract and display code blocks
    code_blocks = re.findall(r'```(?:\w+)?\n(.*?)\n```', proposal_content, re.DOTALL)
    file_sections = re.findall(r'FILE:\s*(.*?\.\w+)', proposal_content)
    
    for i, (file_section, code_block) in enumerate(zip(file_sections, code_blocks)):
        st.markdown(f"**📄 {file_section}**")
        st.markdown(f'<div class="code-block">', unsafe_allow_html=True)
        st.code(code_block, language='python')
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Display explanation
    explanation_match = re.search(r'EXPLANATION:\s*(.*?)(?=FILE:|\Z)', proposal_content, re.DOTALL)
    if explanation_match:
        st.markdown("**💬 Explanation:**")
        st.info(explanation_match.group(1).strip())
    
    # Accept/Reject buttons
    st.markdown('<div class="proposal-actions">', unsafe_allow_html=True)
    st.markdown("**🔧 Actions:**")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✅ Accept Proposal", key=f"accept_{proposal_id}", use_container_width=True, type="primary"):
            st.session_state.pending_accept = proposal_id
            st.rerun()
    
    with col2:
        if st.button("❌ Reject Proposal", key=f"reject_{proposal_id}", use_container_width=True):
            st.session_state.pending_reject = proposal_id
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def main():
    st.markdown('<div class="main-header">⚡ CINTESSA AGENT - CYBER AI IDE</div>', unsafe_allow_html=True)
    
    # Initialize session state
    if "agent" not in st.session_state:
        st.session_state.agent = CintessaAgent()
    
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    if "workspace_path" not in st.session_state:
        st.session_state.workspace_path = None
    
    if "terminal_output" not in st.session_state:
        st.session_state.terminal_output = "⚡ CYBER TERMINAL READY\\n> Type 'help' for commands\\n"
    
    if "file_tree" not in st.session_state:
        st.session_state.file_tree = []
    
    if "agent_paused" not in st.session_state:
        st.session_state.agent_paused = False
    
    if "pending_accept" not in st.session_state:
        st.session_state.pending_accept = None
    
    if "pending_reject" not in st.session_state:
        st.session_state.pending_reject = None

    # Handle pending accept/reject actions
    if st.session_state.pending_accept:
        proposal_id = st.session_state.pending_accept
        result = st.session_state.agent.accept_code_proposal(proposal_id)
        st.session_state.chat_history.append({"role": "system", "content": result})
        st.session_state.pending_accept = None
        st.rerun()
    
    if st.session_state.pending_reject:
        proposal_id = st.session_state.pending_reject
        result = st.session_state.agent.reject_code_proposal(proposal_id)
        st.session_state.chat_history.append({"role": "system", "content": result})
        st.session_state.pending_reject = None
        st.rerun()

    # Sidebar with cyberpunk style
    with st.sidebar:
        st.markdown('<div class="cyber-container">', unsafe_allow_html=True)
        st.header("🔮 WORKSPACE")
        
        # Agent Control Section
        st.markdown("### 🎛️ AGENT CONTROL")
        
        col1, col2 = st.columns(2)
        with col1:
            if not st.session_state.agent_paused:
                if st.button("⏸️ PAUSE", use_container_width=True, key="pause_btn"):
                    st.session_state.agent_paused = True
                    st.rerun()
            else:
                if st.button("▶️ RESUME", use_container_width=True, key="resume_btn"):
                    st.session_state.agent_paused = False
                    st.rerun()
        
        with col2:
            if st.button("🔄 RESTART", use_container_width=True):
                st.session_state.agent = CintessaAgent()
                st.session_state.workspace_path = None
                st.session_state.chat_history = []
                st.session_state.agent_paused = False
                st.success("🔄 Agent restarted!")
                st.rerun()
        
        # Agent status indicator
        if st.session_state.agent_paused:
            st.error("⏸️ **AGENT PAUSED**")
            st.info("Commands will not be processed until resumed")
        else:
            st.success("▶️ **AGENT ACTIVE**")
            st.info("Ready to process commands")
        
        st.markdown("---")
        
        # Workspace status
        if st.session_state.workspace_path:
            st.success("✅ Workspace Active")
            st.markdown(f"**📍 Current Workspace:**")
            st.code(st.session_state.workspace_path, language="text")
            
            # Quick actions
            st.markdown("---")
            st.header("⚡ QUICK ACTIONS")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📋 List Files", use_container_width=True, disabled=st.session_state.agent_paused):
                    result = st.session_state.agent.execute_action("list_files", {})
                    st.session_state.terminal_output += f"\\n> ls\\n{result}\\n"
            
            with col2:
                if st.button("🔄 Refresh Tree", use_container_width=True, disabled=st.session_state.agent_paused):
                    st.session_state.file_tree = get_file_tree(st.session_state.workspace_path)
                    st.rerun()
        
        else:
            st.warning("🌌 No Workspace Set")
            st.info("Chat freely or set a workspace for file operations")
        
        st.markdown('</div>', unsafe_allow_html=True)

    # Main content area with tabs - START ON CHAT TAB
    tab1, tab2, tab3, tab4 = st.tabs(["💬 CHAT", "🌌 FOLDER BROWSER", "📁 EXPLORER", "🖥️ TERMINAL"])
    
    # Tab 1: Chat Interface (DEFAULT TAB)
    with tab1:
        st.markdown('<div class="cyber-container">', unsafe_allow_html=True)
        st.subheader("💬 CHAT WITH CINTESSA")
        
        # Show workspace status
        if not st.session_state.workspace_path:
            st.markdown('<div class="no-workspace-banner">', unsafe_allow_html=True)
            st.info("💡 **No workspace set** - You can chat freely! Set a workspace for file operations.")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Show agent status banner
        if st.session_state.agent_paused:
            st.error("⏸️ **AGENT PAUSED** - Chat commands disabled")
        
        # Display chat history with cyberpunk style
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(f'<div class="chat-message-user">👤 **YOU:** {msg["content"]}</div>', unsafe_allow_html=True)
            elif msg["role"] == "assistant":
                # Check if this is a code proposal
                if "💡 **Code Proposal**" in msg["content"]:
                    # Extract proposal ID
                    proposal_id_match = re.search(r'`([a-f0-9]+)`', msg["content"])
                    if proposal_id_match:
                        proposal_id = proposal_id_match.group(1)
                        display_code_proposal(msg["content"], proposal_id)
                    else:
                        st.markdown(f'<div class="chat-message-assistant">🤖 **CINTESSA:** {msg["content"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="chat-message-assistant">🤖 **CINTESSA:** {msg["content"]}</div>', unsafe_allow_html=True)
            elif msg["role"] == "system":
                st.info(f"🔧 **SYSTEM:** {msg['content']}")
        
        # Chat input at bottom - ALWAYS ENABLED (unless paused)
        if prompt := st.chat_input("💭 Ask Cintessa anything...", 
                                 disabled=st.session_state.agent_paused):
            if st.session_state.agent_paused:
                st.error("❌ Agent is paused. Please resume to process commands.")
            else:
                # Add user message to history
                st.session_state.chat_history.append({"role": "user", "content": prompt})
                
                # Get agent response
                with st.spinner("🔮 Cintessa is processing..."):
                    response = st.session_state.agent.chat(prompt)
                
                # Add assistant response to history
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                
                # Rerun to show new messages
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Tab 2: Folder Browser
    with tab2:
        st.markdown('<div class="cyber-container">', unsafe_allow_html=True)
        st.subheader("📁 FOLDER BROWSER")
        
        st.info("🎯 Browse to select a workspace folder for file operations")
        
        # Run the folder browser
        workspace_selected = browse_folder_interactive()
        
        if workspace_selected:
            st.balloons()
            st.success(f"🚀 Workspace activated! You can now use file operations.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Tab 3: File Explorer (only available when workspace is set)
    with tab3:
        st.markdown('<div class="cyber-container">', unsafe_allow_html=True)
        st.subheader("📁 FILE EXPLORER")
        
        if st.session_state.workspace_path:
            # Show agent status banner
            if st.session_state.agent_paused:
                st.warning("⏸️ **AGENT PAUSED** - File operations disabled")
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.markdown("**🌳 PROJECT TREE**")
                if st.session_state.file_tree:
                    st.markdown('<div class="file-tree">', unsafe_allow_html=True)
                    for item in st.session_state.file_tree[:100]:
                        st.text(item)
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.info("🔄 Click 'Refresh Tree' in sidebar to view file tree")
            
            with col2:
                st.subheader("🔧 FILE OPERATIONS")
                
                op_type = st.selectbox("Select Operation", 
                                     ["Read File", "Write File", "Create File"],
                                     key="file_op")
                
                if op_type == "Read File":
                    file_path = st.text_input("File path (relative to workspace):", 
                                            placeholder="e.g., src/main.py")
                    if st.button("📖 Read File", key="read_btn", disabled=st.session_state.agent_paused):
                        if file_path:
                            content = st.session_state.agent.tools.read_file(file_path)
                            st.text_area("📄 File Content:", content, height=300)
                
                elif op_type == "Write File":
                    file_path = st.text_input("File path to create/edit:", 
                                            placeholder="e.g., src/new_file.py")
                    content = st.text_area("💾 Content:", height=250,
                                         placeholder="# Write your code here...")
                    if st.button("💾 Save File", key="write_btn", disabled=st.session_state.agent_paused):
                        if file_path and content:
                            result = st.session_state.agent.tools.write_file(file_path, content)
                            st.success(result)
                            st.session_state.file_tree = get_file_tree(st.session_state.workspace_path)
                
                elif op_type == "Create File":
                    file_path = st.text_input("New file path:", 
                                            placeholder="e.g., src/cyber_script.py")
                    if st.button("✨ Create File", key="create_btn", disabled=st.session_state.agent_paused):
                        if file_path:
                            result = st.session_state.agent.tools.write_file(file_path, "# New file created by Cintessa\\n")
                            st.success(result)
                            st.session_state.file_tree = get_file_tree(st.session_state.workspace_path)
        
        else:
            st.warning("🎯 Please select a workspace folder first!")
            st.info("Go to the 'FOLDER BROWSER' tab to select your workspace")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Tab 4: Terminal
    with tab4:
        st.markdown('<div class="cyber-container">', unsafe_allow_html=True)
        st.subheader("🖥️ CYBER TERMINAL")
        
        # Show agent status banner
        if st.session_state.agent_paused:
            st.warning("⏸️ **AGENT PAUSED** - Terminal commands disabled")
        
        # Terminal output
        st.markdown('<div class="terminal">', unsafe_allow_html=True)
        st.text(st.session_state.terminal_output)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Terminal input
        col1, col2 = st.columns([4, 1])
        with col1:
            terminal_cmd = st.text_input("⌨️ Enter command:", 
                                       key="term_cmd", 
                                       label_visibility="collapsed",
                                       placeholder="Type command and press Enter...",
                                       disabled=st.session_state.agent_paused)
        with col2:
            if st.button("⚡ RUN", use_container_width=True, 
                       disabled=st.session_state.agent_paused) and terminal_cmd:
                code, out, err = st.session_state.agent.tools.run_shell(terminal_cmd)
                
                # Add to terminal output with cyber style
                st.session_state.terminal_output += f"\\n💲 {terminal_cmd}\\n"
                if out:
                    st.session_state.terminal_output += f"{out}\\n"
                if err:
                    st.session_state.terminal_output += f"🔴 {err}\\n"
                st.session_state.terminal_output += f"📟 [Exit: {code}]\\n"
                
                # Refresh to show new output
                st.rerun()
        
        # Terminal utilities
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🔄 Clear Terminal", use_container_width=True, disabled=st.session_state.agent_paused):
                st.session_state.terminal_output = "⚡ TERMINAL CLEARED\\n> Ready for commands\\n"
                st.rerun()
        with col2:
            if st.button("📊 System Info", use_container_width=True, disabled=st.session_state.agent_paused):
                code, out, err = st.session_state.agent.tools.run_shell("pwd && ls -la")
                st.session_state.terminal_output += f"\\n💲 system info\\n{out}\\n"
                st.rerun()
        with col3:
            if st.button("🐍 Python Check", use_container_width=True, disabled=st.session_state.agent_paused):
                code, out, err = st.session_state.agent.tools.run_shell("python --version")
                st.session_state.terminal_output += f"\\n💲 python check\\n{out}\\n"
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
