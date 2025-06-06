import asyncio
from typing import Dict, List

from utils.kubectl_helper import KubectlHelper
from utils.logger import setup_logger

logger = setup_logger(__name__)


class KubeStellarStatusChecker:
    """Check KubeStellar installation status."""
    
    def __init__(self):
        self.kubectl = KubectlHelper()
    
    async def check_kubestellar_status(self) -> Dict:
        """
        Check for KubeStellar installation status.
        Looks for contexts containing "kubeflex", "kind", or "k3d" and required namespaces.
        """
        status = {
            "context": "",
            "context_found": False,
            "wds1_namespace": False,
            "its1_namespace": False,
            "all_ready": False,
            "message": "No compatible KubeStellar context found",
            "compatible_contexts": [],
            "cluster_info": {}
        }
        
        try:
            # Get all contexts
            contexts = await self.kubectl.get_contexts()
            logger.info(f"Found {len(contexts)} contexts")
            
            # Compatible context types
            compatible_types = ["kubeflex", "kind", "k3d"]
            
            # Check all contexts for compatibility
            for ctx in contexts:
                is_compatible = any(ctx_type in ctx for ctx_type in compatible_types)
                
                if is_compatible:
                    logger.info(f"Found compatible context: {ctx}")
                    status["compatible_contexts"].append(ctx)
                    
                    # Get cluster info
                    cluster_info = await self.kubectl.get_cluster_info(ctx)
                    status["cluster_info"][ctx] = cluster_info
                    
                    if not cluster_info["accessible"]:
                        continue
                    
                    # Check wds1-system namespace
                    wds1_exists = await self.kubectl.check_namespace("wds1-system", ctx)
                    
                    # Check its1-system namespace  
                    its1_exists = await self.kubectl.check_namespace("its1-system", ctx)
                    
                    # If this context has all required namespaces, it's ready
                    if wds1_exists and its1_exists:
                        status.update({
                            "context": ctx,
                            "context_found": True,
                            "wds1_namespace": True,
                            "its1_namespace": True,
                            "all_ready": True,
                            "message": f"KubeStellar ready on context {ctx} with all required namespaces"
                        })
                        return status
                    
                    # If not fully ready but context found, update partial status
                    if not status["context_found"]:
                        missing_namespaces = []
                        if not wds1_exists:
                            missing_namespaces.append("wds1-system")
                        if not its1_exists:
                            missing_namespaces.append("its1-system")
                        
                        status.update({
                            "context": ctx,
                            "context_found": True,
                            "wds1_namespace": wds1_exists,
                            "its1_namespace": its1_exists,
                            "message": f"Compatible context {ctx} found, but missing namespaces: {', '.join(missing_namespaces)}"
                        })
            
            # If no compatible contexts found
            if not status["compatible_contexts"]:
                status["message"] = "No compatible KubeStellar contexts found. Looking for contexts containing 'kubeflex', 'kind', or 'k3d'"
            
            return status
            
        except Exception as e:
            logger.error(f"Error checking KubeStellar status: {e}")
            status["message"] = f"Error checking KubeStellar status: {e}"
            return status
    
    async def get_installation_info(self) -> Dict:
        """Get information about KubeStellar installation requirements."""
        return {
            "documentation_url": "https://docs.kubestellar.io/release-0.27.2/direct/user-guide-intro/",
            "installation_script": "https://raw.githubusercontent.com/kubestellar/kubestellar/refs/tags/v0.27.2/scripts/create-kubestellar-demo-env.sh",
            "requirements": {
                "kubernetes": "kubectl v1.23-1.25+",
                "container_runtime": "Docker or Podman",
                "helm": "Helm 3.x",
                "go": "Go 1.19+",
                "platforms": ["kind", "k3d"],
                "ports": [9443]
            },
            "prerequisites_check": "Run check_prerequisites tool to verify your system"
        }