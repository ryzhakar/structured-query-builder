# Bugs in Q30-Q41 Implementation

## Root Cause
Implemented queries using non-existent constructs that were not in the schema:
- `ComputedExpr` - doesn't exist
- `JoinClause` - should be `JoinSpec`
- `JoinCondition` - doesn't exist, should use `on_conditions` parameter
- `ArithmeticCondition` - doesn't exist

## Affected Queries

### Q30: Index Drift Check (phase1_queries.py:2173)
- ❌ Uses `ComputedExpr`
- ❌ Uses `JoinClause` instead of `JoinSpec`
- ❌ Uses `on=JoinCondition(...)` instead of `on_conditions=[ConditionGroup(...)]`
- ❌ Uses `ArithmeticCondition` for ratio > 1.05 filter

### Q32: SKU Violation Scan (phase1_queries.py:~1606)
- ❌ Uses `ComputedExpr`
- ❌ Uses `JoinClause` instead of `JoinSpec`
- ❌ Uses `on=JoinCondition(...)`

### Q33: Unnecessary Discount Finder (phase1_queries.py:~1496)
- ❌ Uses `ComputedExpr`
- ❌ Uses `JoinClause` instead of `JoinSpec`
- ❌ Uses `on=JoinCondition(...)`

### Q34: Anchor Check (phase1_queries.py:~1568)
- ❌ Uses `ComputedExpr`
- ❌ Uses `JoinClause` instead of `JoinSpec`
- ❌ Uses `on=JoinCondition(...)`

### Q36: Discount Depth Alignment (phase2_queries.py:~402)
- ❌ Uses `ComputedExpr` (multiple times)
- ❌ Uses `JoinClause` instead of `JoinSpec`
- ❌ Uses `on=JoinCondition(...)`
- ❌ Uses `ArithmeticCondition` for discount comparison filter

### Q38: Same-Store Inflation Rate (phase3_queries.py:~361)
- ❌ Uses `JoinClause` instead of `JoinSpec`
- ❌ Uses `on=JoinCondition(...)`

### Q41: New Arrival Survival Rate (phase3_queries.py:~626)
- ❌ Uses `SimpleCondition` with `operator=ComparisonOp.is_not_null` and `value=None`
- This violates Pydantic validation (value must be str|int|float|bool|list)

## Working Queries (Verified)
- ✅ Q31: Average Selling Price Gap - simple aggregates, no joins
- ✅ Q35: Ad-Hoc Keyword Scrape - simple ILIKE filter
- ✅ Q37: Magic Number Distribution - GROUP BY is_markdown
- ✅ Q39: Entry-Level Creep - PERCENTILE_DISC
- ✅ Q40: Semantic Keyword Scrape - multi-ILIKE

## Fix Patterns

### Pattern 1: Replace ComputedExpr
```python
# WRONG:
ComputedExpr(
    expression=CompoundArithmetic(...),
    alias="foo"
)

# CORRECT:
CompoundArithmetic(..., alias="foo")
```

### Pattern 2: Replace JoinClause
```python
# WRONG:
joins=[
    JoinClause(
        join_type=JoinType.inner,
        table=Table.exact_matches,
        alias="m",
        on=JoinCondition(
            left=QualifiedColumn(...),
            right=QualifiedColumn(...),
        ),
    ),
]

# CORRECT:
from_=FromClause(
    table=Table.product_offers,
    alias="my",
    joins=[
        JoinSpec(
            join_type=JoinType.inner,
            table=Table.exact_matches,
            table_alias="m",
            on_conditions=[
                ConditionGroup(
                    conditions=[
                        ColumnComparison(
                            left_column=QualifiedColumn(...),
                            operator=ComparisonOp.eq,
                            right_column=QualifiedColumn(...),
                        )
                    ],
                    logic=LogicOp.and_,
                )
            ],
        ),
    ],
)
```

### Pattern 3: Arithmetic Filters
```python
# WRONG:
ArithmeticCondition(
    left=QualifiedColumn(...),
    operator=ComparisonOp.gt,
    right=CompoundArithmetic(...),
)

# OPTION A: Simplify to ColumnComparison (lose precision)
ColumnComparison(
    left_column=QualifiedColumn(column=Column.markdown_price, table_alias="my"),
    operator=ComparisonOp.gt,
    right_column=QualifiedColumn(column=Column.markdown_price, table_alias="comp"),
)

# OPTION B: Use DerivedTable (preserve precision)
from_=DerivedTable(
    query=Query(
        select=[..., CompoundArithmetic(..., alias="price_ratio")],
        ...
    ),
    alias="t"
),
where=WhereL1(
    groups=[
        ConditionGroup(
            conditions=[
                SimpleCondition(
                    column=QualifiedColumn(column=Column.price_ratio, table_alias="t"),
                    operator=ComparisonOp.gt,
                    value=1.05,
                )
            ],
            ...
        )
    ],
    ...
)
```

### Pattern 4: IS NOT NULL
```python
# WRONG:
SimpleCondition(
    column=QualifiedColumn(column=Column.created_at),
    operator=ComparisonOp.is_not_null,
    value=None  # ← Pydantic validation error!
)

# TODO: Find correct pattern in schema
# Options:
# 1. Special IsNullCondition class?
# 2. NullCheckCondition?
# 3. Different operator pattern?
```

## Notes for ClickHouse Testing

When testing with real ClickHouse:

1. **Window Functions**: Verify LAG/LEAD/STDDEV syntax matches ClickHouse
2. **PERCENTILE_DISC**: ClickHouse uses `quantileExact` or `quantile`
3. **IS NULL/IS NOT NULL**: Verify operator syntax
4. **Table Aliases in Joins**: ClickHouse strict about alias scoping
5. **Arithmetic in WHERE**: May need to test DerivedTable pattern performance
6. **JOIN syntax**: Verify INNER JOIN ... ON pattern works

## Test Strategy

1. Fix all 8 broken queries
2. Add unit test for each Q30-Q41
3. Add smoke test that translates all 36 queries
4. Test SQL generation against actual ClickHouse schema
5. Performance test: DerivedTable vs simplified filters
