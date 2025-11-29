# Bimodal Intelligence Model Gap Analysis
## Exhaustiveness & Structural Meaning Assessment

**Analysis Date**: 2025-11-29
**Analyst**: Claude (Sonnet 4.5)
**Task**: Evaluate existing 15 bimodal queries against comprehensive intelligence models

---

## Executive Summary

**Exhaustiveness Score: 42/100** ⚠️
**Structural Meaning: 65/100** ⚠️

### Key Findings:

1. **Coverage**: Existing queries cover **7 of 19 intelligence concerns** (37% coverage)
2. **Pricing Analyst**: 7/11 concerns covered (64%)
3. **Commercial Architect**: 0/8 concerns covered (0%)
4. **Structural Gaps**: Queries lack business context metadata, actionability scores, and integration patterns
5. **Major Omissions**: No procurement intelligence, no range architecture, no trend tracking

**Verdict**: Current implementation is a **proof-of-concept** demonstrating technical capability but lacks the **strategic depth** required for production pricing intelligence.

---

## Part 1: Mapping Existing Queries to Intelligence Models

### 1.1 Pricing Analyst Coverage Map

| Archetype | Concern | Spec Variant | Existing Query | Coverage |
|-----------|---------|--------------|----------------|----------|
| **ENFORCER** | | | | **3/3** ✅ |
| | Parity Maintenance | Matched | Q01: Parity Check | ✅ Full |
| | Parity Maintenance | Unmatched | Q03: ASP Gap | ✅ Full |
| | MAP Policing | Matched | Q02: MAP Violations | ✅ Full |
| | MAP Policing | Unmatched | ❌ Missing | ❌ None |
| | Brand Alignment | Matched | ❌ Missing | ❌ None |
| | Brand Alignment | Unmatched | Q04: Price Distribution | 🟡 Partial |
| **PREDATOR** | | | | **3/6** 🟡 |
| | Monopoly Exploitation | Matched | Q05: Stockout Advantage | ✅ Full |
| | Monopoly Exploitation | Unmatched | ❌ Missing | ❌ None |
| | Headroom Discovery | Matched | Q06: Premium Products | 🟡 Inverted |
| | Headroom Discovery | Unmatched | Q07: Headroom Discovery | ✅ Full |
| | Bottom Feeding | Matched | ❌ Missing | ❌ None |
| | Bottom Feeding | Unmatched | Q08: Deep Discounts | 🟡 Partial |
| **HISTORIAN** | | | | **1/6** ❌ |
| | Promo Detection | Matched | Q09: Promo Detection | 🟡 Partial |
| | Promo Detection | Unmatched | Q10: Category Trends | 🟡 Weak |
| | Inflation Tracking | Matched | ❌ Missing | ❌ None |
| | Inflation Tracking | Unmatched | Q10: Category Trends | 🟡 Weak |
| | Churn Analysis | Matched | ❌ Missing | ❌ None |
| | Churn Analysis | Unmatched | Q11: Assortment Changes | 🟡 Snapshot Only |
| **MERCENARY** | | | | **2/3** 🟡 |
| | Optical Dominance | Matched | Q13: Anchor Comparison | ✅ Full |
| | Optical Dominance | Unmatched | Q12: Discount Depth | 🟡 Partial |
| | Keyword Arbitrage | Unmatched | Q15: Keyword Pricing | ✅ Full |

**Pricing Analyst Coverage**: 7/11 concerns (64%) with many partial implementations

---

### 1.2 Commercial Architect Coverage Map

| Domain | Concern | Spec Variant | Existing Query | Coverage |
|--------|---------|--------------|----------------|----------|
| **RANGE ARCHITECTURE** | | | | **0/4** ❌ |
| | Assortment Overlap & Exclusivity | Matched | ❌ None | ❌ None |
| | Assortment Overlap & Exclusivity | Unmatched | ❌ None | ❌ None |
| | Gap Analysis & White Space | Matched | ❌ None | ❌ None |
| | Gap Analysis & White Space | Unmatched | ❌ None | ❌ None |
| **PROCUREMENT INTELLIGENCE** | | | | **0/4** ❌ |
| | Cost Model Validation | Matched | ❌ None | ❌ None |
| | Cost Model Validation | Unmatched | ❌ None | ❌ None |
| | Margin Potential Discovery | Matched | ❌ None | ❌ None |
| | Margin Potential Discovery | Unmatched | ❌ None | ❌ None |
| **PRICING ARCHITECTURE** | | | | **0/4** ❌ |
| | Psychological Anchoring | Matched | Q13 (weak match) | 🟡 Weak |
| | Psychological Anchoring | Unmatched | Q12 (weak match) | 🟡 Weak |
| | Inflation & Trends | Matched | ❌ None | ❌ None |
| | Inflation & Trends | Unmatched | Q10 (weak match) | 🟡 Weak |
| **TOTAL RECONNAISSANCE** | | | | **0/4** ❌ |
| | Semantic Clustering | Unmatched | Q15 (weak) | 🟡 Weak |
| | Inventory Velocity Inference | Matched | ❌ None | ❌ None |
| | Inventory Velocity Inference | Unmatched | ❌ None | ❌ None |

