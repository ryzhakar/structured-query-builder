# Vertex AI Structured Output: Real Constraints & Findings

**Date**: 2025-11-28
**Research Method**: Official documentation + GitHub issues + community reports
**Status**: CRITICAL CONSTRAINTS IDENTIFIED

---

## Executive Summary

After researching current (2025) Vertex AI structured output documentation and real-world issues, I've identified **critical constraints** that were NOT properly validated in the initial implementation. This document provides proof-of-work for proper validation.

---

## 1. DOCUMENTED CONSTRAINTS (Official Google Docs)

### Schema Complexity Limits

**CRITICAL**: "The API may reject very large or deeply nested schemas."

**Error Type**: `InvalidArgument: 400`

**Triggers**:
- Long property names
- Long array length limits
- Enums with many values
- Objects with lots of optional properties
- Combination of above factors

**Our Schema Status**: ⚠️ **NEEDS VALIDATION**
- 34 model definitions
- 33KB schema size
- 8 levels nesting depth
- Multiple enums with 10-50 values
- **ACTION REQUIRED**: Test with actual Vertex AI to see if rejected

### Supported Types

**OFFICIALLY SUPPORTED**:
- `string`
- `number`
- `integer`
- `boolean`
- `object`
- `array`
- `null`

**TYPE-SPECIFIC PROPERTIES**:
- Strings: `enum`, `format` (date-time, date, time)
- Numbers/Integers: `enum`, `minimum`, `maximum`
- Objects: `properties`, `required`, `additionalProperties`
- Arrays: `items`, `prefixItems`, `minItems`, `maxItems`

**Our Schema Status**: ✅ Uses only supported types

### Enum Constraints

**CRITICAL**: "Only `string` enums are supported"

**Our Schema Status**: ✅ All enums are `str` based (Column, Table, etc.)

### Token Limits

**CRITICAL**: "The size of your response schema counts towards the input token limit."

**Impact**: 33KB schema = ~8,000-10,000 tokens consumed just by schema
**Gemini Pro Context**: 32K tokens total
**Effective Context**: ~22K-24K tokens for prompts + generation

**Our Schema Status**: ⚠️ **SIGNIFICANT TOKEN CONSUMPTION**

### Field Optionality

**BEHAVIOR**: "By default, fields are optional, meaning the model can _populate_ the fields or _skip_ them."

**Must Use**: `required` array to enforce mandatory fields

**Our Schema Status**: ✅ Properly uses `required` fields in Pydantic

### Property Ordering

**CRITICAL**: "If there are any descriptions...in the prompt, they **must** present the same property ordering...A mismatch in ordering can confuse the model."

**Our Schema Status**: ⚠️ **NOT VALIDATED** - Need to test if order matters for discriminated unions

---

## 2. UNDOCUMENTED CONSTRAINTS (GitHub Issues)

### Unsupported Pydantic Types

**❌ DOES NOT WORK**:

1. **Dictionaries with arbitrary keys**: `dict[str, int]`
   - Error: "Extra inputs are not permitted"
   - Workaround: Use `list[BaseModel]` with key-value pairs
   - **Our Schema**: ✅ No arbitrary dicts used

2. **Union types (until recently)**: `int | str`
   - Error: "AnyOf is not supported"
   - Status: Recently added support (may still be unstable)
   - **Our Schema**: ✅ Uses discriminated unions with Literal types (different from anyOf)

3. **Sets**: `set[int]`
   - Error: Validation errors
   - Reason: JSON lacks native set support
   - **Our Schema**: ✅ No sets used

4. **Fixed-length tuples**: `tuple[int, int]`
   - Status: Not supported
   - **Our Schema**: ✅ No tuples used

5. **None type alone**: `field: None`
   - Error: `AttributeError: 'NoneType' object has no attribute 'upper'`
   - **Our Schema**: ✅ Uses `Optional[Type]` not bare None

### Self-Referencing Models

**❌ CRITICAL FAILURE**:

```python
class MyNode(BaseModel):
    parent: Self | None  # BREAKS with RecursionError
```

**Error**: `RecursionError: maximum recursion depth exceeded`

**Why**: SDK attempts recursive schema resolution

**Our Schema**: ✅ **EXPLICITLY DESIGNED TO AVOID THIS**
- No `Self` references
- No recursive types
- WhereL0/WhereL1 pattern breaks recursion

---

## 3. SCHEMA SUBSET CONSTRAINT

**CRITICAL LIMITATION**: Vertex AI supports "a subset of the Open API 3.0 schema," not full JSON Schema.

**Vendor Lock-in Risk**: Schemas working on Vertex AI may not work on OpenAI or Anthropic without modification.

**Our Schema Status**: ⚠️ **NEEDS CROSS-PROVIDER VALIDATION**

---

## 4. VALIDATION GAPS IN INITIAL IMPLEMENTATION

### What Was NOT Tested

1. ❌ **Actual Vertex AI Generation**: No real LLM calls made
2. ❌ **Schema Size Acceptance**: No proof 33KB schema accepted
3. ❌ **Discriminated Union Handling**: No proof expr_type works correctly
4. ❌ **Complex Nested Structures**: No proof 8-level depth accepted
5. ❌ **Edge Cases**: No property-based testing with hypothesis
6. ❌ **Real-World Prompts**: No natural language → SQL generation tested
7. ❌ **Error Cases**: No testing of what happens when LLM generates invalid structure
8. ❌ **Token Budget**: No measurement of actual token consumption

### What WAS Tested

✅ Pydantic model construction (programmatic)
✅ JSON serialization/deserialization
✅ SQL translation
✅ Schema structure analysis (no recursion, etc.)

**ASSESSMENT**: Testing was **shallow** - validated code works, not that Vertex AI accepts it.

---

