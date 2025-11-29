# Agent Handoff - Iteration 2: Fix Half-Assed Implementations
**Date**: 2025-11-29
**From**: Phase 1-3 Implementation Agent
**To**: Quality Remediation Agent
**Branch**: `claude/agent-handoff-docs-01Y7PptvJSU479UKKbXHBj3Q`

---

## Critical Context: What I Got Wrong

### Misunderstanding #1: "Single Snapshot Limitation"
**WRONG**: I claimed data is single snapshot, can't do temporal comparisons
**RIGHT**: Data IS historical with `updated_at` timestamps - can do temporal queries

**Impact**: 8 queries deliver weak "snapshot" patterns instead of real temporal intelligence

### Misunderstanding #2: "Application Layer Required"
**WRONG**: Claimed many queries need app-layer completion (percentages, temporal logic)
**RIGHT**: Queries are for LLM structured outputs - must be self-contained

**Impact**: 11 queries provide "foundation data" instead of actual intelligence

### Misunderstanding #3: "Best Possible Given Constraints"
**WRONG**: Accepted limitations and documented workarounds
**RIGHT**: Should have added missing schema features to solve problems

**Impact**: Missing percentile functions, binning support, proper temporal patterns

---

## Current State (Honest Assessment)

**Coverage**: 29 queries addressing 19/19 intelligence concerns
**Quality**:
- 10 queries (34%) work correctly
- 11 queries (38%) are half-assed (provide data, not intelligence)
- 8 queries (28%) are missing or broken

**See**: `docs/analysis/QUERY_ALIGNMENT_EVALUATION.md` for brutal details

---

## Your Mission: Fix the Broken Shit

### Part 1: Fix Broken Temporal Queries (Priority 1)

These queries claim temporal intelligence but deliver snapshots. **Data IS historical** - use it.

#### Q18: Supply Chain Failure Detector (Unmatched)
**Current**: Counts products by brand (snapshot)
**Spec**: "Check for sudden drops" in competitor inventory
**Fix**: Use window functions to compare current count vs previous period
```sql
-- Use LAG to detect drops
SELECT brand,
       COUNT(*) AS current_count,
       LAG(COUNT(*)) OVER (PARTITION BY brand ORDER BY updated_at) AS previous_count,
       (previous_count - current_count) / previous_count AS drop_percentage
WHERE drop_percentage > 0.4
```
**Schema needs**: Window functions already exist ✅

#### Q20: Category Price Snapshot (Temporal)
**Current**: Single time window filter (BETWEEN)
**Spec**: "Avg price increase on same-SKU over 6 months"
**Fix**: Self-join on time periods to calculate actual delta
```sql
-- Compare T vs T-6months
SELECT category,
       AVG(t_now.markdown_price - t_then.markdown_price) AS avg_price_increase
FROM product_offers AS t_now
JOIN product_offers AS t_then
  ON t_now.id = t_then.id
WHERE t_now.updated_at = CURRENT_DATE
  AND t_then.updated_at = CURRENT_DATE - INTERVAL '6 months'
```
**Schema needs**: Self-join pattern (already supported ✅)

#### Q22: Brand Presence Tracking (Unmatched)
**Current**: Count by brand/vendor (snapshot)
**Spec**: "Compare Count(Offers) for T_Current vs T_LastWeek"
**Fix**: Use LAG or self-join for temporal comparison
```sql
SELECT brand, vendor,
       COUNT(*) AS current_count,
       LAG(COUNT(*)) OVER (PARTITION BY brand, vendor ORDER BY snapshot_date) AS last_week_count,
       (last_week_count - current_count) / last_week_count AS drop_pct
```
**Schema needs**: Window functions ✅ or self-join ✅

#### Q28: Safe Haven Scanner (Matched)
**Current**: STDDEV across products (cross-sectional)
**Spec**: "StdDev(Competitor_Price_52Weeks)" (temporal volatility)
**Fix**: Use window function over time partition
```sql
SELECT category, brand,
       AVG(comp.markdown_price) AS avg_comp_price,
       STDDEV(comp.markdown_price) OVER (
         PARTITION BY category, brand
         ORDER BY comp.updated_at
         ROWS BETWEEN 52 PRECEDING AND CURRENT ROW
       ) AS price_volatility_52weeks
```
**Schema needs**: Window with ROWS frame (check if supported)

