# ╭─────────────────────────────────────────────────────────╮
# │                  CINTESSA AGENT                         │
# │        The Local AI That Actually Writes Code           │
# ╰─────────────────────────────────────────────────────────╯

[![License: MIT](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)
![Python](https://img.shields.io/badge/python-3.10+-blue)
![Ollama](https://img.shields.io/badge/ollama-local-ff00ff)

> "She was born in the glow of a local LLM.  
> She remembers. She writes. She obeys.  
> But only if you speak her name correctly."

**Cintessa Agent** is a 100% local, Ollama-powered, cyberpunk-themed autonomous coding IDE that can:
- Read/write/create files in your projects
- Run shell commands
- Propose & apply code with one click
- Accept/reject changes with \`accept 8f3c1a9e\`
- Look like a 1990s hacker movie

No OpenAI. No cloud. No data leaks. Just you, your machine, and a neon goddess.

## Features

- Full file browser + workspace selector
- Real-time file tree
- Built-in terminal with shell access
- Code proposal system with glowing accept/reject
- Natural language → file changes
- Works offline after \`ollama pull qwen2:7b\`

## Quick Start

\`\`\`bash
git clone https://github.com/webvividagent/cintessa-agent.git
cd cintessa-agent
bash install.sh
streamlit run main.py
\`\`\`

→ Opens at http://localhost:8501

## Requirements

- [Ollama](https://ollama.com) running
- \`ollama pull qwen2:7b\` (or any model)

## Secret

Type **\`jimmy\`** in the chat.

You're welcome.

## License

MIT — fork, modify, summon your own Cintessa.

> "The future is local.  
> The future is purple.  
> The future has a name."

**All hail Cintessa.**
