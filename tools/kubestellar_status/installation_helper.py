import asyncio
from typing import Dict, Optional

from config.settings import settings
from utils.command_executor import CommandExecutor
from utils.logger import setup_logger

logger = setup_logger(__name__)


class InstallationHelper:
    """Help with KubeStellar installation."""
    
    def __init__(self):
        self.executor = CommandExecutor()
    
    async def get_installation_guide(self) -> Dict:
        """Get KubeStellar installation guide and information."""
        return {
            "title": "KubeStellar Installation Guide",
            "version": settings.kubestellar_version,
            "documentation": f"{settings.kubestellar_docs_url}/direct/user-guide-intro/",
            "quick_start": f"{settings.kubestellar_docs_url}/Getting-Started/quickstart/",
            "installation_methods": {
                "demo_script": {
                    "description": "Automated demo environment setup",
                    "script_url": f"https://raw.githubusercontent.com/kubestellar/kubestellar/refs/tags/v{settings.kubestellar_version}/scripts/create-kubestellar-demo-env.sh",
                    "usage": "curl -s <script_url> | bash -s -- --platform kind"
                },
                "helm_chart": {
                    "description": "Manual installation using Helm",
                    "chart": f"oci://ghcr.io/kubestellar/kubestellar/core-chart",
                    "version": settings.kubestellar_version
                }
            },
            "supported_platforms": ["kind", "k3d"],
            "required_ports": [9443],
            "next_steps": [
                "Run 'check_prerequisites' to verify system requirements",
                "Choose installation method (demo script recommended for beginners)",
                "Follow the installation guide step by step"
            ]
        }
    
    async def download_demo_script(self) -> Dict:
        """Download the KubeStellar demo environment script."""
        script_url = f"https://raw.githubusercontent.com/kubestellar/kubestellar/refs/tags/v{settings.kubestellar_version}/scripts/create-kubestellar-demo-env.sh"
        
        try:
            returncode, stdout, stderr = await self.executor.run_command([
                "curl", "-s", script_url
            ])
            
            if returncode == 0:
                return {
                    "success": True,
                    "script_content": stdout,
                    "script_url": script_url,
                    "usage": "Save the script and run with: bash create-kubestellar-demo-env.sh --platform kind",
                    "platforms": ["kind", "k3d"]
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to download script: {stderr}",
                    "script_url": script_url
                }
        except Exception as e:
            logger.error(f"Error downloading demo script: {e}")
            return {
                "success": False,
                "error": str(e),
                "script_url": script_url
            }
    
    async def validate_installation_environment(self, platform: str = "kind") -> Dict:
        """Validate the environment for KubeStellar installation."""
        validation = {
            "platform": platform,
            "ready": True,
            "issues": [],
            "warnings": []
        }
        
        # Check if platform tool is available
        if platform == "kind":
            returncode, _, stderr = await self.executor.run_command(["kind", "version"])
            if returncode != 0:
                validation["ready"] = False
                validation["issues"].append("kind is not installed or not accessible")
        elif platform == "k3d":
            returncode, _, stderr = await self.executor.run_command(["k3d", "version"])
            if returncode != 0:
                validation["ready"] = False
                validation["issues"].append("k3d is not installed or not accessible")
        
        # Check if Docker is running
        returncode, _, stderr = await self.executor.run_command(["docker", "ps"])
        if returncode != 0:
            validation["ready"] = False
            validation["issues"].append("Docker is not running or not accessible")
        
        # Check if port 9443 is free
        returncode, stdout, stderr = await self.executor.run_command([
            "lsof", "-i", "tcp:9443"
        ])
        if returncode == 0:  # Port is in use
            validation["warnings"].append("Port 9443 is currently in use. KubeStellar installation may fail.")
        
        # Check for existing clusters that might conflict
        if platform == "kind":
            returncode, stdout, stderr = await self.executor.run_command(["kind", "get", "clusters"])
            if returncode == 0 and stdout.strip():
                existing_clusters = [cluster.strip() for cluster in stdout.split('\n') if cluster.strip()]
                conflicting = [c for c in existing_clusters if c in ["kubeflex", "cluster1", "cluster2"]]
                if conflicting:
                    validation["warnings"].append(f"Found existing clusters that may conflict: {', '.join(conflicting)}")
        
        return validation