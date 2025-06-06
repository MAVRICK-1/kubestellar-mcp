import asyncio
import tempfile
from pathlib import Path
from typing import Dict, Optional

from config.settings import settings
from utils.command_executor import CommandExecutor
from utils.logger import setup_logger

logger = setup_logger(__name__)


class DemoEnvironmentManager:
    """Manage KubeStellar demo environment."""
    
    def __init__(self):
        self.executor = CommandExecutor()
    
    async def create_demo_environment(self, platform: str = "kind", cleanup: bool = True) -> Dict:
        """Create KubeStellar demo environment using the official script."""
        result = {
            "success": False,
            "platform": platform,
            "message": "",
            "clusters_created": [],
            "contexts_created": [],
            "script_output": "",
            "next_steps": []
        }
        
        if platform not in ["kind", "k3d"]:
            result["message"] = f"Unsupported platform: {platform}. Use 'kind' or 'k3d'"
            return result
        
        try:
            # Download and execute the demo script
            script_url = f"https://raw.githubusercontent.com/kubestellar/kubestellar/refs/tags/v{settings.kubestellar_version}/scripts/create-kubestellar-demo-env.sh"
            
            logger.info(f"Creating KubeStellar demo environment with platform: {platform}")
            
            # Create temporary script file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
                # Download script content
                returncode, script_content, stderr = await self.executor.run_command([
                    "curl", "-s", script_url
                ])
                
                if returncode != 0:
                    result["message"] = f"Failed to download demo script: {stderr}"
                    return result
                
                f.write(script_content)
                script_path = f.name
            
            # Make script executable
            await self.executor.run_command(["chmod", "+x", script_path])
            
            # Execute the script
            cmd = ["bash", script_path, "--platform", platform]
            returncode, stdout, stderr = await self.executor.run_command(
                cmd, timeout=1800  # 30 minutes timeout
            )
            
            result["script_output"] = stdout + stderr
            
            if returncode == 0:
                result["success"] = True
                result["message"] = "Demo environment created successfully!"
                result["clusters_created"] = ["kubeflex", "cluster1", "cluster2"]
                result["contexts_created"] = [
                    f"{platform}-kubeflex",
                    "cluster1", 
                    "cluster2",
                    "wds1",
                    "its1"
                ]
                result["next_steps"] = [
                    "Set environment variables as shown in script output",
                    "Try the example scenarios from KubeStellar documentation",
                    "Use 'get_cluster_info' tool to verify cluster status"
                ]
            else:
                result["message"] = f"Demo environment creation failed with return code {returncode}"
                logger.error(f"Demo script failed: {stderr}")
            
            # Cleanup script file
            try:
                Path(script_path).unlink()
            except Exception as e:
                logger.warning(f"Failed to cleanup script file: {e}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error creating demo environment: {e}")
            result["message"] = f"Error creating demo environment: {e}"
            return result
    
    async def cleanup_demo_environment(self, platform: str = "kind") -> Dict:
        """Clean up demo environment clusters."""
        result = {
            "success": True,
            "platform": platform,
            "cleaned_clusters": [],
            "cleaned_contexts": [],
            "errors": []
        }
        
        # Clusters to clean up
        clusters = ["kubeflex", "cluster1", "cluster2"]
        
        try:
            # Delete clusters
            for cluster in clusters:
                if platform == "kind":
                    returncode, stdout, stderr = await self.executor.run_command([
                        "kind", "delete", "cluster", "--name", cluster
                    ])
                elif platform == "k3d":
                    returncode, stdout, stderr = await self.executor.run_command([
                        "k3d", "cluster", "delete", cluster
                    ])
                
                if returncode == 0:
                    result["cleaned_clusters"].append(cluster)
                    logger.info(f"Successfully deleted cluster: {cluster}")
                else:
                    result["errors"].append(f"Failed to delete cluster {cluster}: {stderr}")
            
            # Clean up contexts
            contexts_to_clean = ["cluster1", "cluster2"]
            for context in contexts_to_clean:
                returncode, stdout, stderr = await self.executor.run_command([
                    "kubectl", "config", "delete-context", context
                ])
                
                if returncode == 0:
                    result["cleaned_contexts"].append(context)
                    logger.info(f"Successfully deleted context: {context}")
                else:
                    # Don't treat context deletion failures as critical
                    logger.warning(f"Could not delete context {context}: {stderr}")
            
            if result["errors"]:
                result["success"] = len(result["errors"]) < len(clusters)
            
            return result
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            result["success"] = False
            result["errors"].append(str(e))
            return result