# Phase 1 Implementation Plan: Critical Gaps
## Achieving 70% Intelligence Model Coverage

**Status**: READY TO EXECUTE
**Estimated Effort**: 6-8 hours
**Current Coverage**: 37% (7/19 concerns)
**Target Coverage**: 70% (13/19 concerns)
**Approach**: Proof-of-work with runnable code and tests

---

## Success Criteria

**Proof-of-Work**:
- ✅ 10+ new queries implemented as Pydantic Query instances
- ✅ All queries generate valid SQL
- ✅ All queries tested (unit + hypothesis)
- ✅ Examples file executable with `python examples/enhanced_bimodal_queries.py`
- ✅ Commit with passing CI

**Proof-of-Result**:
- ✅ Coverage increases from 37% → 70%
- ✅ All ENFORCER concerns covered (currently 3/3 → 3/3 matched, 1/3 → 3/3 unmatched)
- ✅ All PREDATOR concerns covered (currently 3/6 → 6/6)
- ✅ HISTORIAN temporal patterns demonstrated (0 → 3 queries)
- ✅ BinaryArithmetic schema gap fixed
- ✅ Statistical functions added

---

## Task Breakdown

### Task 1: Schema Fixes (30 minutes)

#### 1.1 Add Statistical Functions to AggregateFunc
**File**: `structured_query_builder/enums.py`
**Lines**: ~Line 45 (AggregateFunc enum)

**Change**:
```python
class AggregateFunc(str, Enum):
    count = "COUNT"
    sum = "SUM"
    avg = "AVG"
    min = "MIN"
    max = "MAX"
    count_distinct = "COUNT_DISTINCT"
    stddev = "STDDEV"              # ← ADD
    stddev_pop = "STDDEV_POP"      # ← ADD
    variance = "VARIANCE"          # ← ADD
    percentile_cont = "PERCENTILE_CONT"  # ← ADD (requires parameter - document limitation)
```

**Tests Required**:
```python
# tests/test_models.py
def test_stddev_aggregate():
    expr = AggregateExpr(
        function=AggregateFunc.stddev,
        column=Column.markdown_price,
        alias="price_volatility"
    )
    assert expr.function == AggregateFunc.stddev
    # Serialize to JSON
    json_str = expr.model_dump_json()
    assert "STDDEV" in json_str
```

**Validation**:
- Run `pytest tests/test_models.py -v`
- Run `pytest tests/test_translator.py -v` (ensure translator handles new functions)

---

#### 1.2 Fix BinaryArithmetic to Support QualifiedColumn
**File**: `structured_query_builder/expressions.py`
**Lines**: ~Line 65 (BinaryArithmetic model)

**Current Limitation**:
```python
class BinaryArithmetic(BaseModel):
    expr_type: Literal["binary_arithmetic"] = "binary_arithmetic"
    left_column: Optional[Column] = None
    left_value: Optional[float] = None
    operator: ArithmeticOp
    right_column: Optional[Column] = None  # ← Can't specify table alias
    right_value: Optional[float] = None
    alias: str
```

**Blocker**: Cannot compute `my.price - comp.price` (both need table aliases)

**Fix** (Two Options):

**Option A**: Add table_alias fields (SIMPLE, maintains backward compatibility)
```python
class BinaryArithmetic(BaseModel):
    expr_type: Literal["binary_arithmetic"] = "binary_arithmetic"
    left_column: Optional[Column] = None
    left_table_alias: Optional[str] = None  # ← ADD
    left_value: Optional[float] = None
    operator: ArithmeticOp
    right_column: Optional[Column] = None
    right_table_alias: Optional[str] = None  # ← ADD
    right_value: Optional[float] = None
    alias: str
```

**Option B**: Upgrade to QualifiedColumn (CLEANER, but breaking change)
```python
class BinaryArithmetic(BaseModel):
    expr_type: Literal["binary_arithmetic"] = "binary_arithmetic"
    left: Union[QualifiedColumn, float]  # ← CHANGE
    operator: ArithmeticOp
    right: Union[QualifiedColumn, float]  # ← CHANGE
    alias: str
```

**Recommendation**: **Option A** (table_alias fields)
- Maintains backward compatibility with existing 15 queries
- No breaking changes to translator
- Minimal test updates

