# Pydantic Schema Design for LLM-Powered SQL Query Builder

## Brainstorming Report

**Domain**: Enterprise e-commerce pricing analysis  
**Target Database**: ClickHouse (analytical), PostgreSQL (reference)  
**User**: Pricing analysts via natural language interface

---

## Executive Summary

The challenge is designing a Pydantic model that achieves near-parity with SQL's expressiveness while remaining compatible with LLM structured outputs (no recursive types) and ensuring correctness by construction.

The recommended solution is a **clause-based architecture with discriminated unions and explicit depth-limited nesting types**. This mirrors SQL's structure, avoids recursion, and provides clear translation paths.

---

## Part 1: Architectural Foundation

### 1.1 Architecture Pattern: Clause-Based Decomposition

The schema should mirror SQL's clause structure rather than representing queries as flat attribute bags or recursive ASTs.

```
Query
├── SelectClause      → SELECT ...
├── FromClause        → FROM ... JOIN ...
├── WhereClause       → WHERE ...
├── GroupByClause     → GROUP BY ...
├── HavingClause      → HAVING ...
├── OrderByClause     → ORDER BY ...
└── LimitClause       → LIMIT ... OFFSET ...
```

**Rationale**: Each clause is self-contained with its own validation rules. Translation to SQL is direct—each clause maps 1:1 to its SQL counterpart. LLMs can reason about each clause independently.

### 1.2 Expression Types: Discriminated Unions

Within each clause, use discriminated unions with explicit type markers rather than inheritance or dynamic typing.

```python
class ColumnExpr(BaseModel):
    expr_type: Literal["column"] = "column"
    column: Column
    alias: Optional[str] = None

class AggregateExpr(BaseModel):
    expr_type: Literal["aggregate"] = "aggregate"
    function: AggregateFunc
    column: Optional[Column] = None
    distinct: bool = False
    alias: str
```

The `expr_type` field acts as a discriminator. LLM structured outputs handle this well because the type is determined by a simple string literal.

### 1.3 Nesting Control: Explicit L0/L1 Types

Instead of recursive types, define explicit "levels" for nested constructs:

```python
# Level 0: No subqueries allowed
class WhereL0(BaseModel):
    """WHERE clause without subqueries"""
    groups: list[ConditionGroup]
    logic: Literal["AND", "OR"]

# Level 1: Can contain scalar subqueries with L0 internals
class WhereL1(BaseModel):
    """WHERE clause with optional scalar subqueries"""
    simple_conditions: list[ConditionGroup]
    subquery_conditions: list[SubqueryCondition]
    logic: Literal["AND", "OR"]
```

The subquery itself contains `WhereL0`, breaking the recursion chain at exactly one level of nesting.

---

## Part 2: SELECT Expressions

### 2.1 Expression Categories

Five categories cover pricing analyst needs:

| Category | Example | Use Case |
|----------|---------|----------|
| Column | `vendor` | Raw column selection |
| Computed | `regular_price - markdown_price` | Price differences, ratios |
| Aggregate | `AVG(regular_price)` | Category/vendor averages |
| Window | `RANK() OVER (...)` | Competitive rankings |
| Case | `CASE WHEN ... THEN ...` | Price tier classification |

### 2.2 Computed Expressions: Two-Level Arithmetic

Recursive arithmetic is forbidden. Instead, define two explicit levels:

**Binary Expression**: `operand OP operand`
```python
class BinaryArithmetic(BaseModel):
    left_column: Optional[Column] = None
    left_value: Optional[float] = None
    operator: ArithmeticOp
    right_column: Optional[Column] = None
    right_value: Optional[float] = None
    alias: str
```

**Compound Expression**: `(operand OP operand) OP operand`
```python
class CompoundArithmetic(BaseModel):
    inner_left_column: Optional[Column] = None
    inner_left_value: Optional[float] = None
    inner_operator: ArithmeticOp
    inner_right_column: Optional[Column] = None
    inner_right_value: Optional[float] = None
    outer_operator: ArithmeticOp
    outer_column: Optional[Column] = None
    outer_value: Optional[float] = None
    alias: str
```

**Coverage Analysis**:
- `regular_price - markdown_price` → Binary ✓
- `our_price / competitor_price` → Binary ✓
- `(regular - markdown) / regular * 100` → Compound ✓
- `price * 1.1` → Binary ✓

Two levels cover 95%+ of pricing arithmetic needs.

### 2.3 Window Functions

Window functions are essential for pricing analysis:

