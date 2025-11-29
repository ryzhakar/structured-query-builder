# Complete Implementation Plan: All Phases
## Coverage Expansion from 37% → 100%

**Status**: IN PROGRESS
**Branch**: `claude/agent-handoff-docs-01Y7PptvJSU479UKKbXHBj3Q`
**Start Date**: 2025-11-29
**Approach**: Short granular commits with conventional commit messages

---

## Overview

**Current State**: 37% intelligence model coverage (7/19 concerns)
**Phase 1 Target**: 70% (13/19 concerns)
**Phase 2 Target**: 85% (16/19 concerns)
**Phase 3 Target**: 100% (19/19 concerns)

**Test Status**: 81 tests passing (80 pass, 1 skip)
**Existing Queries**: 15 bimodal pricing queries

---

## Phase 1: Critical Gaps (37% → 70%)
### Goal: Add 6 intelligence concerns with 10+ new queries

### 1.1 Schema Enhancements (30 min)

#### Task 1.1.1: Add Statistical Functions
**File**: `structured_query_builder/enums.py`
**Changes**:
```python
class AggregateFunc(str, Enum):
    count = "COUNT"
    sum = "SUM"
    avg = "AVG"
    min = "MIN"
    max = "MAX"
    count_distinct = "COUNT_DISTINCT"
    stddev = "STDDEV"              # NEW
    stddev_pop = "STDDEV_POP"      # NEW
    variance = "VARIANCE"          # NEW
    var_pop = "VAR_POP"           # NEW
```
**Commit**: `feat(enums): add statistical aggregate functions`

#### Task 1.1.2: Add updated_at Column
**File**: `structured_query_builder/enums.py`
**Note**: Already exists! (line 35: `created_at = "created_at"`)
**Action**: Verify `updated_at` is present, add if missing
**Commit**: `feat(enums): add updated_at temporal column` (if needed)

#### Task 1.1.3: Add Table Alias Support to BinaryArithmetic
**File**: `structured_query_builder/expressions.py`
**Changes**:
```python
class BinaryArithmetic(BaseModel):
    expr_type: Literal["binary_arithmetic"] = "binary_arithmetic"

    left_column: Optional[Column] = None
    left_table_alias: Optional[str] = None  # NEW
    left_value: Optional[float] = None

    operator: ArithmeticOp

    right_column: Optional[Column] = None
    right_table_alias: Optional[str] = None  # NEW
    right_value: Optional[float] = None

    alias: str
```
**Translator Update**: `structured_query_builder/translator.py`
**Commit**: `feat(expressions): add table_alias support to BinaryArithmetic`

#### Task 1.1.4: Update Translator for New Features
**File**: `structured_query_builder/translator.py`
**Changes**:
- Handle STDDEV/VARIANCE in aggregate translation
- Handle table_alias in BinaryArithmetic translation
**Commit**: `feat(translator): support statistical functions and table aliases`

#### Task 1.1.5: Add Tests for Schema Changes
**File**: `structured_query_builder/tests/test_models.py`
**File**: `structured_query_builder/tests/test_translator.py`
**Commit**: `test: add tests for statistical functions and table aliases`

---

### 1.2 ENFORCER Queries (45 min)

#### Query 16: MAP Violations (Unmatched)
**Coverage**: ENFORCER - MAP Policing (Unmatched)
**Business Value**: Detect MAP violations on ALL competitor products
**File**: `examples/phase1_queries.py` (new file)
**Commit**: `feat(queries): add MAP violations unmatched query`

#### Query 17: Premium Gap Analysis (Matched)
**Coverage**: ENFORCER - Brand Alignment (Matched)
**Business Value**: Quantify premium positioning vs competitor
**Requires**: BinaryArithmetic with table_alias
**Commit**: `feat(queries): add premium gap analysis query`

---

### 1.3 PREDATOR Queries (45 min)

#### Query 18: Supply Chain Failure Detector (Unmatched)
**Coverage**: PREDATOR - Monopoly Exploitation (Unmatched)
**Business Value**: Detect competitor stock drops by brand
**Pattern**: Temporal snapshot comparison
**Commit**: `feat(queries): add supply chain failure detector`