**Translator Update Required**:
```python
# translator.py
def _translate_binary_arithmetic(self, expr: BinaryArithmetic) -> str:
    left = self._format_operand(
        expr.left_column,
        expr.left_value,
        expr.left_table_alias  # ← ADD
    )
    right = self._format_operand(
        expr.right_column,
        expr.right_value,
        expr.right_table_alias  # ← ADD
    )
    return f"({left} {expr.operator.value} {right}) AS {expr.alias}"

def _format_operand(self, column: Optional[Column], value: Optional[float], table_alias: Optional[str] = None) -> str:
    if column:
        if table_alias:
            return f"{table_alias}.{column.value}"
        return column.value
    return str(value)
```

**Tests Required**:
```python
# tests/test_expressions.py
def test_binary_arithmetic_with_table_aliases():
    expr = BinaryArithmetic(
        left_column=Column.markdown_price,
        left_table_alias="my",
        operator=ArithmeticOp.subtract,
        right_column=Column.markdown_price,
        right_table_alias="comp",
        alias="price_gap"
    )
    sql = translator._translate_binary_arithmetic(expr)
    assert sql == "(my.markdown_price - comp.markdown_price) AS price_gap"
```

**Validation**:
- Run existing tests to ensure no regression
- Run new tests for table_alias support
- Validate JSON serialization

---

### Task 2: Missing ENFORCER Queries (45 minutes)

#### Query 16: MAP Violations (Unmatched)
**File**: `examples/enhanced_bimodal_queries.py` (new file)
**Archetype**: ENFORCER
**Concern**: MAP Policing (Unmatched variant)
**Business Value**: Detect MAP violations on non-matched products

**Implementation**:
```python
def query_16_map_violations_unmatched():
    """
    UNMATCHED: Brand floor scan for MAP violations.

    Intelligence Model Mapping:
        Archetype: ENFORCER
        Concern: MAP Policing
        Variant: Unmatched Approximation
        Query Name: "The Brand Floor Scan"

    Business Value:
        Detects MAP violations on ALL competitor products, even those not in exact_matches.
        Most products are NOT matched, so this catches violations Q02 misses.

    Action Trigger:
        Generate evidence packet for brand enforcement teams.
        If violations > 10 → escalate to vendor relationship manager.

    Limitation:
        Requires manual MAP threshold configuration per brand.
        Current example uses $50 for Nike; production needs brand-specific MAP table.
    """
    return Query(
        select=[
            ColumnExpr(source=QualifiedColumn(column=Column.id)),
            ColumnExpr(source=QualifiedColumn(column=Column.title)),
            ColumnExpr(source=QualifiedColumn(column=Column.brand)),
            ColumnExpr(source=QualifiedColumn(column=Column.vendor)),
            ColumnExpr(source=QualifiedColumn(column=Column.markdown_price)),
        ],
        from_=FromClause(table=Table.product_offers),
        where=WhereL1(
            groups=[
                ConditionGroup(
                    conditions=[
                        SimpleCondition(
                            column=QualifiedColumn(column=Column.vendor),
                            operator=ComparisonOp.eq,
                            value="Them"
                        ),
                        SimpleCondition(
                            column=QualifiedColumn(column=Column.brand),
                            operator=ComparisonOp.eq,
                            value="Nike"
                        ),
                        SimpleCondition(
                            column=QualifiedColumn(column=Column.markdown_price),
                            operator=ComparisonOp.lt,
                            value=50.0  # MAP floor
                        ),
                    ],
                    logic=LogicOp.and_
                )
            ],
            group_logic=LogicOp.and_
        ),
        order_by=OrderByClause(
            items=[
                OrderByItem(column=Column.markdown_price, direction=Direction.asc),
            ]
        ),
        limit=LimitClause(limit=100)
    )
```

**Test**:
```python
# tests/test_enhanced_bimodal_queries.py
def test_query_16_map_violations_unmatched():
    query = query_16_map_violations_unmatched()
    sql = translate_query(query)

    # Verify SQL contains expected elements
    assert "WHERE" in sql
    assert "vendor = 'Them'" in sql
    assert "brand = 'Nike'" in sql
    assert "markdown_price < 50" in sql

    # Verify serialization
    json_str = query.model_dump_json()
    assert json_str is not None
```

---

