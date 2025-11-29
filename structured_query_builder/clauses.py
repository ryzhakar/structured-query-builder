"""
Clause models for SQL query structure.

Implements WHERE (with two levels), FROM/JOIN, GROUP BY, HAVING, ORDER BY, and LIMIT.
Uses explicit depth control instead of recursion to maintain compatibility with
LLM structured outputs.
"""

from typing import Literal, Optional, Union
from pydantic import BaseModel, Field
from .enums import (
    Table,
    Column,
    ComparisonOp,
    AggregateFunc,
    JoinType,
    LogicOp,
    Direction,
    NullsOrder,
)
from .expressions import QualifiedColumn, AggregateExpr, SelectExpr, OrderByItem


# ============================================================================
# WHERE Clause Components
# ============================================================================


class SimpleCondition(BaseModel):
    """
    Single comparison condition.

    Maps to: column OP value
    Examples: price > 100, vendor = 'amazon', category IN ('electronics', 'books')
    """

    cond_type: Literal["simple"] = "simple"
    column: QualifiedColumn = Field(..., description="Column to compare")
    operator: ComparisonOp = Field(..., description="Comparison operator")
    value: Union[str, int, float, bool, list[str], list[int], list[float]] = Field(
        ..., description="Value(s) to compare against; list for IN/NOT IN"
    )


class ColumnComparison(BaseModel):
    """
    Column-to-column comparison condition.

    Maps to: left_column OP right_column
    Examples: my_table.price = other_table.price, a.id = b.source_id
    Essential for JOIN ON clauses and cross-table comparisons.
    """

    cond_type: Literal["column_comparison"] = "column_comparison"
    left_column: QualifiedColumn = Field(..., description="Left column to compare")
    operator: ComparisonOp = Field(..., description="Comparison operator")
    right_column: QualifiedColumn = Field(..., description="Right column to compare")


class BetweenCondition(BaseModel):
    """
    BETWEEN condition for range checks.

    Maps to: column BETWEEN low AND high
    """

    cond_type: Literal["between"] = "between"
    column: QualifiedColumn = Field(..., description="Column to check")
    low: Union[str, int, float] = Field(..., description="Lower bound (inclusive)")
    high: Union[str, int, float] = Field(..., description="Upper bound (inclusive)")


# Union type for all condition types
Condition = Union[SimpleCondition, ColumnComparison, BetweenCondition]


class ConditionGroup(BaseModel):
    """
    Group of conditions combined with AND/OR.

    Represents: (cond1 LOGIC cond2 LOGIC ...)
    Supports: SimpleCondition, ColumnComparison, and BetweenCondition
    """

    conditions: list[Condition] = Field(
        ..., description="Conditions to combine", min_length=1
    )
    logic: LogicOp = Field(..., description="Logical operator combining conditions")


class WhereL0(BaseModel):
    """
    WHERE clause without subqueries (Level 0).

    Used inside subqueries and derived tables to prevent infinite nesting.
    Supports: groups of conditions, BETWEEN, combined with AND/OR.
    """

    groups: list[ConditionGroup] = Field(
        default_factory=list, description="Condition groups"
    )
    between_conditions: list[BetweenCondition] = Field(
        default_factory=list, description="BETWEEN conditions"
    )
    group_logic: LogicOp = Field(
        LogicOp.and_, description="Logic combining all groups and BETWEEN conditions"
    )


# ============================================================================
# Subquery Support
# ============================================================================


class ScalarSubquery(BaseModel):
    """
    Scalar subquery returning a single value.

    Used in WHERE conditions like: price > (SELECT AVG(price) FROM ...)
    Contains WhereL0 internally to prevent recursive nesting.
    """

    table: Table = Field(..., description="Table to query")
    aggregate: AggregateExpr = Field(..., description="Aggregate function to compute")
    where: Optional[WhereL0] = Field(None, description="Filter for subquery")
    group_by: list[Column] = Field(default_factory=list, description="GROUP BY columns")


class SubqueryCondition(BaseModel):
    """
    Condition comparing a column to a subquery result.

    Maps to: column OP (SELECT ...)
    """

    column: QualifiedColumn = Field(..., description="Column to compare")
    operator: ComparisonOp = Field(..., description="Comparison operator")
    subquery: ScalarSubquery = Field(..., description="Subquery returning scalar value")