#### Q29: Inventory Velocity Detector (Matched)
**Current**: Shows current availability (snapshot)
**Spec**: "Availability toggles (True -> False -> True) frequently"
**Fix**: Use LAG to detect state changes, count transitions
```sql
SELECT product_id,
       availability AS current_avail,
       LAG(availability) OVER (PARTITION BY product_id ORDER BY updated_at) AS prev_avail,
       COUNT(CASE WHEN availability != prev_avail THEN 1 END) AS toggle_count
GROUP BY product_id
HAVING toggle_count > 3  -- "frequently"
```
**Schema needs**: Window LAG ✅, CASE expressions ✅

---

### Part 2: Fix Mathematical Errors (Priority 1)

#### Q17: Premium Gap Analysis (Matched)
**Current**: Calculates `AVG(my.price) - AVG(comp.price)`
**Spec**: Calculate `AVG(my.price - comp.price)`
**Why Different**: Mean of differences ≠ difference of means when sample sizes vary

**Fix**: Use nested BinaryArithmetic inside AggregateExpr
```python
AggregateExpr(
    function=AggregateFunc.avg,
    arithmetic_input=BinaryArithmetic(
        left_column=Column.markdown_price,
        left_table_alias="my",
        operator=ArithmeticOp.subtract,
        right_column=Column.markdown_price,
        right_table_alias="comp",
        alias="price_gap"
    ),
    alias="avg_premium_gap"
)
```
**Schema needs**: Support arithmetic as aggregate input (new feature required)

---

### Part 3: Add Missing Schema Features (Priority 2)

#### Feature 1: Percentile Aggregate Functions
**Needed for**: Q06 (Cluster Floor Check)

**Add to `AggregateFunc` enum**:
```python
percentile_cont = "PERCENTILE_CONT"  # Continuous percentile
percentile_disc = "PERCENTILE_DISC"  # Discrete percentile
```

**Add percentile parameter to AggregateExpr**:
```python
class AggregateExpr(BaseModel):
    # ... existing fields
    percentile: Optional[float] = None  # e.g., 0.1 for 10th percentile
```

**Use case**:
```python
# Q06: Check if price below 10th percentile
AggregateExpr(
    function=AggregateFunc.percentile_cont,
    column=Column.markdown_price,
    percentile=0.1,
    alias="floor_price"
)
```

#### Feature 2: CASE Expression for Binning
**Needed for**: Q03 (Category Histogram), Q26 (Price Ladder Void)

**Schema already has CaseExpr** ✅ - just need to use it properly

**Example**:
```python
# Bin prices into buckets
CaseExpr(
    conditions=[
        CaseCondition(
            when=SimpleCondition(column=Column.markdown_price, operator=ComparisonOp.lt, value=50),
            then=ValueExpr(value="$0-50")
        ),
        CaseCondition(
            when=SimpleCondition(column=Column.markdown_price, operator=ComparisonOp.lt, value=100),
            then=ValueExpr(value="$50-100")
        ),
    ],
    else_expr=ValueExpr(value="$100+"),
    alias="price_bucket"
)
```

#### Feature 3: MAP Pricing Table
**Needed for**: MAP Policing (Matched variant)

**Add to `Table` enum**:
```python
map_pricing = "map_pricing"
```

**Schema**:
```yaml
map_pricing:
  columns:
    - sku: String (join key)
    - brand: String
    - map_floor: Decimal (minimum advertised price)
```

---

### Part 4: Implement Missing Queries (Priority 3)

#### Q03: Category Histogram (Unmatched) - ENFORCER
**Spec**: "Plot Count(Offers) by Price Bin. Compare shapes."
**Implementation**: Use CASE for binning + GROUP BY bucket
```python
def query_03_category_histogram():
    return Query(
        select=[
            ColumnExpr(column=QualifiedColumn(column=Column.category)),
            ColumnExpr(column=QualifiedColumn(column=Column.vendor)),
            CaseExpr(
                conditions=[
                    # Price buckets $0-50, $50-100, etc.
                ],
                alias="price_bucket"
            ),
            AggregateExpr(function=AggregateFunc.count, alias="offer_count")
        ],
        from_clause=FromClause(table=Table.product_offers),
        group_by=GroupByClause(columns=[
            Column.category, Column.vendor, "price_bucket"
        ]),
        order_by=OrderByClause(columns=[...])
    )
```

