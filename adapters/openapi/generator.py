# Vireo v3.0.0 — OpenAPI Generator

from typing import Dict, Any, List, Optional


class OpenAPIGenerator:
    """OpenAPI specification generator."""
    
    def __init__(self, title: str = "Vireo API", version: str = "3.0.0"):
        self.title = title
        self.version = version
        self._paths: Dict[str, Dict[str, Any]] = {}
        self._schemas: Dict[str, Dict[str, Any]] = {}
    
    def add_path(
        self,
        path: str,
        method: str,
        summary: str,
        operation_id: str,
        parameters: Optional[List[Dict[str, Any]]] = None,
        request_body: Optional[Dict[str, Any]] = None,
        responses: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> None:
        if path not in self._paths:
            self._paths[path] = {}
        
        self._paths[path][method.lower()] = {
            "summary": summary,
            "operationId": operation_id,
            "parameters": parameters or [],
            "requestBody": request_body,
            "responses": responses or {
                "200": {"description": "Success"},
                "400": {"description": "Bad Request"},
                "500": {"description": "Internal Error"},
            },
        }
    
    def add_schema(self, name: str, schema: Dict[str, Any]) -> None:
        self._schemas[name] = schema
    
    def generate(self) -> Dict[str, Any]:
        return {
            "openapi": "3.0.0",
            "info": {
                "title": self.title,
                "version": self.version,
                "description": "Vireo AI-to-AI Communication API",
            },
            "paths": self._paths,
            "components": {
                "schemas": self._schemas,
            },
        }
    
    def to_json(self) -> str:
        import json
        return json.dumps(self.generate(), indent=2)
    
    def to_yaml(self) -> str:
        import yaml
        return yaml.dump(self.generate(), default_flow_style=False)