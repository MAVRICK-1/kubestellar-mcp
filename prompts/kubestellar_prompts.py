from typing import Dict, List

from config.settings import settings


class KubeStellarPrompts:
    """Provide prompt templates for KubeStellar operations."""
    
    @staticmethod
    def get_installation_prompt() -> Dict:
        """Get installation guidance prompt."""
        return {
            "name": "kubestellar_installation_guide",
            "description": "Comprehensive guide for KubeStellar installation",
            "template": f"""
# KubeStellar Installation Assistant

I'll help you install KubeStellar v{settings.kubestellar_version} on your system. Let me guide you through the process step by step.

## What is KubeStellar?
KubeStellar is a Cloud Native Computing Foundation (CNCF) Sandbox project that simplifies multi-cluster Kubernetes management. It allows you to deploy and manage applications across multiple clusters as if they were a single cluster.

## Installation Options

### Option 1: Demo Environment (Recommended for beginners)
- **Time**: 15-30 minutes
- **Best for**: Learning, testing, demos
- **Includes**: Complete setup with sample clusters

### Option 2: Manual Installation
- **Time**: 30-60 minutes  
- **Best for**: Production environments
- **Includes**: Custom configuration options

## Next Steps
1. First, let me check your system prerequisites
2. Choose your installation method
3. Select your Kubernetes platform (kind or k3d)
4. Run the installation
5. Verify the installation

Would you like me to:
- Check your system prerequisites?
- Show you the demo environment setup?
- Guide you through manual installation?
- Explain KubeStellar concepts first?

Just let me know how you'd like to proceed!
            """,
            "variables": {
                "version": settings.kubestellar_version,
                "docs_url": settings.kubestellar_docs_url
            }
        }
    
    @staticmethod
    def get_troubleshooting_prompt() -> Dict:
        """Get troubleshooting guidance prompt."""
        return {
            "name": "kubestellar_troubleshooting",
            "description": "Help diagnose and fix KubeStellar issues",
            "template": """
# KubeStellar Troubleshooting Assistant

I'll help you diagnose and resolve issues with your KubeStellar installation.

## Common Issues I Can Help With:

### Installation Problems
- Prerequisites not met
- Docker/container runtime issues
- Port conflicts (especially port 9443)
- Cluster creation failures
- Helm chart installation problems

### Runtime Issues
- Clusters not accessible
- Missing namespaces (wds1-system, its1-system)
- Workload synchronization problems
- Network connectivity issues

### Environment Issues
- Context configuration problems
- kubectl access issues
- Resource constraints

## Diagnostic Process
1. **System Check**: Verify prerequisites and environment
2. **Cluster Status**: Check cluster accessibility and health
3. **KubeStellar Components**: Verify core components are running
4. **Network & Connectivity**: Test cluster communication
5. **Resource Analysis**: Check for resource conflicts

## How to Get Help
- Describe your issue or error message
- Tell me what you were trying to do
- Share any error output you're seeing
- Let me know your platform (kind, k3d, etc.)

I'll run the appropriate diagnostics and provide specific solutions for your situation.

What issue are you experiencing?
            """
        }
    
    @staticmethod
    def get_cluster_management_prompt() -> Dict:
        """Get cluster management guidance prompt."""
        return {
            "name": "kubestellar_cluster_management",
            "description": "Guide for managing KubeStellar clusters and workloads",
            "template": """
# KubeStellar Cluster Management Assistant

I'll help you manage your KubeStellar clusters and workloads effectively.

## What I Can Help You With:

### Cluster Operations
- View cluster status and information
- Check cluster connectivity
- Manage cluster contexts
- Monitor cluster health

### Workload Management
- Deploy applications across clusters
- Create and manage Binding Policies
- Monitor workload synchronization
- Troubleshoot deployment issues

### Multi-Cluster Operations
- Set up Workload Definition Spaces (WDS)
- Configure Inventory and Transport Spaces (ITS)
- Manage cluster labeling and selection
- Handle cluster lifecycle operations

## Key Concepts

**Workload Definition Space (WDS)**: Where you define what to deploy
**Inventory and Transport Space (ITS)**: Manages cluster inventory and workload transport
**Binding Policies**: Define which workloads go to which clusters
**Managed Clusters**: The target clusters where workloads are deployed

## Available Commands
- `get_cluster_info`: Get detailed cluster information
- `check_kubestellar_status`: Check overall system status
- `diagnose_issues`: Run diagnostics on your setup

## Common Tasks
1. **Check System Status**: Verify all components are healthy
2. **View Cluster Information**: See what clusters are available
3. **Deploy Workloads**: Create and apply Binding Policies
4. **Monitor Status**: Check workload synchronization
5. **Troubleshoot**: Diagnose and fix issues

What would you like to do with your KubeStellar clusters?
            """
        }
    
    @staticmethod
    def get_all_prompts() -> Dict:
        """Get all available prompts."""
        return {
            "installation": KubeStellarPrompts.get_installation_prompt(),
            "troubleshooting": KubeStellarPrompts.get_troubleshooting_prompt(),
            "cluster_management": KubeStellarPrompts.get_cluster_management_prompt()
        }