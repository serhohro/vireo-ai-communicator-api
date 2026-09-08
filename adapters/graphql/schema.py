# Vireo v3.0.0 — GraphQL Schema

from typing import Dict, Any, List, Optional


class GraphQLSchema:
    """GraphQL schema generator."""
    
    def __init__(self):
        self._types: Dict[str, Dict[str, Any]] = {}
        self._queries: Dict[str, Dict[str, Any]] = {}
        self._mutations: Dict[str, Dict[str, Any]] = {}
    
    def add_type(self, name: str, fields: Dict[str, str]) -> None:
        self._types[name] = {"fields": fields}
    
    def add_query(self, name: str, fields: Dict[str, str], returns: str) -> None:
        self._queries[name] = {"fields": fields, "returns": returns}
    
    def add_mutation(self, name: str, fields: Dict[str, str], returns: str) -> None:
        self._mutations[name] = {"fields": fields, "returns": returns}
    
    def generate(self) -> str:
        lines = []
        
        for name, type_def in self._types.items():
            lines.append(f"type {name} {{")
            for field_name, field_type in type_def["fields"].items():
                lines.append(f"  {field_name}: {field_type}")
            lines.append("}")
            lines.append("")
        
        if self._queries:
            lines.append("type Query {")
            for name, query in self._queries.items():
                args = ", ".join(f"{k}: {v}" for k, v in query["fields"].items())
                lines.append(f"  {name}({args}): {query['returns']}")
            lines.append("}")
            lines.append("")
        
        if self._mutations:
            lines.append("type Mutation {")
            for name, mutation in self._mutations.items():
                args = ", ".join(f"{k}: {v}" for k, v in mutation["fields"].items())
                lines.append(f"  {name}({args}): {mutation['returns']}")
            lines.append("}")
        
        return "\n".join(lines)