"""
Structured Query Builder - LLM-powered SQL query schema.

Provides Pydantic models for representing SQL queries in a way that's
compatible with LLM structured outputs (no recursive types).
"""

from .enums import (
    Table,
    Column,
    ArithmeticOp,
    ComparisonOp,
    AggregateFunc,
    WindowFunc,
    JoinType,
    LogicOp,
    Direction,
    NullsOrder,
)

from .expressions import (
    QualifiedColumn,
    ColumnExpr,
    BinaryArithmetic,
    CompoundArithmetic,
    AggregateExpr,
    WindowExpr,
    CaseExpr,
    CaseWhen,
    OrderByItem,
    SelectExpr,
)

from .clauses import (
    SimpleCondition,
    BetweenCondition,
    ConditionGroup,
    WhereL0,
    WhereL1,
    ScalarSubquery,
    SubqueryCondition,
    JoinSpec,
    DerivedTable,
    FromClause,
    GroupByClause,
    HavingCondition,
    HavingClause,
    OrderByClause,
    LimitClause,
)

from .query import Query, BasicQuery

__all__ = [
    # Enums
    "Table",
    "Column",
    "ArithmeticOp",
    "ComparisonOp",
    "AggregateFunc",
    "WindowFunc",
    "JoinType",
    "LogicOp",
    "Direction",
    "NullsOrder",
    # Expressions
    "QualifiedColumn",
    "ColumnExpr",
    "BinaryArithmetic",
    "CompoundArithmetic",
    "AggregateExpr",
    "WindowExpr",
    "CaseExpr",
    "CaseWhen",
    "OrderByItem",
    "SelectExpr",
    # Clauses
    "SimpleCondition",
    "BetweenCondition",
    "ConditionGroup",
    "WhereL0",
    "WhereL1",
    "ScalarSubquery",
    "SubqueryCondition",
    "JoinSpec",
    "DerivedTable",
    "FromClause",
    "GroupByClause",
    "HavingCondition",
    "HavingClause",
    "OrderByClause",
    "LimitClause",
    # Query
    "Query",
    "BasicQuery",
]

__version__ = "0.1.0"
