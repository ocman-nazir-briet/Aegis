import logging
import yaml
import json
from typing import Dict, List, Any, Optional, Tuple

logger = logging.getLogger(__name__)


class InfrastructureParser:
    """Parse Kubernetes, Helm, Docker manifests to extract infrastructure topology."""

    @staticmethod
    def parse_k8s_manifest(manifest_text: str) -> List[Dict[str, Any]]:
        """Parse Kubernetes YAML manifest, return list of resource definitions."""
        resources = []
        try:
            docs = yaml.safe_load_all(manifest_text)
            for doc in docs:
                if doc and isinstance(doc, dict):
                    resources.append(doc)
        except Exception as e:
            logger.error(f"Failed to parse K8s manifest: {e}")
        return resources

    @staticmethod
    def extract_k8s_nodes(resources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract infrastructure nodes from K8s resources."""
        nodes = []
        for resource in resources:
            if not resource or "kind" not in resource:
                continue

            kind = resource.get("kind", "").lower()
            metadata = resource.get("metadata", {})
            spec = resource.get("spec", {})
            name = metadata.get("name", "unknown")
            namespace = metadata.get("namespace", "default")

            if kind == "deployment":
                node = {
                    "name": name,
                    "type": "deployment",
                    "namespace": namespace,
                    "replicas": spec.get("replicas", 1),
                    "image": InfrastructureParser._extract_image(spec),
                    "labels": metadata.get("labels", {}),
                    "annotations": metadata.get("annotations", {}),
                    "resource_limits": InfrastructureParser._extract_resources(spec),
                    "env_vars": InfrastructureParser._extract_env(spec),
                }
                nodes.append(node)

            elif kind == "service":
                node = {
                    "name": name,
                    "type": "service",
                    "namespace": namespace,
                    "labels": metadata.get("labels", {}),
                    "annotations": metadata.get("annotations", {}),
                    "ports": spec.get("ports", []),
                }
                nodes.append(node)

            elif kind in ["statefulset", "daemonset", "job", "cronjob"]:
                node = {
                    "name": name,
                    "type": kind,
                    "namespace": namespace,
                    "image": InfrastructureParser._extract_image(spec),
                    "labels": metadata.get("labels", {}),
                    "resource_limits": InfrastructureParser._extract_resources(spec),
                }
                nodes.append(node)

            elif kind in ["configmap", "secret"]:
                node = {
                    "name": name,
                    "type": kind,
                    "namespace": namespace,
                    "labels": metadata.get("labels", {}),
                    "data_keys": list(resource.get("data", {}).keys()),
                }
                nodes.append(node)

        return nodes

    @staticmethod
    def parse_helm_chart(chart_yaml: str, values_yaml: str) -> Dict[str, Any]:
        """Parse Helm Chart.yaml and values.yaml."""
        result = {"chart_meta": {}, "default_values": {}, "templates": []}

        try:
            chart = yaml.safe_load(chart_yaml)
            if chart:
                result["chart_meta"] = chart
        except Exception as e:
            logger.warning(f"Failed to parse Chart.yaml: {e}")

        try:
            values = yaml.safe_load(values_yaml)
            if values:
                result["default_values"] = values
        except Exception as e:
            logger.warning(f"Failed to parse values.yaml: {e}")

        return result

    @staticmethod
    def parse_docker_compose(compose_text: str) -> Dict[str, List[str]]:
        """Parse docker-compose.yml, extract services and dependencies."""
        services = {}
        try:
            doc = yaml.safe_load(compose_text)
            if doc and "services" in doc:
                for svc_name, svc_config in doc["services"].items():
                    services[svc_name] = {
                        "image": svc_config.get("image", ""),
                        "ports": svc_config.get("ports", []),
                        "environment": svc_config.get("environment", {}),
                        "depends_on": svc_config.get("depends_on", []),
                        "volumes": svc_config.get("volumes", []),
                    }
        except Exception as e:
            logger.error(f"Failed to parse docker-compose: {e}")
        return services

    @staticmethod
    def extract_k8s_edges(resources: List[Dict[str, Any]]) -> List[Tuple[str, str, str]]:
        """Extract relationships (edges) between K8s resources.
        Returns list of (source, target, relationship_type)."""
        edges = []

        # Build a map of service/deployment names for quick lookup
        names = set()
        for resource in resources:
            if "metadata" in resource:
                names.add(resource["metadata"].get("name", ""))

        for resource in resources:
            if not resource or "kind" not in resource:
                continue

            kind = resource.get("kind", "")
            metadata = resource.get("metadata", {})
            spec = resource.get("spec", {})
            name = metadata.get("name", "")

            if kind == "service":
                # Service -> Deployment via label selector
                selector = spec.get("selector", {})
                for label_key, label_val in selector.items():
                    for other in resources:
                        if other.get("kind") == "Deployment":
                            other_labels = other.get("metadata", {}).get("labels", {})
                            if other_labels.get(label_key) == label_val:
                                edges.append((name, other["metadata"]["name"], "service_exposes"))

            elif kind == "deployment":
                # Deployment -> ConfigMap/Secret for config refs
                for container in spec.get("template", {}).get("spec", {}).get("containers", []):
                    for env in container.get("env", []):
                        if "valueFrom" in env:
                            value_from = env["valueFrom"]
                            if "configMapKeyRef" in value_from:
                                ref = value_from["configMapKeyRef"]
                                edges.append((name, ref["name"], "uses_configmap"))
                            elif "secretKeyRef" in value_from:
                                ref = value_from["secretKeyRef"]
                                edges.append((name, ref["name"], "uses_secret"))

        return edges

    @staticmethod
    def _extract_image(spec: Dict[str, Any]) -> Optional[str]:
        """Extract container image from deployment/pod spec."""
        try:
            containers = spec.get("template", {}).get("spec", {}).get("containers", [])
            if containers:
                return containers[0].get("image")
        except Exception:
            pass
        return None

    @staticmethod
    def _extract_resources(spec: Dict[str, Any]) -> Dict[str, str]:
        """Extract resource limits/requests from spec."""
        resources = {}
        try:
            containers = spec.get("template", {}).get("spec", {}).get("containers", [])
            if containers:
                res = containers[0].get("resources", {})
                if res.get("limits"):
                    resources["limits"] = res["limits"]
                if res.get("requests"):
                    resources["requests"] = res["requests"]
        except Exception:
            pass
        return resources

    @staticmethod
    def _extract_env(spec: Dict[str, Any]) -> Dict[str, str]:
        """Extract environment variables from spec."""
        env = {}
        try:
            containers = spec.get("template", {}).get("spec", {}).get("containers", [])
            if containers:
                for env_var in containers[0].get("env", []):
                    key = env_var.get("name")
                    if key and "value" in env_var:
                        env[key] = env_var["value"]
        except Exception:
            pass
        return env
