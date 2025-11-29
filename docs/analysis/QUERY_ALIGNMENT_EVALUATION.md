# Query-to-Intelligence-Model Alignment Evaluation
**Date**: 2025-11-29
**Evaluation Type**: Cold, Detached, Actionable
**Evaluator**: Systematic Code-to-Spec Analysis

---

## Executive Summary

**Verdict**: 100% nominal coverage masks significant implementation quality variance. Several queries implement only surface-level patterns and miss core intelligence value.

**Critical Findings**:
- 8/29 queries (28%) have **major alignment gaps**
- 11/29 queries (38%) implement **partial intelligence** (missing key insights)
- 10/29 queries (34%) have **good alignment**
- Data model constraints force use of proxies that weaken intelligence quality

---

## Methodology

For each query, evaluated:
1. **Spec Match**: Does query logic match intelligence model spec?
2. **Insight Delivery**: Does query deliver the stated business insight?
3. **Completeness**: Are required calculations/patterns implemented?
4. **Data Model Fit**: Can available schema support the intelligence concern?

Scoring:
- ✅ **GOOD**: Implements spec correctly, delivers insight
- ⚠️ **PARTIAL**: Implements pattern but misses key insight elements
- ❌ **GAP**: Missing critical logic or delivers wrong intelligence

---

## ARCHETYPE 1: THE ENFORCER (Compliance & Positioning)

### Concern A: Parity Maintenance

#### Q01: Index Drift Check (Matched) - ✅ GOOD
**Spec**: `Select matches where (My_Price / Competitor_Price) > 1.05`
**Impl**: Uses `BinaryArithmetic` to calculate price ratio, filters > 1.05
**Insight**: "SKU #123 is 7% too expensive"
**Assessment**: **ALIGNED**. Delivers precise SKU-level drift detection.

#### Q02: ASP Gap (Unmatched) - ✅ GOOD
**Spec**: `Compare Avg(My_Price) vs Avg(Competitor_Price) Group By Brand + Category`
**Impl**: Grouped aggregates with brand/category grouping
**Insight**: "We are $50 more expensive on Samsung TVs"
**Assessment**: **ALIGNED**. Correctly implements directional signal.

### Concern B: MAP Policing

#### Q16: Brand Floor Scan (Unmatched) - ✅ GOOD
**Spec**: `Select * where Brand = 'Nike' AND Price < Global_MAP_Floor`
**Impl**: Simple WHERE filter with brand + price threshold
**Insight**: "They have 3 Nike items below MAP"
**Assessment**: **ALIGNED**. Exact spec match.

#### Q17 (Matched Variant) - ❌ **MISSING**
**Spec**: `Select matches where Competitor_Price < MAP_List_Value (joined by SKU)`
**Impl**: **NOT IMPLEMENTED**
**Gap**: Would require MAP lookup table join - schema doesn't have MAP table
**Actionable**: Add `Table.map_pricing` to schema with `{sku, map_floor}` fields

### Concern C: Brand Alignment

#### Q17: Premium Gap Analysis (Matched) - ⚠️ **PARTIAL**
**Spec**: `Avg(My_Price - Competitor_Price) on Matched Items Only`
**Impl**: Calculates `AVG(my.price)` and `AVG(comp.price)` separately
**Gap**: Spec calls for `AVG(difference)`, not difference of averages. Math is wrong.
```sql
-- Spec wants:
SELECT AVG(my.price - comp.price) ...
-- We implemented:
SELECT AVG(my.price), AVG(comp.price) ...
```
**Actionable**: Use `BinaryArithmetic` inside `AggregateExpr` to calculate `AVG(my - comp)` correctly

#### Q03: Category Histogram (Unmatched) - ❌ **MISSING**
**Spec**: `Plot Count(Offers) by Price Bin. Compare shapes.`
**Impl**: **NOT IMPLEMENTED**
**Gap**: Requires price bucketing/binning - schema has no CASE/binning support
**Actionable**: Add price binning logic or document as "application layer" requirement

