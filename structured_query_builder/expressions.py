"""
Expression models for SELECT clause.

Includes column references, computed expressions, aggregates, window functions,
and CASE expressions. Uses discriminated unions to avoid recursion while maintaining
type safety for LLM structured outputs.
"""

from typing import Literal, Optional, Union
from pydantic import BaseModel, Field
from .enums import (
    Column,
    ArithmeticOp,
    ComparisonOp,
    AggregateFunc,
    WindowFunc,
    Direction,
    NullsOrder,
)


class QualifiedColumn(BaseModel):
    """
    Column reference with optional table alias.

    Used for self-joins and multi-table queries where columns need qualification.
    """

    table_alias: Optional[str] = Field(
        None, description="Table alias for qualified references (e.g., 'ours', 'theirs')"
    )
    column: Column = Field(..., description="Column name")


class ColumnExpr(BaseModel):
    """
    Simple column selection.

    Maps to: column_name [AS alias]
    """

    expr_type: Literal["column"] = "column"
    source: QualifiedColumn = Field(..., description="Column to select")
    alias: Optional[str] = Field(None, description="Optional alias for the column")


class BinaryArithmetic(BaseModel):
    """
    Two-operand arithmetic expression.

    Supports: column OP column, column OP value, value OP column
    Examples: regular_price - markdown_price, price * 1.1
    With table aliases: my.price - comp.price
    """

    expr_type: Literal["binary_arithmetic"] = "binary_arithmetic"

    left_column: Optional[Column] = Field(None, description="Left operand as column")
    left_table_alias: Optional[str] = Field(None, description="Table alias for left column")
    left_value: Optional[float] = Field(None, description="Left operand as literal value")

    operator: ArithmeticOp = Field(..., description="Arithmetic operator")

    right_column: Optional[Column] = Field(None, description="Right operand as column")
    right_table_alias: Optional[str] = Field(None, description="Table alias for right column")
    right_value: Optional[float] = Field(None, description="Right operand as literal value")

    alias: str = Field(..., description="Required alias for computed column")


class CompoundArithmetic(BaseModel):
    """
    Three-operand nested arithmetic expression.

    Supports: (operand OP operand) OP operand
    Example: (regular_price - markdown_price) / regular_price * 100
    This covers 95%+ of real-world pricing calculations without recursion.

    Now supports table aliases for multi-table queries.
    """

    expr_type: Literal["compound_arithmetic"] = "compound_arithmetic"

    # Inner expression
    inner_left_column: Optional[Column] = None
    inner_left_table_alias: Optional[str] = None
    inner_left_value: Optional[float] = None
    inner_operator: ArithmeticOp = Field(..., description="Inner arithmetic operator")
    inner_right_column: Optional[Column] = None
    inner_right_table_alias: Optional[str] = None
    inner_right_value: Optional[float] = None

    # Outer operation
    outer_operator: ArithmeticOp = Field(..., description="Outer arithmetic operator")
    outer_column: Optional[Column] = None
    outer_table_alias: Optional[str] = None
    outer_value: Optional[float] = None

    alias: str = Field(..., description="Required alias for computed column")


class AggregateExpr(BaseModel):
    """
    Aggregate function expression.

    Maps to: FUNC([DISTINCT] column) AS alias or FUNC(*) AS alias
    Supports table aliases: AVG(my.price) for multi-table queries
    Supports nested arithmetic: AVG(col1 - col2) for calculating aggregate of differences
    Supports percentile functions: PERCENTILE_CONT(0.1) for 10th percentile
    """

    expr_type: Literal["aggregate"] = "aggregate"
    function: AggregateFunc = Field(..., description="Aggregate function")
    column: Optional[Column] = Field(
        None, description="Column to aggregate; None for COUNT(*) or when using arithmetic_input"
    )
    table_alias: Optional[str] = Field(None, description="Table alias for column")
    distinct: bool = Field(False, description="Whether to use DISTINCT")

    # Support for nested arithmetic in aggregates (e.g., AVG(my.price - comp.price))
    arithmetic_input: Optional["BinaryArithmetic"] = Field(
        None, description="Arithmetic expression to aggregate instead of simple column"
    )

    # Support for percentile functions
    percentile: Optional[float] = Field(
        None, description="Percentile value (0.0 to 1.0) for PERCENTILE_CONT/PERCENTILE_DISC functions"
    )

    alias: str = Field(..., description="Required alias for aggregate result")


class OrderByItem(BaseModel):
    """
    Single ORDER BY item used in window functions and ORDER BY clauses.
    """

    column: Column = Field(..., description="Column to sort by")
    direction: Direction = Field(Direction.desc, description="Sort direction")
    nulls: Optional[NullsOrder] = Field(None, description="Null ordering")


class WindowExpr(BaseModel):
    """
    Window function expression.

    Essential for pricing analysis: rankings, moving averages, lag/lead for trends.
    Maps to: FUNC(column) OVER (PARTITION BY ... ORDER BY ...) AS alias
    """

    expr_type: Literal["window"] = "window"
    function: WindowFunc = Field(..., description="Window function")
    column: Optional[Column] = Field(
        None, description="Column argument for the function; None for COUNT(*)"
    )

    # Window specification
    partition_by: list[Column] = Field(
        default_factory=list, description="Columns to partition by"
    )
    order_by: list[OrderByItem] = Field(
        default_factory=list, description="Ordering within partitions"
    )

    # For LAG/LEAD
    offset: int = Field(1, description="Offset for LAG/LEAD functions")
    default_value: Optional[Union[str, int, float]] = Field(
        None, description="Default value when offset is out of bounds"
    )

    alias: str = Field(..., description="Required alias for window result")


class CaseWhen(BaseModel):
    """
    Single WHEN branch in a CASE expression.

    Simplified to avoid nested conditions - each branch has one simple comparison.
    """

    condition_column: Column = Field(..., description="Column in condition")
    condition_operator: ComparisonOp = Field(..., description="Comparison operator")
    condition_value: Union[str, int, float] = Field(..., description="Value to compare against")

    then_column: Optional[Column] = Field(None, description="Result column if condition true")
    then_value: Optional[Union[str, int, float]] = Field(
        None, description="Result value if condition true"
    )


class CaseExpr(BaseModel):
    """
    CASE expression for conditional logic.

    Maps to: CASE WHEN ... THEN ... ELSE ... END AS alias
    Example use: Classify prices into tiers (cheap/medium/expensive)
    """

    expr_type: Literal["case"] = "case"
    whens: list[CaseWhen] = Field(..., description="WHEN branches", max_length=10)

    else_column: Optional[Column] = Field(None, description="ELSE result column")
    else_value: Optional[Union[str, int, float]] = Field(
        None, description="ELSE result value"
    )

    alias: str = Field(..., description="Required alias for CASE result")


# Union type for all possible SELECT expressions
SelectExpr = Union[
    ColumnExpr,
    BinaryArithmetic,
    CompoundArithmetic,
    AggregateExpr,
    WindowExpr,
    CaseExpr,
]

# Rebuild AggregateExpr to resolve forward reference to BinaryArithmetic
AggregateExpr.model_rebuild()