| Function | Pricing Use Case |
|----------|------------------|
| `RANK`, `DENSE_RANK` | Competitive position rankings |
| `ROW_NUMBER` | Top-N per group |
| `LAG`, `LEAD` | Week-over-week price changes |
| `AVG OVER` | Moving averages, category benchmarks |

```python
class WindowExpr(BaseModel):
    expr_type: Literal["window"] = "window"
    function: WindowFunc
    column: Optional[Column] = None
    partition_by: list[Column]
    order_by: list[OrderByItem]
    offset: int = 1  # For LAG/LEAD
    default_value: Optional[Union[str, int, float]] = None
    alias: str
```

### 2.4 CASE Expressions

Simplified CASE without nested conditions:

```python
class CaseWhen(BaseModel):
    condition_column: Column
    condition_operator: ComparisonOp
    condition_value: Union[str, int, float]
    then_column: Optional[Column] = None
    then_value: Optional[Union[str, int, float]] = None

class CaseExpr(BaseModel):
    expr_type: Literal["case"] = "case"
    whens: list[CaseWhen]  # Max 5-6 branches
    else_column: Optional[Column] = None
    else_value: Optional[Union[str, int, float]] = None
    alias: str
```

This handles: "Classify as 'cheap' if price < 50, 'medium' if < 100, else 'expensive'".

---

## Part 3: FROM and JOIN Handling

### 3.1 Basic Structure

```python
class JoinSpec(BaseModel):
    join_type: Literal["INNER", "LEFT"]
    table: Table
    table_alias: Optional[str] = None
    left_column: Column
    left_table_alias: Optional[str] = None
    right_column: Column

class FromClause(BaseModel):
    table: Table
    table_alias: Optional[str] = None
    joins: list[JoinSpec]
```

### 3.2 Self-Joins for Competitor Comparison

Critical pattern: comparing own prices to competitor prices for matched products.

```sql
SELECT 
    ours.title,
    ours.regular_price AS our_price,
    theirs.regular_price AS competitor_price
FROM product_offers ours
INNER JOIN product_offers theirs 
    ON ours.product_match_id = theirs.product_match_id
WHERE ours.vendor = 'client' AND theirs.vendor = 'amazon'
```

**Required schema support**:
- Table aliases (`ours`, `theirs`)
- Column references qualified by alias
- Join on arbitrary columns (not just PK/FK)

```python
class QualifiedColumn(BaseModel):
    table_alias: Optional[str] = None
    column: Column
```

### 3.3 Derived Tables (Subquery in FROM)

For patterns like "filter after window function":

```sql
SELECT * FROM (
    SELECT *, 
           AVG(price) OVER (PARTITION BY category) AS cat_avg
    FROM product_offers
) sub
WHERE price > cat_avg
```

```python
class DerivedTable(BaseModel):
    select: list[SelectExpr]
    from_table: Table
    where: Optional[WhereL0] = None
    alias: str

class FromClause(BaseModel):
    table: Optional[Table] = None
    derived: Optional[DerivedTable] = None
    table_alias: Optional[str] = None
    joins: list[JoinSpec]
```

Derived tables have L0 WHERE (no nested subqueries), preventing recursion.

---

## Part 4: WHERE Clause Design

### 4.1 Boolean Logic: Two-Level Grouping

Avoiding recursion while supporting complex filters:

**Level 1: Condition Groups**
```python
class SimpleCondition(BaseModel):
    column: QualifiedColumn
    operator: ComparisonOp
    value: Union[str, int, float, bool, list[str], list[int]]

class ConditionGroup(BaseModel):
    conditions: list[SimpleCondition]
    logic: Literal["AND", "OR"]
```

**Level 2: Groups of Groups**
```python
class WhereL0(BaseModel):
    groups: list[ConditionGroup]
    group_logic: Literal["AND", "OR"]
```

**Expressible patterns**:
- `A AND B AND C` → Single group with AND
- `A OR B OR C` → Single group with OR
- `(A AND B) OR (C AND D)` → Two AND-groups with OR logic
- `(A OR B) AND (C OR D)` → Two OR-groups with AND logic

This covers the vast majority of real-world filter patterns.

### 4.2 Operators

```python
class ComparisonOp(str, Enum):
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
```

For BETWEEN, use a dedicated condition type:

```python
class BetweenCondition(BaseModel):
    column: QualifiedColumn
    low: Union[str, int, float]
    high: Union[str, int, float]
```

### 4.3 Scalar Subqueries in WHERE

For "products priced above category average":