#### Query 17: Premium Gap Analysis (Matched)
**Archetype**: ENFORCER
**Concern**: Brand Alignment
**Variant**: Matched execution

**Implementation**:
```python
def query_17_premium_gap_analysis():
    """
    MATCHED: Average price premium we charge vs. competitor on identical products.

    Intelligence Model Mapping:
        Archetype: ENFORCER
        Concern: Brand Alignment
        Variant: Matched Execution
        Query Name: "The Premium Gap Analysis"

    Business Value:
        Quantifies brand premium positioning.
        "Are we consistently 10% more expensive on matched products?"

    Action Trigger:
        If avg_gap > $20 AND category = "Entry Level" → Review pricing strategy
        If avg_gap < $0 → We're cheaper; check if intentional

    Requires:
        BinaryArithmetic with table_alias support (Task 1.2)
    """
    return Query(
        select=[
            ColumnExpr(source=QualifiedColumn(column=Column.brand, table_alias="my")),
            ColumnExpr(source=QualifiedColumn(column=Column.category, table_alias="my")),
            BinaryArithmetic(
                left_column=Column.markdown_price,
                left_table_alias="my",  # ← NEW FEATURE
                operator=ArithmeticOp.subtract,
                right_column=Column.markdown_price,
                right_table_alias="comp",  # ← NEW FEATURE
                alias="price_gap"
            ),
            AggregateExpr(
                function=AggregateFunc.avg,
                column=Column.markdown_price,
                table_alias="my",
                alias="avg_our_price"
            ),
            AggregateExpr(
                function=AggregateFunc.count,
                column=None,
                alias="match_count"
            ),
        ],
        from_=FromClause(
            table=Table.product_offers,
            table_alias="my",
            joins=[
                JoinSpec(
                    join_type=JoinType.inner,
                    table=Table.exact_matches,
                    table_alias="em",
                    on_conditions=[
                        ConditionGroup(
                            conditions=[
                                ColumnComparison(
                                    left_column=QualifiedColumn(column=Column.id, table_alias="my"),
                                    operator=ComparisonOp.eq,
                                    right_column=QualifiedColumn(column=Column.source_id, table_alias="em")
                                )
                            ],
                            logic=LogicOp.and_
                        )
                    ]
                ),
                JoinSpec(
                    join_type=JoinType.inner,
                    table=Table.product_offers,
                    table_alias="comp",
                    on_conditions=[
                        ConditionGroup(
                            conditions=[
                                ColumnComparison(
                                    left_column=QualifiedColumn(column=Column.target_id, table_alias="em"),
                                    operator=ComparisonOp.eq,
                                    right_column=QualifiedColumn(column=Column.id, table_alias="comp")
                                )
                            ],
                            logic=LogicOp.and_
                        )
                    ]
                ),
            ]
        ),
        where=WhereL1(
            groups=[
                ConditionGroup(
                    conditions=[
                        SimpleCondition(
                            column=QualifiedColumn(column=Column.vendor, table_alias="my"),
                            operator=ComparisonOp.eq,
                            value="Us"
                        ),
                    ],
                    logic=LogicOp.and_
                )
            ],
            group_logic=LogicOp.and_
        ),
        group_by=GroupByClause(columns=[Column.brand, Column.category]),
        order_by=OrderByClause(
            items=[
                OrderByItem(column=Column.brand, direction=Direction.asc),
            ]
        ),
    )
```

---

### Task 3: Missing PREDATOR Queries (30 minutes)

#### Query 18: Supply Chain Failure Detector (Unmatched)
**Archetype**: PREDATOR
**Concern**: Monopoly Exploitation
**Variant**: Unmatched Approximation

**Note**: This query requires temporal comparison (current vs. 1 week ago).
Current implementation will be a **snapshot** showing current availability by brand.
**True temporal version** requires Task 4 (temporal patterns).

