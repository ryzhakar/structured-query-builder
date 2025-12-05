"""
Schema dereferencing utilities to work around LangChain's replace_defs_in_schema bugs.

This module provides robust $ref/$defs dereferencing that handles:
- Nested references in dicts AND lists (LangChain only handles dicts)
- anyOf/oneOf/allOf with $ref inside arrays (LangChain Issue #1023)
- Circular reference detection

Usage:
    from structured_query_builder.schema_utils import DereferencedSchemaModel

    # Option 1: Inherit from DereferencedSchemaModel
    class MyModel(DereferencedSchemaModel):
        field: str

    # Option 2: Use dereference_schema() directly
    schema = MyModel.model_json_schema()
    clean_schema = dereference_schema(schema)
"""

from typing import Any, Dict, List, Set
import copy


def dereference_schema(
    schema: Dict[str, Any],
    *,
    detect_cycles: bool = True,
    remove_defs: bool = True
) -> Dict[str, Any]:
    """
    Fully dereference a JSON schema by replacing all $ref pointers.

    This is a robust alternative to LangChain's replace_defs_in_schema that:
    - Handles $ref inside lists (anyOf, oneOf, allOf arrays)
    - Detects circular references (optional)
    - Properly removes $defs after dereferencing

    Args:
        schema: JSON schema dict with potential $ref/$defs
        detect_cycles: If True, raise error on circular references
        remove_defs: If True, remove $defs key after dereferencing

    Returns:
        Dereferenced schema with all $ref replaced by actual definitions

    Raises:
        ValueError: If circular reference detected and detect_cycles=True

    Example:
        >>> schema = {
        ...     "$defs": {"Foo": {"type": "object"}},
        ...     "properties": {"bar": {"$ref": "#/$defs/Foo"}}
        ... }
        >>> dereferenced = dereference_schema(schema)
        >>> dereferenced["properties"]["bar"]
        {"type": "object"}
    """
    # Extract definitions (Pydantic v2 uses $defs, v1 uses definitions)
    definitions = schema.get("$defs", schema.get("definitions", {}))

    if not definitions:
        # No references to resolve
        return schema

    # Track visited refs if cycle detection enabled
    visited: Set[str] = set() if detect_cycles else set()

    # Deep copy to avoid modifying original
    result = copy.deepcopy(schema)

    # Recursively dereference
    result = _dereference_recursive(result, definitions, visited, detect_cycles)

    # Remove definitions after dereferencing
    if remove_defs:
        result.pop("$defs", None)
        result.pop("definitions", None)

    return result


def _dereference_recursive(
    obj: Any,
    definitions: Dict[str, Any],
    visited: Set[str],
    detect_cycles: bool,
    current_path: str = "root"
) -> Any:
    """
    Recursive helper for dereference_schema.

    Handles dicts, lists, and primitive values.
    Unlike LangChain's implementation, this DOES handle lists.
    """
    if isinstance(obj, dict):
        # Check if this is a $ref
        if "$ref" in obj:
            ref_path = obj["$ref"]

            # Extract definition name from ref path
            # Handles both "#/$defs/Name" and "#/definitions/Name"
            if ref_path.startswith("#/$defs/"):
                def_name = ref_path[len("#/$defs/"):]
            elif ref_path.startswith("#/definitions/"):
                def_name = ref_path[len("#/definitions/"):]
            else:
                # External reference or unsupported format
                # Return as-is (could add external file support here)
                return obj

            # Cycle detection
            if detect_cycles:
                if def_name in visited:
                    raise ValueError(
                        f"Circular reference detected: {def_name} at {current_path}\n"
                        f"Reference chain: {' -> '.join(visited)} -> {def_name}"
                    )
                visited.add(def_name)

            # Get the referenced definition
            if def_name not in definitions:
                raise ValueError(f"Reference not found: {ref_path} at {current_path}")

            # Recursively dereference the definition
            resolved = _dereference_recursive(
                definitions[def_name],
                definitions,
                visited.copy() if detect_cycles else visited,  # Copy for branch
                detect_cycles,
                f"{current_path}.$ref[{def_name}]"
            )

            if detect_cycles:
                visited.discard(def_name)

            return resolved

        # Not a $ref, recursively process all keys
        return {
            key: _dereference_recursive(
                value,
                definitions,
                visited,
                detect_cycles,
                f"{current_path}.{key}"
            )
            for key, value in obj.items()
        }

    elif isinstance(obj, list):
        # CRITICAL: Handle lists (LangChain's bug is here)
        # This handles anyOf/oneOf/allOf with $ref inside arrays
        return [
            _dereference_recursive(
                item,
                definitions,
                visited,
                detect_cycles,
                f"{current_path}[{i}]"
            )
            for i, item in enumerate(obj)
        ]

    else:
        # Primitive value, return as-is
        return obj


