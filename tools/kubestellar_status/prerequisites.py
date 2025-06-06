import shutil
from typing import Dict, List

from utils.command_executor import CommandExecutor
from utils.logger import setup_logger

logger = setup_logger(__name__)


class PrerequisitesChecker:
    """Check system prerequisites for KubeStellar."""
    
    def __init__(self):
        self.executor = CommandExecutor()
    
    async def check_prerequisites(self) -> Dict:
        """Check all KubeStellar prerequisites."""
        results = {
            "all_satisfied": True,
            "checks": {},
            "missing": [],
            "recommendations": []
        }
        
        # Required tools
        tools = {
            "kubectl": "kubectl version --client",
            "docker": "docker --version",
            "helm": "helm version",
            "go": "go version",
            "kind": "kind version",
            "k3d": "k3d version"
        }
        
        # Check each tool
        for tool, version_cmd in tools.items():
            check_result = await self._check_tool(tool, version_cmd)
            results["checks"][tool] = check_result
            
            if not check_result["installed"]:
                results["all_satisfied"] = False
                if tool in ["kubectl", "docker", "helm"]:  # Required tools
                    results["missing"].append(tool)
        
        # Check Go version specifically
        if results["checks"]["go"]["installed"]:
            await self._check_go_version(results)
        
        # Check Docker/Podman is running
        if results["checks"]["docker"]["installed"]:
            await self._check_docker_running(results)
        
        # Add installation recommendations
        self._add_recommendations(results)
        
        return results
    
    async def _check_tool(self, tool: str, version_cmd: str) -> Dict:
        """Check if a tool is installed."""
        result = {
            "installed": False,
            "version": "",
            "path": "",
            "error": ""
        }
        
        # Check if tool exists in PATH
        path = shutil.which(tool)
        if path:
            result["path"] = path
            
            # Get version
            cmd_parts = version_cmd.split()
            returncode, stdout, stderr = await self.executor.run_command(cmd_parts)
            
            if returncode == 0:
                result["installed"] = True
                result["version"] = stdout.strip().split('\n')[0]  # First line usually has version
            else:
                result["error"] = stderr.strip() or stdout.strip()
        else:
            result["error"] = f"{tool} not found in PATH"
        
        return result
    
    async def _check_go_version(self, results: Dict) -> None:
        """Check if Go version meets requirements (1.19+)."""
        go_check = results["checks"]["go"]
        if go_check["installed"]:
            try:
                version_str = go_check["version"]
                # Extract version number (e.g., "go version go1.21.0 ...")
                if "go" in version_str:
                    version_part = version_str.split()[2]  # "go1.21.0"
                    version_num = version_part.replace("go", "")  # "1.21.0"
                    major, minor = map(int, version_num.split(".")[:2])
                    
                    if major == 1 and minor < 19:
                        go_check["error"] = f"Go version {version_num} is too old. Requires Go 1.19+"
                        results["missing"].append("go (version 1.19+)")
                        results["all_satisfied"] = False
            except Exception as e:
                logger.warning(f"Could not parse Go version: {e}")
    
    async def _check_docker_running(self, results: Dict) -> None:
        """Check if Docker is running."""
        returncode, stdout, stderr = await self.executor.run_command(["docker", "ps"])
        
        if returncode != 0:
            results["checks"]["docker"]["error"] = "Docker is not running or not accessible"
            results["missing"].append("docker (running)")
            results["all_satisfied"] = False
    
    def _add_recommendations(self, results: Dict) -> None:
        """Add installation recommendations based on missing tools."""
        recommendations = []
        
        for missing in results["missing"]:
            if "kubectl" in missing:
                recommendations.append("Install kubectl: https://kubernetes.io/docs/tasks/tools/install-kubectl/")
            elif "docker" in missing:
                recommendations.append("Install Docker: https://docs.docker.com/get-docker/ or Podman: https://podman.io/getting-started/installation")
            elif "helm" in missing:
                recommendations.append("Install Helm: https://helm.sh/docs/intro/install/")
            elif "go" in missing:
                recommendations.append("Install Go 1.19+: https://golang.org/doc/install")
            elif "kind" in missing:
                recommendations.append("Install kind: https://kind.sigs.k8s.io/docs/user/quick-start/#installation")
            elif "k3d" in missing:
                recommendations.append("Install k3d: https://k3d.io/v5.4.6/#installation")
        
        if not results["missing"]:
            recommendations.append("All prerequisites are satisfied! You can proceed with KubeStellar installation.")
        
        results["recommendations"] = recommendations