from typing import Dict, List


from config.settings import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)


class DocsProvider:
    """Provide access to KubeStellar documentation."""
    
    def __init__(self):
        self.base_url = settings.kubestellar_docs_url
        self.repo_url = settings.kubestellar_repo_url
    
    async def get_documentation_index(self) -> Dict:
        """Get the documentation index."""
        return {
            "title": "KubeStellar Documentation",
            "version": settings.kubestellar_version,
            "base_url": self.base_url,
            "sections": {
                "getting_started": f"{self.base_url}/Getting-Started/",
                "user_guide": f"{self.base_url}/direct/user-guide-intro/",
                "installation": f"{self.base_url}/direct/user-guide-intro/",
                "architecture": f"{self.base_url}/direct/architecture/",
                "examples": f"{self.base_url}/direct/examples/",
                "troubleshooting": f"{self.base_url}/direct/installation-errors/",
                "api_reference": f"{self.base_url}/direct/API-Reference/",
                "contributing": f"{self.base_url}/contribution-guidelines/"
            },
            "quick_links": {
                "quick_start": f"{self.base_url}/Getting-Started/quickstart/",
                "prerequisites": f"{self.base_url}/Getting-Started/",
                "demo_script": f"{self.repo_url}/blob/main/scripts/create-kubestellar-demo-env.sh",
                "known_issues": f"{self.base_url}/direct/installation-errors/"
            }
        }
    
    async def get_installation_docs(self) -> Dict:
        """Get installation-specific documentation."""
        return {
            "title": "KubeStellar Installation Guide",
            "overview": "KubeStellar installation can be done through multiple methods",
            "methods": {
                "demo_environment": {
                    "title": "Demo Environment (Recommended for beginners)",
                    "description": "Automated setup using the create-kubestellar-demo-env.sh script",
                    "url": f"{self.base_url}/Getting-Started/quickstart/",
                    "script_url": f"https://raw.githubusercontent.com/kubestellar/kubestellar/refs/tags/v{settings.kubestellar_version}/scripts/create-kubestellar-demo-env.sh",
                    "platforms": ["kind", "k3d"],
                    "time_estimate": "15-30 minutes"
                },
                "manual_installation": {
                    "title": "Manual Installation",
                    "description": "Step-by-step manual installation using Helm",
                    "url": f"{self.base_url}/direct/user-guide-intro/",
                    "time_estimate": "30-60 minutes"
                }
            },
            "prerequisites": {
                "required_tools": ["kubectl", "docker", "helm", "go"],
                "optional_tools": ["kind", "k3d"],
                "system_requirements": "Linux/macOS/Windows with WSL",
                "documentation": f"{self.base_url}/Getting-Started/"
            },
            "troubleshooting": {
                "common_issues": f"{self.base_url}/direct/installation-errors/",
                "known_issues": f"{self.base_url}/direct/knownissue-kind-config/",
                "support": "https://github.com/kubestellar/kubestellar/issues"
            }
        }