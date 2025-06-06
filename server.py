import asyncio
import json
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import Prompt
from mcp.server.fastmcp.resources import Resource

from config.settings import settings
from tools.kubestellar_status.status_checker import KubeStellarStatusChecker
from tools.kubestellar_status.prerequisites import PrerequisitesChecker
from tools.kubestellar_status.installation_helper import InstallationHelper
from tools.kubestellar_status.cluster_manager import ClusterManager
from tools.kubestellar_status.diagnostics import DiagnosticsRunner
from tools.kubestellar_status.demo_environment import DemoEnvironmentManager
from resources.docs_provider import DocsProvider
from resources.script_provider import ScriptProvider
from prompts.kubestellar_prompts import KubeStellarPrompts
from utils.logger import setup_logger

logger = setup_logger(__name__)

# Initialize the FastMCP server
mcp = FastMCP(settings.server_name)

# Initialize service classes
status_checker = KubeStellarStatusChecker()
prerequisites_checker = PrerequisitesChecker()
installation_helper = InstallationHelper()
cluster_manager = ClusterManager()
diagnostics_runner = DiagnosticsRunner()
demo_manager = DemoEnvironmentManager()
docs_provider = DocsProvider()
script_provider = ScriptProvider()


@mcp.tool()
async def check_kubestellar_status() -> Dict:
    """Check the status of KubeStellar installation and identify missing components."""
    logger.info("Checking KubeStellar status")
    result = await status_checker.check_kubestellar_status()
    
    # Add formatted message for better display
    if result['all_ready']:
        result['formatted_message'] = f"""✅ **KubeStellar Status: READY**

🎯 **Context**: {result['context']}
✅ **WDS1 Namespace**: Available
✅ **ITS1 Namespace**: Available

Your KubeStellar installation is complete and ready to use!

**Next Steps:**
- Deploy workloads using Binding Policies
- Check cluster information with `get_cluster_info`
- Visit: https://docs.kubestellar.io/release-0.27.2/direct/examples/
"""
    elif result['context_found']:
        missing_ns = []
        if not result['wds1_namespace']:
            missing_ns.append("wds1-system")
        if not result['its1_namespace']:
            missing_ns.append("its1-system")
        
        result['formatted_message'] = f"""⚠️ **KubeStellar Status: INCOMPLETE**

🎯 **Context Found**: {result['context']}
❌ **Missing Namespaces**: {', '.join(missing_ns)}

**Next Steps:**
1. Complete KubeStellar installation
2. Use `install_kubestellar` for guidance
3. Or run demo environment setup: `create_demo_environment`
"""
    else:
        result['formatted_message'] = f"""❌ **KubeStellar Status: NOT INSTALLED**

No compatible KubeStellar contexts found.
Looking for contexts containing: 'kubeflex', 'kind', or 'k3d'

**Next Steps:**
1. Check prerequisites: `check_prerequisites`
2. Install KubeStellar: `install_kubestellar`
3. Or create demo environment: `create_demo_environment`
4. Visit: https://docs.kubestellar.io/release-0.27.2/direct/user-guide-intro/
"""
    
    return result


@mcp.tool()
async def check_prerequisites() -> Dict:
    """Check system prerequisites for KubeStellar installation."""
    logger.info("Checking prerequisites")
    result = await prerequisites_checker.check_prerequisites()
    
    # Add formatted summary
    status_icon = "✅" if result['all_satisfied'] else "❌"
    result['formatted_summary'] = f"""{status_icon} **Prerequisites Check**

**Overall Status**: {'All Satisfied' if result['all_satisfied'] else 'Issues Found'}

**Tool Status:**"""
    
    for tool, check in result['checks'].items():
        icon = "✅" if check['installed'] else "❌"
        result['formatted_summary'] += f"\n- **{tool}**: {icon}"
        if check['installed'] and check['version']:
            # Show just the first line of version for brevity
            version_short = check['version'].split('\n')[0]
            result['formatted_summary'] += f" ({version_short})"
    
    if result['missing']:
        result['formatted_summary'] += f"\n\n**Missing**: {', '.join(result['missing'])}"
    
    return result


