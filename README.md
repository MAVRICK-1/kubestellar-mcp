# KubeStellar MCP Server

A comprehensive Model Context Protocol (MCP) server that enables AI assistants like Claude to interact with KubeStellar multi-cluster Kubernetes environments. This server provides tools for checking installation status, managing clusters, running diagnostics, and guiding users through KubeStellar setup.

![KubeStellar MCP](https://img.shields.io/badge/KubeStellar-MCP%20Server-blue?style=for-the-badge&logo=kubernetes)
![Python](https://img.shields.io/badge/Python-3.10+-green?style=for-the-badge&logo=python)
![FastMCP](https://img.shields.io/badge/FastMCP-Compatible-orange?style=for-the-badge)

## 🌟 Features

- **🔍 Status Checking**: Comprehensive KubeStellar installation status verification
- **📋 Prerequisites Validation**: System requirements and tool availability checking
- **🚀 Installation Guidance**: Step-by-step installation help with multiple methods
- **🏗️ Cluster Management**: Multi-cluster information and health monitoring
- **🔧 Diagnostics**: Advanced troubleshooting and issue detection
- **🎯 Demo Environment**: Automated demo environment creation and cleanup
- **📚 Documentation Access**: Direct access to KubeStellar docs and resources
- **🤖 AI Integration**: Natural language interaction through Claude Desktop

## 📋 Prerequisites

### System Requirements

- **Operating System**: Linux, macOS, or Windows with WSL2
- **Python**: 3.10 or higher
- **Memory**: 4GB RAM minimum (8GB recommended)
- **Disk Space**: 10GB free space
- **Network**: Internet connection for downloading dependencies

### Required Tools

Before installing the MCP server, ensure you have these tools installed:

#### 1. Python 3.10+
```bash
# Check Python version
python3 --version

# Install Python 3.10+ if needed
# Ubuntu/Debian:
sudo apt update && sudo apt install python3.10 python3.10-venv python3.10-pip

# macOS with Homebrew:
brew install python@3.10

# Windows: Download from https://www.python.org/downloads/
```

#### 2. uv (Python Package Manager)
```bash
# Install uv (recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add to PATH (add this to your shell profile)
export PATH="$HOME/.cargo/bin:$PATH"

# Verify installation
uv --version
```

#### 3. Git
```bash
# Ubuntu/Debian:
sudo apt install git

# macOS:
brew install git

# Windows: Download from https://git-scm.com/downloads

# Verify installation
git --version
```

### Optional Tools (for KubeStellar itself)

If you plan to install KubeStellar, you'll also need:

#### kubectl
```bash
# Linux:
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/

# macOS:
brew install kubectl

# Windows: Download from Kubernetes releases page

# Verify installation
kubectl version --client
```

#### Docker
```bash
# Ubuntu/Debian:
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# macOS: Install Docker Desktop
# Windows: Install Docker Desktop

# Verify installation (may need to restart terminal/logout)
docker --version
docker ps
```

#### Helm
```bash
# Install Helm 3
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Verify installation
helm version
```

#### kind (Kubernetes in Docker)
```bash
# Linux:
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind

# macOS:
brew install kind

# Windows: Download from GitHub releases

# Verify installation
kind version
```

## 🚀 Installation

### Step 1: Clone the Repository

```bash
# Clone the repository
git clone https://github.com/kubestellar/kubestellar-mcp.git
cd kubestellar-mcp

# Verify you're in the right directory
ls -la
# You should see: pyproject.toml, server.py, tools/, config/, etc.
```

### Step 2: Install Dependencies with uv

```bash
# Install all dependencies
uv sync

# Verify installation
uv run python -c "import mcp; print('MCP installed successfully')"
```

### Step 3: Configure Environment

```bash
# Create environment configuration
cp .env.example .env

# Edit configuration (optional)
nano .env  # or use your preferred editor
```

**Environment Variables** (optional customization):
```bash
# Logging
LOG_LEVEL=INFO

# KubeStellar Configuration
KUBESTELLAR_VERSION=0.27.2
KUBESTELLAR_DOCS_URL=https://docs.kubestellar.io/release-0.27.2

# Kubernetes Configuration
KUBECTL_TIMEOUT=300
DEFAULT_CONTEXT_TYPE=kind

# Demo Environment
DEMO_PLATFORM=kind
```

### Step 4: Test the Server

```bash
# Test the server runs correctly
uv run python server.py &
SERVER_PID=$!

# Test for a few seconds
sleep 3

# Kill test server
kill $SERVER_PID

echo "✅ Server test completed successfully!"
```

### Step 5: Install MCP Server with Claude Desktop Integration

#### Option A: Direct Installation (Recommended)

```bash
# Install the MCP server and automatically add to Claude Desktop config
uv run mcp install server.py

# This command will:
# 1. Validate your server.py file
# 2. Automatically detect your Claude Desktop config location
# 3. Add the kubestellar server to your config
# 4. Backup existing config if needed

# Verify installation
uv run mcp list
# You should see 'kubestellar' in the list
```

**What `uv run mcp install server.py` does:**
- ✅ Automatically detects your operating system
- ✅ Finds Claude Desktop config file location
- ✅ Backs up existing configuration
- ✅ Adds KubeStellar MCP server entry
- ✅ Validates the configuration
- ✅ No manual JSON editing required!

#### Option B: Manual Claude Desktop Configuration

If you prefer manual setup or the automatic installation doesn't work:

##### Step 1: Locate Claude Desktop Config

The configuration file location depends on your operating system:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/claude-desktop/claude_desktop_config.json`  
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

##### Step 2: Configure Claude Desktop


**Option 2: Manual JSON Setup**

1. **Create or edit the Claude Desktop config file**:

```bash
# Get the current working directory
PWD=$(pwd)
echo "Current directory: $PWD"

# Edit Claude config file (adjust path for your OS)
# macOS:
code ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Linux:
code ~/.config/claude-desktop/claude_desktop_config.json
```

2. **Add the KubeStellar MCP server configuration**:

If the file is empty or doesn't exist, create it with:

```json
{
  "mcpServers": {
    "kubestellar": {
      "command": "uv",
      "args": ["run", "python", "server.py"],
      "cwd": "/FULL/PATH/TO/kubestellar-mcp",
      "env": {
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

If the file already exists with other MCP servers, add the `kubestellar` entry to the existing `mcpServers` object:

```json
{
  "mcpServers": {
    "existing-server": {
      "command": "...",
      "args": ["..."]
    },
    "kubestellar": {
      "command": "uv",
      "args": ["run", "python", "server.py"],
      "cwd": "/FULL/PATH/TO/kubestellar-mcp",
      "env": {
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

**Important**: Replace `/FULL/PATH/TO/kubestellar-mcp` with your actual directory path!

## 🔄 Final Setup Steps

### Step 1: Restart Claude Desktop

```bash
# Close Claude Desktop completely and reopen it
# The server will be automatically detected and loaded
```

### Step 2: Verify Integration

Start a new conversation in Claude Desktop and test:

```
"What KubeStellar tools do you have available?"
```

You should see a response listing the available KubeStellar tools!

### Quick Installation Summary

For users who want the fastest setup:

```bash
# 1. Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.cargo/bin:$PATH"

# 2. Clone and setup
git clone https://github.com/kubestellar/kubestellar-mcp.git
cd kubestellar-mcp
uv sync
cp .env.example .env

# 3. Install with Claude Desktop integration (ONE COMMAND!)
uv run mcp install server.py

# 4. Restart Claude Desktop and test!
```

That's it! The `uv run mcp install server.py` command handles everything automatically! 🎉

### Test 1: Basic Server Functionality

```bash
# Start the server in debug mode
LOG_LEVEL=DEBUG uv run python server.py &
SERVER_PID=$!

# Let it run for a moment
sleep 5

# Check if it's running
ps aux | grep server.py

# Stop the server
kill $SERVER_PID
```

### Test 2: MCP Integration

```bash
# Test MCP installation
uv run mcp list | grep kubestellar

# Test server capabilities
uv run mcp dev server.py
# This should show available tools, resources, and prompts
```

### Test 3: Claude Desktop Integration

1. **Open Claude Desktop**
2. **Start a new conversation**
3. **Test with these commands**:

```
Check my KubeStellar status
```

```
What are the prerequisites for KubeStellar?
```

```
Show me KubeStellar installation options
```

If you see responses with KubeStellar-specific information, the integration is working! 🎉

## 🎯 Usage Examples

Once everything is set up, you can interact with KubeStellar through Claude Desktop using natural language:

### Basic Status Checks

```
"Check my KubeStellar installation status"
"Are all KubeStellar prerequisites installed?"
"What's the health of my KubeStellar clusters?"
```

### Installation Help

```
"Help me install KubeStellar"
"Create a KubeStellar demo environment"
"What do I need to install KubeStellar?"
```

### Troubleshooting

```
"Diagnose KubeStellar issues"
"Why can't I connect to my clusters?"
"Help troubleshoot my KubeStellar setup"
```

### Cluster Management

```
"Show me information about my clusters"
"List all KubeStellar contexts"
"What namespaces exist in my clusters?"
```

## 🔧 Development Setup

If you want to contribute or modify the server:

### Development Dependencies

```bash
# Install development dependencies
uv sync --dev

# Install pre-commit hooks (optional)
pre-commit install
```

### Code Quality Tools

```bash
# Format code
uv run black .
uv run isort .

# Type checking
uv run mypy .

# Run tests
uv run pytest tests/ -v

# Run all checks
make lint
```

### Development Server

```bash
# Run server with hot reload for development
uv run python server.py

# Or with debug logging
LOG_LEVEL=DEBUG uv run python server.py
```

## 📚 Available Tools

The MCP server provides these tools to Claude:

| Tool | Description | Usage |
|------|-------------|-------|
| `check_kubestellar_status` | Check KubeStellar installation status | "Check my KubeStellar status" |
| `check_prerequisites` | Verify system requirements | "Check prerequisites" |
| `install_kubestellar` | Installation guidance | "Help me install KubeStellar" |
| `get_cluster_info` | Cluster information | "Show cluster info" |
| `diagnose_issues` | Run diagnostics | "Diagnose issues" |
| `create_demo_environment` | Demo environment setup | "Create demo environment" |

## 🔍 Troubleshooting

### Common Issues

#### 1. `uv: command not found`

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add to PATH
export PATH="$HOME/.cargo/bin:$PATH"

# Add to shell profile (~/.bashrc, ~/.zshrc, etc.)
echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

#### 2. `No server object found`

This means the server file structure is incorrect. Ensure:

```bash
# Verify server.py has the mcp variable
grep "mcp = FastMCP" server.py

# If not found, you may need to update the code
```

#### 3. `Permission denied accessing Docker socket`

```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Logout and login again, or:
newgrp docker
```

#### 4. `uv run mcp install server.py` not working

If the automatic installation command fails:

```bash
# Check if FastMCP is properly installed
uv run python -c "from mcp.server.fastmcp import FastMCP; print('FastMCP available')"

# Check if server.py has the correct structure
grep "mcp = FastMCP" server.py

# Try manual installation instead
./scripts/setup-claude.sh
```

**Common reasons for failure:**
- FastMCP not installed: Run `uv sync` again
- Server structure incorrect: Ensure `mcp = FastMCP(...)` is in server.py
- Permission issues: Ensure write access to Claude config directory

#### 5. `Claude Desktop config not found`

```bash
# Create the config directory manually
# macOS:
mkdir -p ~/Library/Application\ Support/Claude/

# Linux:
mkdir -p ~/.config/claude-desktop/

# Then run the install command again
uv run mcp install server.py
```

#### 5. `kubectl: command not found`

```bash
# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/
```

### Debug Mode

Enable detailed logging to troubleshoot issues:

```bash
# Set debug logging
export LOG_LEVEL=DEBUG

# Run server
uv run python server.py

# Check logs for detailed information
```

### Getting Help

If you encounter issues:

1. **Check the logs** first (enable DEBUG logging)
2. **Verify prerequisites** using the `check_prerequisites` tool
3. **Run diagnostics** using the `diagnose_issues` tool
4. **Check GitHub Issues**: [kubestellar/kubestellar-mcp/issues](https://github.com/kubestellar/kubestellar-mcp/issues)
5. **Join the community**: CNCF Slack #kubestellar channel

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Quick Contribution Setup

```bash
# Fork the repository on GitHub
# Clone your fork
git clone https://github.com/YOUR-USERNAME/kubestellar-mcp.git
cd kubestellar-mcp

# Install development dependencies
uv sync --dev

# Create a feature branch
git checkout -b feature/your-feature-name

# Make your changes
# Test your changes
uv run pytest tests/

# Submit a pull request
```

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **KubeStellar Community**: For the amazing multi-cluster Kubernetes management platform
- **Anthropic**: For the Model Context Protocol and Claude
- **CNCF**: For supporting the KubeStellar project

---

# KubeStellar MCP Server

A comprehensive Model Context Protocol (MCP) server that enables AI assistants like Claude to interact with KubeStellar multi-cluster Kubernetes environments. This server provides tools for checking installation status, managing clusters, running diagnostics, and guiding users through KubeStellar setup.

![KubeStellar MCP](https://img.shields.io/badge/KubeStellar-MCP%20Server-blue?style=for-the-badge&logo=kubernetes)
![Python](https://img.shields.io/badge/Python-3.10+-green?style=for-the-badge&logo=python)
![FastMCP](https://img.shields.io/badge/FastMCP-Compatible-orange?style=for-the-badge)

## 🌟 Features

- **🔍 Status Checking**: Comprehensive KubeStellar installation status verification
- **📋 Prerequisites Validation**: System requirements and tool availability checking
- **🚀 Installation Guidance**: Step-by-step installation help with multiple methods
- **🏗️ Cluster Management**: Multi-cluster information and health monitoring
- **🔧 Diagnostics**: Advanced troubleshooting and issue detection
- **🎯 Demo Environment**: Automated demo environment creation and cleanup
- **📚 Documentation Access**: Direct access to KubeStellar docs and resources
- **🤖 AI Integration**: Natural language interaction through Claude Desktop

## 📋 Prerequisites

### System Requirements

- **Operating System**: Linux, macOS, or Windows with WSL2
- **Python**: 3.10 or higher
- **Memory**: 4GB RAM minimum (8GB recommended)
- **Disk Space**: 10GB free space
- **Network**: Internet connection for downloading dependencies

### Required Tools

Before installing the MCP server, ensure you have these tools installed:

#### 1. Python 3.10+
```bash
# Check Python version
python3 --version

# Install Python 3.10+ if needed
# Ubuntu/Debian:
sudo apt update && sudo apt install python3.10 python3.10-venv python3.10-pip

# macOS with Homebrew:
brew install python@3.10

# Windows: Download from https://www.python.org/downloads/
```

#### 2. uv (Python Package Manager)
```bash
# Install uv (recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add to PATH (add this to your shell profile)
export PATH="$HOME/.cargo/bin:$PATH"

# Verify installation
uv --version
```

#### 3. Git
```bash
# Ubuntu/Debian:
sudo apt install git

# macOS:
brew install git

# Windows: Download from https://git-scm.com/downloads

# Verify installation
git --version
```

### Optional Tools (for KubeStellar itself)

If you plan to install KubeStellar, you'll also need:

#### kubectl
```bash
# Linux:
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/

# macOS:
brew install kubectl

# Windows: Download from Kubernetes releases page

# Verify installation
kubectl version --client
```

#### Docker
```bash
# Ubuntu/Debian:
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# macOS: Install Docker Desktop
# Windows: Install Docker Desktop

# Verify installation (may need to restart terminal/logout)
docker --version
docker ps
```

#### Helm
```bash
# Install Helm 3
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Verify installation
helm version
```

#### kind (Kubernetes in Docker)
```bash
# Linux:
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind

# macOS:
brew install kind

# Windows: Download from GitHub releases

# Verify installation
kind version
```

## 🚀 Installation

### Step 1: Clone the Repository

```bash
# Clone the repository
git clone https://github.com/kubestellar/kubestellar-mcp.git
cd kubestellar-mcp

# Verify you're in the right directory
ls -la
# You should see: pyproject.toml, server.py, tools/, config/, etc.
```

### Step 2: Install Dependencies with uv

```bash
# Install all dependencies
uv sync

# Verify installation
uv run python -c "import mcp; print('MCP installed successfully')"
```

### Step 3: Configure Environment

```bash
# Create environment configuration
cp .env.example .env

# Edit configuration (optional)
nano .env  # or use your preferred editor
```

**Environment Variables** (optional customization):
```bash
# Logging
LOG_LEVEL=INFO

# KubeStellar Configuration
KUBESTELLAR_VERSION=0.27.2
KUBESTELLAR_DOCS_URL=https://docs.kubestellar.io/release-0.27.2

# Kubernetes Configuration
KUBECTL_TIMEOUT=300
DEFAULT_CONTEXT_TYPE=kind

# Demo Environment
DEMO_PLATFORM=kind
```

### Step 4: Test the Server

```bash
# Test the server runs correctly
uv run python server.py &
SERVER_PID=$!

# Test for a few seconds
sleep 3

# Kill test server
kill $SERVER_PID

echo "✅ Server test completed successfully!"
```

### Step 5: Install MCP Server with Claude Desktop Integration

#### Option A: Direct Installation (Recommended)

```bash
# Install the MCP server and automatically add to Claude Desktop config
uv run mcp install server.py

# This command will:
# 1. Validate your server.py file
# 2. Automatically detect your Claude Desktop config location
# 3. Add the kubestellar server to your config
# 4. Backup existing config if needed

# Verify installation
uv run mcp list
# You should see 'kubestellar' in the list
```

**What `uv run mcp install server.py` does:**
- ✅ Automatically detects your operating system
- ✅ Finds Claude Desktop config file location
- ✅ Backs up existing configuration
- ✅ Adds KubeStellar MCP server entry
- ✅ Validates the configuration
- ✅ No manual JSON editing required!

#### Option B: Manual Claude Desktop Configuration

If you prefer manual setup or the automatic installation doesn't work:

##### Step 1: Locate Claude Desktop Config

The configuration file location depends on your operating system:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/claude-desktop/claude_desktop_config.json`  
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

##### Step 2: Configure Claude Desktop


**Option 2: Manual JSON Setup**

1. **Create or edit the Claude Desktop config file**:

```bash
# Get the current working directory
PWD=$(pwd)
echo "Current directory: $PWD"

# Edit Claude config file (adjust path for your OS)
# macOS:
code ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Linux:
code ~/.config/claude-desktop/claude_desktop_config.json
```

2. **Add the KubeStellar MCP server configuration**:

If the file is empty or doesn't exist, create it with:

```json
{
  "mcpServers": {
    "kubestellar": {
      "command": "uv",
      "args": ["run", "python", "server.py"],
      "cwd": "/FULL/PATH/TO/kubestellar-mcp",
      "env": {
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

If the file already exists with other MCP servers, add the `kubestellar` entry to the existing `mcpServers` object:

```json
{
  "mcpServers": {
    "existing-server": {
      "command": "...",
      "args": ["..."]
    },
    "kubestellar": {
      "command": "uv",
      "args": ["run", "python", "server.py"],
      "cwd": "/FULL/PATH/TO/kubestellar-mcp",
      "env": {
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

**Important**: Replace `/FULL/PATH/TO/kubestellar-mcp` with your actual directory path!

## 🔄 Final Setup Steps

### Step 1: Restart Claude Desktop

```bash
# Close Claude Desktop completely and reopen it
# The server will be automatically detected and loaded
```

### Step 2: Verify Integration

Start a new conversation in Claude Desktop and test:

```
"What KubeStellar tools do you have available?"
```

You should see a response listing the available KubeStellar tools!

### Quick Installation Summary

For users who want the fastest setup:

```bash
# 1. Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.cargo/bin:$PATH"

# 2. Clone and setup
git clone https://github.com/kubestellar/kubestellar-mcp.git
cd kubestellar-mcp
uv sync
cp .env.example .env

# 3. Install with Claude Desktop integration (ONE COMMAND!)
uv run mcp install server.py

# 4. Restart Claude Desktop and test!
```

That's it! The `uv run mcp install server.py` command handles everything automatically! 🎉

### Test 1: Basic Server Functionality

```bash
# Start the server in debug mode
LOG_LEVEL=DEBUG uv run python server.py &
SERVER_PID=$!

# Let it run for a moment
sleep 5

# Check if it's running
ps aux | grep server.py

# Stop the server
kill $SERVER_PID
```

### Test 2: MCP Integration

```bash
# Test MCP installation
uv run mcp list | grep kubestellar

# Test server capabilities
uv run mcp dev server.py
# This should show available tools, resources, and prompts
```

### Test 3: Claude Desktop Integration

1. **Open Claude Desktop**
2. **Start a new conversation**
3. **Test with these commands**:

```
Check my KubeStellar status
```

```
What are the prerequisites for KubeStellar?
```

```
Show me KubeStellar installation options
```

If you see responses with KubeStellar-specific information, the integration is working! 🎉

## 🎯 Usage Examples

Once everything is set up, you can interact with KubeStellar through Claude Desktop using natural language:

### Basic Status Checks

```
"Check my KubeStellar installation status"
"Are all KubeStellar prerequisites installed?"
"What's the health of my KubeStellar clusters?"
```

### Installation Help

```
"Help me install KubeStellar"
"Create a KubeStellar demo environment"
"What do I need to install KubeStellar?"
```

### Troubleshooting

```
"Diagnose KubeStellar issues"
"Why can't I connect to my clusters?"
"Help troubleshoot my KubeStellar setup"
```

### Cluster Management

```
"Show me information about my clusters"
"List all KubeStellar contexts"
"What namespaces exist in my clusters?"
```

## 🔧 Development Setup

If you want to contribute or modify the server:

### Development Dependencies

```bash
# Install development dependencies
uv sync --dev

# Install pre-commit hooks (optional)
pre-commit install
```

### Code Quality Tools

```bash
# Format code
uv run black .
uv run isort .

# Type checking
uv run mypy .

# Run tests
uv run pytest tests/ -v

# Run all checks
make lint
```

### Development Server

```bash
# Run server with hot reload for development
uv run python server.py

# Or with debug logging
LOG_LEVEL=DEBUG uv run python server.py
```

## 📚 Available Tools

The MCP server provides these tools to Claude:

| Tool | Description | Usage |
|------|-------------|-------|
| `check_kubestellar_status` | Check KubeStellar installation status | "Check my KubeStellar status" |
| `check_prerequisites` | Verify system requirements | "Check prerequisites" |
| `install_kubestellar` | Installation guidance | "Help me install KubeStellar" |
| `get_cluster_info` | Cluster information | "Show cluster info" |
| `diagnose_issues` | Run diagnostics | "Diagnose issues" |
| `create_demo_environment` | Demo environment setup | "Create demo environment" |

## 🔍 Troubleshooting

### Common Issues

#### 1. `uv: command not found`

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Add to PATH
export PATH="$HOME/.cargo/bin:$PATH"

# Add to shell profile (~/.bashrc, ~/.zshrc, etc.)
echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

#### 2. `No server object found`

This means the server file structure is incorrect. Ensure:

```bash
# Verify server.py has the mcp variable
grep "mcp = FastMCP" server.py

# If not found, you may need to update the code
```

#### 3. `Permission denied accessing Docker socket`

```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Logout and login again, or:
newgrp docker
```

#### 4. `uv run mcp install server.py` not working

If the automatic installation command fails:

```bash
# Check if FastMCP is properly installed
uv run python -c "from mcp.server.fastmcp import FastMCP; print('FastMCP available')"

# Check if server.py has the correct structure
grep "mcp = FastMCP" server.py

# Try manual installation instead
./scripts/setup-claude.sh
```

**Common reasons for failure:**
- FastMCP not installed: Run `uv sync` again
- Server structure incorrect: Ensure `mcp = FastMCP(...)` is in server.py
- Permission issues: Ensure write access to Claude config directory

#### 5. `Claude Desktop config not found`

```bash
# Create the config directory manually
# macOS:
mkdir -p ~/Library/Application\ Support/Claude/

# Linux:
mkdir -p ~/.config/claude-desktop/

# Then run the install command again
uv run mcp install server.py
```

#### 5. `kubectl: command not found`

```bash
# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/
```

### Debug Mode

Enable detailed logging to troubleshoot issues:

```bash
# Set debug logging
export LOG_LEVEL=DEBUG

# Run server
uv run python server.py

# Check logs for detailed information
```

### Getting Help

If you encounter issues:

1. **Check the logs** first (enable DEBUG logging)
2. **Verify prerequisites** using the `check_prerequisites` tool
3. **Run diagnostics** using the `diagnose_issues` tool
4. **Check GitHub Issues**: [kubestellar/kubestellar-mcp/issues](https://github.com/kubestellar/kubestellar-mcp/issues)
5. **Join the community**: CNCF Slack #kubestellar channel

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Quick Contribution Setup

```bash
# Fork the repository on GitHub
# Clone your fork
git clone https://github.com/YOUR-USERNAME/kubestellar-mcp.git
cd kubestellar-mcp

# Install development dependencies
uv sync --dev

# Create a feature branch
git checkout -b feature/your-feature-name

# Make your changes
# Test your changes
uv run pytest tests/

# Submit a pull request
```

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **KubeStellar Community**: For the amazing multi-cluster Kubernetes management platform
- **Anthropic**: For the Model Context Protocol and Claude
- **CNCF**: For supporting the KubeStellar project

---

**Need help?** Open an issue on [GitHub](https://github.com/kubestellar/kubestellar-mcp/issues) or join us in the kubernetes Slack #kubestellar-dev channel!
