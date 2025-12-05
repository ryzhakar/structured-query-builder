# LangChain + Vertex AI: Abstraction Costs for Structured Outputs

**Last Updated**: 2025-12-05
**Focus**: Impact of LangChain abstraction layer on Vertex AI structured output reliability
**Audience**: Developers using `langchain_google_vertexai.ChatVertexAI.with_structured_output()`

---

## Executive Summary

Using LangChain as an abstraction layer over Vertex AI's structured outputs **introduces several preprocessing transformations** that can silently break schemas or reduce reliability. This document catalogs all discovered transformations, their failure modes, and recommendations for your specific use case.

**Key Finding**: LangChain's `with_structured_output()` method performs **schema dereferencing** (flattening `$defs`/`$ref`) that can break complex discriminated unions and nested schemas. This is **separate from and in addition to** Vertex AI's native limitations.

**Your Risk Level**: **MEDIUM** - Your schema uses discriminated unions and nested models, which are affected by LangChain's preprocessing.

---

## 1. LangChain's Preprocessing Pipeline

### 1.1 Transformation Layers

When you call `llm.with_structured_output(YourSchema)`, LangChain applies these transformations:

```
Your Pydantic Model
    ↓
[1] Pydantic v2 → JSON Schema (with $defs)
    ↓
[2] LangChain: replace_defs_in_schema() → Flattened schema (no $defs/$ref)
    ↓
[3] LangChain: _format_json_schema_to_gapic() → Vertex AI GAPIC format
    ↓
[4] Vertex AI: Native validation & generation
    ↓
[5] LangChain: PydanticOutputParser → Validation against original schema
```

**Critical Point**: Layers [2] and [3] are **LangChain-specific preprocessing** not present when using Vertex AI directly.