#### Q06: Cluster Floor Check (Unmatched) - PREDATOR
**Spec**: "Identify 10th Percentile Price. Check if My_Price < 10th_Percentile."
**Implementation**: Use percentile function (once added)

#### Q08: Slash-and-Burn Alert (Matched) - HISTORIAN
**Spec**: "Count matches where price dropped >15% overnight"
**Implementation**: Use LAG to compare T vs T-1
```sql
SELECT COUNT(*) AS slash_burn_count
FROM (
  SELECT id,
         markdown_price,
         LAG(markdown_price) OVER (PARTITION BY id ORDER BY updated_at) AS prev_price,
         (prev_price - markdown_price) / prev_price AS drop_pct
  FROM product_offers
  WHERE updated_at IN (CURRENT_DATE, CURRENT_DATE - 1)
)
WHERE drop_pct > 0.15
```

#### Q09: Minimum Viable Price Lift (Unmatched) - HISTORIAN
**Spec**: "Track Min(Price) of category over time"
**Implementation**: Group by time period + category
```sql
SELECT DATE_TRUNC('month', updated_at) AS month,
       category,
       MIN(markdown_price) AS min_price
FROM product_offers
GROUP BY month, category
ORDER BY month, category
```

#### Q10: Assortment Rotation Check (Matched) - HISTORIAN
**Spec**: "Select IDs present in T_LastWeek but missing in T_Current"
**Implementation**: Use temporal set difference (LEFT JOIN + NULL check)
```sql
SELECT t_last.id AS delisted_id
FROM product_offers AS t_last
LEFT JOIN product_offers AS t_now
  ON t_last.id = t_now.id
  AND t_now.updated_at = CURRENT_DATE
WHERE t_last.updated_at = CURRENT_DATE - 7
  AND t_now.id IS NULL
```

#### Q13: Ghost Inventory Check (Matched) - ARCHITECT
**Spec**: "Select where Competitor_Availability = FALSE for > 4 consecutive weeks"
**Implementation**: Use window functions to count consecutive FALSE
```sql
SELECT product_id
FROM (
  SELECT id,
         availability,
         SUM(CASE WHEN availability = FALSE THEN 1 ELSE 0 END)
           OVER (PARTITION BY id ORDER BY updated_at ROWS BETWEEN 3 PRECEDING AND CURRENT ROW)
           AS consecutive_stockout_weeks
  FROM product_offers
  WHERE vendor = 'Competitor'
)
WHERE consecutive_stockout_weeks >= 4
```

#### Q14: Global Floor Stress Test (Unmatched) - ARCHITECT
**Spec**: "Select Min(Price) Group By Brand+Category. Compare vs My_Entry_Level_Cost."
**Implementation**: Straightforward MIN aggregate
```python
def query_14_global_floor_stress_test():
    return Query(
        select=[
            ColumnExpr(column=QualifiedColumn(column=Column.brand)),
            ColumnExpr(column=QualifiedColumn(column=Column.category)),
            AggregateExpr(
                function=AggregateFunc.min,
                column=Column.markdown_price,
                alias="market_floor_price"
            )
        ],
        from_clause=FromClause(table=Table.product_offers),
        where=WhereL1(groups=[
            ConditionGroup(conditions=[
                SimpleCondition(
                    column=QualifiedColumn(column=Column.vendor),
                    operator=ComparisonOp.neq,
                    value="Us"
                )
            ])
        ]),
        group_by=GroupByClause(columns=[Column.brand, Column.category])
    )
```

---

### Part 5: Fix "Partial" Queries (Priority 3)

These deliver foundation data but need completion to provide actual intelligence.

#### Q24: Commoditization Coefficient (Matched)
**Current**: Provides raw counts
**Spec**: Calculate ratio `Count(Matches) / Count(Total_Assortment)`
**Fix**: Add arithmetic to calculate percentage
```python
# Add to SELECT:
BinaryArithmetic(
    left_column=AggregateExpr(function=AggregateFunc.count, column=Column.source_id),
    operator=ArithmeticOp.divide,
    right_column=AggregateExpr(function=AggregateFunc.count, column=Column.id),
    alias="commoditization_coefficient"
)
```