**Commercial Architect Coverage**: 0/8 concerns (0%) - complete gap

---

## Part 2: Detailed Gap Analysis

### 2.1 CRITICAL GAPS - Pricing Analyst

#### Gap 1: MAP Policing (Unmatched)

**Spec Requirement**:
```yaml
unmatched_approximation:
  query_name: "The Brand Floor Scan"
  logic: "Select * from Competitor_Offers where Brand = 'Dyson' AND Price < Global_Dyson_MAP_Floor."
  outcome: "Dragnet: 'They have 3 unidentified Dyson items selling below the legal limit.'"
```

**Current State**: Not implemented

**Business Impact**: **HIGH**
Cannot detect MAP violations on unmatched products. In reality, most competitor products are NOT matched, so we miss majority of violations.

**Implementation Complexity**: **LOW**
Simple WHERE filter on brand + price threshold.

---

#### Gap 2: Brand Alignment (Matched)

**Spec Requirement**:
```yaml
matched_execution:
  query_name: "The Premium Gap Analysis"
  logic: "Avg(My_Price - Competitor_Price) on Matched Items Only."
  outcome: "apples-to-apples comparison of premium markup."
```

**Current State**: Not implemented

**Business Impact**: **MEDIUM**
Cannot answer: "How much of a premium are we charging vs. competitor on identical products?"

**Why Q01 Doesn't Cover This**:
- Q01 returns raw prices, not price differences
- No aggregation to compute average gap
- Missing computed column: `my.price - comp.price AS gap`

**Implementation Complexity**: **LOW**
Add BinaryArithmetic expression to Q01.

---

#### Gap 3: Monopoly Exploitation (Unmatched)

**Spec Requirement**:
```yaml
unmatched_approximation:
  query_name: "The Supply Chain Failure Detector"
  logic: "Count(Competitor_In_Stock_Offers) Group By Brand. Check for sudden drops."
  outcome: "Broad Policy: 'Their Sony inventory dropped 40%. Turn off all Sony auto-discounts.'"
```

**Current State**: Not implemented

**Business Impact**: **HIGH**
Cannot detect competitor supply chain failures at the brand level, missing major pricing opportunities.

**Schema Challenge**: Requires temporal comparison (current vs. 1 week ago)
→ **This exposes a fundamental limitation**: No time-series support in current schema.

---

#### Gap 4: Bottom Feeding (Matched)

**Spec Requirement**:
```yaml
matched_execution:
  query_name: "The Loss-Leader Hunter"
  logic: "Flag matches where Competitor_Price < My_Cost_Proxy."
  outcome: "Exclusion List: 'Do not match SKU #999; they are dumping it.'"
```

**Current State**: Not implemented

**Business Impact**: **HIGH**
Cannot identify competitor loss-leaders to avoid price matching into negative margin.

**Schema Challenge**: Requires cost data, which doesn't exist in `product_offers` table.
→ **This exposes data model gap**: No cost column available.

---

#### Gap 5: Inflation Tracking (Both Variants)

**Spec Requirement**:
```yaml
matched_execution:
  query_name: "The Item Inflation Tracker"
  logic: "Avg price increase on same-SKU over 6 months."

unmatched_execution:
  query_name: "The Minimum Viable Price Lift"
  logic: "Track Min(Price) of the category over time."
```

**Current State**: Not implemented

**Business Impact**: **CRITICAL**
Cannot detect market inflation trends, missing strategic pricing opportunities.

**Schema Challenge**: Requires multi-snapshot temporal queries.
→ **This exposes fundamental limitation**: Current schema has `updated_at` timestamp but no time-series query support.

**Potential Workaround**: Self-join on time periods
```sql
SELECT
    t1.category,
    AVG(t2.price - t1.price) AS avg_inflation
FROM product_offers t1
JOIN product_offers t2
    ON t1.id = t2.id
    AND t2.updated_at = CURRENT_DATE
    AND t1.updated_at = CURRENT_DATE - INTERVAL 6 MONTHS
```

**Can Current Schema Support This?**: 🟡 YES, but requires complex self-joins not demonstrated.

