from typing import Dict, List

from utils.command_executor import CommandExecutor
from utils.kubectl_helper import KubectlHelper
from utils.logger import setup_logger

logger = setup_logger(__name__)


class DiagnosticsRunner:
    """Run diagnostics on KubeStellar installation."""
    
    def __init__(self):
        self.kubectl = KubectlHelper()
        self.executor = CommandExecutor()
    
    async def diagnose_issues(self) -> Dict:
        """Run comprehensive diagnostics on KubeStellar installation."""
        diagnostics = {
            "status": "running",
            "checks": {},
            "issues_found": [],
            "recommendations": [],
            "summary": {
                "total_checks": 0,
                "passed": 0,
                "warnings": 0,
                "failures": 0
            }
        }
        
        # List of diagnostic checks
        checks = [
            ("docker_status", self._check_docker_status),
            ("kubectl_access", self._check_kubectl_access),
            ("kubestellar_contexts", self._check_kubestellar_contexts),
            ("kubestellar_namespaces", self._check_kubestellar_namespaces),
            ("cluster_connectivity", self._check_cluster_connectivity),
            ("port_conflicts", self._check_port_conflicts),
            ("resource_availability", self._check_resource_availability)
        ]
        
        diagnostics["summary"]["total_checks"] = len(checks)
        
        # Run each diagnostic check
        for check_name, check_func in checks:
            try:
                logger.info(f"Running diagnostic check: {check_name}")
                check_result = await check_func()
                diagnostics["checks"][check_name] = check_result
                
                # Update summary
                if check_result["status"] == "pass":
                    diagnostics["summary"]["passed"] += 1
                elif check_result["status"] == "warning":
                    diagnostics["summary"]["warnings"] += 1
                else:
                    diagnostics["summary"]["failures"] += 1
                
                # Collect issues and recommendations
                if "issues" in check_result:
                    diagnostics["issues_found"].extend(check_result["issues"])
                if "recommendations" in check_result:
                    diagnostics["recommendations"].extend(check_result["recommendations"])
                    
            except Exception as e:
                logger.error(f"Diagnostic check {check_name} failed: {e}")
                diagnostics["checks"][check_name] = {
                    "status": "error",
                    "message": f"Check failed: {e}"
                }
                diagnostics["summary"]["failures"] += 1
        
        # Overall status
        if diagnostics["summary"]["failures"] > 0:
            diagnostics["status"] = "issues_found"
        elif diagnostics["summary"]["warnings"] > 0:
            diagnostics["status"] = "warnings"
        else:
            diagnostics["status"] = "healthy"
        
        return diagnostics
    
    async def _check_docker_status(self) -> Dict:
        """Check Docker daemon status."""
        result = {"status": "pass", "message": "Docker is running"}
        
        returncode, stdout, stderr = await self.executor.run_command(["docker", "ps"])
        
        if returncode != 0:
            result.update({
                "status": "fail",
                "message": "Docker is not running or not accessible",
                "issues": ["Docker daemon is not running"],
                "recommendations": ["Start Docker daemon: sudo systemctl start docker"]
            })
        
        return result
    
    async def _check_kubectl_access(self) -> Dict:
        """Check kubectl accessibility."""
        result = {"status": "pass", "message": "kubectl is accessible"}
        
        returncode, stdout, stderr = await self.executor.run_command(["kubectl", "version", "--client"])
        
        if returncode != 0:
            result.update({
                "status": "fail",
                "message": "kubectl is not accessible",
                "issues": ["kubectl is not installed or not in PATH"],
                "recommendations": ["Install kubectl: https://kubernetes.io/docs/tasks/tools/install-kubectl/"]
            })
        
        return result
    
    async def _check_kubestellar_contexts(self) -> Dict:
        """Check for KubeStellar contexts."""
        result = {"status": "pass", "message": "KubeStellar contexts found"}
        
        contexts = await self.kubectl.get_contexts()
        kubestellar_contexts = [
            ctx for ctx in contexts 
            if any(ks_type in ctx for ks_type in ["kubeflex", "kind", "k3d", "wds", "its"])
        ]
        
        if not kubestellar_contexts:
            result.update({
                "status": "warning",
                "message": "No KubeStellar contexts found",
                "issues": ["No contexts containing 'kubeflex', 'kind', 'k3d', 'wds', or 'its' found"],
                "recommendations": ["Run KubeStellar installation or demo environment setup"]
            })
        else:
            result["message"] = f"Found {len(kubestellar_contexts)} KubeStellar contexts: {', '.join(kubestellar_contexts)}"
        
        return result
    
    async def _check_kubestellar_namespaces(self) -> Dict:
        """Check for required KubeStellar namespaces."""
        result = {"status": "pass", "message": "KubeStellar namespaces found"}
        
        contexts = await self.kubectl.get_contexts()
        required_namespaces = ["wds1-system", "its1-system"]
        found_namespaces = {}
        
        for ctx in contexts:
            if any(ks_type in ctx for ks_type in ["kubeflex", "kind", "k3d"]):
                found_namespaces[ctx] = {}
                for ns in required_namespaces:
                    exists = await self.kubectl.check_namespace(ns, ctx)
                    found_namespaces[ctx][ns] = exists
        
        if not found_namespaces:
            result.update({
                "status": "warning",
                "message": "No KubeStellar contexts to check namespaces in",
                "issues": ["No suitable contexts found for namespace checking"]
            })
        else:
            missing_any = False
            for ctx, namespaces in found_namespaces.items():
                missing = [ns for ns, exists in namespaces.items() if not exists]
                if missing:
                    missing_any = True
            
            if missing_any:
                result.update({
                    "status": "warning",
                    "message": "Some KubeStellar namespaces are missing",
                    "issues": ["Required KubeStellar namespaces not found in some contexts"],
                    "recommendations": ["Complete KubeStellar installation to create missing namespaces"]
                })
        
        return result
    
    async def _check_cluster_connectivity(self) -> Dict:
        """Check cluster connectivity."""
        result = {"status": "pass", "message": "All clusters are accessible"}
        
        contexts = await self.kubectl.get_contexts()
        inaccessible = []
        
        for ctx in contexts:
            if any(ks_type in ctx for ks_type in ["kubeflex", "kind", "k3d", "cluster"]):
                returncode, stdout, stderr = await self.executor.run_command([
                    "kubectl", "cluster-info", "--context", ctx
                ], timeout=30)
                
                if returncode != 0:
                    inaccessible.append(ctx)
        
        if inaccessible:
            result.update({
                "status": "warning",
                "message": f"Some clusters are not accessible: {', '.join(inaccessible)}",
                "issues": [f"Cannot connect to clusters: {', '.join(inaccessible)}"],
                "recommendations": ["Check if clusters are running and kubeconfig is correct"]
            })
        
        return result
    
    async def _check_port_conflicts(self) -> Dict:
        """Check for port conflicts on required ports."""
        result = {"status": "pass", "message": "No port conflicts detected"}
        
        required_ports = [9443]
        conflicting_ports = []
        
        for port in required_ports:
            returncode, stdout, stderr = await self.executor.run_command([
                "lsof", "-i", f"tcp:{port}"
            ])
            
            if returncode == 0:  # Port is in use
                conflicting_ports.append(port)
        
        if conflicting_ports:
            result.update({
                "status": "warning",
                "message": f"Port conflicts detected on: {conflicting_ports}",
                "issues": [f"Ports {conflicting_ports} are in use"],
                "recommendations": ["Stop services using these ports or use different ports"]
            })
        
        return result
    
    async def _check_resource_availability(self) -> Dict:
        """Check system resource availability."""
        result = {"status": "pass", "message": "System resources look good"}
        
        issues = []
        recommendations = []
        
        # Check disk space
        returncode, stdout, stderr = await self.executor.run_command(["df", "-h", "/"])
        if returncode == 0:
            lines = stdout.strip().split('\n')
            if len(lines) > 1:
                # Parse disk usage (assumes standard df output)
                fields = lines[1].split()
                if len(fields) >= 5:
                    usage_percent = fields[4].replace('%', '')
                    try:
                        if int(usage_percent) > 90:
                            issues.append(f"Disk usage is high: {usage_percent}%")
                            recommendations.append("Free up disk space before installation")
                    except ValueError:
                        pass
        
        # Check memory (simplified check)
        returncode, stdout, stderr = await self.executor.run_command(["free", "-m"])
        if returncode == 0:
            lines = stdout.strip().split('\n')
            if len(lines) > 1:
                # Simple check - if available memory is very low
                if "available" in stdout.lower() and any(int(x) < 1000 for x in stdout.split() if x.isdigit() and int(x) > 100):
                    issues.append("Available memory may be low")
                    recommendations.append("Consider freeing up memory before installation")
        
        if issues:
            result.update({
                "status": "warning",
                "message": "Some resource issues detected",
                "issues": issues,
                "recommendations": recommendations
            })
        
        return result