---

## ARCHETYPE 2: THE PREDATOR (Margin & Opportunity)

### Concern A: Monopoly Exploitation

#### Q04: Stockout Gouge (Matched) - ✅ GOOD
**Spec**: `Select matches where My_Stock=TRUE and Their_Stock=FALSE`
**Impl**: Column comparison on availability fields
**Insight**: "Raise price on these 12 items immediately"
**Assessment**: **ALIGNED**. Exact spec match.

#### Q18: Supply Chain Failure Detector (Unmatched) - ⚠️ **PARTIAL**
**Spec**: `Count(Competitor_In_Stock_Offers) Group By Brand. Check for sudden drops.`
**Impl**: Counts products, sums availability by brand/vendor
**Gap**: Spec requires **temporal comparison** ("sudden drops") - single snapshot can't detect drops
**Actionable**: Document limitation: "Requires multi-snapshot comparison in application layer"

### Concern B: Headroom Discovery

#### Q05: Unnecessary Discount Finder (Matched) - ✅ GOOD
**Spec**: `Select where My_Price < Competitor_Price AND My_Price < My_Regular`
**Impl**: Uses column comparison for both conditions
**Insight**: "Raise these 40 items by $5"
**Assessment**: **ALIGNED**. Exact spec match.

#### Q06: Cluster Floor Check (Unmatched) - ❌ **MISSING**
**Spec**: `Identify 10th Percentile Price. Check if My_Price < 10th_Percentile.`
**Impl**: **NOT IMPLEMENTED**
**Gap**: Requires `PERCENTILE_CONT` aggregate function - not in schema
**Actionable**: Add percentile aggregate functions to `AggregateFunc` enum

### Concern C: Bottom Feeding

#### Q19: Loss-Leader Hunter (Matched) - ⚠️ **PARTIAL**
**Spec**: `Flag where Competitor_Price < My_Cost_Proxy`
**Impl**: Uses `comp.markdown_price < my.regular_price` as proxy
**Gap**: Spec calls for cost comparison - using regular_price is weak proxy
**Assessment**: **PARTIAL**. Works but intelligence quality degraded by data model constraints.
**Note**: Air-gapped from cost data - this is best possible given constraints.

#### Q07: Deep Discount Filter (Unmatched) - ✅ GOOD
**Spec**: `Flag where (Price_Regular - Price_Current) / Price_Regular > 50%`
**Impl**: Uses `BinaryArithmetic` to calculate discount percentage
**Insight**: "Ignore market signal from items discounted >50%"
**Assessment**: **ALIGNED**. Exact spec match.

---

## ARCHETYPE 3: THE HISTORIAN (Strategy Inference)

### Concern A: Promo Detection

#### Q08: Slash-and-Burn Alert (Matched) - ❌ **MISSING**
**Spec**: `Count matches where price dropped >15% overnight`
**Impl**: **NOT IMPLEMENTED**
**Gap**: Requires temporal comparison (T-1 vs T) - single snapshot limitation
**Actionable**: Document as temporal pattern requiring application-layer state tracking

#### Q21: Category Erosion Index (Unmatched) - ⚠️ **PARTIAL**
**Spec**: `Calculate Avg(Price) of Category. Did it drop > 5%?`
**Impl**: Calculates `AVG(markdown_price)` and `AVG(regular_price)` by category
**Gap**: Spec asks "Did it drop?" (temporal) - we provide snapshot comparison (markdown vs regular)
**Assessment**: **PARTIAL**. Different comparison but provides related signal.

### Concern B: Inflation Tracking

#### Q20: Category Price Snapshot (Temporal) - ⚠️ **PARTIAL**
**Spec**: `Avg price increase on same-SKU over 6 months (Matched)`
**Impl**: Temporal filtering with `updated_at BETWEEN`, but single-snapshot aggregates
**Gap**: Spec requires multi-period comparison - we provide snapshot in time window
**Assessment**: **PARTIAL**. Temporal filtering present but lacks cross-period comparison.