@mcp.tool()
async def install_kubestellar(
    method: str = "guide",
    platform: str = "kind"
) -> Dict:
    """
    Get KubeStellar installation guide and information.
    
    Args:
        method: Installation method - 'guide', 'download_script', or 'validate_environment'
        platform: Kubernetes platform to use - 'kind' or 'k3d'
    """
    logger.info(f"Getting installation help: method={method}, platform={platform}")
    
    if method == "guide":
        result = await installation_helper.get_installation_guide()
        result['formatted_guide'] = f"""# 🚀 {result['title']}

**Version**: {result['version']}
📚 **Documentation**: {result['documentation']}

## 🎯 Quick Start (Recommended)

### Demo Environment Setup
```bash
curl -s {result['installation_methods']['demo_script']['script_url']} | bash -s -- --platform {platform}
```

**What this does:**
- Creates 3 clusters: kubeflex, cluster1, cluster2
- Installs KubeStellar core components
- Sets up OCM (Open Cluster Management)
- Ready-to-use demo environment in 15-30 minutes

### Manual Installation
- **Chart**: `{result['installation_methods']['helm_chart']['chart']}`
- **Version**: {result['installation_methods']['helm_chart']['version']}

## 📋 Requirements
- **Platforms**: {', '.join(result['supported_platforms'])}
- **Ports**: {', '.join(map(str, result['required_ports']))}

## 🎯 Next Steps
1. Run `check_prerequisites` first
2. Choose your platform ({platform})
3. Use `create_demo_environment` for automated setup
"""
        
    elif method == "download_script":
        result = await installation_helper.download_demo_script()
        if result['success']:
            result['formatted_guide'] = f"""# 📥 Demo Script Ready

**Usage**: Save and run this script
```bash
# Save the script
curl -s {result['script_url']} > create-kubestellar-demo-env.sh
chmod +x create-kubestellar-demo-env.sh

# Run with your preferred platform
./create-kubestellar-demo-env.sh --platform {platform}
```

**Platforms**: {', '.join(result['platforms'])}
**Estimated Time**: 15-30 minutes
"""
        else:
            result['formatted_guide'] = f"""# ❌ Script Download Failed

**Error**: {result['error']}

**Manual Download**: {result['script_url']}
"""
    
    elif method == "validate_environment":
        result = await installation_helper.validate_installation_environment(platform)
        status_icon = "✅" if result['ready'] else "❌"
        
        result['formatted_guide'] = f"""# 🔍 Environment Validation

**Platform**: {result['platform']}
**Ready**: {status_icon} {'Yes' if result['ready'] else 'No'}

"""
        if result['issues']:
            result['formatted_guide'] += "**❌ Issues Found:**\n"
            for issue in result['issues']:
                result['formatted_guide'] += f"- {issue}\n"
        
        if result['warnings']:
            result['formatted_guide'] += "\n**⚠️ Warnings:**\n"
            for warning in result['warnings']:
                result['formatted_guide'] += f"- {warning}\n"
        
        if result['ready']:
            result['formatted_guide'] += "\n🎉 **Ready to install KubeStellar!**"
    
    return result