**Sources**:
- [[LangChain ChatVertexAI Source](https://github.com/langchain-ai/langchain-google/blob/main/libs/vertexai/langchain_google_vertexai/chat_models.py)]
- [[Issue #659](https://github.com/langchain-ai/langchain-google/issues/659)] - "$defs warning"
- [[PR #843](https://github.com/langchain-ai/langchain-google/pull/843)] - $defs resolution fix

### 1.2 The `replace_defs_in_schema()` Function

**Purpose**: Dereferences all `$ref` and `$defs` because Vertex AI doesn't support JSON Schema references.

**What It Does**:
1. Extracts all definitions from `$defs` (Pydantic v2) or `definitions` (Pydantic v1)
2. Replaces every `{"$ref": "#/$defs/ModelName"}` with the actual schema inline
3. Removes the top-level `$defs` key
4. **WARNING**: Only handles `dict` objects, **not `list` objects**

**Critical Bug** [[Issue #1023](https://github.com/langchain-ai/langchain-google/issues/1023)]:
```python
# This pattern breaks
{
  "anyOf": [
    {"$ref": "#/$defs/Type1"},
    {"$ref": "#/$defs/Type2"}
  ]
}

# Because replace_defs_in_schema doesn't recurse into arrays
# Result: $ref inside anyOf array stays unreferenced
```

**Impact on Your Schema**:
- ✅ Standard nested models: **Works** (dict-based references)
- ⚠️ Discriminated unions with Pydantic `RootModel[Type1 | Type2]`: **May break**
- ⚠️ anyOf with $ref in array: **Broken until fixed**

**Status**: [[Issue #1023](https://github.com/langchain-ai/langchain-google/issues/1023)] marked as "no longer needed" after [[PR #1288](https://github.com/langchain-ai/langchain-google/pull/1288)], but no independent confirmation.

**Source**: [[Issue #1023](https://github.com/langchain-ai/langchain-google/issues/1023)]

### 1.3 The `_format_json_schema_to_gapic()` Function

**Purpose**: Converts JSON Schema to Vertex AI's GAPIC format.

**Known Transformations**:
1. Logs warning "Key '$defs' is not supported in schema, ignoring" [[Issue #659](https://github.com/langchain-ai/langchain-google/issues/659)]
2. Handles schema type detection
3. Adds `response_mime_type="application/json"` if not specified

**Source**: [[PR #843](https://github.com/langchain-ai/langchain-google/pull/843)]

---

## 2. Known Issues with LangChain + Vertex AI

### 2.1 Issue #953: Complex Pydantic Schemas Fail

**Status**: OPEN (as of Dec 2025)

**Affected Versions**: `langchain-google-vertexai` 2.0.20 - 2.0.28 (possibly later)

**Failure Pattern**:
```python
class Foo(BaseModel):
    foo: str

class Bar(BaseModel):
    foos: list[Foo] = Field(default_factory=list)
    bargl: int | None = Field(None)
    # BOTH fields required to trigger bug
```

**Error**:
```
EnumStringValueParseError: Invalid enum value string for enum type
google.cloud.aiplatform.v1beta1.Type at
Schema.properties[params].properties[chart_type].anyOf[0].type
```

**Root Cause**: Combination of:
- `list[NestedModel]` (list of Pydantic models)
- `Optional[int]` field (anyOf with None)
- Likely related to `replace_defs_in_schema` not handling nested schemas in lists

**Workaround**: Users report switching to **LiteLLM gateway + ChatOpenAI** client works fine [[Issue #953](https://github.com/langchain-ai/langchain-google/issues/953#issuecomment-3162076862)]

**Your Risk**: **HIGH** - Your schema has `list[SelectExpr]`, `list[OrderExpr]`, etc.

**Source**: [[Issue #953](https://github.com/langchain-ai/langchain-google/issues/953)]

### 2.2 Issue #1023: `$ref` Inside `anyOf` Array Breaks

**Status**: CLOSED (claimed fixed, but unverified)

**Failure Pattern**:
```python
# Pydantic RootModel with Union
class MyUnion(RootModel[Type1 | Type2 | Type3]):
    pass

# Generates schema with $ref inside anyOf array
{
  "anyOf": [
    {"$ref": "#/$defs/Type1"},
    {"$ref": "#/$defs/Type2"}
  ]
}

# replace_defs_in_schema() doesn't handle lists, so $ref stays
```

**Impact**: Discriminated unions using `RootModel` pattern may fail.

**Your Schema**: Uses discriminated unions via `Literal` discriminators (different pattern), likely **not affected** by this specific bug.

**Source**: [[Issue #1023](https://github.com/langchain-ai/langchain-google/issues/1023)]

### 2.3 Issue #659: "$defs Not Supported" Warning

**Status**: CLOSED (fixed in PR #843)

**Problem**: LangChain logs warning about `$defs` not being supported, causing confusion.

**Resolution**: Warning improved, schema dereferencing works correctly (for dict-based refs).

**Source**: [[Issue #659](https://github.com/langchain-ai/langchain-google/issues/659)]

### 2.4 Issue #463: Union Types in Tool Calling

**Status**: CLOSED

**Problem**: Tool calling with `Union` types in arguments failed.

**Note**: This is **tool calling**, not structured output, but shows LangChain struggles with Union type handling.

**Source**: [[Issue #463](https://github.com/langchain-ai/langchain-google/issues/463)]

---

## 3. LangChain's Output Parsing Layer

### 3.1 PydanticOutputParser

When using `with_structured_output()` with a Pydantic model, LangChain wraps the response in `PydanticOutputParser`.

**What It Does**:
1. Takes raw text output from Vertex AI
2. Parses as JSON
3. **Validates against original Pydantic model** (with `$defs`)
4. Raises `ValidationError` if doesn't match

**Critical Point**: Validation happens **against your original schema**, not the dereferenced version sent to Vertex AI.

**Implications**:
- If Vertex AI generates valid JSON for dereferenced schema
- But it doesn't match original schema structure
- **PydanticOutputParser will fail**

**Example Failure**:
```python
# Your schema (with nested model reference)
class Inner(BaseModel):
    value: int

class Outer(BaseModel):
    inner: Inner  # Creates $ref to Inner

# LangChain sends dereferenced version to Vertex AI:
# inner: {type: object, properties: {value: {type: integer}}}

# Vertex AI generates: {"inner": {"value": 42}}

# PydanticOutputParser validates against original: ✅ Works

# BUT if dereferencing broke the schema structure:
# Vertex AI might generate: {"inner_value": 42}

# PydanticOutputParser validates: ❌ Fails with ValidationError
```

**Sources**:
- [[PydanticOutputParser Docs](https://python.langchain.com/api_reference/core/output_parsers/langchain_core.output_parsers.pydantic.PydanticOutputParser.html)]
- [[LangChain Structured Output Guide](https://mirascope.com/blog/langchain-structured-output)]

### 3.2 include_raw Parameter

```python
llm_with_structure = llm.with_structured_output(
    YourSchema,
    include_raw=True  # Returns both raw and parsed
)

# Returns:
{
  "raw": <AIMessage with raw response>,
  "parsed": <YourSchema instance or None>,
  "parsing_error": <Exception or None>
}
```

**Use Case**: Debug when PydanticOutputParser fails but Vertex AI returned valid JSON.

**Source**: [[ChatVertexAI Docs](https://python.langchain.com/api_reference/google_vertexai/chat_models/langchain_google_vertexai.chat_models.ChatVertexAI.html)]

---

## 4. Direct Vertex AI vs LangChain Comparison

### 4.1 What You Gain with LangChain

**✅ Benefits**:
1. **Vendor abstraction**: `llm.with_structured_output()` works across OpenAI, Anthropic, Vertex AI
2. **Automatic output parsing**: PydanticOutputParser validates and parses responses
3. **LCEL compatibility**: Chains work with LangChain Expression Language
4. **Prompt templates**: Integrated with `ChatPromptTemplate`

**Example**:
```python
# Same code works for multiple providers
from langchain_google_vertexai import ChatVertexAI
from langchain_openai import ChatOpenAI

llm = ChatVertexAI(model="gemini-2.5-flash")  # or ChatOpenAI(model="gpt-4")
structured_llm = llm.with_structured_output(Query)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a SQL query builder"),
    ("user", "{request}")
])

chain = prompt | structured_llm  # Works for both providers
```

### 4.2 What You Lose with LangChain

**❌ Costs**:
1. **Additional schema transformations**: `replace_defs_in_schema()` introduces bugs
2. **Opaque preprocessing**: Hard to debug what schema actually reaches Vertex AI
3. **Version lag**: LangChain must catch up to Vertex AI API changes
4. **Extra validation layer**: PydanticOutputParser can fail even if Vertex AI succeeded
5. **Less control**: Can't access Vertex AI-specific features (e.g., `thinking_level`)

**Example - What You Can't Do**:
```python
# ❌ Can't use Vertex AI-specific parameters through LangChain
llm = ChatVertexAI(
    model="gemini-3-pro-preview",
    thinking_level="low",  # Not exposed in LangChain
)

# ❌ Can't use propertyOrdering directly
# ❌ Can't inspect dereferenced schema sent to API
# ❌ Can't bypass replace_defs_in_schema if it breaks your schema
```

### 4.3 Comparison Table

| Feature | Direct Vertex AI (`google.genai`) | LangChain (`langchain_google_vertexai`) |
|---------|-----------------------------------|----------------------------------------|
| Schema dereferencing | ❌ Not needed (Vertex AI handles $defs) | ✅ Automatic (but can break) |
| $ref support | ❌ Not supported by Vertex AI | ⚠️ Dereferenced (with bugs) |
| anyOf in arrays | ⚠️ Limited Vertex AI support | ⚠️ + LangChain bugs |
| List of nested models | ⚠️ Vertex AI constraints | ❌ Additional LangChain bugs (#953) |
| Vendor switching | ❌ Vertex AI only | ✅ Works across providers |
| Output parsing | Manual | ✅ Automatic (PydanticOutputParser) |
| Vertex AI features | ✅ Full access | ⚠️ Limited (no `thinking_level`, etc.) |
| Debugging | ✅ Direct API errors | ❌ Opaque transformations |
| Performance | ✅ Direct API calls | ⚠️ Extra parsing layer |

---

## 5. Impact on Your Schema

### 5.1 Your Schema Characteristics

Based on `test_vertexai_integration.py`:

```python
# Your schema structure
class Query(BaseModel):
    select: list[SelectExpr]  # List of union types
    from_: From
    where: Optional[WhereL0] = None
    group_by: Optional[list[GroupByExpr]] = None
    having: Optional[HavingL0] = None
    order_by: Optional[list[OrderExpr]] = None
    limit: Optional[int] = None

# SelectExpr is Union of discriminated types
SelectExpr = Union[ColumnExpr, BinaryArithmetic, AggregateExpr, WindowExpr, CaseExpr, ...]

# Each has discriminator
class ColumnExpr(BaseModel):
    expr_type: Literal["column"]
    source: ColumnSource

class BinaryArithmetic(BaseModel):
    expr_type: Literal["binary_arithmetic"]
    operator: ArithmeticOp
    left: SelectExpr  # Nested union reference
    right: SelectExpr
```

### 5.2 Risk Assessment

**✅ Low Risk Areas**:
1. **Discriminator pattern**: Uses `Literal` discriminators, not `RootModel` (avoids Issue #1023)
2. **No recursive types**: WhereL0/WhereL1 pattern avoids recursion (by design)
3. **String enums**: All enums inherit from `str` (safe)

**⚠️ Medium Risk Areas**:
1. **Lists of union types**: `list[SelectExpr]` matches Issue #953 failure pattern
2. **Nested unions**: `SelectExpr` within `BinaryArithmetic` creates deep nesting
3. **Optional fields**: `Optional[WhereL0]` uses anyOf with None

**Observed Behavior from Your Tests**:
```python
# test_vertexai_integration.py line 111-114
llm = ChatVertexAI(
    model="gemini-1.5-pro",  # Note: Not latest model
    temperature=0,
)
llm_with_structure = llm.with_structured_output(Query)
```

**Question**: Have you tested with:
- Gemini 2.5 models? (Issue #953 affects 2.5)
- Complex queries with multiple nested SelectExpr? (stress test dereferencing)
- All discriminated union variants? (ensure discriminator works post-dereferencing)

### 5.3 Specific Failure Scenarios

**Scenario 1**: Issue #953 Pattern Match
```python
# Your schema has this pattern:
class Query(BaseModel):
    select: list[SelectExpr]  # list[Union]
    limit: Optional[int] = None  # Optional field

# Issue #953 triggers on:
class Bar(BaseModel):
    foos: list[Foo]  # list[Model]
    bargl: int | None = Field(None)  # Optional field

# Pattern similarity: HIGH
# Risk: Schema dereferencing may break with Gemini 2.5+
```

**Scenario 2**: Deep Nesting
```python
# Your schema allows:
BinaryArithmetic(
    left=BinaryArithmetic(
        left=ColumnExpr(...),
        right=CaseExpr(
            when=[...],  # More unions
            then=[...]
        )
    ),
    right=WindowExpr(...)
)

# LangChain must dereference ALL nested unions
# If dereferencing breaks at depth=3, you won't see it until production
```

**Scenario 3**: Discriminator After Dereferencing
```python
# Before dereferencing (what you define):
SelectExpr = Union[ColumnExpr, BinaryArithmetic, ...]
# Discriminated by expr_type

# After dereferencing (what Vertex AI sees):
# All types inlined, discriminator must still work
# If schema structure changes, discriminator may break
```

---

## 6. Testing Strategy

### 6.1 Validate LangChain Preprocessing

**Test 1**: Inspect Dereferenced Schema
```python
from langchain_google_vertexai import ChatVertexAI
from langchain_google_vertexai._utils import replace_defs_in_schema
import json

# Get your schema
schema = Query.model_json_schema()
print("Original schema size:", len(json.dumps(schema)))
print("Has $defs:", "$defs" in schema)

# Apply LangChain preprocessing
dereferenced = replace_defs_in_schema(schema)
print("\nDereferenced schema size:", len(json.dumps(dereferenced)))
print("Has $defs:", "$defs" in dereferenced)

# Validate structure preserved
assert "select" in dereferenced["properties"]
assert "expr_type" in str(dereferenced)  # Discriminator still present

# Check for unexpected transformations
# (e.g., refs not fully dereferenced, structure changed)
```

**Test 2**: Compare Direct vs LangChain
```python
from google import genai
from langchain_google_vertexai import ChatVertexAI

# Direct Vertex AI
direct_client = genai.Client(vertexai=True)
direct_response = direct_client.models.generate_content(
    model='gemini-2.5-flash',
    contents=prompt,
    config=GenerateContentConfig(
        response_mime_type='application/json',
        response_schema=Query,
    ),
)

# LangChain wrapper
langchain_llm = ChatVertexAI(model='gemini-2.5-flash')
langchain_response = langchain_llm.with_structured_output(Query).invoke(prompt)

# Compare results
assert type(direct_response.parsed) == type(langchain_response)
# If they differ, LangChain transformation caused issues
```

**Test 3**: Stress Test Deep Nesting
```python
# Generate query with maximum nesting depth
prompt = """
Create a query that calculates:
(price * quantity) - (discount + tax) + CASE WHEN category = 'A' THEN 10 ELSE 20 END
With window function ranking by the result
"""

llm_with_structure = llm.with_structured_output(Query, include_raw=True)
result = llm_with_structure.invoke(prompt)

if result["parsing_error"]:
    print("Parsing failed!")
    print("Raw output:", result["raw"].content)
    print("Error:", result["parsing_error"])
    # Indicates dereferencing broke schema structure
```

### 6.2 Test Issue #953 Pattern

```python
# Create minimal repro matching Issue #953
class Foo(BaseModel):
    foo: str

class Bar(BaseModel):
    foos: list[Foo] = Field(default_factory=list)
    bargl: int | None = Field(None)

# Test with Gemini 2.5
llm = ChatVertexAI(model="gemini-2.5-flash")
structured_llm = llm.with_structured_output(Bar)

try:
    result = structured_llm.invoke("Give me sample data")
    print("✅ Works:", result)
except Exception as e:
    print("❌ Issue #953 affects you:", e)
    # If this fails, your Query schema likely has same issue
```

---

## 7. Mitigation Strategies

### 7.1 Stay on LangChain (Safer for Your Use Case)

**Rationale**: You need vendor abstraction for early-stage product.

**Actions**:
1. **Pin versions**:
   ```
   langchain-google-vertexai==2.0.28  # Last tested version
   langchain-core==0.3.60
   ```

2. **Test with multiple models**:
   ```python
   models_to_test = [
       "gemini-1.5-pro",  # Your current
       "gemini-2.0-flash",
       "gemini-2.5-flash",  # Issue #953 risk
       "gemini-3-pro-preview",  # Latest
   ]
   ```

3. **Use `include_raw=True` in production**:
   ```python
   llm_with_structure = llm.with_structured_output(
       Query,
       include_raw=True  # Captures parsing failures
   )

   result = llm_with_structure.invoke(prompt)
   if result["parsing_error"]:
       # Log raw output for debugging
       logger.error(f"Parsing failed: {result['parsing_error']}")
       logger.info(f"Raw output: {result['raw'].content}")
       # Fallback strategy
   ```

4. **Monitor LangChain issues**:
   - [[Issue #953](https://github.com/langchain-ai/langchain-google/issues/953)] - If closed, test immediately
   - Watch for PRs mentioning "replace_defs_in_schema" or "vertex"

### 7.2 Hybrid Approach (Use LangChain for Abstraction, Not Preprocessing)

**Strategy**: Use LangChain for prompt templating and vendor switching, but bypass `with_structured_output()`.

```python
from langchain_google_vertexai import ChatVertexAI
from langchain_core.prompts import ChatPromptTemplate
from google import genai
from google.genai.types import GenerateContentConfig

# Use LangChain for prompts (vendor-agnostic)
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a SQL query builder"),
    ("user", "{request}")
])

# But call Vertex AI directly for structured output
llm = ChatVertexAI(model="gemini-2.5-flash")
formatted_prompt = prompt.format_messages(request="Show me average price by category")

# Convert LangChain messages to Vertex AI format
vertex_client = genai.Client(vertexai=True)
response = vertex_client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[msg.content for msg in formatted_prompt],
    config=GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=Query,  # Direct, no LangChain preprocessing
    ),
)

query = response.parsed  # Vertex AI's native parsing
```

**Pros**:
- ✅ Keeps prompt template abstraction
- ✅ Avoids LangChain's schema preprocessing bugs
- ✅ Access to Vertex AI-specific features
- ✅ Easier debugging (direct API errors)

**Cons**:
- ❌ More code (manual message conversion)
- ❌ Can't use LCEL chains
- ❌ Must handle vendor-specific response formats

### 7.3 Switch to Direct Vertex AI (Maximum Control)

**When to Consider**:
- Issue #953 confirmed to affect your schema
- Need `thinking_level` or other Gemini 3 features
- Vendor lock-in acceptable for now

**Migration**:
```python
# Before (LangChain)
from langchain_google_vertexai import ChatVertexAI

llm = ChatVertexAI(model="gemini-1.5-pro")
structured_llm = llm.with_structured_output(Query)
result = structured_llm.invoke(prompt)

# After (Direct Vertex AI)
from google import genai
from google.genai.types import GenerateContentConfig

client = genai.Client(vertexai=True, project="your-project")
response = client.models.generate_content(
    model="gemini-3-pro-preview",
    contents=prompt,
    config=GenerateContentConfig(
        response_mime_type="application/json",
        response_schema=Query,
        thinking_level="low",  # Gemini 3 feature
    ),
)
result = response.parsed
```

**Pros**:
- ✅ No LangChain preprocessing bugs
- ✅ Full Vertex AI feature access
- ✅ Simpler debugging
- ✅ Potentially better performance

**Cons**:
- ❌ Vendor lock-in
- ❌ Must rewrite for each provider
- ❌ Lose LangChain ecosystem (agents, chains, etc.)

### 7.4 Use LiteLLM Gateway (Workaround from Issue #953)

Users report success with [[LiteLLM](https://www.litellm.ai/)] gateway:

```python
from langchain_openai import ChatOpenAI

# Point OpenAI client to LiteLLM gateway routing to Gemini
llm = ChatOpenAI(
    model="gemini-2.5-flash",  # LiteLLM routes this
    base_url="http://localhost:8000",  # LiteLLM gateway
)

# Use OpenAI's with_structured_output (different preprocessing)
structured_llm = llm.with_structured_output(Query)
result = structured_llm.invoke(prompt)
```

**Why This Works**:
- OpenAI's `ChatOpenAI` uses **different schema preprocessing** than `ChatVertexAI`
- LiteLLM translates OpenAI format to Vertex AI format
- Avoids LangChain's `replace_defs_in_schema` bugs

**Pros**:
- ✅ Keeps LangChain abstraction
- ✅ Works around Issue #953
- ✅ Easy vendor switching via LiteLLM config

**Cons**:
- ❌ Extra infrastructure (LiteLLM gateway)
- ❌ Network hop (latency)
- ❌ LiteLLM must support latest Gemini features

**Source**: [[Issue #953 Comment](https://github.com/langchain-ai/langchain-google/issues/953#issuecomment-3162076862)]

---

## 8. Recommendations for Your Project

### 8.1 Immediate Actions

1. **✅ Test with Gemini 2.5**:
   ```python
   llm = ChatVertexAI(model="gemini-2.5-flash")  # Instead of 1.5-pro
   ```
   Run your full test suite. If Issue #953 affects you, you'll know immediately.

2. **✅ Add `include_raw=True` to production code**:
   ```python
   llm_with_structure = llm.with_structured_output(Query, include_raw=True)
   ```
   Capture parsing failures for debugging.

3. **✅ Inspect dereferenced schema** (Test 6.1.1 above):
   Verify LangChain's preprocessing doesn't break your discriminated unions.

4. **✅ Pin LangChain versions**:
   ```
   langchain-google-vertexai>=2.0.28,<2.1.0
   ```
   Prevent surprise breakages from updates.

### 8.2 Short-Term Strategy (Next 3 Months)

**Recommendation**: **Stay on LangChain** but with defensive measures.

**Justification**:
- Vendor abstraction critical for early-stage product
- Your schema *likely* avoids Issue #953 (discriminator pattern different)
- LangChain actively maintains Vertex AI integration
- Cost of switching outweighs risk (for now)

**Defensive Measures**:
1. Comprehensive testing with all Gemini models (1.5, 2.0, 2.5, 3.0)
2. Monitor `parsing_error` rate in production
3. Have direct Vertex AI fallback ready (Section 7.3 code)
4. Watch Issue #953 and related PRs

### 8.3 Long-Term Strategy (6+ Months)

**Decision Point**: When to switch from LangChain to direct Vertex AI?

**Switch if**:
- Issue #953 confirmed to affect your schema
- Need Gemini 3-specific features (`thinking_level`, better grounding)
- Vendor lock-in becomes acceptable (picked primary provider)
- LangChain preprocessing causes >5% parsing failures

**Stay if**:
- Still evaluating multiple vendors
- Issue #953 doesn't affect you
- LangChain ecosystem features valuable (agents, chains)
- Parsing success rate >95%

### 8.4 Monitoring Metrics

Track these metrics to inform decision:

| Metric | Threshold | Action if Exceeded |
|--------|-----------|-------------------|
| Parsing failure rate | >5% | Investigate LangChain preprocessing |
| `include_raw` parsing errors | >10/day | Switch to direct Vertex AI |
| Schema dereferencing time | >100ms | Consider caching dereferenced schema |
| LangChain version lag | >2 months behind Vertex AI features | Re-evaluate abstraction value |

---

## 9. Testing Checklist

Before deploying with LangChain + Vertex AI:

**Schema Validation**:
- [ ] Inspect dereferenced schema (no `$defs` remain)
- [ ] Verify discriminators present in dereferenced schema
- [ ] Validate schema size <50KB after dereferencing
- [ ] Check for unexpected structural changes

**Model Compatibility**:
- [ ] Test with Gemini 1.5 Pro
- [ ] Test with Gemini 2.0 Flash
- [ ] Test with Gemini 2.5 Flash (Issue #953 risk)
- [ ] Test with Gemini 3 Pro Preview (if using new features)

**Query Complexity**:
- [ ] Simple queries (SELECT * FROM table)
- [ ] Aggregate queries (AVG by category)
- [ ] Window functions (RANK OVER PARTITION BY)
- [ ] Deep nesting (BinaryArithmetic with 3+ levels)
- [ ] All discriminated union variants (ColumnExpr, AggregateExpr, WindowExpr, CaseExpr)

**Error Handling**:
- [ ] `include_raw=True` configured
- [ ] Logging for `parsing_error` cases
- [ ] Fallback strategy defined
- [ ] Alert on parsing failure rate >5%

**Performance**:
- [ ] Baseline latency (direct Vertex AI)
- [ ] LangChain overhead measured (<20% acceptable)
- [ ] Token consumption tracked (schema + prompt + output)

---

## 10. Conclusion

**TL;DR**:

1. **LangChain adds preprocessing**: `replace_defs_in_schema()` dereferences `$defs`/$ref
2. **Known bugs exist**: Issue #953 affects `list[Model]` + `Optional[T]` pattern
3. **Your schema at risk**: Matches Issue #953 pattern, needs testing
4. **Recommended strategy**: Stay on LangChain but test heavily, have fallback ready
5. **Key test**: Run with Gemini 2.5 Flash immediately to confirm Issue #953 impact

**Critical Actions**:
- ✅ Test with Gemini 2.5 Flash **today**
- ✅ Add `include_raw=True` to production
- ✅ Pin LangChain versions
- ⏳ Monitor Issue #953 for resolution
- ⏳ Prepare direct Vertex AI fallback code

---

## 11. References

### 11.1 LangChain Issues

1. [[Issue #953](https://github.com/langchain-ai/langchain-google/issues/953)] - Structured output failure (OPEN)
2. [[Issue #1023](https://github.com/langchain-ai/langchain-google/issues/1023)] - $ref inside anyOf (CLOSED)
3. [[Issue #659](https://github.com/langchain-ai/langchain-google/issues/659)] - $defs warning (CLOSED)
4. [[Issue #463](https://github.com/langchain-ai/langchain-google/issues/463)] - Union types in tools (CLOSED)

### 11.2 LangChain PRs

1. [[PR #843](https://github.com/langchain-ai/langchain-google/pull/843)] - Fix $defs resolution
2. [[PR #1288](https://github.com/langchain-ai/langchain-google/pull/1288)] - Fix $ref in anyOf (claimed)

### 11.3 LangChain Documentation

1. [[ChatVertexAI API Docs](https://python.langchain.com/api_reference/google_vertexai/chat_models/langchain_google_vertexai.chat_models.ChatVertexAI.html)]
2. [[Structured Output Guide](https://python.langchain.com/v0.1/docs/modules/model_io/chat/structured_output/)]
3. [[PydanticOutputParser](https://python.langchain.com/api_reference/core/output_parsers/langchain_core.output_parsers.pydantic.PydanticOutputParser.html)]

### 11.4 Related Resources

1. [[LangChain Structured Output Analysis](https://mirascope.com/blog/langchain-structured-output)]
2. [[Pydantic with LangChain](https://atamel.dev/posts/2024/12-09_control_llm_output_langchain_structured_pydantic/)]
3. [[LiteLLM Gateway](https://www.litellm.ai/)] - Workaround for Issue #953

---

**Document Status**: Complete, based on latest available information (Dec 2025)
**Next Review**: When Issue #953 closed, or when Gemini 3 Pro stable release
**Feedback**: Test findings against your actual workload and update document
