from typing import Dict, List, Optional, Tuple

from utils.command_executor import CommandExecutor
from utils.logger import setup_logger

logger = setup_logger(__name__)


class KubectlHelper:
    """Helper class for kubectl operations."""
    
    def __init__(self):
        self.executor = CommandExecutor()
    
    async def get_contexts(self) -> List[str]:
        """Get all kubectl contexts."""
        returncode, stdout, stderr = await self.executor.run_command([
            "kubectl", "config", "get-contexts", "-o=name"
        ])
        
        if returncode == 0:
            return [ctx.strip() for ctx in stdout.split('\n') if ctx.strip()]
        else:
            logger.error(f"Failed to get contexts: {stderr}")
            return []
    
    async def check_namespace(self, namespace: str, context: str) -> bool:
        """Check if a namespace exists in the given context."""
        returncode, stdout, stderr = await self.executor.run_command([
            "kubectl", "get", "ns", namespace,
            "--context", context, "--ignore-not-found"
        ])
        
        return returncode == 0 and namespace in stdout
    
    async def get_cluster_info(self, context: str) -> Dict:
        """Get basic cluster information."""
        info = {
            "context": context,
            "accessible": False,
            "nodes": [],
            "namespaces": []
        }
        
        # Check if cluster is accessible
        returncode, stdout, stderr = await self.executor.run_command([
            "kubectl", "cluster-info", "--context", context
        ])
        
        if returncode == 0:
            info["accessible"] = True
            
            # Get nodes
            returncode, stdout, stderr = await self.executor.run_command([
                "kubectl", "get", "nodes", "--context", context, "-o=name"
            ])
            if returncode == 0:
                info["nodes"] = [node.strip() for node in stdout.split('\n') if node.strip()]
            
            # Get namespaces
            returncode, stdout, stderr = await self.executor.run_command([
                "kubectl", "get", "namespaces", "--context", context, "-o=name"
            ])
            if returncode == 0:
                info["namespaces"] = [ns.strip() for ns in stdout.split('\n') if ns.strip()]
        
        return info