@mcp.tool()
async def get_cluster_info(context: Optional[str] = None) -> Dict:
    """
    Get information about KubeStellar clusters and contexts.
    
    Args:
        context: Specific context to get info for (optional)
    """
    logger.info(f"Getting cluster info for context: {context or 'all'}")
    result = await cluster_manager.get_cluster_info(context)
    
    if "error" in result:
        result['formatted_info'] = f"❌ **Error**: {result['error']}"
        return result
    
    # Format the cluster information
    result['formatted_info'] = f"""# 🔍 Cluster Information

## 📊 Summary
- **Total Contexts**: {result['summary']['total_contexts']}
- **KubeStellar Contexts**: {result['summary']['kubestellar_contexts']}
- **Accessible**: {result['summary']['accessible_clusters']}

## 🏗️ Cluster Details
"""
    
    for ctx, info in result['clusters'].items():
        accessible_icon = "✅" if info['accessible'] else "❌"
        result['formatted_info'] += f"\n### 🎯 {ctx}\n"
        result['formatted_info'] += f"**Status**: {accessible_icon} {'Accessible' if info['accessible'] else 'Not Accessible'}\n"
        
        if info['accessible']:
            result['formatted_info'] += f"**Nodes**: {len(info['nodes'])}\n"
            result['formatted_info'] += f"**Namespaces**: {len(info['namespaces'])}\n"
            
            if 'kubestellar_namespaces' in info:
                result['formatted_info'] += "\n**KubeStellar Namespaces**:\n"
                for ns, exists in info['kubestellar_namespaces'].items():
                    status = "✅" if exists else "❌"
                    result['formatted_info'] += f"- {ns}: {status}\n"
            
            if 'kubestellar_resources' in info:
                resources = info['kubestellar_resources']
                if any(resources.values()):
                    result['formatted_info'] += "\n**KubeStellar Resources**:\n"
                    for resource_type, items in resources.items():
                        if items:
                            result['formatted_info'] += f"- {resource_type.replace('_', ' ').title()}: {len(items)}\n"
    
    return result


@mcp.tool()
async def diagnose_issues() -> Dict:
    """Run comprehensive diagnostics on KubeStellar installation."""
    logger.info("Running diagnostics")
    result = await diagnostics_runner.diagnose_issues()
    
    # Format the diagnostic results
    status_map = {
        "healthy": "🟢 HEALTHY",
        "warnings": "🟡 WARNINGS", 
        "issues_found": "🔴 ISSUES FOUND",
        "running": "🔄 RUNNING"
    }
    
    result['formatted_report'] = f"""# 🔍 KubeStellar Diagnostics Report

## 📊 Overall Status: {status_map.get(result['status'], result['status'].upper())}

### Summary
- **Total Checks**: {result['summary']['total_checks']}
- **✅ Passed**: {result['summary']['passed']}
- **⚠️ Warnings**: {result['summary']['warnings']}
- **❌ Failed**: {result['summary']['failures']}

## 🔍 Detailed Results
"""
    
    status_icons = {"pass": "✅", "warning": "⚠️", "fail": "❌", "error": "💥"}
    
    for check_name, check_result in result['checks'].items():
        icon = status_icons.get(check_result['status'], "❓")
        result['formatted_report'] += f"\n### {icon} {check_name.replace('_', ' ').title()}\n"
        result['formatted_report'] += f"**Status**: {check_result['status'].upper()}\n"
        result['formatted_report'] += f"**Details**: {check_result['message']}\n"
    
    if result['issues_found']:
        result['formatted_report'] += "\n## 🚨 Issues Found\n"
        for issue in result['issues_found']:
            result['formatted_report'] += f"- ❌ {issue}\n"
    
    if result['recommendations']:
        result['formatted_report'] += "\n## 💡 Recommendations\n"
        for rec in result['recommendations']:
            result['formatted_report'] += f"- 💡 {rec}\n"
    
    return result


