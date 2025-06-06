from typing import Dict


from config.settings import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)


class ScriptProvider:
    """Provide access to KubeStellar scripts and resources."""
    
    def __init__(self):
        self.repo_url = settings.kubestellar_repo_url
        self.version = settings.kubestellar_version
    
    async def get_demo_script(self) -> Dict:
        """Get the demo environment creation script."""
        script_url = f"https://raw.githubusercontent.com/kubestellar/kubestellar/refs/tags/v{self.version}/scripts/create-kubestellar-demo-env.sh"
        
        return {
            "name": "create-kubestellar-demo-env.sh",
            "description": "Creates a complete KubeStellar demo environment",
            "url": script_url,
            "usage": {
                "basic": f"curl -s {script_url} | bash",
                "with_platform": f"curl -s {script_url} | bash -s -- --platform kind",
                "download_first": f"curl -s {script_url} > create-kubestellar-demo-env.sh && chmod +x create-kubestellar-demo-env.sh && ./create-kubestellar-demo-env.sh --platform kind"
            },
            "platforms": ["kind", "k3d"],
            "features": [
                "Automatic cleanup of existing clusters",
                "Creates kubeflex, cluster1, and cluster2",
                "Sets up KubeStellar core components",
                "Configures OCM (Open Cluster Management)",
                "Ready-to-use demo environment"
            ],
            "estimated_time": "15-30 minutes",
            "requirements": ["Docker", "kubectl", "helm", "kind or k3d"]
        }
    
    async def get_prerequisite_check_script(self) -> Dict:
        """Get the prerequisite checking script."""
        script_url = f"https://raw.githubusercontent.com/kubestellar/kubestellar/v{self.version}/scripts/check_pre_req.sh"
        
        return {
            "name": "check_pre_req.sh",
            "description": "Checks system prerequisites for KubeStellar",
            "url": script_url,
            "usage": {
                "basic": f"curl -s {script_url} | bash",
                "with_assertion": f"curl -s {script_url} | bash -s -- --assert -V kflex ocm helm kubectl docker kind",
                "check_specific": f"curl -s {script_url} | bash -s -- kflex helm kubectl"
            },
            "checks": [
                "kflex (KubeFlex CLI)",
                "ocm (Open Cluster Management CLI)",
                "helm",
                "kubectl", 
                "docker",
                "kind",
                "k3d"
            ]
        }
    
    async def get_all_scripts(self) -> Dict:
        """Get information about all available scripts."""
        return {
            "scripts": {
                "demo_environment": await self.get_demo_script(),
                "prerequisite_check": await self.get_prerequisite_check_script()
            },
            "repository": {
                "url": self.repo_url,
                "scripts_directory": f"{self.repo_url}/tree/main/scripts",
                "version": self.version
            },
            "usage_tips": [
                "Always check prerequisites before installation",
                "Use demo script for quick setup and learning",
                "Customize platform (kind vs k3d) based on your preference",
                "Ensure Docker is running before executing scripts"
            ]
        }