#### Query 19: Loss-Leader Hunter (Matched)
**Coverage**: PREDATOR - Bottom Feeding (Matched)
**Business Value**: Identify competitor loss-leaders to avoid
**Limitation**: Uses regular_price as cost proxy
**Commit**: `feat(queries): add loss-leader hunter query`

---

### 1.4 HISTORIAN Temporal Queries (1 hour)

#### Query 20: Category Price Snapshot
**Coverage**: HISTORIAN - Inflation Tracking (Unmatched)
**Business Value**: Track minimum price by category over time
**Pattern**: Snapshot + application-layer comparison
**Commit**: `feat(queries): add category price snapshot query`

#### Query 21: Promo Erosion Index (Unmatched)
**Coverage**: HISTORIAN - Promo Detection (Unmatched)
**Business Value**: Detect category-wide price drops
**Commit**: `feat(queries): add promo erosion index query`

#### Query 22: Assortment Churn Tracking (Unmatched)
**Coverage**: HISTORIAN - Churn Analysis (Unmatched)
**Business Value**: Track competitor assortment changes
**Commit**: `feat(queries): add assortment churn tracking query`

---

### 1.5 MERCENARY Advanced Query (30 min)

#### Query 23: Discount Depth Distribution (Unmatched)
**Coverage**: MERCENARY - Optical Dominance (Unmatched)
**Business Value**: Compare discount perception
**Commit**: `feat(queries): add discount depth distribution query`

---

### 1.6 Integration & Documentation (1 hour)

#### Task 1.6.1: Create Enhanced Examples File
**File**: `examples/phase1_queries.py`
**Content**: All 10 new queries (Q16-Q25)
**Commit**: `feat(examples): create phase 1 enhanced queries file`

#### Task 1.6.2: Update Tests
**File**: `structured_query_builder/tests/test_phase1_queries.py` (new)
**Content**: Test each new query for valid SQL generation
**Commit**: `test: add comprehensive tests for phase 1 queries`

#### Task 1.6.3: Update Documentation
**Files**:
- `README.md` - Update coverage percentage
- `docs/planning/PHASE_1_IMPLEMENTATION_PLAN.md` - Mark complete
**Commit**: `docs: update coverage metrics to 70%`

---

## Phase 2: Advanced Intelligence (70% → 85%)
### Goal: Add 3 intelligence concerns with metadata framework

### 2.1 Query Metadata Framework (2 hours)

**Purpose**: Enable operational deployment and filtering
**File**: `structured_query_builder/metadata.py` (new)

```python
class QueryMetadata(BaseModel):
    query_id: str
    archetype: str  # ENFORCER, PREDATOR, HISTORIAN, MERCENARY
    concern: str
    variant: str  # matched, unmatched
    business_value: str
    action_trigger: str
    data_freshness_requirement: str  # real-time, hourly, daily
    complexity_score: int  # 1-10
    cost_impact: str  # low, medium, high
```

**Commit**: `feat(metadata): add query metadata framework`

### 2.2 ARCHITECT Range Queries (1.5 hours)

#### Query 24: Commoditization Coefficient
**Coverage**: ARCHITECT - Assortment Overlap (Matched)
**Formula**: `COUNT(matches) / COUNT(total_my_assortment)`
**Commit**: `feat(queries): add commoditization coefficient query`

#### Query 25: Brand Weighting Fingerprint
**Coverage**: ARCHITECT - Assortment Overlap (Unmatched)
**Formula**: `Share_of_shelf % per brand (Us vs Them)`
**Commit**: `feat(queries): add brand weighting fingerprint query`

#### Query 26: Price Ladder Void Scanner
**Coverage**: ARCHITECT - Gap Analysis (Unmatched)
**Pattern**: Binning prices, finding empty buckets
**Commit**: `feat(queries): add price ladder void scanner`

---

## Phase 3: Complete Coverage (85% → 100%)
### Goal: Add 3 remaining intelligence concerns with cost model

### 3.1 Cost Data Model Extension (2 hours)

