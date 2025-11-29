# Unique Value Analysis - Poisoned Files
**Date**: 2025-11-29
**Purpose**: Determine what would be LOST if we delete poisoned files
**Method**: Deep reading + comparison with healed docs

---

## Methodology

For each poisoned file:
1. Extract sections/content
2. Check if equivalent exists in healed docs (README, GUIDE, audit docs)
3. Identify UNIQUE value (if any)
4. Recommendation: PRESERVE, MIGRATE, or DELETE

---

## Analysis

### 🔴 archive/deprecated-claims/README.md

**Size**: 409 lines (36 code blocks)

**Content Overview**:
- Quick start examples
- Architecture explanation (clause-based, discriminated unions, depth control)
- Supported SQL features list
- Use case descriptions for pricing analysts

**Checking against healed docs**...
📊 Comparing sections...

**Old README sections**:
## Overview
## Installation
## Quick Start
## Supported SQL Features
## Architecture
## Use Cases
## Testing
## Schema Customization
## Performance
## Limitations
## Examples
## Documentation
## Contributing
## License
## References

**New README sections**:
## ⚠️ IMPORTANT: Documentation Restructuring Notice
## What This Is
## Quick Start
## What Actually Works ✅
## Known Limitations ⚠️
## Architecture
## Documentation
## Project Structure
## Contributing
## Honest Assessment
## History
## License

**Comparison Result**:
- ✅ Architecture explanation: COVERED in new README
- ✅ Quick start: COVERED in new README
- ✅ SQL features: COVERED in new README
- ⚠️ **Detailed use case examples**: More detailed in old README

**Unique Value**:
- Pricing analyst workflow examples (4-5 detailed scenarios)
- More code examples for manual query construction

**Recommendation**: 📝 MIGRATE use case examples to GUIDE.md, then DELETE

---

### 🔴 archive/deprecated-claims/IMPLEMENTATION_SUMMARY.md

**Size**: 391 lines (12 code blocks)

**Content Overview**:

**Design Decisions & Rationale section**:
## Design Decisions & Rationale

### 1. Clause-Based Architecture
**Decision**: Structure models to mirror SQL clauses
**Rationale**:
- Natural mental model for SQL users
- Direct translation path (each clause → SQL clause)
- Clear separation of concerns
- LLMs understand structure better

### 2. No Recursive Types
**Decision**: Use explicit L0/L1 depth models
**Rationale**:
- LLM structured outputs can't handle recursion
- Prevents infinite nesting issues
- Still covers 95%+ of real-world queries
- Clear depth limits improve reliability

### 3. Discriminated Unions
**Decision**: Use `expr_type` literal field
**Rationale**:
- LLMs need clear type markers
- Prevents ambiguity in union generation
- Better error messages
- Industry best practice for structured outputs

### 4. Enum-Based Schema
**Decision**: Tables, columns, operators as enums
**Rationale**:
- Self-documenting
- Prevents typos and invalid references
- Clear schema for LLMs
- Type-safe at generation time

### 5. CTEs Excluded
**Decision**: No CTE support, use subqueries
**Rationale**:
- CTEs and subqueries achieve same goals
- Multiple approaches increase complexity
- Subqueries more familiar to analysts
- Simpler schema = fewer LLM errors

---

## Production Readiness Checklist

**Checking against healed docs**:
- Design decisions: Covered in GUIDE.md ✅
- Architecture: Covered in README.md ✅
- Performance metrics: **NOT in healed docs** ⚠️
- Project statistics: **NOT in healed docs** ⚠️

**Unique Value**:
1. **Performance benchmarks** (model construction, translation times)
2. **Project statistics** (LOC, model count, test count)
3. **Design rationale** (why clause-based, why no CTEs, etc.)

**Recommendation**: 📝 MIGRATE performance metrics and design rationale to GUIDE.md, then DELETE

---

### 🔴 archive/deprecated-claims/VERTEXAI_FINDINGS.md

**Size**: 460 lines (20 code blocks)

**Vertex AI Specific Quirks & Best Practices**:
## Vertex AI Specific Quirks & Best Practices

### Quirk 1: Union Type Ordering

**Observation**: When generating discriminated unions, LLMs may prefer simpler types first.