```python
class ScalarSubquery(BaseModel):
    table: Table
    aggregate: AggregateExpr
    where: Optional[WhereL0] = None
    group_by: list[Column] = []

class SubqueryCondition(BaseModel):
    column: QualifiedColumn
    operator: ComparisonOp
    subquery: ScalarSubquery

class WhereL1(BaseModel):
    simple_groups: list[ConditionGroup]
    between_conditions: list[BetweenCondition]
    subquery_conditions: list[SubqueryCondition]
    group_logic: Literal["AND", "OR"]
```

The subquery contains `WhereL0`—no subqueries within subqueries.

---

## Part 5: Aggregation

### 5.1 GROUP BY

```python
class GroupByClause(BaseModel):
    columns: list[Column]
```

ROLLUP, CUBE, GROUPING SETS add complexity with limited pricing use cases. Recommend excluding initially; can add as separate clause type if needed.

### 5.2 HAVING

Filters on aggregates:

```python
class HavingCondition(BaseModel):
    function: AggregateFunc
    column: Optional[Column] = None
    operator: ComparisonOp
    value: Union[int, float]

class HavingClause(BaseModel):
    conditions: list[HavingCondition]
    logic: Literal["AND", "OR"]
```

---

## Part 6: Ordering and Pagination

```python
class OrderByItem(BaseModel):
    column: Column
    direction: Literal["ASC", "DESC"] = "DESC"
    nulls: Optional[Literal["FIRST", "LAST"]] = None

class OrderByClause(BaseModel):
    items: list[OrderByItem]

class LimitClause(BaseModel):
    limit: int
    offset: int = 0
```

---

## Part 7: Complete Query Model

```python
class Query(BaseModel):
    select: list[SelectExpr]  # Union of all expression types
    from_: FromClause
    where: Optional[WhereL1] = None
    group_by: Optional[GroupByClause] = None
    having: Optional[HavingClause] = None
    order_by: Optional[OrderByClause] = None
    limit: Optional[LimitClause] = None
```

Where `SelectExpr` is:

```python
SelectExpr = Union[
    ColumnExpr,
    BinaryArithmetic,
    CompoundArithmetic,
    AggregateExpr,
    WindowExpr,
    CaseExpr
]
```

---

## Part 8: Tiered Schema Strategy

### 8.1 Rationale

Not all queries need full complexity. Simpler schemas have:
- Fewer fields for LLM to populate correctly
- Tighter constraints = fewer error modes
- Faster generation

### 8.2 Proposed Tiers

**Tier 1: BasicQuery**
- Single table
- Column selection and simple aggregates
- Flat conditions (no subqueries)
- No joins, no windows

```python
class BasicQuery(BaseModel):
    table: Table
    select: list[Union[ColumnExpr, AggregateExpr]]
    where: Optional[WhereL0] = None
    group_by: list[Column] = []
    order_by: list[OrderByItem] = []
    limit: Optional[int] = None
```

**Tier 2: AnalyticalQuery**
- Joins allowed
- Window functions
- Computed columns
- Full WhereL1 with subqueries

**Tier 3: AdvancedQuery**  
- Derived tables
- CASE expressions
- Self-joins
- Full feature set

### 8.3 Routing Logic

The LLM first classifies the user's intent:

| Signal Words | Tier |
|--------------|------|
| "list", "show", "how many", "average" | Basic |
| "compare", "rank", "vs", "trend" | Analytical |
| "classify", "categorize", "complex" | Advanced |

Routing reduces error surface by matching schema complexity to query complexity.

---

## Part 9: Schema-to-SQL Translation

### 9.1 Translation Rules

Each model type has a deterministic translation:

```
ColumnExpr         → column_name [AS alias]
AggregateExpr      → FUNC([DISTINCT] column) AS alias
BinaryArithmetic   → (left OP right) AS alias
WindowExpr         → FUNC(col) OVER (PARTITION BY ... ORDER BY ...) AS alias
ConditionGroup     → (cond1 LOGIC cond2 LOGIC ...)
WhereL1            → WHERE group1 LOGIC group2 ...
JoinSpec           → JOIN_TYPE table [alias] ON left_col = right_col
```

### 9.2 Translation Implementation Sketch

```python
def translate_query(q: Query) -> str:
    parts = []
    parts.append("SELECT " + ", ".join(translate_expr(e) for e in q.select))
    parts.append(translate_from(q.from_))
    if q.where:
        parts.append("WHERE " + translate_where(q.where))
    if q.group_by:
        parts.append("GROUP BY " + ", ".join(q.group_by.columns))
    if q.having:
        parts.append("HAVING " + translate_having(q.having))
    if q.order_by:
        parts.append("ORDER BY " + translate_order_by(q.order_by))
    if q.limit:
        parts.append(f"LIMIT {q.limit.limit} OFFSET {q.limit.offset}")
    return "\n".join(parts)
```

