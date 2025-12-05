"""
Query Registry: Metadata-tagged query catalog with programmatic filtering.

This module provides a decorator-based registry system for all pricing intelligence
queries, allowing queries to be tagged with rich metadata from the intelligence models
and enabling programmatic access and filtering.
"""

from textwrap import dedent
from typing import Any, Callable, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


# =============================================================================
# Metadata Models
# =============================================================================


class QueryMetadata(BaseModel):
    """Complete metadata for a pricing intelligence query."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    # Core identification
    query_number: int = Field(..., description="Query number (e.g., 30)")
    function_name: str = Field(..., description="Python function name")
    query_name: str = Field(..., description="Intelligence model query name")

    # Intelligence model classification
    archetype: Literal[
        "ENFORCER", "PREDATOR", "HISTORIAN", "MERCENARY", "ARCHITECT"
    ] = Field(..., description="Query archetype")
    concern: str = Field(..., description="Business concern addressed")
    variant: Literal["Matched Execution", "Unmatched Approximation"] = Field(
        ..., description="Execution pattern"
    )

    # Business context
    universal_reasoning: str = Field(
        ..., description="High-level business question being answered"
    )
    model_logic: str = Field(..., description="Query logic from intelligence model")
    model_outcome: str = Field(..., description="Expected business outcome/insight")

    # Technical implementation
    code_pattern: str = Field(..., description="Technical implementation patterns used")

    # Programmatic access
    query_function: Optional[Callable] = Field(
        None, description="Reference to the actual query function"
    )


# =============================================================================
# Registry Implementation
# =============================================================================


class QueryRegistry:
    """
    Central registry for all pricing intelligence queries.

    Provides decorator-based registration and flexible filtering/access patterns.
    """

    def __init__(self):
        self._queries: dict[str, QueryMetadata] = {}
        self._by_number: dict[int, QueryMetadata] = {}

    def register(
        self,
        query_number: int,
        query_name: str,
        archetype: Literal["ENFORCER", "PREDATOR", "HISTORIAN", "MERCENARY", "ARCHITECT"],
        concern: str,
        variant: Literal["Matched Execution", "Unmatched Approximation"],
        universal_reasoning: str,
        model_logic: str,
        model_outcome: str,
        code_pattern: str,
    ) -> Callable:
        """
        Decorator to register a query with complete metadata.

        Args:
            query_number: Query number (e.g., 30)
            query_name: Intelligence model query name
            archetype: Query archetype
            concern: Business concern addressed
            variant: Execution pattern (Matched/Unmatched)
            universal_reasoning: High-level business question
            model_logic: Query logic from intelligence model
            model_outcome: Expected business outcome
            code_pattern: Technical implementation patterns

        Returns:
            Decorated function (unchanged)
        """

        def decorator(func: Callable) -> Callable:
            metadata = QueryMetadata(
                query_number=query_number,
                function_name=func.__name__,
                query_name=query_name,
                archetype=archetype,
                concern=concern,
                variant=variant,
                universal_reasoning=dedent(universal_reasoning).strip(),
                model_logic=dedent(model_logic).strip(),
                model_outcome=dedent(model_outcome).strip(),
                code_pattern=dedent(code_pattern).strip(),
                query_function=func,
            )

            self._queries[func.__name__] = metadata
            self._by_number[query_number] = metadata

            return func

        return decorator

    def get(self, function_name: str) -> Optional[QueryMetadata]:
        """Get query metadata by function name."""
        return self._queries.get(function_name)

    def get_by_number(self, query_number: int) -> Optional[QueryMetadata]:
        """Get query metadata by query number."""
        return self._by_number.get(query_number)

    def all(self) -> list[QueryMetadata]:
        """Get all registered queries."""
        return sorted(self._queries.values(), key=lambda q: q.query_number)

    def filter(self, **criteria) -> list[QueryMetadata]:
        """
        Filter queries by metadata criteria.

        Args:
            **criteria: Field name and value pairs to filter by
                       (e.g., archetype="ENFORCER", variant="Matched Execution")

        Returns:
            List of matching queries sorted by query number

        Examples:
            registry.filter(archetype="ENFORCER")
            registry.filter(variant="Matched Execution")
            registry.filter(archetype="PREDATOR", concern="Monopoly Exploitation")
        """
        results = []

        for query in self._queries.values():
            match = True
            for key, value in criteria.items():
                if not hasattr(query, key) or getattr(query, key) != value:
                    match = False
                    break
            if match:
                results.append(query)

        return sorted(results, key=lambda q: q.query_number)

    def classify_by(self, field: str) -> dict[Any, list[QueryMetadata]]:
        """
        Classify all queries by a metadata field.

        Args:
            field: Metadata field name to classify by

        Returns:
            Dictionary mapping field values to lists of queries

        Examples:
            registry.classify_by("archetype")
            registry.classify_by("concern")
            registry.classify_by("variant")
        """
        classification: dict[Any, list[QueryMetadata]] = {}

        for query in self._queries.values():
            if hasattr(query, field):
                value = getattr(query, field)
                if value not in classification:
                    classification[value] = []
                classification[value].append(query)

        # Sort each group by query number
        for key in classification:
            classification[key] = sorted(classification[key], key=lambda q: q.query_number)

        return classification

    def all_matched(self) -> list[QueryMetadata]:
        """Get all queries with Matched Execution variant."""
        return self.filter(variant="Matched Execution")

    def all_unmatched(self) -> list[QueryMetadata]:
        """Get all queries with Unmatched Approximation variant."""
        return self.filter(variant="Unmatched Approximation")

    def export_to_yaml(self) -> str:
        """
        Generate canonical reference YAML from registry.

        Returns:
            YAML string with complete query mapping
        """
        from textwrap import indent

        lines = []
        lines.append("# " + "=" * 77)
        lines.append("# COMPLETE QUERY MAPPING: Intelligence Models → Code Implementation")
        lines.append("# " + "=" * 77)
        lines.append("# This file is AUTO-GENERATED from the query registry.")
        lines.append("# DO NOT EDIT MANUALLY - edit decorators in pricing_intelligence_queries.py")
        lines.append("# " + "=" * 77)
        lines.append("")

        # Group by archetype
        by_archetype = self.classify_by("archetype")
        archetype_order = ["ENFORCER", "PREDATOR", "HISTORIAN", "MERCENARY", "ARCHITECT"]

        for archetype in archetype_order:
            if archetype not in by_archetype:
                continue

            queries = by_archetype[archetype]

            # Archetype header
            lines.append(f"# ARCHETYPE: {archetype}")
            lines.append("# " + "-" * 77)
            lines.append("")

            # Group by concern within archetype
            by_concern: dict[str, list[QueryMetadata]] = {}
            for q in queries:
                if q.concern not in by_concern:
                    by_concern[q.concern] = []
                by_concern[q.concern].append(q)

            for concern, concern_queries in by_concern.items():
                # Concern header
                lines.append(f"concern: {concern}")
                lines.append(f"universal_reasoning: |")
                # Use first query's universal reasoning for the concern
                reasoning = concern_queries[0].universal_reasoning
                lines.append(indent(reasoning, "  "))
                lines.append("")

                # Group by variant
                matched = [q for q in concern_queries if q.variant == "Matched Execution"]
                unmatched = [q for q in concern_queries if q.variant == "Unmatched Approximation"]

                if matched:
                    lines.append("  matched_execution:")
                    for q in matched:
                        lines.append(f"    - query_number: Q{q.query_number:02d}")
                        lines.append(f"      query_name: \"{q.query_name}\"")
                        lines.append(f"      function_name: {q.function_name}")
                        lines.append(f"      model_logic: |")
                        lines.append(indent(q.model_logic, "        "))
                        lines.append(f"      model_outcome: |")
                        lines.append(indent(q.model_outcome, "        "))
                        lines.append(f"      code_pattern: |")
                        lines.append(indent(q.code_pattern, "        "))
                        lines.append("")

                if unmatched:
                    lines.append("  unmatched_approximation:")
                    for q in unmatched:
                        lines.append(f"    - query_number: Q{q.query_number:02d}")
                        lines.append(f"      query_name: \"{q.query_name}\"")
                        lines.append(f"      function_name: {q.function_name}")
                        lines.append(f"      model_logic: |")
                        lines.append(indent(q.model_logic, "        "))
                        lines.append(f"      model_outcome: |")
                        lines.append(indent(q.model_outcome, "        "))
                        lines.append(f"      code_pattern: |")
                        lines.append(indent(q.code_pattern, "        "))
                        lines.append("")

                lines.append("")

        # Summary statistics
        lines.append("# " + "=" * 77)
        lines.append("# COVERAGE SUMMARY")
        lines.append("# " + "=" * 77)
        lines.append(f"total_queries: {len(self._queries)}")
        lines.append(f"matched_queries: {len(self.all_matched())}")
        lines.append(f"unmatched_queries: {len(self.all_unmatched())}")
        lines.append("")

        by_arch = self.classify_by("archetype")
        lines.append("by_archetype:")
        for archetype in archetype_order:
            if archetype in by_arch:
                lines.append(f"  {archetype}: {len(by_arch[archetype])}")
        lines.append("")

        return "\n".join(lines)


# =============================================================================
# Global Registry Instance
# =============================================================================

registry = QueryRegistry()