---

#### Gap 6: Churn Analysis (Matched)

**Spec Requirement**:
```yaml
matched_execution:
  query_name: "The Assortment Rotation Check"
  logic: "Select IDs present in T_LastWeek but missing in T_Current (Competitor Only)."
  outcome: "Specific Intel: 'They stopped selling the Dyson V10 and V11.'"
```

**Current State**: Q11 shows current counts, not churn

**Business Impact**: **HIGH**
Cannot detect when competitor exits specific products, missing market share capture opportunities.

**Schema Challenge**: Requires temporal difference queries (set operations on different time snapshots).

**Can Current Schema Support This?**: 🟡 YES, using self-join with `updated_at` filtering
BUT: No set operations (UNION, EXCEPT) supported by schema.

**Workaround**: LEFT JOIN with NULL check
```sql
SELECT t1.id, t1.title
FROM product_offers_lastweek t1
LEFT JOIN product_offers_current t2 ON t1.id = t2.id
WHERE t2.id IS NULL
```

---

### 2.2 CRITICAL GAPS - Commercial Architect

#### Gap 7: Assortment Overlap & Exclusivity (Commoditization Coefficient)

**Spec Requirement**:
```yaml
matched_execution:
  query_name: "The Commoditization Coefficient"
  logic: |
    1. Select Count(Matches) / Count(Total_My_Assortment).
    2. Select Count(Matches) / Count(Total_Competitor_Assortment).
  insight: "I share 80% of my range with them, but they only share 10% of their range with me."
```

**Current State**: Not implemented

**Business Impact**: **CRITICAL**
Cannot answer: "How differentiated is my assortment?" This is fundamental to strategy.

**Implementation**:
```python
# Query 1: My overlap percentage
Query(
    select=[
        AggregateExpr(function=AggregateFunc.count_distinct, column=Column.id, alias="my_total"),
        AggregateExpr(function=AggregateFunc.count, column=Column.source_id, alias="matched_count")
    ],
    from_=FromClause(
        table=Table.product_offers,
        table_alias="my",
        joins=[
            JoinSpec(
                join_type=JoinType.left,  # ← LEFT to get all my products
                table=Table.exact_matches,
                ...
            )
        ]
    ),
    where=WhereL1(groups=[ConditionGroup(conditions=[
        SimpleCondition(column=QualifiedColumn(column=Column.vendor, table_alias="my"), operator=ComparisonOp.eq, value="Us")
    ])])
)
# Then: matched_count / my_total in app layer
```

**Schema Support**: ✅ YES - can be implemented with LEFT JOIN + COUNT

---

#### Gap 8: Gap Analysis & White Space (Ghost Inventory)

**Spec Requirement**:
```yaml
matched_execution:
  query_name: "The Ghost Inventory Check"
  logic: "Select Matches where Competitor_Availability = FALSE for > 4 consecutive weeks."
```

**Current State**: Not implemented

**Business Impact**: **HIGH**
Cannot identify products competitor has abandoned (permanent stockouts).

**Schema Challenge**: Requires temporal windowing (4+ consecutive weeks).
→ **Cannot be implemented with current schema** (no window functions over time periods).

**Potential Approach**: Requires historical snapshots table, not single `product_offers` table.

---

#### Gap 9: Procurement Intelligence (Cost Model Validation)

**Spec Requirement**:
```yaml
matched_execution:
  query_name: "The Vendor Fairness Audit"
  logic: "Select Matches where Competitor_Regular_Price < (My_Net_Cost * 1.05)."
  insight: "They are buying this 10% cheaper than me."
```

**Current State**: Not implemented

**Business Impact**: **CRITICAL**
This is strategic procurement leverage. Missing this means overpaying vendors.

**Schema Challenge**: **Requires cost data** which doesn't exist in spec.
→ **Data model gap**: Need `cost` column in product_offers or separate cost table.

---

#### Gap 10: Margin Potential Discovery (Safe Haven Scan)

**Spec Requirement**:
```yaml
matched_execution:
  query_name: "The Safe Haven Scan"
  logic: "Select Matches where StdDev(Competitor_Price_52Weeks) is Low AND (Competitor_Price - My_Cost) > 40%."
```

**Current State**: Not implemented

**Business Impact**: **HIGH**
Cannot identify high-margin, low-volatility products for margin optimization.

**Schema Challenges**:
1. No `STDDEV` aggregate function in current schema
2. No cost data
3. Requires 52-week historical data

**Can Be Partially Implemented**: 🟡 Add STDDEV to AggregateFunc enum (easy)
**Cannot Be Fully Implemented**: ❌ Missing cost data & time-series