**Best Practice**:
- Put most common expression types (ColumnExpr, AggregateExpr) first in prompts
- Use clear system messages explaining available expression types

**Example Prompt**:
```
You are a SQL query builder. Available expression types:
- column: Simple column selection
- aggregate: COUNT, SUM, AVG, MIN, MAX
- binary_arithmetic: Two-operand math (price - discount)
- compound_arithmetic: Three-operand math ((a - b) / c)
- window: RANK, ROW_NUMBER, LAG, LEAD
- case: Conditional expressions
```

### Quirk 2: Optional Field Handling

**Observation**: LLMs may omit optional fields entirely vs. setting to None.

**Impact**: No issue - Pydantic handles both correctly

**Best Practice**:
- Always use `Optional[]` with default `None`
- Don't rely on optional fields in validation logic

### Quirk 3: Enum Value Generation

**Observation**: LLMs reliably generate correct enum values when schema is clear.

**Best Practice**:
- Keep enum names descriptive (`ComparisonOp.eq` vs `Op.EQ`)
- Use string enums with sensible values (`"="` not `"EQUALS"`)

### Quirk 4: Field Descriptions Matter

**Observation**: Field descriptions significantly improve LLM accuracy.

**Impact**: Critical for complex fields like WindowExpr

**Best Practice**:
- Every field must have a description
- Include examples in descriptions for complex types
- Explain relationships between fields

---

## Testing Results

**Checking against healed docs**:
- Vertex AI quirks: **NOT in healed docs** ⚠️
- Best practices for LLM prompting: **NOT in healed docs** ⚠️
- Union type ordering advice: **UNIQUE** ⚠️
- Field description importance: **UNIQUE** ⚠️

**Unique Value**:
1. **Vertex AI specific quirks** (4 documented quirks with examples)
2. **LLM prompting best practices** (how to use discriminated unions effectively)
3. **Practical recommendations** for schema usage with Gemini

**Recommendation**: 📝 MIGRATE Vertex AI quirks to GUIDE.md or technical docs, then DELETE

---

### 🔴 archive/deprecated-claims/PRICING_ANALYST_QUERIES.md

**Size**: 1,085 lines (40 code blocks)

**Checking query content**:
Number of queries documented: 10

## Query 1: Competitive Price Gap Analysis

### Business Context

**When**: Daily morning routine, Monday-Friday
**Why**: Identify where we're overpriced vs Amazon (our main competitor)
**Business Impact**: Drives immediate price adjustments to stay competitive
**Typical User**: Pricing Manager reviewing overnight competitor price changes

### Natural Language Request

> "Show me all products where our regular price is higher than Amazon's for the same product, sorted by the price difference (biggest gaps first). Include the product title and both prices so I can decide which ones to adjust."

### Natural SQL

```sql
SELECT
    ours.title AS product_name,
    ours.regular_price AS our_price,
    amazon.regular_price AS amazon_price,
    (ours.regular_price - amazon.regular_price) AS price_gap,
    ((ours.regular_price - amazon.regular_price) / ours.regular_price * 100) AS price_gap_percent
FROM product_offers AS ours
INNER JOIN id_mapping ON ours.id = id_mapping.our_product_id
INNER JOIN product_offers AS amazon ON id_mapping.their_product_id = amazon.id
WHERE
    ours.vendor = 'our_company'
    AND amazon.vendor = 'amazon'
    AND ours.regular_price > amazon.regular_price
ORDER BY price_gap DESC
LIMIT 50;
```

**Why This SQL**:
- Self-join pattern: Same table joined twice with different aliases
- id_mapping table: Links our products to competitors' equivalent products
- Filter before compare: vendor = conditions ensure correct comparison
- Computed columns: Both absolute (price_gap) and relative (price_gap_percent)
- Business-relevant ordering: Biggest problems first
- Practical limit: 50 items = manageable daily action list

### Pydantic Model

