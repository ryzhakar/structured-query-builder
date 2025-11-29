# Agent Handoff: Query Quality Remediation

## Context

**Codebase**: Pydantic-based SQL query builder for LLM structured outputs
**Data Model**: Historical competitive pricing data with `updated_at` timestamps
**Current State**: 29 queries, 101 tests, 19/19 intelligence concerns addressed
**Quality Gap**: Alignment audit (`docs/analysis/QUERY_ALIGNMENT_EVALUATION.md`) shows 47% of queries deliver partial/degraded intelligence

## Data Schema

```yaml
product_offers:
  - id, title, brand, category, vendor
  - markdown_price, regular_price, availability
  - updated_at  # Historical timestamps for temporal queries

exact_matches:
  - source_id (our product)
  - target_id (competitor product)
```

**Key Capability**: Data IS historical - can do temporal comparisons, window functions, period-over-period analysis

## Schema Features Available

✅ Window functions: RANK, LAG, LEAD, ROW_NUMBER
✅ Aggregates: COUNT, SUM, AVG, MIN, MAX, STDDEV, VARIANCE
✅ CASE expressions for conditional logic
✅ Self-joins for temporal comparison
✅ Column-to-column comparisons
✅ Table aliases for multi-table operations

## Tasks

### 1. Fix Broken Temporal Queries

#### Q17: Premium Gap Analysis
**Issue**: Calculates `AVG(my) - AVG(comp)` instead of `AVG(my - comp)`
**Fix**: Support nested arithmetic in aggregate expressions
**Test**: Verify math matches spec requirement

#### Q18: Supply Chain Failure Detector
**Issue**: Snapshot count, should detect "sudden drops"
**Fix**: Use LAG window function to compare period-over-period
**Test**: Query detects 40%+ drop in competitor inventory

#### Q20: Category Price Snapshot
**Issue**: Single time window, should show price increase over period
**Fix**: Self-join comparing T vs T-6months
**Test**: Returns period-over-period delta

#### Q22: Brand Presence Tracking
**Issue**: Snapshot count, should detect brand volume drops
**Fix**: LAG window to compare current vs previous week
**Test**: Detects 40% drop in brand count

#### Q28: Safe Haven Scanner
**Issue**: STDDEV across products (cross-sectional), should be temporal volatility
**Fix**: Window function STDDEV over time partition (52-week rolling)
**Test**: Returns price stability over time not across products

#### Q29: Inventory Velocity Detector
**Issue**: Shows availability snapshot, should detect "frequent toggles"
**Fix**: LAG to count availability state changes (True→False→True)
**Test**: Identifies products with 3+ stockout cycles

### 2. Add Missing Schema Features

#### Percentile Functions
**Add**: `PERCENTILE_CONT`, `PERCENTILE_DISC` to `AggregateFunc` enum
**Add**: `percentile: Optional[float]` parameter to `AggregateExpr`
**Test**: Query can calculate 10th percentile price

#### Nested Arithmetic in Aggregates
**Add**: `arithmetic_input: Optional[BinaryArithmetic]` to `AggregateExpr`
**Update**: Translator to handle `AVG(col1 - col2)` pattern
**Test**: Q17 calculates average of differences correctly

#### Price Binning Support
**Verify**: `CaseExpr` works for price bucket assignment
**Test**: Can group by price ranges ($0-50, $50-100, etc.)

### 3. Implement Missing Queries

#### Q03: Category Histogram (ENFORCER)
**Pattern**: CASE for price binning + GROUP BY bucket + COUNT
**Output**: Count of offers per price bin, grouped by category/vendor
**Test**: Shows distribution shape (e.g., "cluster at $20")

#### Q06: Cluster Floor Check (PREDATOR)
**Pattern**: PERCENTILE_CONT(0.1) for 10th percentile price
**Output**: Products priced below market 10th percentile
**Test**: Identifies outlier low prices

#### Q08: Slash-and-Burn Alert (HISTORIAN)
**Pattern**: LAG for overnight price comparison, filter >15% drop
**Output**: Count of products with sudden price cuts
**Test**: Detects promotional campaigns

#### Q09: Minimum Viable Price Lift (HISTORIAN)
**Pattern**: MIN(price) grouped by month + category
**Output**: Time series of category floor prices
**Test**: Shows price floor increasing over time

#### Q10: Assortment Rotation Check (HISTORIAN)
**Pattern**: LEFT JOIN T-7days to T-now, NULL check for delisted products
**Output**: Product IDs removed from competitor catalog
**Test**: Identifies discontinued items

#### Q13: Ghost Inventory Check (ARCHITECT)
**Pattern**: Window SUM of stockouts over 4-week rolling window
**Output**: Products out-of-stock for 4+ consecutive weeks
**Test**: Finds persistent supply failures

#### Q14: Global Floor Stress Test (ARCHITECT)
**Pattern**: MIN(competitor_price) GROUP BY brand+category
**Output**: Lowest market price per brand/category
**Test**: Shows market floor for vendor negotiation

### 4. Complete Partial Queries

#### Q24: Commoditization Coefficient
**Add**: Ratio calculation `COUNT(matches) / COUNT(total)` using BinaryArithmetic
**Test**: Returns percentage not raw counts

#### Q25: Brand Weighting Fingerprint
**Add**: Percentage calculation using window SUM for total
**Test**: Returns share-of-shelf % not raw counts

#### Q26: Price Ladder Void Scanner
**Replace**: Statistics with CASE binning to show actual voids
**Test**: Identifies missing price ranges (e.g., "zero offers $50-80")

## Acceptance Criteria

### Per Query
- [ ] Matches intelligence model spec exactly (see `intelligence_models/*.yaml`)
- [ ] Generates valid SQL via translator
- [ ] Has comprehensive test coverage
- [ ] Committed to repository
- [ ] No "requires application layer" gaps

### Per Task Category
- [ ] All 6 temporal queries use historical data properly
- [ ] All 3 schema features added and tested
- [ ] All 7 missing queries implemented
- [ ] All 3 partial queries completed

### Overall
- [ ] 101+ tests passing (add ~20 new tests)
- [ ] Zero mathematical errors
- [ ] Zero "partial implementation" flags
- [ ] All queries self-contained for LLM structured outputs

## Implementation Order

1. **Schema features** (enables everything else)
2. **Fix Q17** (blocking for ENFORCER archetype)
3. **Temporal queries** (6 queries, highest impact)
4. **Missing queries** (7 queries, coverage completion)
5. **Partial queries** (3 queries, quality cleanup)

## Essential Files

**Specs**: `intelligence_models/*.yaml` - exact requirements
**Gap Analysis**: `docs/analysis/QUERY_ALIGNMENT_EVALUATION.md` - detailed issues
**Examples**: `examples/phase*_queries.py` - implementation patterns
**Tests**: `structured_query_builder/tests/test_phase*_queries.py` - test patterns
**Schema**: `structured_query_builder/enums.py`, `expressions.py` - models to enhance

## Output Format

**Commits**: Granular, conventional format (`feat:`, `fix:`, `test:`)
**Tests**: One test class per concern, descriptive test names
**Queries**: Pydantic models in `examples/`, function per query
**Documentation**: Update README metrics when complete

## Success Metric

**Before**: 34% good, 38% partial, 28% gap
**Target**: 100% good, 0% partial, 0% gap

All 29 queries deliver spec-compliant intelligence.