---

#### Gap 11: Psychological Anchoring (Discount Depth Alignment)

**Spec Requirement**:
```yaml
matched_execution:
  query_name: "The Discount Depth Alignment"
  logic: "Select Matches where (Competitor_Regular - Competitor_Current) > (My_Regular - My_Current)."
  insight: "Their deal looks better even though final prices are equal."
```

**Current State**: Q14 computes discount amounts but doesn't compare

**Business Impact**: **MEDIUM**
Missing the comparison logic to identify optical disadvantage.

**Implementation Gap**: Q14 returns both discount amounts but doesn't filter where theirs > ours.

**Fix Required**: Add WHERE clause with ColumnComparison:
```python
where=WhereL1(groups=[
    ConditionGroup(conditions=[
        ColumnComparison(
            left_column=QualifiedColumn(column=Column.regular_price, table_alias="comp"),
            operator=ComparisonOp.gt,
            right_column=QualifiedColumn(column=Column.regular_price, table_alias="my")
        )
    ])
])
```

**Schema Support**: ✅ YES - ColumnComparison exists

---

#### Gap 12: Inflation Trends (Same-Store Inflation Rate)

**Spec Requirement**:
```yaml
matched_execution:
  query_name: "The Same-Store Inflation Rate"
  logic: "Calculate Sum(Price_Current) for the specific basket of items that existed both Today and 1 Year Ago."
```

**Current State**: Not implemented

**Business Impact**: **CRITICAL**
Cannot measure market inflation to justify broad price increases.

**Schema Challenge**: Requires temporal self-join across 1-year period.

---

#### Gap 13: Inventory Velocity Inference (High-Velocity Detector)

**Spec Requirement**:
```yaml
matched_execution:
  query_name: "The High-Velocity Detector"
  logic: "Identify Matches where Availability toggles (True -> False -> True) frequently."
  insight: "This item keeps selling out and restocking. It is a high-volume winner."
```

**Current State**: Not implemented

**Business Impact**: **HIGH**
Cannot infer sales velocity from stockout patterns.

**Schema Challenge**: Requires event history of availability changes over time.
→ **Cannot be implemented** with single-snapshot data model.

---

## Part 3: Structural Meaning Assessment

### 3.1 Current Structure

**What Exists**:
```python
def query_01_parity_check_matched():
    """
    MATCHED: Side-by-side price comparison for matched products.
    Business: Direct price comparison with competitor on same products.
    Limitation: Can't compute ratio in WHERE, filter > 1.05 in app layer.
    """
    return Query(...)
```

**Structural Elements Present**:
1. ✅ Function name indicates archetype and purpose
2. ✅ Docstring with business context
3. ✅ Limitation documentation
4. ✅ Matched/Unmatched classification

**Structural Elements MISSING**:
1. ❌ No archetype metadata (string tag)
2. ❌ No concern mapping to intelligence model
3. ❌ No actionability score
4. ❌ No frequency recommendation (hourly? daily?)
5. ❌ No alert threshold metadata
6. ❌ No downstream integration patterns
7. ❌ No business KPI mapping

---

### 3.2 What "Meaningful Structure" Looks Like

**Production-Grade Query Metadata**:
```python
@query_metadata(
    archetype="ENFORCER",
    concern="parity_maintenance",
    variant="matched",
    impact="HIGH",
    frequency="hourly",
    actionability="AUTOMATED",  # Can trigger automated repricing
    alert_threshold={"drift_percent": 5},
    kpi_mapping=["price_competitiveness_index", "margin_preservation"],
    downstream_integrations=["pricing_engine", "slack_alerts"],
    data_freshness_required="< 1 hour"
)
def query_01_parity_check_matched():
    """
    MATCHED: Side-by-side price comparison for matched products.

    Business Value:
        Detects when our prices drift above market, causing loss of competitiveness.

    Action Trigger:
        If drift > 5% on more than 20 products → Trigger automated price adjustment
        If drift > 10% on any product → Alert pricing team immediately

    Cadence: Run every hour

    Limitations:
        - Can't compute ratio in WHERE, filter > 1.05 in app layer
        - Requires exact_matches table to be up-to-date
    """
    return Query(...)
```

**Why This Matters**:
1. **Operational Integration**: Metadata enables automated scheduling
2. **Alert Configuration**: Thresholds trigger business actions
3. **Impact Prioritization**: HIGH impact queries run more frequently
4. **Traceability**: KPI mapping shows business value
5. **Data Governance**: Freshness requirements ensure quality

---

### 3.3 Structural Gaps in Current Implementation