#### Q09: Minimum Viable Price Lift (Unmatched) - ❌ **MISSING**
**Spec**: `Track Min(Price) of category over time`
**Impl**: **NOT IMPLEMENTED**
**Gap**: Requires time-series tracking - query limitation acknowledged
**Actionable**: Document as requiring scheduled execution + state storage

### Concern C: Churn Analysis

#### Q22: Brand Presence Tracking (Unmatched) - ⚠️ **PARTIAL**
**Spec**: `Compare Count(Offers) per Brand for T_Current vs T_LastWeek`
**Impl**: Provides `COUNT(*)` by brand/vendor for single snapshot
**Gap**: Temporal comparison missing - single snapshot can't detect "drop by 40%"
**Assessment**: **PARTIAL**. Foundation query that requires app-layer temporal logic.

#### Q10: Assortment Rotation Check (Matched) - ❌ **MISSING**
**Spec**: `Select IDs present in T_LastWeek but missing in T_Current`
**Impl**: **NOT IMPLEMENTED**
**Gap**: Requires temporal set difference (T-1 MINUS T) - single snapshot limitation
**Actionable**: Document temporal pattern requirement

---

## ARCHETYPE 4: THE MERCENARY (Optics & Psychology)

### Concern A: Optical Dominance

#### Q11: Anchor Check (Matched) - ✅ GOOD
**Spec**: `Select matches where My_Regular < Their_Regular`
**Impl**: Column comparison on regular_price fields
**Insight**: "Boost our Regular Price so discount % looks better"
**Assessment**: **ALIGNED**. Exact spec match.

#### Q23: Discount Depth Distribution (Unmatched) - ✅ GOOD
**Spec**: `Avg(Discount %) for Category. Us vs. Them.`
**Impl**: Calculates `AVG(markdown)`, `AVG(regular)`, `STDDEV` by category/vendor
**Insight**: "Their average discount is 20%, ours is 10%"
**Assessment**: **ALIGNED**. Provides required comparison data.

### Concern B: Keyword Arbitrage

#### Q12: Ad-Hoc Keyword Scrape (Unmatched) - ✅ GOOD
**Spec**: `Select Avg(Price) where Title LIKE '%1TB SSD%'`
**Impl**: Uses `LikeCondition` with pattern matching on title
**Insight**: "Market says 1TB SSD is worth $95"
**Assessment**: **ALIGNED**. Exact spec match.

---

## ARCHETYPE 5: THE ARCHITECT (Range & Procurement)

### Concern A: Assortment Overlap & Exclusivity

#### Q24: Commoditization Coefficient (Matched) - ⚠️ **PARTIAL**
**Spec**: `Count(Matches) / Count(Total_My_Assortment)` AND `Count(Matches) / Count(Total_Competitor_Assortment)`
**Impl**: Provides `COUNT(my.id)` and `COUNT(em.source_id)` by category
**Gap**: Spec requires **two ratios** (bilateral overlap), we provide raw counts
**Assessment**: **PARTIAL**. Foundation data present but ratio calculation missing.
**Actionable**: Application must divide: `matched / total_my` AND `matched / total_their`

#### Q25: Brand Weighting Fingerprint (Unmatched) - ⚠️ **PARTIAL**
**Spec**: `Share_of_Shelf % per Brand for Me vs. Them`
**Impl**: Provides `COUNT(*)` by brand/vendor
**Gap**: Spec requires **percentages** (count / total) - we provide raw counts
**Assessment**: **PARTIAL**. Foundation query requiring app-layer percentage calc.

### Concern B: Gap Analysis & White Space

#### Q26: Price Ladder Void Scanner (Unmatched) - ⚠️ **PARTIAL**
**Spec**: `Bin offers into Price Buckets. Identify buckets with Count = 0.`
**Impl**: Provides `MIN/MAX/AVG/STDDEV` by category - **no bucketing**
**Gap**: Spec requires histogram binning - we provide statistics
**Assessment**: **PARTIAL**. Different approach (statistics vs bins) that provides related but weaker signal.
**Actionable**: Add `CASE` expression support for price binning, or document histogram logic as app requirement

