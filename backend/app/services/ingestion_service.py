import os
import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
import re

logger = logging.getLogger(__name__)


class RepoIngestionService:
    def __init__(self, neo4j_service):
        self.neo4j = neo4j_service
        self.supported_languages = {
            ".py": "Python",
            ".ts": "TypeScript",
            ".tsx": "TypeScript",
            ".js": "JavaScript",
            ".jsx": "JavaScript",
            ".java": "Java",
            ".go": "Go",
            ".rs": "Rust",
        }

    def ingest_repository(self, repo_path: str, repo_url: str) -> Dict[str, Any]:
        """Ingest a repository and build the knowledge graph."""
        logger.info(f"Starting ingestion of {repo_url} from {repo_path}")

        if not os.path.isdir(repo_path):
            raise ValueError(f"Repository path not found: {repo_path}")

        repo_name = Path(repo_path).name
        language = self._detect_language(repo_path)

        service_info = self.neo4j.add_service(
            name=repo_name,
            repo_url=repo_url,
            language=language,
            runtime="unknown"
        )

        service_id = service_info["id"]
        stats = {"services": 1, "functions": 0, "endpoints": 0}

        functions = self._extract_functions(repo_path, service_id)
        stats["functions"] = len(functions)

        endpoints = self._extract_endpoints(repo_path, service_id)
        stats["endpoints"] = len(endpoints)

        logger.info(f"Ingestion complete: {stats}")
        return {
            "status": "success",
            "service_id": service_id,
            "statistics": stats
        }

    def _detect_language(self, repo_path: str) -> str:
        """Detect primary language of the repository."""
        ext_counts = {}
        for root, dirs, files in os.walk(repo_path):
            # Skip hidden and common non-source directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'venv']]
            for file in files:
                ext = Path(file).suffix
                if ext in self.supported_languages:
                    ext_counts[ext] = ext_counts.get(ext, 0) + 1

        if not ext_counts:
            return "Unknown"

        primary_ext = max(ext_counts, key=ext_counts.get)
        return self.supported_languages[primary_ext]

    def _extract_functions(self, repo_path: str, service_id: str) -> List[Dict[str, Any]]:
        """Extract functions from source files."""
        functions = []
        function_pattern = re.compile(r'^\s*(def|function|func|fn)\s+(\w+)\s*\(')

        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'venv']]

            for file in files:
                if Path(file).suffix not in self.supported_languages:
                    continue

                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, repo_path)

                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        for i, line in enumerate(lines, 1):
                            match = function_pattern.search(line)
                            if match:
                                func_name = match.group(2)
                                signature = f"{func_name}({i})"

                                func_info = self.neo4j.add_function(
                                    name=func_name,
                                    signature=signature,
                                    file_path=rel_path,
                                    service_id=service_id
                                )
                                functions.append(func_info)
                except Exception as e:
                    logger.warning(f"Failed to parse {file_path}: {e}")

        return functions

    def _extract_endpoints(self, repo_path: str, service_id: str) -> List[Dict[str, Any]]:
        """Extract HTTP endpoints from source files."""
        endpoints = []
        # Simple pattern matching for common endpoint definitions
        patterns = [
            (re.compile(r'@app\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']'), 'flask/fastapi'),
            (re.compile(r'@router\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']'), 'fastapi'),
            (re.compile(r'app\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']'), 'express'),
            (re.compile(r'router\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']'), 'express'),
        ]

        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'venv']]

            for file in files:
                if Path(file).suffix not in self.supported_languages:
                    continue

                file_path = os.path.join(root, file)

                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        for pattern, framework in patterns:
                            for match in pattern.finditer(content):
                                method = match.group(1).upper()
                                route = match.group(2)

                                endpoint_info = self.neo4j.add_endpoint(
                                    route=route,
                                    method=method,
                                    service_id=service_id
                                )
                                endpoints.append(endpoint_info)
                except Exception as e:
                    logger.warning(f"Failed to parse {file_path}: {e}")

        return endpoints