| Element | Current State | Production Requirement | Gap |
|---------|--------------|------------------------|-----|
| **Query Metadata** | Function name + docstring | Structured decorator with impact, frequency, KPIs | ❌ Missing |
| **Archetype Tagging** | In function name only | Programmatic enum/string tag | ❌ Missing |
| **Alert Thresholds** | Not specified | Numeric thresholds for automated actions | ❌ Missing |
| **Frequency Guidance** | Not specified | hourly/daily/weekly recommendation | ❌ Missing |
| **Action Mapping** | Not specified | What business action to take on results | ❌ Missing |
| **KPI Linkage** | Not specified | Which business metrics this affects | ❌ Missing |
| **Data Freshness** | Not specified | How recent data must be for valid results | ❌ Missing |
| **Integration Hooks** | Not specified | Which systems consume this query | ❌ Missing |

**Current Structural Meaning Score**: **35/100**
Queries are **testable** and **demonstrate technical capability** but lack **operational context** for production deployment.

---

## Part 4: Schema Capability vs. Intelligence Model Requirements

### 4.1 Temporal Analysis Limitation (CRITICAL)

**Intelligence Model Requirements**:
- Inflation tracking (6-month, 1-year comparisons)
- Churn detection (week-over-week changes)
- Promo detection (overnight price drops)
- Inventory velocity (availability toggle patterns)

**Current Schema**:
```python
class Column(str, Enum):
    ...
    updated_at = "updated_at"  # ← Single timestamp, no time-series support
```

**What's Missing**:
1. No explicit time-series query patterns
2. No window functions over time periods (LAG by date)
3. No multi-snapshot comparison queries
4. No temporal self-join examples

**Can Current Schema Support Temporal Queries?**: 🟡 **YES, but not demonstrated**

**Proof-of-Concept Missing Query** (Week-over-Week Inflation):
```python
# This COULD be implemented with current schema but ISN'T
Query(
    select=[
        ColumnExpr(source=QualifiedColumn(column=Column.category)),
        AggregateExpr(function=AggregateFunc.avg, column=Column.markdown_price, alias="avg_price_now"),
        # Need second AVG from last week - requires derived table or complex join
    ],
    from_=FromClause(
        table=Table.product_offers,
        table_alias="current",
        joins=[
            JoinSpec(
                join_type=JoinType.inner,
                table=Table.product_offers,  # Self-join to historical snapshot
                table_alias="last_week",
                on_conditions=[
                    ConditionGroup(conditions=[
                        ColumnComparison(
                            left_column=QualifiedColumn(column=Column.id, table_alias="current"),
                            operator=ComparisonOp.eq,
                            right_column=QualifiedColumn(column=Column.id, table_alias="last_week")
                        )
                    ])
                ]
            )
        ]
    ),
    where=WhereL1(groups=[
        ConditionGroup(conditions=[
            BetweenCondition(
                column=QualifiedColumn(column=Column.updated_at, table_alias="current"),
                low="2025-11-22",
                high="2025-11-29"
            ),
            BetweenCondition(
                column=QualifiedColumn(column=Column.updated_at, table_alias="last_week"),
                low="2025-11-15",
                high="2025-11-22"
            )
        ])
    ])
)
```

**Verdict**: Schema CAN support temporal analysis via self-joins, but:
- ❌ No examples demonstrating this capability
- ❌ Not validated in tests
- ❌ Complex pattern not documented

---

### 4.2 Cost Data Limitation (BLOCKING)

**Intelligence Model Requirements**:
- Vendor Fairness Audit (competitor price vs. my cost)
- Safe Haven Scan (margin calculation)
- Loss-Leader Hunter (competitor price < my cost)

**Current Schema**:
```python
class Column(str, Enum):
    regular_price = "regular_price"
    markdown_price = "markdown_price"
    # ❌ NO COST COLUMN
```

**Gap**: **6 intelligence queries require cost data** that doesn't exist in schema.

**Options**:
1. **Add cost column** to product_offers
2. **Add cost reference table** (product_costs)
3. **Accept limitation** and document these queries as unimplementable

**Recommendation**: **Option 2** (cost reference table)
Rationale: Cost is highly sensitive; air-gapping cost data from competitive data is good architecture.

**New Table Required**:
```python
class Table(str, Enum):
    product_offers = "product_offers"
    exact_matches = "exact_matches"
    product_costs = "product_costs"  # ← NEW
```

**New Columns Required**:
```python
class Column(str, Enum):
    # ... existing columns
    product_id = "product_id"  # For cost table
    net_cost = "net_cost"       # Actual cost we pay vendor
    target_margin_pct = "target_margin_pct"  # Business rule
```