def get_dereferenced_schema(model_class) -> Dict[str, Any]:
    """
    Get a fully dereferenced JSON schema from a Pydantic model.

    This is a convenience function that combines model_json_schema()
    with dereference_schema().

    Args:
        model_class: Pydantic BaseModel class

    Returns:
        Dereferenced JSON schema dict

    Example:
        >>> from pydantic import BaseModel
        >>> class User(BaseModel):
        ...     name: str
        >>> schema = get_dereferenced_schema(User)
    """
    schema = model_class.model_json_schema()
    return dereference_schema(schema)


class DereferencedSchemaModel:
    """
    Mixin for Pydantic models that provides dereferenced schema generation.

    Usage:
        class MyModel(BaseModel, DereferencedSchemaModel):
            field: str

        # This will use dereferenced schema
        llm.with_structured_output(MyModel)

    How it works:
        Overrides model_json_schema() to return dereferenced schema.
        LangChain calls this method, gets clean schema, skips buggy preprocessing.
    """

    @classmethod
    def model_json_schema(
        cls,
        *,
        by_alias: bool = True,
        ref_template: str = ...,
        schema_generator: type = ...,
        mode: str = "validation",
    ) -> Dict[str, Any]:
        """
        Generate dereferenced JSON schema for this model.

        Overrides BaseModel.model_json_schema() to return schema
        WITHOUT $defs, preventing LangChain's replace_defs_in_schema
        from running (or at least making it a no-op).
        """
        # Import here to avoid circular dependency
        from pydantic import BaseModel

        # Get original schema with $defs
        schema = super(BaseModel, cls).model_json_schema(
            by_alias=by_alias,
            ref_template=ref_template if ref_template is not ... else ...,
            schema_generator=schema_generator if schema_generator is not ... else ...,
            mode=mode,
        )

        # Dereference it
        return dereference_schema(schema, detect_cycles=True)


# Alternative: Decorator approach
def dereferenced_schema(cls):
    """
    Decorator to add dereferenced schema generation to a Pydantic model.

    Usage:
        @dereferenced_schema
        class MyModel(BaseModel):
            field: str

    This modifies the model_json_schema classmethod to return
    dereferenced schemas.
    """
    original_method = cls.model_json_schema

    @classmethod
    def dereferenced_model_json_schema(
        cls_inner,
        *,
        by_alias: bool = True,
        ref_template: str = ...,
        schema_generator: type = ...,
        mode: str = "validation",
    ) -> Dict[str, Any]:
        schema = original_method(
            by_alias=by_alias,
            ref_template=ref_template if ref_template is not ... else ...,
            schema_generator=schema_generator if schema_generator is not ... else ...,
            mode=mode,
        )
        return dereference_schema(schema, detect_cycles=True)

    cls.model_json_schema = dereferenced_model_json_schema
    return cls


# For debugging: Analyze schema complexity
def analyze_schema_refs(schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze $ref usage in a schema.

    Returns:
        Dict with statistics about references
    """
    defs = schema.get("$defs", schema.get("definitions", {}))

    ref_count = 0
    refs_in_lists = 0
    max_depth = 0

    def count_refs(obj, depth=0):
        nonlocal ref_count, refs_in_lists, max_depth
        max_depth = max(max_depth, depth)

        if isinstance(obj, dict):
            if "$ref" in obj:
                ref_count += 1
            for value in obj.values():
                count_refs(value, depth + 1)
        elif isinstance(obj, list):
            for item in obj:
                if isinstance(item, dict) and "$ref" in item:
                    refs_in_lists += 1
                count_refs(item, depth + 1)

    count_refs(schema)

    return {
        "num_definitions": len(defs),
        "total_refs": ref_count,
        "refs_in_lists": refs_in_lists,
        "max_depth": max_depth,
        "has_anyOf": "anyOf" in str(schema),
        "has_oneOf": "oneOf" in str(schema),
        "langchain_bug_risk": refs_in_lists > 0,  # Issue #1023
    }


if __name__ == "__main__":
    # Test with example schema
    test_schema = {
        "$defs": {
            "Foo": {
                "type": "object",
                "properties": {
                    "value": {"type": "integer"}
                }
            },
            "Bar": {
                "type": "object",
                "properties": {
                    "foo": {"$ref": "#/$defs/Foo"}
                }
            }
        },
        "type": "object",
        "properties": {
            "items": {
                "type": "array",
                "items": {
                    "anyOf": [
                        {"$ref": "#/$defs/Foo"},
                        {"$ref": "#/$defs/Bar"}
                    ]
                }
            }
        }
    }

    print("Original schema:")
    print(test_schema)

    print("\nAnalysis:")
    print(analyze_schema_refs(test_schema))

    print("\nDereferenced schema:")
    dereferenced = dereference_schema(test_schema)
    print(dereferenced)

    print("\nVerify no $ref remaining:")
    print("$ref" in str(dereferenced))