**Implementation**:
```python
def query_18_supply_chain_failure_detector():
    """
    UNMATCHED: Competitor stock levels by brand (snapshot).

    Intelligence Model Mapping:
        Archetype: PREDATOR
        Concern: Monopoly Exploitation
        Variant: Unmatched Approximation
        Query Name: "The Supply Chain Failure Detector"

    Business Value:
        Identifies brands with low competitor stock levels.
        When run weekly, drops indicate supply chain issues → pricing opportunities.

    Limitation:
        Snapshot only. Intelligence model requires week-over-week comparison.
        For true "dropped 40%" detection, see query_24_temporal_stock_drops.

    Action Trigger:
        If in_stock_count < 5 AND brand = premium_brand → Test 5-10% price increase
    """
    return Query(
        select=[
            ColumnExpr(source=QualifiedColumn(column=Column.brand)),
            ColumnExpr(source=QualifiedColumn(column=Column.vendor)),
            AggregateExpr(
                function=AggregateFunc.count,
                column=None,
                alias="total_products"
            ),
            # Count in-stock items
            AggregateExpr(
                function=AggregateFunc.sum,
                column=Column.availability,  # Boolean counts as 1/0
                alias="in_stock_count"
            ),
        ],
        from_=FromClause(table=Table.product_offers),
        where=WhereL1(
            groups=[
                ConditionGroup(
                    conditions=[
                        SimpleCondition(
                            column=QualifiedColumn(column=Column.vendor),
                            operator=ComparisonOp.eq,
                            value="Them"
                        ),
                    ],
                    logic=LogicOp.and_
                )
            ],
            group_logic=LogicOp.and_
        ),
        group_by=GroupByClause(columns=[Column.brand, Column.vendor]),
        order_by=OrderByClause(
            items=[
                OrderByItem(column=Column.brand, direction=Direction.asc),
            ]
        ),
    )
```

---

#### Query 19: Loss-Leader Hunter (Matched)
**Archetype**: PREDATOR
**Concern**: Bottom Feeding
**Variant**: Matched Execution

**Blocker**: Requires cost data (not in current schema)

**Alternative Implementation** (using regular_price as cost proxy):
```python
def query_19_loss_leader_hunter():
    """
    MATCHED: Identify competitor products priced below our regular price (cost proxy).

    Intelligence Model Mapping:
        Archetype: PREDATOR
        Concern: Bottom Feeding
        Variant: Matched Execution
        Query Name: "The Loss-Leader Hunter"

    Business Value:
        Flags competitor loss-leaders to avoid price-matching into unprofitable territory.

    Limitation:
        Uses regular_price as cost proxy (not actual cost).
        Intelligence model requires actual cost data.
        For true cost-based analysis, see PHASE_3_COST_MODEL.md.

    Action Trigger:
        Exclude these products from automated price matching rules.
    """
    return Query(
        select=[
            ColumnExpr(source=QualifiedColumn(column=Column.id, table_alias="my")),
            ColumnExpr(source=QualifiedColumn(column=Column.title, table_alias="my")),
            ColumnExpr(source=QualifiedColumn(column=Column.regular_price, table_alias="my")),
            ColumnExpr(source=QualifiedColumn(column=Column.markdown_price, table_alias="comp")),
        ],
        from_=FromClause(
            table=Table.product_offers,
            table_alias="my",
            joins=[
                # ... standard exact_matches join pattern ...
            ]
        ),
        where=WhereL1(
            groups=[
                ConditionGroup(
                    conditions=[
                        SimpleCondition(
                            column=QualifiedColumn(column=Column.vendor, table_alias="my"),
                            operator=ComparisonOp.eq,
                            value="Us"
                        ),
                        # Competitor price < our regular price (cost proxy)
                        ColumnComparison(
                            left_column=QualifiedColumn(column=Column.markdown_price, table_alias="comp"),
                            operator=ComparisonOp.lt,
                            right_column=QualifiedColumn(column=Column.regular_price, table_alias="my")
                        ),
                    ],
                    logic=LogicOp.and_
                )
            ],
            group_logic=LogicOp.and_
        ),
        limit=LimitClause(limit=50)
    )
```

---

### Task 4: Temporal Comparison Queries (2 hours)

**Goal**: Demonstrate that current schema CAN support time-series analysis via self-joins.

#### Query 20: Week-Over-Week Price Inflation
**Archetype**: HISTORIAN
**Concern**: Inflation Tracking
**Pattern**: Temporal self-join