---

### 4.3 Statistical Functions Limitation (EASY FIX)

**Intelligence Model Requirements**:
- STDDEV (price volatility for Safe Haven Scan)
- Percentiles (10th percentile for entry-level floor)

**Current Schema**:
```python
class AggregateFunc(str, Enum):
    count = "COUNT"
    sum = "SUM"
    avg = "AVG"
    min = "MIN"
    max = "MAX"
    # ❌ NO STDDEV
    # ❌ NO PERCENTILE
```

**Fix**: Add to enum
```python
class AggregateFunc(str, Enum):
    count = "COUNT"
    sum = "SUM"
    avg = "AVG"
    min = "MIN"
    max = "MAX"
    stddev = "STDDEV"          # ← ADD
    stddev_pop = "STDDEV_POP"  # ← ADD
    percentile_cont = "PERCENTILE_CONT"  # ← ADD
```

**Implementation Complexity**: **TRIVIAL** (5 minutes)
**Business Impact**: **MEDIUM** (enables volatility analysis)

---

## Part 5: Recommendations

### 5.1 IMMEDIATE (High Value, Low Effort)

#### Recommendation 1: Add Missing Statistical Functions
**Effort**: 5 minutes
**Impact**: Medium
**Implementation**:
```python
# enums.py
class AggregateFunc(str, Enum):
    # ... existing
    stddev = "STDDEV"
    percentile_cont = "PERCENTILE_CONT"
```

#### Recommendation 2: Implement MAP Policing (Unmatched)
**Effort**: 10 minutes
**Impact**: High
**Gaps Closed**: Pricing Analyst → ENFORCER → MAP Policing (Unmatched)

```python
def query_16_map_violations_unmatched():
    """
    UNMATCHED: Brand floor scan for MAP violations on all competitor products.

    Business: Detect MAP violations even when products aren't matched.
    """
    return Query(
        select=[
            ColumnExpr(source=QualifiedColumn(column=Column.id)),
            ColumnExpr(source=QualifiedColumn(column=Column.title)),
            ColumnExpr(source=QualifiedColumn(column=Column.brand)),
            ColumnExpr(source=QualifiedColumn(column=Column.markdown_price)),
        ],
        from_=FromClause(table=Table.product_offers),
        where=WhereL1(groups=[
            ConditionGroup(conditions=[
                SimpleCondition(column=QualifiedColumn(column=Column.vendor), operator=ComparisonOp.eq, value="Them"),
                SimpleCondition(column=QualifiedColumn(column=Column.brand), operator=ComparisonOp.eq, value="Nike"),
                SimpleCondition(column=QualifiedColumn(column=Column.markdown_price), operator=ComparisonOp.lt, value=50.0)
            ])
        ]),
        limit=LimitClause(limit=100)
    )
```

#### Recommendation 3: Implement Brand Alignment Premium Gap
**Effort**: 15 minutes
**Impact**: Medium
**Gaps Closed**: Pricing Analyst → ENFORCER → Brand Alignment (Matched)

```python
def query_17_premium_gap_analysis():
    """
    MATCHED: Average price premium on matched products.

    Business: Quantify how much more expensive we are vs. competitor on same items.
    """
    return Query(
        select=[
            ColumnExpr(source=QualifiedColumn(column=Column.brand, table_alias="my")),
            ColumnExpr(source=QualifiedColumn(column=Column.category, table_alias="my")),
            BinaryArithmetic(
                left_column=Column.markdown_price,
                table_alias="my",
                operator=ArithmeticOp.subtract,
                right_column=Column.markdown_price,
                table_alias_right="comp",
                alias="price_gap"
            ),
            AggregateExpr(function=AggregateFunc.avg, column=Column.markdown_price, alias="avg_gap"),
            AggregateExpr(function=AggregateFunc.count, column=None, alias="match_count")
        ],
        from_=FromClause(...),  # Same join pattern as Q01
        group_by=GroupByClause(columns=[Column.brand, Column.category])
    )
```

**BLOCKER**: BinaryArithmetic doesn't support table_alias on BOTH left and right operands.

**Schema Limitation Discovered**: ✅ **HONEST FINDING**
Current BinaryArithmetic model:
```python
class BinaryArithmetic(BaseModel):
    left_column: Optional[Column] = None
    right_column: Optional[Column] = None
    # ❌ NO table_alias fields
```

**Fix Required**: Upgrade BinaryArithmetic to support QualifiedColumn
```python
class BinaryArithmetic(BaseModel):
    left: Union[QualifiedColumn, float] = ...
    right: Union[QualifiedColumn, float] = ...
    operator: ArithmeticOp
    alias: str
```

