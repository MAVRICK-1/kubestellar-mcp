import asyncio
import subprocess
from typing import Dict, List, Optional, Tuple

from utils.logger import setup_logger

logger = setup_logger(__name__)


class CommandExecutor:
    """Execute shell commands with proper error handling."""
    
    @staticmethod
    async def run_command(
        command: List[str],
        timeout: int = 300,
        cwd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
        capture_output: bool = True
    ) -> Tuple[int, str, str]:
        """
        Run a command asynchronously.
        
        Returns:
            Tuple of (return_code, stdout, stderr)
        """
        try:
            logger.info(f"Executing command: {' '.join(command)}")
            
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=subprocess.PIPE if capture_output else None,
                stderr=subprocess.PIPE if capture_output else None,
                cwd=cwd,
                env=env
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )
            
            stdout_str = stdout.decode('utf-8') if stdout else ""
            stderr_str = stderr.decode('utf-8') if stderr else ""
            
            logger.debug(f"Command completed with return code: {process.returncode}")
            if stdout_str:
                logger.debug(f"STDOUT: {stdout_str}")
            if stderr_str and process.returncode != 0:
                logger.warning(f"STDERR: {stderr_str}")
            
            return process.returncode, stdout_str, stderr_str
            
        except asyncio.TimeoutError:
            logger.error(f"Command timed out after {timeout} seconds")
            return 1, "", f"Command timed out after {timeout} seconds"
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            return 1, "", str(e)
    
    @staticmethod
    def run_command_sync(
        command: List[str],
        timeout: int = 300,
        cwd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None
    ) -> Tuple[int, str, str]:
        """Run a command synchronously."""
        try:
            logger.info(f"Executing command: {' '.join(command)}")
            
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=cwd,
                env=env
            )
            
            logger.debug(f"Command completed with return code: {result.returncode}")
            return result.returncode, result.stdout, result.stderr
            
        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out after {timeout} seconds")
            return 1, "", f"Command timed out after {timeout} seconds"
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            return 1, "", str(e)

# File: utils/kubectl_helper.py
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