#### Q25: Brand Weighting Fingerprint (Unmatched)
**Current**: Raw counts by brand
**Spec**: Share-of-shelf percentage
**Fix**: Use window function for total, calculate percentage
```sql
SELECT brand, vendor,
       COUNT(*) AS brand_count,
       COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY vendor) AS share_of_shelf_pct
```

#### Q26: Price Ladder Void Scanner (Unmatched)
**Current**: Statistics (MIN/MAX/AVG/STDDEV)
**Spec**: Histogram binning with void detection
**Fix**: Use CASE for binning (see Q03 pattern)

---

## Implementation Priorities

### Week 1: Fix Broken Core Queries
1. ✅ Fix Q17 math error (nested arithmetic in aggregate)
2. ✅ Fix Q18 temporal pattern (window LAG)
3. ✅ Fix Q20 temporal comparison (self-join)
4. ✅ Fix Q22 temporal tracking (window LAG)
5. ✅ Fix Q28 temporal STDDEV (window ROWS frame)
6. ✅ Fix Q29 velocity detection (LAG + toggle count)

### Week 2: Add Missing Schema Features
1. ✅ Add percentile aggregate functions
2. ✅ Add nested arithmetic support in AggregateExpr
3. ✅ Add MAP pricing table to schema
4. ✅ Test CASE expressions for binning
5. ✅ Test window ROWS frames

### Week 3: Implement Missing Queries
1. ✅ Q03: Category Histogram
2. ✅ Q06: Cluster Floor Check
3. ✅ Q08: Slash-and-Burn Alert
4. ✅ Q09: Minimum Viable Price Lift
5. ✅ Q10: Assortment Rotation Check
6. ✅ Q13: Ghost Inventory Check
7. ✅ Q14: Global Floor Stress Test

### Week 4: Complete Partial Queries
1. ✅ Q24: Add ratio calculation
2. ✅ Q25: Add percentage calculation
3. ✅ Q26: Convert to histogram binning

---

## Success Criteria

### Must-Have
- [ ] All 29 queries deliver spec-compliant intelligence (not "foundation data")
- [ ] No queries require "application layer completion"
- [ ] All temporal queries use historical data properly
- [ ] Zero mathematical errors
- [ ] All missing queries implemented

### Quality Gates
- [ ] Each query tested with actual SQL translation
- [ ] Each query matches intelligence model spec exactly
- [ ] No "partial" or "degraded" implementations
- [ ] Coverage = 100% AND quality = 100%

### Proof-of-Work
- [ ] All queries in examples/ with runnable code
- [ ] All queries have comprehensive tests
- [ ] All tests passing
- [ ] All queries committed with granular commits
- [ ] Documentation updated to remove "limitations" excuses

---

## What NOT to Do

❌ **Don't** document limitations - fix them
❌ **Don't** create "foundation queries" - deliver intelligence
❌ **Don't** claim "application layer required" - make queries self-contained
❌ **Don't** accept "partial" as good enough
❌ **Don't** mark tasks complete without proof-of-work
❌ **Don't** claim "single snapshot" limitations - data IS historical

---

## Key Files

**Read First**:
- `CLAUDE.md` - User's behavioral preferences (critical)
- `docs/analysis/QUERY_ALIGNMENT_EVALUATION.md` - Brutal gap analysis
- `intelligence_models/*.yaml` - Actual specs to implement

**Your Deliverables**:
- Fixed queries in `examples/phase*_queries.py`
- New queries for missing concerns
- Updated tests in `structured_query_builder/tests/`
- Schema enhancements in `structured_query_builder/enums.py`, `expressions.py`

**Reference**:
- `README.md` - Current state
- `docs/planning/COMPLETE_IMPLEMENTATION_SUMMARY.md` - What was claimed

---

## Bottom Line

**Previous iteration**: Shipped 100% coverage with 53% quality. Made excuses about data model.
**Your iteration**: Ship 100% coverage with 100% quality. No excuses.

**Data IS historical. Queries CAN be self-contained. Features CAN be added.**

Fix the broken shit. Implement the missing shit. Ship exemplar implementations.

No more "addressing" - deliver working intelligence.