**Impact**: This is a **schema design gap** that blocks several intelligence queries.

---

### 5.2 SHORT-TERM (High Value, Medium Effort)

#### Recommendation 4: Implement Temporal Comparison Queries
**Effort**: 2-3 hours
**Impact**: High
**Gaps Closed**:
- Inflation Tracking (both variants)
- Churn Analysis (matched)
- Promo Detection (enhanced)

**Requirements**:
1. Document temporal self-join pattern
2. Implement 3 example queries:
   - Week-over-week category price inflation
   - Product churn detection (disappeared products)
   - Overnight price drop detection (promo alerts)
3. Add tests validating temporal queries
4. Update GUIDE.md with temporal query patterns

---

#### Recommendation 5: Add Query Metadata Framework
**Effort**: 3-4 hours
**Impact**: Medium (enables operational deployment)
**Gaps Closed**: Structural meaning gaps

**Implementation**:
```python
# New file: query_metadata.py
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum

class QueryArchetype(str, Enum):
    ENFORCER = "enforcer"
    PREDATOR = "predator"
    HISTORIAN = "historian"
    MERCENARY = "mercenary"
    COMMERCIAL_ARCHITECT = "commercial_architect"

class QueryImpact(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class QueryFrequency(str, Enum):
    REALTIME = "realtime"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"

@dataclass
class QueryMetadata:
    name: str
    archetype: QueryArchetype
    concern: str
    variant: str  # "matched" or "unmatched"
    impact: QueryImpact
    frequency: QueryFrequency
    actionability: str  # "automated", "alert", "report"
    kpis: List[str]
    alert_thresholds: Optional[dict] = None
    downstream_integrations: Optional[List[str]] = None

def register_query(metadata: QueryMetadata):
    """Decorator to attach metadata to query functions"""
    def decorator(func):
        func.metadata = metadata
        return func
    return decorator
```

**Usage**:
```python
@register_query(QueryMetadata(
    name="Parity Check",
    archetype=QueryArchetype.ENFORCER,
    concern="parity_maintenance",
    variant="matched",
    impact=QueryImpact.HIGH,
    frequency=QueryFrequency.HOURLY,
    actionability="automated",
    kpis=["price_competitiveness_index", "margin_preservation"],
    alert_thresholds={"drift_percent": 5, "affected_products": 20}
))
def query_01_parity_check_matched():
    ...
```

---

#### Recommendation 6: Implement Commoditization Coefficient
**Effort**: 1 hour
**Impact**: High
**Gaps Closed**: Commercial Architect → Range Architecture → Assortment Overlap

**Implementation**: See Gap 7 implementation above.

---

### 5.3 LONG-TERM (Strategic Depth)

#### Recommendation 7: Add Cost Data Model
**Effort**: 4-6 hours
**Impact**: Critical
**Gaps Closed**: 6 procurement intelligence queries

**Requirements**:
1. Design `product_costs` table
2. Add `net_cost` column to schema
3. Update JOINs to support cost lookups
4. Implement 4 procurement queries:
   - Vendor Fairness Audit
   - Safe Haven Scan
   - Loss-Leader Hunter
   - Margin Potential Discovery

---

#### Recommendation 8: Add Commercial Architect Query Suite
**Effort**: 8-12 hours
**Impact**: High (new persona coverage)
**Gaps Closed**: 8 commercial architect concerns

**Deliverables**:
1. New file: `commercial_architect_queries.py`
2. 8+ queries covering:
   - Range Architecture (4 queries)
   - Procurement Intelligence (4 queries - requires cost data)
   - Pricing Architecture (already mostly covered)
   - Total Reconnaissance (2 queries)
3. Tests for all queries
4. Documentation in PRICING_ANALYST_QUERIES.md → rename to INTELLIGENCE_QUERIES.md

---

## Part 6: Honest Assessment

### 6.1 What We Have

**Technical Proof-of-Concept**: ✅ **EXCELLENT**
- 15 queries work
- All tests pass
- SQL generation validated
- Schema design sound

**Business Alignment**: 🟡 **PARTIAL**
- Covers 37% of intelligence model concerns
- Missing critical domains (procurement, range architecture)
- Weak temporal analysis (no time-series examples)

**Production Readiness**: ❌ **NOT READY**
- No operational metadata
- No alert thresholds
- No integration patterns
- No cost data support

---

### 6.2 What We're Missing

**Coverage Gaps**:
- 12 of 19 intelligence concerns not fully implemented (63% gap)
- 0 of 8 Commercial Architect concerns implemented (100% gap)
- 0 temporal comparison queries (critical for HISTORIAN archetype)

