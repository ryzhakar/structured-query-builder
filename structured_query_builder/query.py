"""
Main Query model bringing together all clauses.

Represents a complete SQL SELECT query with all supported features.
This is the top-level model that LLMs generate via structured outputs.
"""

from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from .expressions import SelectExpr
from .clauses import (
    FromClause,
    WhereL1,
    GroupByClause,
    HavingClause,
    OrderByClause,
    LimitClause,
)


class Query(BaseModel):
    """
    Complete SQL SELECT query.

    Structure mirrors SQL clause order:
    SELECT ... FROM ... WHERE ... GROUP BY ... HAVING ... ORDER BY ... LIMIT ...

    All components use discriminated unions and explicit depth limits to ensure
    compatibility with LLM structured output requirements (no recursive types).
    """

    select: list[SelectExpr] = Field(
        ...,
        description="Columns and expressions to select",
        min_length=1,
    )

    from_: FromClause = Field(
        ...,
        description="FROM clause with optional joins",
        alias="from",
    )

    where: Optional[WhereL1] = Field(
        None,
        description="WHERE clause for filtering rows",
    )

    group_by: Optional[GroupByClause] = Field(
        None,
        description="GROUP BY clause for aggregation",
    )

    having: Optional[HavingClause] = Field(
        None,
        description="HAVING clause for filtering aggregated results",
    )

    order_by: Optional[OrderByClause] = Field(
        None,
        description="ORDER BY clause for sorting results",
    )

    limit: Optional[LimitClause] = Field(
        None,
        description="LIMIT clause for pagination",
    )

    model_config = ConfigDict(populate_by_name=True)  # Allow both 'from_' and 'from'


# ============================================================================
# Simplified Query Models (Tiered Approach)
# ============================================================================


class BasicQuery(BaseModel):
    """
    Simplified query for basic analytical needs.

    Single table, simple filters, no joins, no window functions.
    Covers ~60% of pricing analyst queries with tighter constraints.
    """

    table: str = Field(..., description="Table to query")
    select: list[SelectExpr] = Field(
        ...,
        description="Columns to select (columns and simple aggregates only)",
        min_length=1,
    )
    where: Optional[WhereL1] = Field(None, description="Filter conditions")
    group_by: Optional[list[str]] = Field(None, description="Columns to group by")
    order_by: Optional[list[str]] = Field(None, description="Columns to sort by")
    limit: Optional[int] = Field(None, description="Maximum rows to return", gt=0)

    model_config = ConfigDict(
        json_schema_extra={
            "description": "Simplified query for single-table analytical queries"
        }
    )