class WhereL1(BaseModel):
    """
    WHERE clause with optional subqueries (Level 1).

    Top-level WHERE that can contain scalar subqueries.
    Subqueries use WhereL0 internally, limiting nesting to exactly 1 level.
    """

    groups: list[ConditionGroup] = Field(
        default_factory=list, description="Simple condition groups"
    )
    between_conditions: list[BetweenCondition] = Field(
        default_factory=list, description="BETWEEN conditions"
    )
    subquery_conditions: list[SubqueryCondition] = Field(
        default_factory=list, description="Conditions with subqueries"
    )
    group_logic: LogicOp = Field(
        LogicOp.and_, description="Logic combining all condition types"
    )


# ============================================================================
# FROM and JOIN Clauses
# ============================================================================


class JoinSpec(BaseModel):
    """
    JOIN specification.

    Maps to: JOIN_TYPE table [alias] ON conditions
    Supports both simple column equality and complex conditions.
    """

    join_type: JoinType = Field(..., description="Type of join")
    table: Table = Field(..., description="Table to join")
    table_alias: Optional[str] = Field(None, description="Alias for joined table")

    # Join conditions - flexible pattern using ConditionGroup
    on_conditions: list[ConditionGroup] = Field(
        ...,
        description="Conditions for JOIN ON clause; supports ColumnComparison, SimpleCondition, etc.",
        min_length=1
    )


class DerivedTable(BaseModel):
    """
    Derived table (subquery in FROM clause).

    Maps to: (SELECT ... FROM table [JOIN ...] WHERE ... GROUP BY ...) AS alias
    Used for patterns like:
    - Filtering after window functions
    - Calculating ratios on aggregates
    - Multi-step aggregations
    Contains WhereL0 to prevent recursive nesting.
    """

    select: list[SelectExpr] = Field(..., description="Columns to select")
    from_table: Table = Field(..., description="Source table")
    table_alias: Optional[str] = Field(None, description="Alias for source table in derived query")
    joins: list["JoinSpec"] = Field(default_factory=list, description="Joins within derived table")
    where: Optional[WhereL0] = Field(None, description="Filter conditions")
    group_by: Optional["GroupByClause"] = Field(None, description="GROUP BY clause")
    alias: str = Field(..., description="Required alias for derived table")


class FromClause(BaseModel):
    """
    FROM clause with optional joins.

    Supports:
    - Simple table: FROM table [alias]
    - Derived table: FROM (SELECT ...) alias
    - With joins: FROM table [alias] JOIN ... JOIN ...
    """

    table: Optional[Table] = Field(None, description="Simple table reference")
    derived: Optional[DerivedTable] = Field(None, description="Derived table (subquery)")
    table_alias: Optional[str] = Field(None, description="Alias for table")
    joins: list[JoinSpec] = Field(default_factory=list, description="JOIN specifications")


# ============================================================================
# GROUP BY and HAVING
# ============================================================================


class GroupByClause(BaseModel):
    """
    GROUP BY clause.

    Maps to: GROUP BY col1, col2, ...
    """

    columns: list[Column] = Field(..., description="Columns to group by", min_length=1)


class HavingCondition(BaseModel):
    """
    Single HAVING condition (filter on aggregates).

    Maps to: FUNC(column) OP value
    Example: AVG(price) > 100
    """

    function: AggregateFunc = Field(..., description="Aggregate function")
    column: Optional[Column] = Field(None, description="Column to aggregate; None for COUNT(*)")
    operator: ComparisonOp = Field(..., description="Comparison operator")
    value: Union[int, float] = Field(..., description="Value to compare against")


class HavingClause(BaseModel):
    """
    HAVING clause for filtering aggregated results.

    Maps to: HAVING cond1 LOGIC cond2 LOGIC ...
    """

    conditions: list[HavingCondition] = Field(
        ..., description="Conditions on aggregates", min_length=1
    )
    logic: LogicOp = Field(LogicOp.and_, description="Logic combining conditions")


# ============================================================================
# ORDER BY and LIMIT
# ============================================================================


class OrderByClause(BaseModel):
    """
    ORDER BY clause.

    Maps to: ORDER BY item1, item2, ...
    """

    items: list[OrderByItem] = Field(
        ..., description="Sort specifications", min_length=1
    )


class LimitClause(BaseModel):
    """
    LIMIT/OFFSET clause for pagination.

    Maps to: LIMIT n OFFSET m
    """

    limit: int = Field(..., description="Maximum rows to return", gt=0)
    offset: int = Field(0, description="Number of rows to skip", ge=0)