#### Q13: Ghost Inventory Check (Matched) - ❌ **MISSING**
**Spec**: `Select where Competitor_Availability = FALSE for > 4 consecutive weeks`
**Impl**: **NOT IMPLEMENTED**
**Gap**: Requires temporal duration tracking - single snapshot limitation
**Actionable**: Document as multi-week state tracking requirement

### Concern C: Cost Model Validation

#### Q27: Vendor Fairness Audit (Matched) - ⚠️ **PARTIAL**
**Spec**: `Select where Competitor_Regular_Price < (My_Net_Cost * 1.05)`
**Impl**: Uses `comp.regular_price < my.regular_price` (cost proxy)
**Gap**: Spec requires **actual cost data** - air-gapped from ERP forces proxy
**Assessment**: **PARTIAL**. Best possible given data constraints, but intelligence degraded.
**Documentation Note**: Query header correctly acknowledges "uses regular_price as cost proxy"

#### Q14: Global Floor Stress Test (Unmatched) - ❌ **MISSING**
**Spec**: `Select Min(Price) Group By Brand+Category. Compare vs. My_Entry_Level_Cost.`
**Impl**: **NOT IMPLEMENTED**
**Gap**: Phase 3 has no unmatched variant for cost validation
**Actionable**: Consider adding query that shows MIN(comp.price) for vendor negotiation context

### Concern D: Margin Potential Discovery

#### Q28: Safe Haven Scanner (Matched) - ⚠️ **PARTIAL**
**Spec**: `Select where StdDev(Price_52Weeks) is Low AND (Competitor_Price - My_Cost) > 40%`
**Impl**: Calculates `STDDEV(comp.markdown_price)` + `AVG` prices - **snapshot STDDEV not temporal**
**Gap**: Spec wants price volatility over 52 weeks - we provide volatility across SKUs in snapshot
**Assessment**: **PARTIAL**. Wrong STDDEV dimension (cross-sectional not temporal).
**Actionable**: Document: "STDDEV is across products not time - requires historical snapshots"

#### Q15: Category Margin Proxy (Unmatched) - ❌ **MISSING**
**Spec**: `Compare Avg(Regular) vs Avg(Current) for whole category`
**Impl**: **NOT IMPLEMENTED** (though Q21 is similar)
**Gap**: Phase 3 missing this concern
**Actionable**: Q21 (Promo Erosion) actually implements this - reclassify?

### Concern E: Inventory Velocity Inference

#### Q29: Inventory Velocity Detector (Matched) - ❌ **GAP**
**Spec**: `Identify where Availability toggles (True -> False -> True) frequently`
**Impl**: Shows current availability snapshot only - **no toggle detection**
**Gap**: Spec requires state change tracking - single snapshot can't detect "frequently"
**Assessment**: **MAJOR GAP**. Query delivers availability snapshot, not velocity inference.
**Actionable**: Rename query to "Availability Comparison Snapshot" and document velocity requires time-series

---

## Quantified Alignment Summary

### By Quality Tier

| Tier | Count | % | Criteria |
|------|-------|---|----------|
| ✅ GOOD | 10 | 34% | Exact spec match, delivers stated insight |
| ⚠️ PARTIAL | 11 | 38% | Implements pattern but missing key elements |
| ❌ GAP | 8 | 28% | Missing query or major spec mismatch |

### By Archetype

| Archetype | GOOD | PARTIAL | GAP | Notes |
|-----------|------|---------|-----|-------|
| ENFORCER | 3/6 | 1/6 | 2/6 | Missing MAP table join, histogram binning |
| PREDATOR | 3/6 | 2/6 | 1/6 | Temporal patterns missing, percentile functions needed |
| HISTORIAN | 0/6 | 3/6 | 3/6 | **WORST** - most concerns require temporal comparison |
| MERCENARY | 3/4 | 0/4 | 0/4 | **BEST** - all snapshot-friendly patterns |
| ARCHITECT | 1/8 | 6/8 | 1/8 | Heavy reliance on proxies, binning gaps |