@mcp.tool()
async def create_demo_environment(
    action: str = "create",
    platform: str = "kind"
) -> Dict:
    """
    Create or manage KubeStellar demo environment.
    
    Args:
        action: Action to perform - 'create' or 'cleanup'
        platform: Kubernetes platform to use - 'kind' or 'k3d'
    """
    logger.info(f"Demo environment action: {action} with platform: {platform}")
    
    if action == "create":
        result = await demo_manager.create_demo_environment(platform)
        
        status_icon = "✅" if result['success'] else "❌"
        result['formatted_result'] = f"""# 🚀 Demo Environment Creation

**Platform**: {result['platform']}
**Status**: {status_icon} {'Success' if result['success'] else 'Failed'}

**Result**: {result['message']}

"""
        
        if result['success']:
            result['formatted_result'] += f"""## 🎉 Created Resources
**Clusters**: {', '.join(result['clusters_created'])}
**Contexts**: {', '.join(result['contexts_created'])}

## 🎯 Next Steps
"""
            for i, step in enumerate(result['next_steps'], 1):
                result['formatted_result'] += f"{i}. {step}\n"
            
            result['formatted_result'] += f"""
## 🧪 Test Your Installation
```bash
# Check status
kubectl get namespaces --context its1
kubectl get managedclusters --context its1

# Deploy a sample workload
kubectl apply -f https://raw.githubusercontent.com/kubestellar/kubestellar/main/examples/basic/example-workload.yaml --context wds1
```
"""
        else:
            result['formatted_result'] += f"""## 🔧 Troubleshooting
1. Check Docker is running: `docker ps`
2. Verify {platform} is installed: `{platform} version`
3. Run prerequisites check: `check_prerequisites`
4. Check diagnostics: `diagnose_issues`

## 📋 Installation Requirements
- Docker/Podman running
- kubectl installed
- {platform} installed
- Helm 3.x installed
- Ports 9443 available

**Script Output** (last 500 chars):
```
{result.get('script_output', 'No output')[-500:]}
```
"""
    
    elif action == "cleanup":
        result = await demo_manager.cleanup_demo_environment(platform)
        
        status_icon = "✅" if result['success'] else "⚠️"
        result['formatted_result'] = f"""# 🧹 Demo Environment Cleanup

**Platform**: {result['platform']}
**Status**: {status_icon} {'Success' if result['success'] else 'Partial Success'}

## 🗑️ Cleaned Resources
**Clusters**: {', '.join(result['cleaned_clusters']) if result['cleaned_clusters'] else 'None'}
**Contexts**: {', '.join(result['cleaned_contexts']) if result['cleaned_contexts'] else 'None'}

"""
        
        if result['errors']:
            result['formatted_result'] += "## ⚠️ Cleanup Issues\n"
            for error in result['errors']:
                result['formatted_result'] += f"- {error}\n"
            result['formatted_result'] += "\nSome resources may need manual cleanup.\n"
        else:
            result['formatted_result'] += "✅ **All demo resources successfully cleaned up!**\n"
    
    return result


# Resources
@mcp.resource("kubestellar://docs/installation")
async def get_installation_docs() -> str:
    """Complete installation guide and documentation."""
    result = await docs_provider.get_installation_docs()
    return json.dumps(result, indent=2)


@mcp.resource("kubestellar://docs/index")
async def get_docs_index() -> str:
    """Main documentation index with all sections."""
    result = await docs_provider.get_documentation_index()
    return json.dumps(result, indent=2)


@mcp.resource("kubestellar://scripts/demo")
async def get_demo_script() -> str:
    """Script to create KubeStellar demo environment."""
    result = await script_provider.get_demo_script()
    return json.dumps(result, indent=2)


@mcp.resource("kubestellar://scripts/all")
async def get_all_scripts() -> str:
    """Information about all available scripts."""
    result = await script_provider.get_all_scripts()
    return json.dumps(result, indent=2)


# Prompts
@mcp.prompt()
async def kubestellar_installation_guide() -> str:
    """Comprehensive guide for KubeStellar installation."""
    prompt_data = KubeStellarPrompts.get_installation_prompt()
    return prompt_data["template"]


@mcp.prompt()
async def kubestellar_troubleshooting() -> str:
    """Help diagnose and fix KubeStellar issues."""
    prompt_data = KubeStellarPrompts.get_troubleshooting_prompt()
    return prompt_data["template"]


@mcp.prompt()
async def kubestellar_cluster_management() -> str:
    """Guide for managing KubeStellar clusters and workloads."""
    prompt_data = KubeStellarPrompts.get_cluster_management_prompt()
    return prompt_data["template"]


def main():
    """Main entry point for the server."""
    logger.info(f"Starting {settings.server_name} v{settings.server_version}")
    mcp.run()

if __name__ == "__main__":
    logger.info(f"Starting {settings.server_name} v{settings.server_version}")
    asyncio.run(main())