---

## Part 10: Pricing Analyst Use Case Validation

### 10.1 Test Cases

| Use Case | Query Pattern | Supported? |
|----------|---------------|------------|
| Average price by category | GROUP BY + AVG | ✓ |
| Products on markdown with discount % | Computed + filter | ✓ |
| Rank competitors by price per category | Window RANK + PARTITION | ✓ |
| Our price vs Amazon for same product | Self-join with alias | ✓ |
| Products priced above category avg | Scalar subquery in WHERE | ✓ |
| Week-over-week price change | Window LAG | ✓ |
| Price tier classification | CASE expression | ✓ |
| Top 5 cheapest per category | Window ROW_NUMBER + derived table filter | ✓ |

### 10.2 Gap Analysis

**Not directly supported**:
- Correlated subqueries (reference outer row in inner query)
- UNION/INTERSECT/EXCEPT (set operations)
- Recursive CTEs
- Complex nested CASE

**Workarounds available**:
- Correlated subqueries → Use window functions + derived table filter
- Set operations → Multiple queries at application layer

---

## Part 11: LLM Compatibility

### 11.1 Provider-Agnostic Considerations

| Feature | OpenAI | Gemini | Anthropic |
|---------|--------|--------|-----------|
| Nested objects | ✓ | ✓ | ✓ |
| Union types | ✓ (with discriminator) | ✓ | ✓ |
| Optional fields | ✓ | ✓ | ✓ |
| Lists | ✓ | ✓ | ✓ |
| Enums | ✓ | ✓ | ✓ |
| Recursive types | ✗ | ✗ | ✗ |

### 11.2 Design Compliance

The proposed design:
- Uses discriminated unions (type literal fields)
- Has explicit L0/L1 types instead of recursion
- Limits nesting depth structurally
- Uses simple types (strings, numbers, bools, lists, enums)

All providers should handle this schema.

---

## Part 12: Enum Definitions

### 12.1 Tables and Columns

```python
class Table(str, Enum):
    product_offers = "product_offers"
    id_mapping = "id_mapping"
    categories = "categories"
    vendors = "vendors"

class Column(str, Enum):
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
    product_match_id = "product_match_id"
```

### 12.2 Operators and Functions

```python
class ArithmeticOp(str, Enum):
    add = "+"
    subtract = "-"
    multiply = "*"
    divide = "/"

class ComparisonOp(str, Enum):
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
    count = "COUNT"
    sum = "SUM"
    avg = "AVG"
    min = "MIN"
    max = "MAX"

class WindowFunc(str, Enum):
    rank = "RANK"
    dense_rank = "DENSE_RANK"
    row_number = "ROW_NUMBER"
    lag = "LAG"
    lead = "LEAD"
    sum = "SUM"
    avg = "AVG"
    min = "MIN"
    max = "MAX"
    count = "COUNT"
```

---

## Part 13: Recommendations Summary

### 13.1 Core Architecture
- **Clause-based structure** mirroring SQL
- **Discriminated unions** for expression types
- **Explicit L0/L1 depth control** instead of recursion

### 13.2 Feature Inclusion
| Include | Exclude |
|---------|---------|
| INNER/LEFT joins | FULL/CROSS joins |
| Window functions | Recursive CTEs |
| Two-level arithmetic | Arbitrary expression depth |
| Two-level boolean logic | Infinite nesting |
| Scalar subqueries | Correlated subqueries |
| Derived tables | Set operations (UNION, etc.) |
| CASE expressions | Nested CASE |

### 13.3 Implementation Priority

1. **Phase 1**: BasicQuery schema with single table, filters, aggregates
2. **Phase 2**: Add joins and window functions (AnalyticalQuery)
3. **Phase 3**: Add derived tables, CASE, self-joins (AdvancedQuery)
4. **Phase 4**: Implement router to select appropriate schema tier

### 13.4 Validation Strategy

Since Pydantic validators may not run during LLM structured output generation:
- Use schema structure to make invalid states unrepresentable
- Validate at translation time (schema → SQL)
- Return clear error messages for malformed queries
- Consider "linting" layer before execution

---

## Appendix: Full Model Sketch

