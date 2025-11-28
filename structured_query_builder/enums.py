"""
Enum definitions for SQL query builder.

All tables, columns, operators, and functions are represented as enums
to provide explicit, self-documenting schemas compatible with LLM structured outputs.
"""

from enum import Enum


class Table(str, Enum):
    """Database tables available for querying."""

    product_offers = "product_offers"
    id_mapping = "id_mapping"
    categories = "categories"
    vendors = "vendors"


class Column(str, Enum):
    """Columns available across tables."""

    # product_offers columns
    id = "id"
    vendor = "vendor"
    category = "category"
    brand = "brand"
    title = "title"
    description = "description"
    regular_price = "regular_price"
    markdown_price = "markdown_price"
    is_markdown = "is_markdown"
    created_at = "created_at"

    # id_mapping columns
    product_match_id = "product_match_id"

    # Generic/computed columns
    discount_amount = "discount_amount"
    discount_percent = "discount_percent"


class ArithmeticOp(str, Enum):
    """Arithmetic operators for computed expressions."""

    add = "+"
    subtract = "-"
    multiply = "*"
    divide = "/"


class ComparisonOp(str, Enum):
    """Comparison operators for WHERE, HAVING, and CASE conditions."""

    eq = "="
    ne = "!="
    gt = ">"
    lt = "<"
    ge = ">="
    le = "<="
    like = "LIKE"
    ilike = "ILIKE"
    in_ = "IN"
    not_in = "NOT IN"
    is_null = "IS NULL"
    is_not_null = "IS NOT NULL"


class AggregateFunc(str, Enum):
    """Aggregate functions for GROUP BY queries."""

    count = "COUNT"
    sum = "SUM"
    avg = "AVG"
    min = "MIN"
    max = "MAX"
    count_distinct = "COUNT_DISTINCT"  # Special handling for COUNT(DISTINCT ...)


class WindowFunc(str, Enum):
    """Window functions for analytical queries."""

    # Ranking functions
    rank = "RANK"
    dense_rank = "DENSE_RANK"
    row_number = "ROW_NUMBER"

    # Offset functions
    lag = "LAG"
    lead = "LEAD"

    # Aggregate window functions
    sum = "SUM"
    avg = "AVG"
    min = "MIN"
    max = "MAX"
    count = "COUNT"


class JoinType(str, Enum):
    """Supported join types."""

    inner = "INNER"
    left = "LEFT"


class LogicOp(str, Enum):
    """Logical operators for combining conditions."""

    and_ = "AND"
    or_ = "OR"


class Direction(str, Enum):
    """Sort direction for ORDER BY."""

    asc = "ASC"
    desc = "DESC"


class NullsOrder(str, Enum):
    """Null ordering for ORDER BY."""

    first = "FIRST"
    last = "LAST"
