"""
Enum definitions for SQL query builder.

All tables, columns, operators, and functions are represented as enums
to provide explicit, self-documenting schemas compatible with LLM structured outputs.
"""

from enum import Enum


class Table(str, Enum):
    """Database tables available for querying."""

    product_offers = "product_offers"
    exact_matches = "exact_matches"  # NEW: Exact product matches (source_id, target_id)
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
    availability = "availability"  # In stock / out of stock boolean
    created_at = "created_at"
    updated_at = "updated_at"  # Timestamp for temporal queries

    # exact_matches columns (lexicographically sorted, no A:B + B:A duplicates by ETL convention)
    source_id = "source_id"  # Lexicographically smaller offer ID
    target_id = "target_id"  # Lexicographically larger offer ID

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
    stddev = "STDDEV"  # Standard deviation (sample)
    stddev_pop = "STDDEV_POP"  # Standard deviation (population)
    variance = "VARIANCE"  # Variance (sample)
    var_pop = "VAR_POP"  # Variance (population)
    percentile_cont = "PERCENTILE_CONT"  # Continuous percentile (interpolated)
    percentile_disc = "PERCENTILE_DISC"  # Discrete percentile (actual value)


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