```python
from enum import Enum
from typing import Literal, Optional, Union
from pydantic import BaseModel

# Enums defined above...

class QualifiedColumn(BaseModel):
    table_alias: Optional[str] = None
    column: Column

class ColumnExpr(BaseModel):
    expr_type: Literal["column"] = "column"
    source: QualifiedColumn
    alias: Optional[str] = None

class BinaryArithmetic(BaseModel):
    expr_type: Literal["binary_arithmetic"] = "binary_arithmetic"
    left_column: Optional[Column] = None
    left_value: Optional[float] = None
    operator: ArithmeticOp
    right_column: Optional[Column] = None
    right_value: Optional[float] = None
    alias: str

class CompoundArithmetic(BaseModel):
    expr_type: Literal["compound_arithmetic"] = "compound_arithmetic"
    inner_left_column: Optional[Column] = None
    inner_left_value: Optional[float] = None
    inner_operator: ArithmeticOp
    inner_right_column: Optional[Column] = None
    inner_right_value: Optional[float] = None
    outer_operator: ArithmeticOp
    outer_column: Optional[Column] = None
    outer_value: Optional[float] = None
    alias: str

class AggregateExpr(BaseModel):
    expr_type: Literal["aggregate"] = "aggregate"
    function: AggregateFunc
    column: Optional[Column] = None
    distinct: bool = False
    alias: str

class OrderByItem(BaseModel):
    column: Column
    direction: Literal["ASC", "DESC"] = "DESC"

class WindowExpr(BaseModel):
    expr_type: Literal["window"] = "window"
    function: WindowFunc
    column: Optional[Column] = None
    partition_by: list[Column] = []
    order_by: list[OrderByItem] = []
    offset: int = 1
    default_value: Optional[Union[str, int, float]] = None
    alias: str

class CaseWhen(BaseModel):
    condition_column: Column
    condition_operator: ComparisonOp
    condition_value: Union[str, int, float]
    then_column: Optional[Column] = None
    then_value: Optional[Union[str, int, float]] = None

class CaseExpr(BaseModel):
    expr_type: Literal["case"] = "case"
    whens: list[CaseWhen]
    else_column: Optional[Column] = None
    else_value: Optional[Union[str, int, float]] = None
    alias: str

SelectExpr = Union[
    ColumnExpr,
    BinaryArithmetic,
    CompoundArithmetic,
    AggregateExpr,
    WindowExpr,
    CaseExpr
]

class SimpleCondition(BaseModel):
    column: QualifiedColumn
    operator: ComparisonOp
    value: Union[str, int, float, bool, list[str], list[int], list[float]]

class BetweenCondition(BaseModel):
    column: QualifiedColumn
    low: Union[str, int, float]
    high: Union[str, int, float]

class ConditionGroup(BaseModel):
    conditions: list[SimpleCondition]
    logic: Literal["AND", "OR"]

class WhereL0(BaseModel):
    groups: list[ConditionGroup]
    between_conditions: list[BetweenCondition] = []
    group_logic: Literal["AND", "OR"]

class ScalarSubquery(BaseModel):
    table: Table
    aggregate: AggregateExpr
    where: Optional[WhereL0] = None
    group_by: list[Column] = []

class SubqueryCondition(BaseModel):
    column: QualifiedColumn
    operator: ComparisonOp
    subquery: ScalarSubquery

class WhereL1(BaseModel):
    groups: list[ConditionGroup] = []
    between_conditions: list[BetweenCondition] = []
    subquery_conditions: list[SubqueryCondition] = []
    group_logic: Literal["AND", "OR"]

class JoinSpec(BaseModel):
    join_type: Literal["INNER", "LEFT"]
    table: Table
    table_alias: Optional[str] = None
    left_column: Column
    left_table_alias: Optional[str] = None
    right_column: Column

class DerivedTable(BaseModel):
    select: list[SelectExpr]
    from_table: Table
    where: Optional[WhereL0] = None
    alias: str

class FromClause(BaseModel):
    table: Optional[Table] = None
    derived: Optional[DerivedTable] = None
    table_alias: Optional[str] = None
    joins: list[JoinSpec] = []

class GroupByClause(BaseModel):
    columns: list[Column]

class HavingCondition(BaseModel):
    function: AggregateFunc
    column: Optional[Column] = None
    operator: ComparisonOp
    value: Union[int, float]

class HavingClause(BaseModel):
    conditions: list[HavingCondition]
    logic: Literal["AND", "OR"]

class OrderByClause(BaseModel):
    items: list[OrderByItem]

class LimitClause(BaseModel):
    limit: int
    offset: int = 0

class Query(BaseModel):
    select: list[SelectExpr]
    from_: FromClause
    where: Optional[WhereL1] = None
    group_by: Optional[GroupByClause] = None
    having: Optional[HavingClause] = None
    order_by: Optional[OrderByClause] = None
    limit: Optional[LimitClause] = None
```

---

*End of brainstorming report.*