**Implementation**:
```python
def query_20_week_over_week_inflation():
    """
    TEMPORAL: Category price inflation (week-over-week comparison).

    Intelligence Model Mapping:
        Archetype: HISTORIAN
        Concern: Inflation Tracking
        Variant: Unmatched Execution
        Query Name: "The Minimum Viable Price Lift"

    Business Value:
        Tracks market floor movement over time.
        "Did the cheapest TV increase from $200 to $250 this week?"

    Pattern: TEMPORAL SELF-JOIN
        This demonstrates that current schema SUPPORTS time-series queries
        without requiring recursive types or new models.

    How It Works:
        1. Join product_offers to itself on product ID
        2. Filter left side to last week's snapshot (updated_at between T-7 and T)
        3. Filter right side to this week's snapshot (updated_at between T and T+7)
        4. Compare prices

    Limitation:
        Requires database to maintain historical snapshots.
        If product_offers is updated in-place, this query won't work.
        Consider separate historical_snapshots table for production.
    """
    return Query(
        select=[
            ColumnExpr(source=QualifiedColumn(column=Column.category, table_alias="current")),
            AggregateExpr(
                function=AggregateFunc.min,
                column=Column.markdown_price,
                table_alias="last_week",
                alias="min_price_last_week"
            ),
            AggregateExpr(
                function=AggregateFunc.min,
                column=Column.markdown_price,
                table_alias="current",
                alias="min_price_current"
            ),
            BinaryArithmetic(
                left_value=None,  # Will use subquery result
                operator=ArithmeticOp.subtract,
                right_value=None,
                alias="price_increase"
                # NOTE: This requires computed column in SELECT from aggregates
                # May need to use derived table pattern
            ),
        ],
        from_=FromClause(
            table=Table.product_offers,
            table_alias="current",
            joins=[
                JoinSpec(
                    join_type=JoinType.inner,
                    table=Table.product_offers,  # Self-join
                    table_alias="last_week",
                    on_conditions=[
                        ConditionGroup(
                            conditions=[
                                # Join on same category
                                ColumnComparison(
                                    left_column=QualifiedColumn(column=Column.category, table_alias="current"),
                                    operator=ComparisonOp.eq,
                                    right_column=QualifiedColumn(column=Column.category, table_alias="last_week")
                                ),
                            ],
                            logic=LogicOp.and_
                        )
                    ]
                ),
            ]
        ),
        where=WhereL1(
            groups=[
                ConditionGroup(
                    conditions=[
                        # Current week's data
                        BetweenCondition(
                            column=QualifiedColumn(column=Column.updated_at, table_alias="current"),
                            low="2025-11-22",
                            high="2025-11-29"
                        ),
                        # Last week's data
                        BetweenCondition(
                            column=QualifiedColumn(column=Column.updated_at, table_alias="last_week"),
                            low="2025-11-15",
                            high="2025-11-22"
                        ),
                    ],
                    logic=LogicOp.and_
                )
            ],
            group_logic=LogicOp.and_
        ),
        group_by=GroupByClause(columns=[Column.category]),
    )
```

**Blocker Identified**: Cannot compute `MIN(current) - MIN(last_week)` in SELECT.
**Workaround**: Use derived table pattern (already supported by schema!)

**Revised Implementation Using Derived Table**:
```python
def query_20_week_over_week_inflation():
    # ... same docstring ...

    # Inner query: Get current week min prices
    inner_current = Query(
        select=[
            ColumnExpr(source=QualifiedColumn(column=Column.category)),
            AggregateExpr(
                function=AggregateFunc.min,
                column=Column.markdown_price,
                alias="min_price"
            ),
        ],
        from_=FromClause(table=Table.product_offers),
        where=WhereL1(
            groups=[
                ConditionGroup(
                    conditions=[
                        BetweenCondition(
                            column=QualifiedColumn(column=Column.updated_at),
                            low="2025-11-22",
                            high="2025-11-29"
                        ),
                    ],
                    logic=LogicOp.and_
                )
            ]
        ),
        group_by=GroupByClause(columns=[Column.category])
    )

    # Outer query joins current to last week
    # ...
    # Actually, this gets complex. Let me simplify to snapshot comparison.
```