```python
Query(
    select=[
        ColumnExpr(
            source=QualifiedColumn(table_alias="ours", column=Column.title),
            alias="product_name"
        ),
        ColumnExpr(
            source=QualifiedColumn(table_alias="ours", column=Column.regular_price),
            alias="our_price"
        ),
        ColumnExpr(
            source=QualifiedColumn(table_alias="amazon", column=Column.regular_price),
            alias="amazon_price"
        ),
        BinaryArithmetic(
            left_column=Column.regular_price,  # Needs table qualification in translator

**Comparing with working examples**:
- examples/bimodal_pricing_queries.py has 15 working queries ✅
- Old doc has 10 documented queries with business context
- Old doc has natural language → SQL → Pydantic progression

**Unique Value**:
1. **Business context** for each query (when, why, business impact, typical user)
2. **Natural language requests** (what analyst would actually say)
3. **Natural SQL** (how expert would write it manually)
4. **Progressive complexity** (shows thought process from request to implementation)

**Recommendation**: 📝 MIGRATE business context to examples file docstrings, DELETE doc
(Or keep as reference for "how to think about query design")

---

### 🔴 archive/deprecated-claims/VALIDATION_REPORT.md

**Size**: 489 lines (14 code blocks)

## 2. Property-Based Testing with Hypothesis (PROOF OF WORK)

### Methodology

- **Tool**: Hypothesis 6.148.3
- **Strategy**: Generate random valid Query instances
- **Coverage**: 320+ queries tested across multiple test cases

### Test Results

```
Test                                    Examples    Status
=====================================================  =======  ======
test_generated_queries_serialize           100      ✅ PASS
test_generated_queries_translate_to_sql    100      ✅ PASS
test_generated_queries_have_valid_structure 50      ✅ PASS
test_query_complexity_limits               50      ✅ PASS
test_where_clause_complexity               20      ✅ PASS
-----------------------------------------------------
TOTAL                                      320      ✅ ALL PASSING
```

### Bugs Discovered by Hypothesis

**Bug #1**: Mixed-type lists in IN operators

```
# Hypothesis generated:
SimpleCondition(
    column=Column.vendor,
    operator=ComparisonOp.in_,
    value=['', 0]  # ❌ Mixed str and int
)

# Error: 7 validation errors for SimpleCondition
```

**Fix**: Modified strategy to generate homogeneous lists:
```python
if operator in (ComparisonOp.in_, ComparisonOp.not_in):
    value_type = draw(st.sampled_from(['str', 'int', 'float']))
    if value_type == 'str':
        value = draw(st.lists(st.text(...), ...))
    # ... etc
```

**Proof**: This is exactly what property-based testing is for - finding edge cases humans miss!

### Schema Metrics (Measured)


**Checking against healed docs**:
- Hypothesis testing approach: Mentioned in README ✅
- Schema metrics: **ACTUAL MEASUREMENTS** ⚠️
- Bug discovery story: **UNIQUE** ⚠️

**Unique Value**:
1. **Hypothesis bug discovery story** (found mixed-type lists in IN operators)
2. **Actual schema metrics** (20.4KB size, depth 6, ~5.2K tokens - measured)
3. **Methodology documentation** (how validation was done)

**Recommendation**: 📝 MIGRATE schema metrics and Hypothesis findings to GUIDE.md, DELETE

---

### 🔴 archive/defensive-overcorrection/BIMODAL_QUERIES_HONEST_ASSESSMENT.md

**Size**: 251 lines
## The Problem I Encountered

### Schema Limitation

The user's YAML spec included queries like:

```yaml
matched_execution:
  logic: "Select matches where (My_Price / Competitor_Price) > 1.05"
```

This requires:
1. Table-qualified column expressions (`my_offers.markdown_price`)
2. Arithmetic expression (`price1 / price2`)
3. Using that arithmetic in a WHERE clause comparison

### Current Schema Pattern

Our `BinaryArithmetic` model works like:
```python
class BinaryArithmetic(BaseModel):
    left_column: Optional[Column] = None  # Just column, not table-qualified
    operator: ArithmeticOp
    right_column: Optional[Column] = None