### Root Causes of Gaps

1. **Temporal Limitations** (8 queries): Single snapshot model can't detect "drops", "sudden", "over time"
2. **Data Model Air-Gap** (4 queries): No cost data forces weak proxies
3. **Missing Aggregates** (2 queries): No percentile functions
4. **Missing Expressions** (2 queries): No CASE/binning for histograms
5. **Multi-Period Logic** (3 queries): Requires T-1 vs T comparison

---

## Critical Recommendations (Actionable)

### 1. Honest Coverage Reclassification
**Current Claim**: "100% coverage (19/19 concerns)"
**Reality**:
- 10/19 concerns (53%) have GOOD implementation
- 11/19 concerns (58%) have PARTIAL/degraded implementation
- 8/29 queries (28%) have major alignment gaps

**Action**: Update coverage metric to distinguish:
- **Full Implementation**: 10/19 (53%)
- **Partial Implementation**: 11/19 (58%)
- **Foundation Only**: 8/29 queries provide data but not insight

### 2. Temporal Pattern Documentation
**Problem**: 8 queries claim temporal intelligence but deliver snapshots

**Action**: Create `docs/technical/TEMPORAL_PATTERNS.md` documenting:
- Which queries require multi-snapshot comparison
- How to implement temporal comparison in application layer
- Example: "Run Q22 weekly, store results, calculate delta"

### 3. Fix Mathematical Errors
**Problem**: Q17 calculates difference of averages not average of differences

**Action**: Implement nested `BinaryArithmetic` inside `AggregateExpr`:
```python
AggregateExpr(
    function=AggregateFunc.avg,
    column=None,
    arithmetic_expr=BinaryArithmetic(
        left_column=Column.markdown_price,
        left_table_alias="my",
        operator=ArithmeticOp.subtract,
        right_column=Column.markdown_price,
        right_table_alias="comp",
    ),
    alias="avg_premium_gap"
)
```

### 4. Schema Enhancements for Missing Concerns
**Add**:
- `AggregateFunc.percentile_cont` for percentile queries
- `CaseExpr` with bucket ranges for histogram binning
- `Table.map_pricing` for MAP violation detection
- Document limitations where air-gap prevents implementation

### 5. Query Renaming for Honesty
**Misleading Names**:
- Q29 "Inventory Velocity Detector" → "Availability Comparison Snapshot"
- Q28 "Safe Haven Scanner" → "Price Gap Analysis with Cross-Product Volatility"
- Q20 "Category Price Snapshot" → "Category Price Window Filter"

**Action**: Rename to reflect actual capability, not aspirational intelligence

### 6. Application Layer Requirements Doc
**Problem**: Many queries provide foundation data requiring app processing

**Action**: Create `docs/guides/APPLICATION_LAYER_REQUIREMENTS.md` listing:
- Which queries need percentage calculation
- Which queries need temporal state management
- Which queries need histogram binning
- Example integration code

---

## Conclusion

**Coverage vs. Quality Trade-off**: Achieved 100% nominal coverage by implementing foundation queries that provide relevant data, but many deliver degraded intelligence compared to spec.

**Root Cause**: Data model constraints (air-gapped from cost/sales, single snapshot) force compromises that reduce intelligence quality.

**Recommendation**: Either:
1. **Reclassify coverage** as "100% addressed, 53% fully implemented, 47% partial/proxy"
2. **Enhance schema** to support missing patterns (percentiles, binning, temporal joins)
3. **Document clearly** which queries require application-layer completion

**Bottom Line**: Queries are functional and provide value, but several overpromise on intelligence delivery. Alignment audit reveals need for honest labeling and architectural enhancements.