**Schema Changes**:
```python
# Add to Column enum
class Column(str, Enum):
    # ... existing ...
    net_cost = "net_cost"  # NEW
    landed_cost = "landed_cost"  # NEW
    map_floor = "map_floor"  # NEW
```

**New Table**:
```python
class Table(str, Enum):
    # ... existing ...
    cost_data = "cost_data"  # NEW: product_id, net_cost, landed_cost
```

**Commit**: `feat(schema): add cost data model support`

### 3.2 ARCHITECT Procurement Queries (1.5 hours)

#### Query 27: Vendor Fairness Audit
**Coverage**: ARCHITECT - Cost Model Validation (Matched)
**Formula**: `competitor_price < (my_net_cost * 1.05)`
**Requires**: cost_data table JOIN
**Commit**: `feat(queries): add vendor fairness audit query`

#### Query 28: Margin Potential Scanner
**Coverage**: ARCHITECT - Margin Potential Discovery (Matched)
**Formula**: `STDDEV(price_52weeks) is LOW AND (price - cost) > 40%`
**Requires**: Historical price data + cost
**Commit**: `feat(queries): add margin potential scanner query`

### 3.3 ARCHITECT Total Reconnaissance (1 hour)

#### Query 29: Inventory Velocity Detector
**Coverage**: ARCHITECT - Inventory Velocity Inference (Matched)
**Pattern**: Availability toggle frequency tracking
**Commit**: `feat(queries): add inventory velocity detector`

---

## Phase 4: Production Hardening (Optional)

### 4.1 Query Validation Framework
- Schema validation against real database
- Query performance profiling
- LLM output testing with Vertex AI

### 4.2 Query Library Organization
- Categorize by use case
- Add query templates
- Create query builder helpers

### 4.3 Integration Patterns
- REST API wrapper
- Batch query execution
- Result caching strategies

---

## Execution Schedule

### Week 1 (Phase 1): Critical Gaps
- Day 1: Schema enhancements (Tasks 1.1.1-1.1.5)
- Day 2: ENFORCER + PREDATOR queries (Tasks 1.2-1.3)
- Day 3: HISTORIAN + MERCENARY queries (Tasks 1.4-1.5)
- Day 4: Integration & testing (Task 1.6)

### Week 2 (Phase 2): Advanced Intelligence
- Day 1: Metadata framework (Task 2.1)
- Day 2: ARCHITECT range queries (Task 2.2)
- Day 3: Testing & documentation

### Week 3 (Phase 3): Complete Coverage
- Day 1: Cost data model (Task 3.1)
- Day 2: ARCHITECT procurement queries (Task 3.2)
- Day 3: Total reconnaissance + final testing (Task 3.3)

---

## Success Metrics

### Phase 1 Completion:
- ✅ 81+ tests passing (no regressions)
- ✅ 25+ queries total (15 existing + 10 new)
- ✅ 70% intelligence model coverage (13/19 concerns)
- ✅ All schema enhancements tested
- ✅ Documentation updated

### Phase 2 Completion:
- ✅ Metadata framework implemented
- ✅ 28+ queries total
- ✅ 85% coverage (16/19 concerns)

### Phase 3 Completion:
- ✅ Cost model integrated
- ✅ 29+ queries total
- ✅ 100% coverage (19/19 concerns)
- ✅ All intelligence requirements met

---

## Commit Message Convention

Following conventional commits:
- `feat(scope): description` - New features
- `fix(scope): description` - Bug fixes
- `test(scope): description` - Test additions
- `docs(scope): description` - Documentation
- `refactor(scope): description` - Code refactoring

**Examples**:
- `feat(enums): add statistical aggregate functions`
- `feat(queries): add MAP violations unmatched query`
- `test: add comprehensive tests for phase 1 queries`
- `docs: update coverage metrics to 70%`

---

## Proof-of-Work Standards

**NEVER claim complete without**:
1. Runnable code in examples/
2. Passing tests in tests/
3. Valid SQL generation verified
4. Committed to repository

**ALWAYS document**:
1. What works (with evidence)
2. What doesn't work (limitations)
3. What's untested (gaps)
4. Coverage percentages (actual math)

---

**End of Complete Implementation Plan**