```

It doesn't easily support:
- Table-qualified columns in arithmetic (`my_offers.price / comp_offers.price`)
- Using arithmetic expressions directly in WHERE clause conditions

### What I Should Have Done

**Option 1**: Work within schema limitations
- Simplify queries to use what the schema supports
- Document limitations honestly
- Show what IS possible

**Option 2**: Extend the schema
- Add support for table-qualified arithmetic
- Update translator

**Unique Value**:
1. **Schema limitation discovery story** (SimpleCondition couldn't do column=column)
2. **Problem-solving progression** (from failure to solution)
3. **Historical context** of commit 08 confession

**Recommendation**: 🗑️ DELETE - This is covered in CRITICAL_FINDINGS.md
(Historical value only, no technical merit not captured elsewhere)

---

### 🔴 archive/defensive-overcorrection/BIMODAL_QUERIES_COMPLETE.md

**Size**: 239 lines

**Content**: Documents ColumnComparison addition and schema fix

**Unique Value**:
1. **Schema evolution story** (problem → solution)
2. **Before/After comparison** (what changed in commits 09-10)

**Recommendation**: 🗑️ DELETE - Git history shows this, audit docs capture it
(No unique technical value)

---

### 🔴 archive/defensive-overcorrection/PROJECT_ALIGNMENT_ANALYSIS.md

**Size**: 955 lines (40 code blocks)
## Part 2: Design Principles Adherence

### 2.1 Principle: Single Path

**Original Statement** (task.yaml):
> "When multiple SQL constructs achieve the same result, choose ONE. Prefer the most conventional, self-explanatory approach."

**Implementation Evidence**:
1. **CTEs excluded** (task.yaml, sql_features.excluded):
   > "CTEs solve same problems as subqueries. Rule: when two approaches achieve the same thing, pick the simpler one and make it exclusive."

   ✅ **Verified**: No CTE models exist. Subqueries used exclusively.

2. **Arithmetic expressions**: Only BinaryArithmetic and CompoundArithmetic
   - No arbitrary expression trees
   - No recursive nesting
   - Two explicit levels covers 95%+ of cases

**Verdict**: ✅ **RIGOROUSLY APPLIED**

---

### 2.2 Principle: Impact Over Power

**Original Statement** (task.yaml):
> "Match SQL's computational impact (what results can be obtained), not its full expressive power (all ways to obtain them)."

**Implementation Evidence**:

| SQL Feature | Impact | Included? | Rationale |
|-------------|--------|-----------|-----------|
| Window functions | Rankings, trends, LAG/LEAD | ✅ Yes | Essential for pricing analysis |
| Scalar subqueries | Comparisons to aggregates | ✅ Yes | "Products above category avg" |
| Correlated subqueries | Same as window functions | ❌ No | Window functions preferred |
| UNION/INTERSECT | Set operations | ❌ No | Handle at application layer |
| FULL/CROSS JOIN | Cartesian products | ❌ No | Performance risk |

**Verdict**: ✅ **RIGOROUSLY APPLIED**
Every inclusion/exclusion decision aligns with "impact over power" principle.

---

### 2.3 Principle: Explicit Depth

**Original Statement** (task.yaml):
> "No infinite recursion or self-reference in types. Define explicit models for each nesting level to control depth."

**Implementation Evidence**:

| Construct | Max Depth | Enforcement Mechanism |
|-----------|-----------|----------------------|
| WHERE subqueries | 1 level | WhereL1 → ScalarSubquery → WhereL0 |
| Arithmetic expressions | 2 operands or 3 | BinaryArithmetic, CompoundArithmetic (no recursion) |
| Boolean logic | 2 levels | ConditionGroup → WhereL0/L1 |
| FROM subqueries | 1 level | DerivedTable → WhereL0 |

**Verdict**: ✅ **PERFECTLY ENFORCED**
No recursive types exist anywhere in the codebase. Every nesting level is explicit.

---

### 2.4 Principle: Correctness by Construction

**Original Statement** (task.yaml):
> "Proto-queries must be correct by schema design. No separate validation step. The Pydantic model guides toward valid SQL."

**Implementation Evidence**:

1. **Enum-based tables and columns**:
   ```python
   class Table(str, Enum):
       product_offers = "product_offers"
       exact_matches = "exact_matches"
   ```
   → **Cannot reference non-existent tables**

2. **Type-safe operators**:
   ```python
   class ComparisonOp(str, Enum):
       eq = "="

**Unique Value**:
1. **Design principles validation** (proves adherence to 5 principles from task.yaml)
2. **Deviation analysis** (2-tier vs 3-tier schema discussion)
3. **Architectural comparison** (vision vs reality with scoring)

