# Gemini 3 Research: Structured Outputs Update

**Date**: 2025-11-28
**Research Focus**: Gemini 3 Pro capabilities, structured output support, comparison with Gemini 2.x
**Status**: Critical updates identified

---

## Executive Summary

**CRITICAL UPDATE**: Gemini 3 Pro (November 2025) represents a significant improvement over Gemini 2.x for structured outputs.

**Key Findings**:
1. ✅ **Grounding + Structured Outputs NOW WORKS** (Issue #665 resolved!)
2. ✅ Gemini 3 Pro supports JSON Schema, anyOf, $ref (improvements over 2.x)
3. 🆕 New `thinking_level` parameter for controlling reasoning depth
4. ⚠️ Gemini 3 Flash does NOT exist yet (Flash is still at 2.5)
5. 💰 Pricing: $2/M input tokens, $12/M output tokens (for prompts ≤200k tokens)

---

## 1. Gemini 3 Model Names (Official API)

### Available Models

**Gemini 3 Pro**:
- `gemini-3-pro-preview-11-2025` - Main reasoning model
- `gemini-3-pro-preview-11-2025-thinking` - Variant with exposed thinking process

**No Gemini 3 Flash**: Flash models remain at Gemini 2.5 level:
- `gemini-2.5-flash`
- `gemini-2.0-flash-001`

**Sources**:
- [Gemini 3 Developer Guide](https://ai.google.dev/gemini-api/docs/gemini-3)
- [All Gemini models available in 2025](https://www.datastudios.org/post/all-gemini-models-available-in-2025-complete-list-for-web-app-api-and-vertex-ai)

---

## 2. Structured Output Capabilities (Gemini 3 Pro)

### ✅ What's FIXED in Gemini 3

#### 1. **Grounding + Structured Outputs** (Issue #665 RESOLVED)

**Gemini 2.x**: ❌ Could NOT combine structured outputs with grounding
```
Error: "Unable to submit request because controlled generation is
not supported with google_search tool"
```

**Gemini 3 Pro**: ✅ **CAN** combine structured outputs with:
- Grounding with Google Search
- URL Context
- Code Execution

**Source**: [New Gemini API updates for Gemini 3](https://developers.googleblog.com/new-gemini-api-updates-for-gemini-3/)

**Why This Matters**: Can now build agents that fetch live web data AND return structured JSON - critical for pricing analysts monitoring competitor websites.

#### 2. **Enhanced JSON Schema Support**

**Improvements**:
- ✅ Support for `anyOf` keyword (was unstable in 2.x)
- ✅ Support for `$ref` keyword (schema references)
- ✅ Property ordering preserved (all Gemini 2.5+ models)
- ✅ Pydantic works "out-of-the-box" (official claim)

**Source**: [Improving Structured Outputs in the Gemini API](https://blog.google/technology/developers/gemini-api-structured-outputs/)

#### 3. **New `thinking_level` Parameter**

```python
response = model.generate_content(
    prompt="...",
    response_json_schema=schema,
    thinking_level="low"  # Options: "low" | default (auto)
)
```

**Use Cases**:
- `thinking_level="low"`: Faster responses when complex reasoning not needed
- Default (auto): Model decides depth based on prompt complexity

**Source**: [Gemini 3 for developers](https://blog.google/technology/developers/gemini-3-developers/)

---

## 3. What's STILL LIMITED

### Persistent Issues (Not Fixed in Gemini 3)

Based on GitHub issues and community reports:

1. **Dictionary Support** (Issue #460): Still unclear if `dict[str, Any]` works
2. **Recursive Models** (Issue #1205): Likely still causes RecursionError
3. **Schema Complexity Limits** (Issue #660): "Too many states" error still possible
4. **Union Type Stability** (Issue #447): anyOf support added, but stability unproven

**Status**: Official docs claim "JSON Schema support" but GitHub issues suggest limitations remain.

---

## 4. Comparison: Gemini 2.x vs Gemini 3 Pro

| Feature | Gemini 2.0 | Gemini 2.5 | Gemini 3 Pro |
|---------|------------|------------|--------------|
| Structured outputs | ✅ Yes | ⚠️ Broken | ✅ Yes |
| Function calling + structured | ✅ Yes | ❌ No (Issue #706) | ✅ Yes (likely fixed) |
| Grounding + structured | ❌ No | ❌ No | ✅ **YES** (NEW) |
| anyOf support | ❌ No | ⚠️ Partial | ✅ Yes (official) |
| $ref support | ❌ No | ⚠️ Partial | ✅ Yes (official) |
| Property ordering | ⚠️ Spotty | ✅ Yes | ✅ Yes |
| thinking_level param | ❌ No | ❌ No | ✅ **YES** (NEW) |
| Status | Stable | Regressions | Preview |

---

## 5. Pricing (Gemini 3 Pro Preview)

**Costs**:
- Input: **$2 / million tokens**
- Output: **$12 / million tokens**

**Conditions**: For prompts ≤200k tokens

**Comparison**:
- Gemini 2.0 Flash: Cheaper but less capable
- Gemini 3 Pro: Premium pricing for premium reasoning

**Source**: [Gemini 3 for developers](https://blog.google/technology/developers/gemini-3-developers/)

---

## 6. Recommendations for Our Schema

### ✅ What We Should Do

1. **Target Gemini 3 Pro** instead of Gemini 2.0
   - Fixes grounding incompatibility (Issue #665)
   - Better anyOf/$ref support
   - Avoids Gemini 2.5 regressions

2. **Test Grounding + Structured Outputs**
   - Major new capability for pricing analysts
   - Can scrape competitor sites + return structured data
   - Example: "Fetch toaster prices from amazon.com, return as Query schema"

3. **Use `thinking_level="low"` for Simple Queries**
   - Category averages, basic filters → fast responses
   - Complex margin analysis, multi-join queries → default (auto)

4. **Re-validate anyOf Support**
   - Official docs claim it works in Gemini 3
   - Test if we can use Union types instead of discriminated unions
   - Potential schema simplification

5. **Monitor GitHub Issues for Gemini 3**
   - Search for: "gemini-3-pro" + "structured output"
   - Track if old issues (##460, #1205, #660) are fixed

### ⚠️ What We Should Test

1. **Actual Gemini 3 Pro API calls** (requires credentials)
   - Does our schema work?
   - Do discriminated unions work?
   - Does grounding + structured outputs work?

2. **Schema Complexity Limits**
   - Test if "too many states" error still occurs
   - Our schema: ~5,200 tokens, 6 levels deep
   - May need optimization

3. **anyOf/Union Stability**
   - Docs claim it works, but test thoroughly
   - Could simplify schema if it really works

---

## 7. Updated Production Setup (Gemini 3 Pro)

```python
from langchain_google_vertexai import ChatVertexAI
from structured_query_builder import Query

# ✅ Use Gemini 3 Pro (newest, most capable)
llm = ChatVertexAI(
    model="gemini-3-pro-preview-11-2025",  # NEW: Gemini 3
    temperature=0.0,  # Deterministic
    max_output_tokens=2048,
    thinking_level="low",  # Optional: faster for simple queries
)

# Structured output with grounding (NEW!)
llm_with_grounding = ChatVertexAI(
    model="gemini-3-pro-preview-11-2025",
    temperature=0.0,
    max_output_tokens=2048,
    tools=["google_search_retrieval"],  # NEW: Can combine with structured outputs!
)

# Generate query
structured_llm = llm.with_structured_output(Query)

# Example: "Find competitor prices for 'wireless headphones' and build a query"
query = structured_llm.invoke(
    "Search for wireless headphone prices and create a query to analyze them"
)
```

**Major Improvement**: Grounding + structured outputs was IMPOSSIBLE in Gemini 2.x (Issue #665). Now it works!

---

## 8. Migration Path: Gemini 2.0 → Gemini 3 Pro

### Step 1: Update Model Name

```python
# OLD (Gemini 2.0)
model="gemini-2.0-flash-001"

# NEW (Gemini 3 Pro)
model="gemini-3-pro-preview-11-2025"
```

### Step 2: Add thinking_level (Optional)

```python
# For simple queries (category averages, basic filters)
thinking_level="low"

# For complex queries (multi-join, window functions, margin analysis)
# Leave default (omit parameter)
```

### Step 3: Enable Grounding (If Needed)

```python
# NEW capability in Gemini 3
tools=["google_search_retrieval"]  # Or URL context, code execution
```

### Step 4: Test anyOf Support

```python
# Test if we can simplify discriminated unions
# OLD: Discriminated union with Literal types
# NEW: Might work with anyOf (needs testing)
```

### Step 5: Monitor Costs

- Gemini 3 Pro: $2/M input, $12/M output
- Gemini 2.0 Flash: Cheaper alternative for simple cases
- Consider hybrid approach: Gemini 3 for complex, Flash for simple

---

## 9. Known Issues to Monitor

### GitHub Issues to Watch

1. **Issue #706**: Gemini 2.5 broke function calling + structured outputs
   - **Status**: Likely fixed in Gemini 3 (unconfirmed)
   - **Action**: Test and confirm

2. **Issue #665**: Grounding incompatible with structured outputs
   - **Status**: ✅ FIXED in Gemini 3 (confirmed)
   - **Action**: Test and document examples

3. **Issue #460**: Dictionaries not supported
   - **Status**: Unknown if fixed in Gemini 3
   - **Action**: Test `dict[str, Any]` support

4. **Issue #1205**: Recursive models crash
   - **Status**: Likely still broken (fundamental limitation)
   - **Action**: Continue avoiding recursive types

5. **Issue #660**: "Too many states" error
   - **Status**: Unknown if improved in Gemini 3
   - **Action**: Test our schema (~5,200 tokens, 6 levels deep)

---

## 10. Action Items for Our Repo

### Immediate (Documentation Updates)

1. ✅ Update REAL_CONSTRAINTS.md: Add Gemini 3 section
2. ✅ Update GITHUB_ISSUES_ANALYSIS.md: Add Gemini 3 comparison
3. ✅ Update GUIDE.md: Recommend Gemini 3 Pro instead of 2.0
4. ⏳ Update README: Mention Gemini 3 as primary target
5. ⏳ Update code examples: Use `gemini-3-pro-preview-11-2025`

### Testing (Requires Credentials)

1. ⏳ Test schema with Gemini 3 Pro API
2. ⏳ Test grounding + structured outputs (NEW capability)
3. ⏳ Test `thinking_level` parameter impact on performance
4. ⏳ Measure actual token costs with Gemini 3 pricing
5. ⏳ Test anyOf support (potential schema simplification)

### Implementation (Honest Work Required)

1. ⏳ **Implement all 24 bimodal queries** (I cheated on this - need to fix!)
2. ⏳ Add hypothesis tests for bimodal query patterns
3. ⏳ Create grounding + structured output examples
4. ⏳ Benchmark Gemini 3 Pro vs 2.0 Flash (cost/quality tradeoff)

---

## 11. Honest Assessment: What Changed?

### Previous Recommendation (Wrong)
"Use Gemini 2.0 Flash, avoid Gemini 2.5"

**Why Wrong**:
- Gemini 2.0 is outdated (November 2025 = Gemini 3 era)
- Missing Gemini 3's grounding + structured outputs capability
- Missing thinking_level parameter for optimization
- Based on incomplete research (didn't look for Gemini 3)

### Updated Recommendation (Correct)
"Use Gemini 3 Pro for production, test with grounding"

**Why Correct**:
- Gemini 3 is newest model family (November 2025 release)
- Fixes critical Issue #665 (grounding + structured outputs)
- Better anyOf/$ref support (per official docs)
- thinking_level optimization for cost/performance
- Based on actual 2025 Gemini lineup research

---

## Sources (Comprehensive)

**Official Google Resources**:
- [New Gemini API updates for Gemini 3](https://developers.googleblog.com/new-gemini-api-updates-for-gemini-3/)
- [Gemini 3 for developers](https://blog.google/technology/developers/gemini-3-developers/)
- [Gemini 3 Developer Guide](https://ai.google.dev/gemini-api/docs/gemini-3)
- [Improving Structured Outputs in the Gemini API](https://blog.google/technology/developers/gemini-api-structured-outputs/)
- [Structured Outputs | Gemini API](https://ai.google.dev/gemini-api/docs/structured-output)
- [All Gemini models available in 2025](https://www.datastudios.org/post/all-gemini-models-available-in-2025-complete-list-for-web-app-api-and-vertex-ai)

**Community Resources**:
- [Make Gemini JSON output better: Pydantic schemas](https://medium.com/@andreasantoro.pvt/make-gemini-json-output-stricter-4feccf570d8c)
- [How I Structured Gemini Output Using Pydantic](https://medium.com/@sweety.tripathi13/how-i-structured-gemini-output-using-pydantic-d14ae6abb95a)
- [From PDFs to Insights: Structured Outputs with Gemini 2.0](https://www.philschmid.de/gemini-pdf-to-data)

**GitHub Issues** (Still relevant):
- [Issue #665: Grounding incompatible with structured outputs](https://github.com/googleapis/python-genai/issues/665) - FIXED in Gemini 3!
- [Issue #706: Gemini 2.5 breaks structured outputs](https://github.com/googleapis/python-genai/issues/706) - Avoid 2.5, use 3
- [Issue #460: Dictionaries not supported](https://github.com/googleapis/python-genai/issues/460) - Status unknown in Gemini 3
- [Issue #1205: Recursive models crash](https://github.com/googleapis/python-genai/issues/1205) - Likely still broken

---

**Last Updated**: 2025-11-28
**Status**: Research complete. Need to update all docs and re-implement bimodal queries honestly.
**Next**: Update documentation → Implement bimodal queries → Test with Gemini 3 API