**Simplified Snapshot Comparison** (More realistic):
```python
def query_20_category_price_snapshot():
    """
    TEMPORAL SNAPSHOT: Minimum price by category for specific date range.

    To detect inflation:
        1. Run this query with date range = last week → save results
        2. Run this query with date range = this week → save results
        3. Compare in application layer

    This is more practical than complex temporal self-joins.
    """
    return Query(
        select=[
            ColumnExpr(source=QualifiedColumn(column=Column.category)),
            ColumnExpr(source=QualifiedColumn(column=Column.vendor)),
            AggregateExpr(
                function=AggregateFunc.min,
                column=Column.markdown_price,
                alias="min_price"
            ),
            AggregateExpr(
                function=AggregateFunc.avg,
                column=Column.markdown_price,
                alias="avg_price"
            ),
        ],
        from_=FromClause(table=Table.product_offers),
        where=WhereL1(
            groups=[
                ConditionGroup(
                    conditions=[
                        BetweenCondition(
                            column=QualifiedColumn(column=Column.updated_at),
                            low="2025-11-22",  # Parameterize in production
                            high="2025-11-29"
                        ),
                    ],
                    logic=LogicOp.and_
                )
            ],
            group_logic=LogicOp.and_
        ),
        group_by=GroupByClause(columns=[Column.category, Column.vendor]),
        order_by=OrderByClause(
            items=[
                OrderByItem(column=Column.category, direction=Direction.asc),
            ]
        ),
    )
```

**Honest Assessment**: True week-over-week comparison in single query is complex with current schema.
**Recommended Pattern**: Snapshot + application-layer comparison.

---

### Task 5: Documentation & Testing (1.5 hours)

#### 5.1 Update Test Suite
**File**: `tests/test_enhanced_bimodal_queries.py` (new)

**Requirements**:
- Test each new query generates valid SQL
- Test JSON serialization
- Test all new schema features (table_alias in BinaryArithmetic, STDDEV)
- Run hypothesis testing on new queries

#### 5.2 Update Examples File
**File**: `examples/enhanced_bimodal_queries.py`

**Requirements**:
- All 25 queries (15 existing + 10 new)
- Runnable main() function
- Clear archetype organization
- Intelligence model mapping in docstrings

#### 5.3 Update Documentation
**Files**:
- `README.md` - Add note about intelligence model coverage
- `IMPLEMENTATION_SUMMARY.md` - Update with Phase 1 completion
- `BIMODAL_INTELLIGENCE_GAP_ANALYSIS.md` - Mark Phase 1 gaps as closed

---

## Execution Order

1. ✅ **Commit 1**: Schema fixes (Task 1)
   - Add STDDEV/PERCENTILE to enums
   - Add table_alias to BinaryArithmetic
   - Update translator
   - Update tests
   - **Proof**: All existing tests pass + new tests pass

2. ✅ **Commit 2**: ENFORCER queries (Task 2)
   - Query 16: MAP violations unmatched
   - Query 17: Premium gap analysis
   - Tests for both
   - **Proof**: Queries generate valid SQL

3. ✅ **Commit 3**: PREDATOR queries (Task 3)
   - Query 18: Supply chain failure detector
   - Query 19: Loss-leader hunter
   - Tests for both
   - **Proof**: Queries generate valid SQL

4. ✅ **Commit 4**: Temporal patterns (Task 4)
   - Query 20: Category price snapshot
   - Documentation of temporal pattern
   - Test for temporal query
   - **Proof**: Demonstrates schema supports time-series

5. ✅ **Commit 5**: Documentation & integration (Task 5)
   - Update all docs
   - Create enhanced examples file
   - Update gap analysis
   - **Proof**: All docs consistent, examples runnable

---

## Success Validation

**After Phase 1 Completion**:

```bash
# 1. All tests pass
pytest tests/ -v --cov=structured_query_builder

# 2. Examples run successfully
python examples/enhanced_bimodal_queries.py

# 3. Coverage increased
# Before: 15 queries, 37% coverage (7/19 concerns)
# After: 25 queries, 70% coverage (13/19 concerns)

# 4. New features validated
# - STDDEV aggregate works
# - BinaryArithmetic with table_alias works
# - Temporal snapshot pattern works
```

**Deliverables**:
- 5 git commits with clear proof-of-work
- 10 new runnable queries
- Updated test suite (100% coverage maintained)
- Updated documentation
- Intelligence model coverage: 37% → 70%

---

## Next Steps (Phase 2)

After Phase 1:
- Add query metadata framework (operational deployment)
- Implement commoditization coefficient
- Plan cost data model for Phase 3

**End of Phase 1 Plan**
