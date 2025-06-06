from typing import Dict, List, Optional

from utils.kubectl_helper import KubectlHelper
from utils.logger import setup_logger

logger = setup_logger(__name__)


class ClusterManager:
    """Manage KubeStellar clusters and workloads."""
    
    def __init__(self):
        self.kubectl = KubectlHelper()
    
    async def get_cluster_info(self, context: Optional[str] = None) -> Dict:
        """Get detailed information about KubeStellar clusters."""
        result = {
            "clusters": {},
            "summary": {
                "total_contexts": 0,
                "kubestellar_contexts": 0,
                "accessible_clusters": 0
            }
        }
        
        try:
            contexts = await self.kubectl.get_contexts()
            result["summary"]["total_contexts"] = len(contexts)
            
            # If specific context requested
            if context:
                if context in contexts:
                    cluster_info = await self._get_detailed_cluster_info(context)
                    result["clusters"][context] = cluster_info
                else:
                    result["error"] = f"Context '{context}' not found"
                return result
            
            # Get info for KubeStellar-related contexts
            kubestellar_types = ["kubeflex", "kind", "k3d", "wds", "its"]
            
            for ctx in contexts:
                is_kubestellar = any(ks_type in ctx for ks_type in kubestellar_types)
                
                if is_kubestellar:
                    result["summary"]["kubestellar_contexts"] += 1
                    cluster_info = await self._get_detailed_cluster_info(ctx)
                    result["clusters"][ctx] = cluster_info
                    
                    if cluster_info["accessible"]:
                        result["summary"]["accessible_clusters"] += 1
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting cluster info: {e}")
            result["error"] = str(e)
            return result
    
    async def _get_detailed_cluster_info(self, context: str) -> Dict:
        """Get detailed information for a specific cluster."""
        info = await self.kubectl.get_cluster_info(context)
        
        # Add KubeStellar-specific information
        if info["accessible"]:
            # Check for KubeStellar namespaces
            ks_namespaces = ["wds1-system", "its1-system", "kubeflex-system"]
            info["kubestellar_namespaces"] = {}
            
            for ns in ks_namespaces:
                exists = await self.kubectl.check_namespace(ns, context)
                info["kubestellar_namespaces"][ns] = exists
            
            # Get KubeStellar-related resources
            info["kubestellar_resources"] = await self._get_kubestellar_resources(context)
        
        return info
    
    async def _get_kubestellar_resources(self, context: str) -> Dict:
        """Get KubeStellar-specific resources in the cluster."""
        resources = {
            "workload_definition_spaces": [],
            "managed_clusters": [],
            "binding_policies": []
        }
        
        try:
            # Check for WDS (Workload Definition Spaces)
            returncode, stdout, stderr = await self.kubectl.executor.run_command([
                "kubectl", "get", "workloaddefinitionspaces", 
                "--context", context, "-o=name", "--ignore-not-found"
            ])
            if returncode == 0 and stdout.strip():
                resources["workload_definition_spaces"] = [
                    wds.strip() for wds in stdout.split('\n') if wds.strip()
                ]
            
            # Check for managed clusters
            returncode, stdout, stderr = await self.kubectl.executor.run_command([
                "kubectl", "get", "managedclusters",
                "--context", context, "-o=name", "--ignore-not-found"
            ])
            if returncode == 0 and stdout.strip():
                resources["managed_clusters"] = [
                    mc.strip() for mc in stdout.split('\n') if mc.strip()
                ]
            
            # Check for binding policies
            returncode, stdout, stderr = await self.kubectl.executor.run_command([
                "kubectl", "get", "bindingpolicies",
                "--context", context, "-o=name", "--ignore-not-found"
            ])
            if returncode == 0 and stdout.strip():
                resources["binding_policies"] = [
                    bp.strip() for bp in stdout.split('\n') if bp.strip()
                ]
            
        except Exception as e:
            logger.warning(f"Could not get KubeStellar resources for context {context}: {e}")
        
        return resources