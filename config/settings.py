import os
from pathlib import Path
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuration settings for KubeStellar MCP Server."""
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # KubeStellar Configuration
    kubestellar_version: str = Field(default="0.27.2", env="KUBESTELLAR_VERSION")
    kubestellar_docs_url: str = Field(
        default="https://docs.kubestellar.io/release-0.27.2",
        env="KUBESTELLAR_DOCS_URL"
    )
    kubestellar_repo_url: str = Field(
        default="https://github.com/kubestellar/kubestellar",
        env="KUBESTELLAR_REPO_URL"
    )
    
    # Kubernetes Configuration
    kubectl_timeout: int = Field(default=300, env="KUBECTL_TIMEOUT")
    default_context_type: str = Field(default="kind", env="DEFAULT_CONTEXT_TYPE")
    
    # Container Runtime
    container_runtime: str = Field(default="docker", env="CONTAINER_RUNTIME")
    
    # Demo Environment
    demo_platform: str = Field(default="kind", env="DEMO_PLATFORM")
    demo_clusters: List[str] = Field(
        default=["cluster1", "cluster2"],
        env="DEMO_CLUSTERS"
    )
    
    # MCP Server Configuration
    server_name: str = Field(default="KubeStellar MCP Server", env="SERVER_NAME")
    server_version: str = Field(default="0.1.0", env="SERVER_VERSION")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()