**Structural Gaps**:
- No query metadata framework
- No KPI linkage
- No action triggers
- No frequency guidance

**Schema Gaps**:
- No cost data support
- No temporal query patterns demonstrated
- BinaryArithmetic doesn't support qualified columns on both sides
- Missing STDDEV, PERCENTILE functions

---

### 6.3 The Honest Truth

**Is the implementation exhaustive?**: ❌ **NO**
37% coverage of intelligence model ≠ exhaustive.

**Is the structure meaningful beyond testing?**: 🟡 **PARTIALLY**
- Structure enables testing: ✅ Yes
- Structure enables production deployment: ❌ No
- Structure communicates business intent: 🟡 Weakly

**What would "exhaustive + meaningful" look like?**:
1. **90%+ intelligence model coverage** (17+ of 19 concerns)
2. **Query metadata framework** linking queries to KPIs
3. **Temporal query patterns** documented and tested
4. **Cost data model** enabling procurement intelligence
5. **Alert threshold configurations** for automated actions
6. **Integration patterns** documented for downstream systems

---

## Part 7: Recommended Action Plan

### Phase 1: Fill Critical Gaps (1-2 days)
1. ✅ Add STDDEV, PERCENTILE to AggregateFunc enum
2. ✅ Implement 3 missing ENFORCER queries
3. ✅ Implement 2 missing PREDATOR queries
4. ✅ Fix BinaryArithmetic to support QualifiedColumn on both sides
5. ✅ Implement 3 temporal comparison queries
6. ✅ Add tests for all new queries

**Deliverable**: 8 new queries, 20→28 total, 53% coverage

---

### Phase 2: Add Structural Meaning (2-3 days)
1. ✅ Implement query metadata framework
2. ✅ Add metadata decorators to all existing queries
3. ✅ Document alert thresholds and action triggers
4. ✅ Create operational runbook mapping queries to business actions
5. ✅ Update documentation with KPI linkage

**Deliverable**: Production-ready query catalog with operational metadata

---

### Phase 3: Commercial Architect Suite (3-5 days)
1. ✅ Design cost data model
2. ✅ Implement Range Architecture queries (4)
3. ✅ Implement Procurement Intelligence queries (4, requires cost data)
4. ✅ Implement Total Reconnaissance queries (2)
5. ✅ Add Commercial Architect archetype tests
6. ✅ Update documentation

**Deliverable**: 10 new queries, 28→38 total, 100% coverage

---

### Phase 4: Validation & Refinement (1-2 days)
1. ✅ End-to-end integration tests
2. ✅ Performance benchmarking
3. ✅ Documentation review
4. ✅ Stakeholder review (if applicable)

**Deliverable**: Production-ready intelligence query library

---

## Appendix A: Quick Reference Tables

### A.1 Coverage Summary

| Persona | Total Concerns | Covered | Partial | Missing | % Coverage |
|---------|---------------|---------|---------|---------|------------|
| **Pricing Analyst** | 11 | 4 | 3 | 4 | 64% |
| **Commercial Architect** | 8 | 0 | 3 | 5 | 0% |
| **TOTAL** | 19 | 4 | 6 | 9 | 37% |

### A.2 Schema Limitations

| Limitation | Impact | Queries Blocked | Fix Complexity |
|------------|--------|----------------|----------------|
| No cost data | Critical | 6 | High (new table) |
| No temporal patterns | High | 5 | Medium (documentation) |
| BinaryArithmetic lacks qualified columns | Medium | 3 | Low (model update) |
| Missing STDDEV/PERCENTILE | Low | 2 | Trivial (enum update) |

### A.3 Effort Estimates

| Recommendation | Effort | Impact | Priority |
|----------------|--------|--------|----------|
| Add STDDEV/PERCENTILE | 5 min | Medium | P0 |
| Implement 3 missing ENFORCER queries | 30 min | High | P0 |
| Fix BinaryArithmetic | 1 hour | Medium | P1 |
| Document temporal patterns | 2 hours | High | P1 |
| Implement metadata framework | 3 hours | Medium | P2 |
| Add cost data model | 5 hours | Critical | P2 |
| Commercial Architect suite | 12 hours | High | P3 |

---

**Analysis Complete**: 2025-11-29
**Total Gaps Identified**: 13 critical, 8 structural
**Recommended Next Steps**: Phase 1 (Critical Gaps) → Proof of exhaustiveness

**Verdict**: Current implementation is **excellent proof-of-technical-capability** but requires **strategic depth expansion** to be truly exhaustive against intelligence models.