**Recommendation**: 📝 MIGRATE design principles section to GUIDE.md, DELETE rest
(Self-grading is suspect, but principles validation is useful)

---

## Summary: What's Unique That We'd Lose

### 🎯 High Value (Should Migrate)

1. **Vertex AI Quirks & Best Practices** (VERTEXAI_FINDINGS.md)
   - 4 specific quirks with workarounds
   - LLM prompting guidance
   - → Migrate to: GUIDE.md or docs/technical/VERTEX_AI_USAGE.md

2. **Performance Metrics** (IMPLEMENTATION_SUMMARY.md)
   - Actual measured performance (model construction <1ms, translation 0.5-3ms)
   - Token usage estimates (300-2000 per query)
   - → Migrate to: GUIDE.md "Performance" section

3. **Schema Metrics** (VALIDATION_REPORT.md)
   - Measured: 20.4KB size, depth 6, ~5.2K tokens
   - → Migrate to: GUIDE.md or README.md

4. **Design Rationale** (IMPLEMENTATION_SUMMARY.md)
   - Why clause-based, why no CTEs, why no recursion
   - → Migrate to: GUIDE.md "Architecture Decisions" section

5. **Hypothesis Bug Discovery** (VALIDATION_REPORT.md)
   - Story of finding mixed-type lists bug
   - → Migrate to: GUIDE.md "Lessons Learned" or testing docs

### 📚 Medium Value (Consider Migrating)

6. **Business Context for Queries** (PRICING_ANALYST_QUERIES.md)
   - When/why/who for each query pattern
   - Natural language → SQL progression
   - → Could enhance examples/bimodal_pricing_queries.py docstrings

7. **Pricing Analyst Use Case Examples** (README.md archive)
   - 4-5 detailed workflow scenarios
   - → Could add to GUIDE.md

8. **Design Principles Validation** (PROJECT_ALIGNMENT_ANALYSIS.md)
   - Shows adherence to 5 core principles
   - → Extract principles section only, migrate to GUIDE.md

### 🗑️ Low Value (Safe to Delete)

9. Historical confession narratives (BIMODAL_QUERIES_HONEST_ASSESSMENT.md)
10. Schema evolution stories (BIMODAL_QUERIES_COMPLETE.md)
11. Self-grading sections (PROJECT_ALIGNMENT_ANALYSIS.md)
12. Stale "production ready" claims (all files)

---

## Recommendations by Action

### MIGRATE IMMEDIATELY (Before Deletion)

**Target**: docs/guides/GUIDE.md

**New Sections to Add**:
1. **Performance Characteristics**
   - Model construction: <1ms
   - SQL translation: 0.5-3ms
   - Schema size: 20.4KB (~5.2K tokens)
   - Token usage: 300-2000 per query

2. **Vertex AI Usage Guide**
   - Quirk 1: Union type ordering
   - Quirk 2: Optional field handling
   - Quirk 3: Enum value generation
   - Quirk 4: Field descriptions importance
   - Best practices for prompting

3. **Architecture Decisions**
   - Why clause-based (natural mental model)
   - Why no CTEs (subqueries achieve same goal)
   - Why no recursion (LLM compatibility)
   - Why discriminated unions (clear type markers)

4. **Testing Insights**
   - Hypothesis discovered mixed-type lists bug
   - Property-based testing approach
   - 320+ random queries validated

### SAFE TO DELETE (After Migration)

All files in `archive/deprecated-claims/` and `archive/defensive-overcorrection/`
AFTER extracting the 8 sections listed above.

---

## Migration Script Plan

```bash
# 1. Extract valuable content from poisoned files
# 2. Append to GUIDE.md in appropriate sections
# 3. Verify migration complete
# 4. Delete poisoned files
# 5. Update DEPRECATION_INDEX.md
# 6. Commit with clear migration log
```

---

**Conclusion**: ~8 sections of unique value worth preserving
**Estimate**: ~200-300 lines of actual unique content in 4,000+ lines of poison
**Recovery Rate**: ~5-7% unique value, 93-95% redundant or poisonous

After migration: Safe to delete ALL poisoned files with no loss of value.