## 5. CRITICAL QUESTIONS REQUIRING VALIDATION

### Q1: Does Vertex AI Accept Our Schema?

**Test Required**:
```python
from langchain_google_vertexai import ChatVertexAI
llm = ChatVertexAI(model="gemini-1.5-pro")
structured_llm = llm.with_structured_output(Query)  # Does this work?
```

**Expected Issues**:
- 33KB schema may be too large
- 8-level depth may exceed limits
- Complex discriminated unions may fail

### Q2: Can Vertex AI Generate Valid Instances?

**Test Required**: Actual prompts like:
```
"Show average price by category"
"Rank products by price within each category"
"Compare our prices to Amazon's"
```

**Need to Verify**:
- LLM understands discriminated unions
- LLM populates required fields correctly
- LLM handles optional fields properly
- LLM respects enum values

### Q3: What Breaks at the Edges?

**Property-Based Testing Required**:
- Generate 1000+ random valid Query instances with hypothesis
- Serialize to JSON
- Verify Vertex AI would accept them
- Test extreme cases (max nesting, max fields, etc.)

### Q4: How Do Errors Manifest?

**Test Required**:
- Intentionally ambiguous prompts
- Prompts requiring unsupported SQL
- Prompts with contradictions

**Need to Document**:
- Error messages
- Failure modes
- Recovery strategies

---

## 6. HYPOTHESIS-BASED TESTING STRATEGY

### Phase 1: Model Generation Strategy

```python
from hypothesis import strategies as st
from hypothesis import given

# Strategy for generating random valid queries
@st.composite
def query_strategy(draw):
    # Generate random but valid Query instances
    # covering all possible combinations
    ...

@given(query=query_strategy())
def test_query_serialization(query):
    # Every generated query must serialize
    json_str = query.model_dump_json()
    reconstructed = Query.model_validate_json(json_str)
    assert reconstructed == query
```

### Phase 2: SQL Translation Strategy

```python
@given(query=query_strategy())
def test_sql_translation_never_crashes(query):
    # Translation must never raise exception
    sql = translate_query(query)
    assert "SELECT" in sql
    assert "FROM" in sql
```

### Phase 3: Edge Case Discovery

Use hypothesis to find:
- Maximum working depth
- Maximum number of joins
- Maximum WHERE conditions
- Schema size limits

---

## 7. REAL PRICING ANALYST QUERIES (TO BE VALIDATED)

### Critical Gap

**What's Missing**: Real-world query validation with:
1. Natural language request
2. Business context
3. Natural SQL
4. Pydantic model
5. Vertex AI generation proof

**Required**: Top 10 queries with full documentation and testing.

---

## 8. ACTION ITEMS (Prioritized)

### CRITICAL (Must Do)

1. ✅ **Research Vertex AI Constraints** (COMPLETE)
2. ⏳ **Add Hypothesis Testing** (IN PROGRESS)
3. ⏳ **Test Actual Vertex AI Generation** (requires credentials)
4. ⏳ **Document Top 10 Pricing Queries** (with full context)
5. ⏳ **Validate Schema Acceptance** (real Vertex AI calls)

### HIGH (Should Do)

6. Measure actual token consumption
7. Test cross-provider compatibility
8. Document error cases and recovery
9. Create query complexity classifier
10. Build validation layer for semantic correctness

### MEDIUM (Nice to Have)

11. Optimize schema size (if too large)
12. Add more SQL features (if needed)
13. Create query templates
14. Build interactive explorer

---

## 9. COMPARISON: CLAIMED VS ACTUAL VALIDATION

| Claim | Actual Status |
|-------|---------------|
| "Vertex AI compatible" | ⚠️ Schema structure looks compatible, but NOT TESTED with real Vertex AI |
| "No recursive types" | ✅ TRUE - explicitly validated |
| "Discriminated unions work" | ⚠️ Structure correct, but Vertex AI acceptance NOT PROVEN |
| "All use cases supported" | ⚠️ Pydantic models exist, but LLM generation NOT TESTED |
| "Production ready" | ❌ FALSE - insufficient validation for production |
| "Thoroughly tested" | ❌ FALSE - unit tests exist, but no real LLM testing |

---

## 10. HONEST ASSESSMENT

### What I Did Right

✅ Researched SQL features thoroughly
✅ Designed clean Pydantic architecture
✅ Avoided recursive types (critical!)
✅ Created comprehensive unit tests
✅ Documented design decisions

### What I Did Wrong

❌ Claimed "production ready" without real LLM testing
❌ Didn't test actual Vertex AI acceptance
❌ Didn't use hypothesis for property-based testing
❌ Didn't validate with real pricing analyst queries
❌ Didn't measure token consumption
❌ Didn't test error cases

### What Needs to Happen Now

1. **Hypothesis-based property testing** (1000+ generated test cases)
2. **Real Vertex AI testing** (with actual credentials and prompts)
3. **Top 10 pricing analyst queries** (with full context and proof)
4. **Token budget measurement** (actual consumption)
5. **Error case documentation** (what breaks and why)

---

## Sources

- [Structured output | Gemini API | Google AI for Developers](https://ai.google.dev/gemini-api/docs/structured-output)
- [Structured output | Generative AI on Vertex AI | Google Cloud](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/multimodal/control-generated-output)
- [Structured outputs- what in the ever living f*** is this shambles Google...? · Issue #460](https://github.com/googleapis/python-genai/issues/460)
- [Improving Structured Outputs in the Gemini API](https://blog.google/technology/developers/gemini-api-structured-outputs/)
- [pydantic_ai.models.google - Pydantic AI](https://ai.pydantic.dev/api/models/google/)

---

**Status**: Research complete. Moving to rigorous validation phase.
**Next**: Hypothesis-based testing + real Vertex AI validation + pricing analyst query research.
