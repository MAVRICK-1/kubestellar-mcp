import asyncio
import json
from typing import Any, Dict, List

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions # type: ignore
import mcp.server.stdio
import mcp.types as types

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

# Initialize the MCP server
server = Server(settings.server_name)

# Initialize service classes
status_checker = KubeStellarStatusChecker()
prerequisites_checker = PrerequisitesChecker()
installation_helper = InstallationHelper()
cluster_manager = ClusterManager()
diagnostics_runner = DiagnosticsRunner()
demo_manager = DemoEnvironmentManager()
docs_provider = DocsProvider()
script_provider = ScriptProvider()


@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """List available tools."""
    return [
        types.Tool(
            name="check_kubestellar_status",
            description="Check the status of KubeStellar installation and identify missing components",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        types.Tool(
            name="check_prerequisites",
            description="Check system prerequisites for KubeStellar installation",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        types.Tool(
            name="install_kubestellar",
            description="Get KubeStellar installation guide and information",
            inputSchema={
                "type": "object",
                "properties": {
                    "method": {
                        "type": "string",
                        "enum": ["guide", "download_script", "validate_environment"],
                        "description": "Installation method: guide, download_script, or validate_environment",
                        "default": "guide"
                    },
                    "platform": {
                        "type": "string",
                        "enum": ["kind", "k3d"],
                        "description": "Kubernetes platform to use",
                        "default": "kind"
                    }
                },
                "required": []
            }
        ),
        types.Tool(
            name="get_cluster_info",
            description="Get information about KubeStellar clusters and contexts",
            inputSchema={
                "type": "object",
                "properties": {
                    "context": {
                        "type": "string",
                        "description": "Specific context to get info for (optional)"
                    }
                },
                "required": []
            }
        ),
        types.Tool(
            name="diagnose_issues",
            description="Run comprehensive diagnostics on KubeStellar installation",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        types.Tool(
            name="create_demo_environment",
            description="Create or manage KubeStellar demo environment",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["create", "cleanup"],
                        "description": "Action to perform: create or cleanup",
                        "default": "create"
                    },
                    "platform": {
                        "type": "string",
                        "enum": ["kind", "k3d"],
                        "description": "Kubernetes platform to use",
                        "default": "kind"
                    }
                },
                "required": []
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle tool calls."""
    try:
        if name == "check_kubestellar_status":
            logger.info("Checking KubeStellar status")
            result = await status_checker.check_kubestellar_status()
            
            # Format the response
            response = f"""# KubeStellar Status Check

**Status**: {result['message']}

## Details:
- **Context Found**: {result['context_found']}
- **Current Context**: {result['context']}
- **WDS1 Namespace**: {result['wds1_namespace']}
- **ITS1 Namespace**: {result['its1_namespace']}
- **All Ready**: {result['all_ready']}

## Compatible Contexts Found:
{', '.join(result['compatible_contexts']) if result['compatible_contexts'] else 'None'}

## Next Steps:
"""
            
            if result['all_ready']:
                response += "✅ KubeStellar is fully installed and ready to use!"
            elif result['context_found']:
                response += """
1. Complete the KubeStellar installation to create missing namespaces
2. Run `install_kubestellar` tool for installation guidance
3. Check the installation documentation: https://docs.kubestellar.io/release-0.27.2/direct/user-guide-intro/
"""
            else:
                response += """
1. Install KubeStellar using the demo environment setup
2. Run `check_prerequisites` to verify system requirements
3. Use `create_demo_environment` tool to set up a complete demo environment
4. Visit: https://docs.kubestellar.io/release-0.27.2/direct/user-guide-intro/
"""
            
            return [types.TextContent(type="text", text=response)]
        
        elif name == "check_prerequisites":
            logger.info("Checking prerequisites")
            result = await prerequisites_checker.check_prerequisites()
            
            response = f"""# Prerequisites Check

**Overall Status**: {'✅ All Satisfied' if result['all_satisfied'] else '❌ Issues Found'}

## Tool Availability:
"""
            
            for tool, check in result['checks'].items():
                status_icon = "✅" if check['installed'] else "❌"
                response += f"- **{tool}**: {status_icon} "
                if check['installed']:
                    response += f"Installed at {check['path']}\n"
                    if check['version']:
                        response += f"  Version: {check['version']}\n"
                else:
                    response += f"Not available - {check['error']}\n"
            
            if result['missing']:
                response += f"\n## Missing Requirements:\n"
                for missing in result['missing']:
                    response += f"- {missing}\n"
            
            response += f"\n## Recommendations:\n"
            for rec in result['recommendations']:
                response += f"- {rec}\n"
            
            return [types.TextContent(type="text", text=response)]
        
        elif name == "install_kubestellar":
            method = arguments.get("method", "guide")
            platform = arguments.get("platform", "kind")
            
            if method == "guide":
                result = await installation_helper.get_installation_guide()
                response = f"""# {result['title']}

**Version**: {result['version']}
**Documentation**: {result['documentation']}

## Installation Methods:

### 1. Demo Script (Recommended)
- **Description**: {result['installation_methods']['demo_script']['description']}
- **Script URL**: {result['installation_methods']['demo_script']['script_url']}
- **Usage**: `{result['installation_methods']['demo_script']['usage']}`

### 2. Helm Chart
- **Description**: {result['installation_methods']['helm_chart']['description']}
- **Chart**: {result['installation_methods']['helm_chart']['chart']}
- **Version**: {result['installation_methods']['helm_chart']['version']}

## Supported Platforms:
{', '.join(result['supported_platforms'])}

## Required Ports:
{', '.join(map(str, result['required_ports']))}

## Next Steps:
"""
                for step in result['next_steps']:
                    response += f"1. {step}\n"
                
            elif method == "download_script":
                result = await installation_helper.download_demo_script()
                if result['success']:
                    response = f"""# Demo Script Downloaded

**Script URL**: {result['script_url']}

## Usage:
{result['usage']}

## Supported Platforms:
{', '.join(result['platforms'])}

## Script Content:
```bash
{result['script_content'][:1000]}...
```

Save this script and run it to create your KubeStellar demo environment.
"""
                else:
                    response = f"""# Script Download Failed

**Error**: {result['error']}
**Script URL**: {result['script_url']}

Please download the script manually from the URL above.
"""
            
            elif method == "validate_environment":
                result = await installation_helper.validate_installation_environment(platform)
                response = f"""# Environment Validation

**Platform**: {result['platform']}
**Ready for Installation**: {'✅ Yes' if result['ready'] else '❌ No'}

## Issues Found:
"""
                if result['issues']:
                    for issue in result['issues']:
                        response += f"❌ {issue}\n"
                else:
                    response += "✅ No issues found\n"
                
                if result['warnings']:
                    response += "\n## Warnings:\n"
                    for warning in result['warnings']:
                        response += f"⚠️ {warning}\n"
            
            return [types.TextContent(type="text", text=response)]
        
        elif name == "get_cluster_info":
            context = arguments.get("context")
            result = await cluster_manager.get_cluster_info(context)
            
            if "error" in result:
                response = f"❌ Error: {result['error']}"
            else:
                response = f"""# Cluster Information

## Summary:
- **Total Contexts**: {result['summary']['total_contexts']}
- **KubeStellar Contexts**: {result['summary']['kubestellar_contexts']}
- **Accessible Clusters**: {result['summary']['accessible_clusters']}

## Cluster Details:
"""
                
                for ctx, info in result['clusters'].items():
                    response += f"\n### Context: {ctx}\n"
                    response += f"- **Accessible**: {'✅ Yes' if info['accessible'] else '❌ No'}\n"
                    
                    if info['accessible']:
                        response += f"- **Nodes**: {len(info['nodes'])}\n"
                        response += f"- **Namespaces**: {len(info['namespaces'])}\n"
                        
                        if 'kubestellar_namespaces' in info:
                            response += "- **KubeStellar Namespaces**:\n"
                            for ns, exists in info['kubestellar_namespaces'].items():
                                status = "✅" if exists else "❌"
                                response += f"  - {ns}: {status}\n"
                        
                        if 'kubestellar_resources' in info:
                            resources = info['kubestellar_resources']
                            if any(resources.values()):
                                response += "- **KubeStellar Resources**:\n"
                                for resource_type, items in resources.items():
                                    if items:
                                        response += f"  - {resource_type}: {len(items)}\n"
            
            return [types.TextContent(type="text", text=response)]
        
        elif name == "diagnose_issues":
            logger.info("Running diagnostics")
            result = await diagnostics_runner.diagnose_issues()
            
            response = f"""# KubeStellar Diagnostics Report

**Overall Status**: {result['status'].upper()}

## Summary:
- **Total Checks**: {result['summary']['total_checks']}
- **Passed**: ✅ {result['summary']['passed']}
- **Warnings**: ⚠️ {result['summary']['warnings']}
- **Failures**: ❌ {result['summary']['failures']}

## Detailed Results:
"""
            
            for check_name, check_result in result['checks'].items():
                status_icon = {"pass": "✅", "warning": "⚠️", "fail": "❌", "error": "💥"}.get(check_result['status'], "❓")
                response += f"\n### {check_name.replace('_', ' ').title()}\n"
                response += f"{status_icon} **Status**: {check_result['status'].upper()}\n"
                response += f"**Message**: {check_result['message']}\n"
            
            if result['issues_found']:
                response += "\n## Issues Found:\n"
                for issue in result['issues_found']:
                    response += f"❌ {issue}\n"
            
            if result['recommendations']:
                response += "\n## Recommendations:\n"
                for rec in result['recommendations']:
                    response += f"💡 {rec}\n"
            
            return [types.TextContent(type="text", text=response)]
        
        elif name == "create_demo_environment":
            action = arguments.get("action", "create")
            platform = arguments.get("platform", "kind")
            
            if action == "create":
                logger.info(f"Creating demo environment with platform: {platform}")
                result = await demo_manager.create_demo_environment(platform)
                
                response = f"""# Demo Environment Creation

**Platform**: {result['platform']}
**Status**: {'✅ Success' if result['success'] else '❌ Failed'}

**Message**: {result['message']}

"""
                
                if result['success']:
                    response += f"""## Created Resources:
- **Clusters**: {', '.join(result['clusters_created'])}
- **Contexts**: {', '.join(result['contexts_created'])}

## Next Steps:
"""
                    for step in result['next_steps']:
                        response += f"1. {step}\n"
                else:
                    response += f"""## Troubleshooting:
1. Check the script output below for specific errors
2. Ensure Docker is running
3. Verify {platform} is installed and accessible
4. Run `check_prerequisites` to verify system requirements
5. Run `diagnose_issues` for detailed diagnostics

## Script Output:
```
{result.get('script_output', 'No output available')[:2000]}...
```
"""
            
            elif action == "cleanup":
                logger.info(f"Cleaning up demo environment for platform: {platform}")
                result = await demo_manager.cleanup_demo_environment(platform)
                
                response = f"""# Demo Environment Cleanup

**Platform**: {result['platform']}
**Status**: {'✅ Success' if result['success'] else '❌ Partial Success'}

## Cleaned Resources:
- **Clusters**: {', '.join(result['cleaned_clusters']) if result['cleaned_clusters'] else 'None'}
- **Contexts**: {', '.join(result['cleaned_contexts']) if result['cleaned_contexts'] else 'None'}

"""
                
                if result['errors']:
                    response += "## Errors:\n"
                    for error in result['errors']:
                        response += f"❌ {error}\n"
            
            return [types.TextContent(type="text", text=response)]
        
        else:
            return [types.TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]
    
    except Exception as e:
        logger.error(f"Error in tool {name}: {e}")
        return [types.TextContent(
            type="text",
            text=f"Error executing {name}: {str(e)}"
        )]


@server.list_resources()
async def handle_list_resources() -> List[types.Resource]:
    """List available resources."""
    return [
        types.Resource(
            uri="kubestellar://docs/installation",
            name="KubeStellar Installation Documentation",
            description="Complete installation guide and documentation",
            mimeType="application/json"
        ),
        types.Resource(
            uri="kubestellar://docs/index",
            name="KubeStellar Documentation Index",
            description="Main documentation index with all sections",
            mimeType="application/json"
        ),
        types.Resource(
            uri="kubestellar://scripts/demo",
            name="Demo Environment Script",
            description="Script to create KubeStellar demo environment",
            mimeType="application/json"
        ),
        types.Resource(
            uri="kubestellar://scripts/prerequisites",
            name="Prerequisites Check Script",
            description="Script to check system prerequisites",
            mimeType="application/json"
        ),
        types.Resource(
            uri="kubestellar://scripts/all",
            name="All KubeStellar Scripts",
            description="Information about all available scripts",
            mimeType="application/json"
        )
    ]


@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Read a specific resource."""
    try:
        if uri == "kubestellar://docs/installation":
            result = await docs_provider.get_installation_docs()
            return json.dumps(result, indent=2)
        
        elif uri == "kubestellar://docs/index":
            result = await docs_provider.get_documentation_index()
            return json.dumps(result, indent=2)
        
        elif uri == "kubestellar://scripts/demo":
            result = await script_provider.get_demo_script()
            return json.dumps(result, indent=2)
        
        elif uri == "kubestellar://scripts/prerequisites":
            result = await script_provider.get_prerequisite_check_script()
            return json.dumps(result, indent=2)
        
        elif uri == "kubestellar://scripts/all":
            result = await script_provider.get_all_scripts()
            return json.dumps(result, indent=2)
        
        else:
            raise ValueError(f"Unknown resource URI: {uri}")
    
    except Exception as e:
        logger.error(f"Error reading resource {uri}: {e}")
        raise


@server.list_prompts()
async def handle_list_prompts() -> List[types.Prompt]:
    """List available prompts."""
    prompts = KubeStellarPrompts.get_all_prompts()
    
    return [
        types.Prompt(
            name="kubestellar_installation_guide",
            description="Comprehensive guide for KubeStellar installation",
            arguments=[]
        ),
        types.Prompt(
            name="kubestellar_troubleshooting",
            description="Help diagnose and fix KubeStellar issues",
            arguments=[]
        ),
        types.Prompt(
            name="kubestellar_cluster_management",
            description="Guide for managing KubeStellar clusters and workloads",
            arguments=[]
        )
    ]


@server.get_prompt()
async def handle_get_prompt(name: str, arguments: Dict[str, str]) -> types.GetPromptResult:
    """Get a specific prompt."""
    prompts = KubeStellarPrompts.get_all_prompts()
    
    if name in prompts:
        prompt_data = prompts[name]
        return types.GetPromptResult(
            description=prompt_data["description"],
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=prompt_data["template"]
                    )
                )
            ]
        )
    else:
        raise ValueError(f"Unknown prompt: {name}")


async def main():
    """Main entry point for the server."""
    # Server configuration
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name=settings.server_name,
                server_version=settings.server_version,
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )


if __name__ == "__main__":
    logger.info(f"Starting {settings.server_name} v{settings.server_version}")
    asyncio.run(main())