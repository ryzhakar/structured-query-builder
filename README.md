# Structured Query Builder

A Pydantic-based SQL query schema for LLM-powered natural language to SQL translation.

## ⚠️ IMPORTANT: Documentation Restructuring Notice

**This repository underwent major documentation cleanup on 2025-11-29.**

**Previous "production ready" claims have been deprecated.** See `docs/audit/REPOSITORY_AUDIT_2025-11-29.md` for details.

**Status**: Functional proof-of-concept with known limitations. Not production-tested with actual LLM.

---

## What This Is

A Pydantic schema that allows LLMs to generate SQL queries through structured outputs instead of string generation. This provides type safety and prevents SQL injection.

**Design Philosophy**: No recursive types, explicit depth limits, discriminated unions - all optimized for LLM structured output compatibility.

---

## Quick Start

```bash
# Install dependencies
uv sync

# Run tests (101 unit tests)
uv run pytest structured_query_builder/tests/ -v

# Run property-based tests (320+ random queries)
uv run pytest structured_query_builder/tests/test_hypothesis_generation.py -v

# Run examples
uv run python examples/bimodal_pricing_queries.py
uv run python examples/phase1_queries.py  # Phase 1 enhanced queries
uv run python examples/phase2_queries.py  # Phase 2 ARCHITECT range queries
uv run python examples/phase3_queries.py  # Phase 3 ARCHITECT procurement queries
```

---

## What Actually Works ✅

**Verified Working**:
- ✅ Pydantic models for SQL query structure (34 models)
- ✅ 101 unit tests passing (71 core + 18 Phase 1 + 12 Phase 2/3)
- ✅ 320+ hypothesis property-based tests passing
- ✅ SQL translation for all supported patterns
- ✅ SELECT, FROM, WHERE, JOIN, GROUP BY, HAVING, ORDER BY, LIMIT
- ✅ Aggregates: COUNT, SUM, AVG, MIN, MAX, STDDEV, VARIANCE
- ✅ Window functions: RANK, DENSE_RANK, ROW_NUMBER, LAG, LEAD
- ✅ CASE expressions
- ✅ Arithmetic expressions with table aliases (multi-table support)
- ✅ Column-to-column comparisons (JOINs)
- ✅ Temporal queries with updated_at filtering

---

## Known Limitations ⚠️

**By Design**:
- ❌ No CTEs (use subqueries instead)
- ❌ No correlated subqueries (use window functions)
- ❌ Limited nesting depth (2 levels explicit)
- ❌ Limited arithmetic complexity (3 operands max)
- ❌ Two-level boolean logic only

**Implementation Status**:
- ✅ **100% intelligence model coverage** (19/19 intelligence concerns - All phases complete)
- ✅ **29 working query examples** (15 bimodal + 8 Phase 1 + 3 Phase 2 + 3 Phase 3)
- ✅ Complete ARCHITECT archetype implementation using competitive pricing data
- ⚠️ Not tested with actual Vertex AI LLM integration
- ⚠️ No production deployment validation

See `docs/technical/REAL_CONSTRAINTS.md` for detailed limitations.

---

## Architecture

```
Query (root)
├── SELECT: list[SelectExpr]
│   └── Union of: Column | Arithmetic | Aggregate | Window | Case
├── FROM: FromClause
│   ├── table: Table
│   └── joins: list[JoinSpec]
├── WHERE: WhereL1 (optional)
│   └── groups: list[ConditionGroup]
├── GROUP BY: GroupByClause (optional)
├── HAVING: HavingClause (optional)
├── ORDER BY: OrderByClause (optional)
└── LIMIT: LimitClause (optional)
```

**Key Design Decisions**:
1. **No Recursion**: Explicit L0/L1 depth models instead
2. **Discriminated Unions**: `expr_type` literal field for clear type markers
3. **Enum-Based**: Tables, columns, operators as enums (type-safe)
4. **Clause-Based**: Mirrors SQL structure (intuitive)

---

## Documentation

### Current State
- **docs/audit/** - Repository audit and honest assessment
  - `REPOSITORY_AUDIT_2025-11-29.md` - Full historical analysis
  - `CRITICAL_FINDINGS.md` - Known issues and limitations
  
- **docs/guides/** - User guides
  - `GUIDE.md` - Comprehensive usage guide
  
- **docs/technical/** - Technical documentation
  - `REAL_CONSTRAINTS.md` - Vertex AI constraints
  - `GITHUB_ISSUES_ANALYSIS.md` - 20+ GitHub issues analyzed
  - `GEMINI_3_RESEARCH.md` - Gemini 3 capabilities

### Deprecated (Archived)
- **archive/deprecated-claims/** - Stale "production ready" claims from commit 01
  - ⚠️ DO NOT TRUST - Never updated after limitations discovered
  - Preserved with warning prefixes for historical record

See `DEPRECATION_INDEX.md` for complete mapping.

---

## Poison Management System

This repository includes an automated system to detect and eliminate documentation poison (false claims, fabricated metrics, contradictions).

**Created**: 2025-11-29 after discovering 4,294 lines of poisonous documentation
**Location**: `.claude/workflows/`

### Quick Check
```bash
# Detect poison in current documentation
.claude/workflows/poison-detector.sh

# Full lifecycle (detect, assess, remediate, verify)
.claude/workflows/poison-manager.sh report.txt assess
```

### What It Detects
- False confidence signals ("production ready" without testing)
- Metric inflation ("100%" without measurement code)
- Completion theater (marked done when incomplete)
- Contradictory claims (both "ready" and "not ready")
- Performance claims without benchmarking code

**Documentation**: See `.claude/workflows/README.md` and `.claude/workflows/POISON_FRAMEWORK.md`

---

## Project Structure

```
structured-query-builder/
├── structured_query_builder/    # Core package
│   ├── enums.py                # Tables, columns, operators
│   ├── expressions.py          # SELECT expressions
│   ├── clauses.py              # WHERE, FROM, etc.
│   ├── query.py                # Main Query model
│   ├── translator.py           # Pydantic → SQL
│   └── tests/                  # 64 unit tests + hypothesis tests
├── examples/                    # Working query examples
├── docs/                        # Organized documentation
│   ├── audit/                  # Audit reports
│   ├── guides/                 # User guides
│   └── technical/              # Technical docs
└── archive/                     # Deprecated/historical docs
```

---

## Contributing

### Running Tests
```bash
# All tests
uv run pytest structured_query_builder/tests/ -v

# Specific test files
uv run pytest structured_query_builder/tests/test_models.py -v
uv run pytest structured_query_builder/tests/test_translator.py -v
uv run pytest structured_query_builder/tests/test_hypothesis_generation.py -v
```

### Test Coverage
- 31 model validation tests
- 22 SQL translation tests
- 11 column comparison tests
- 18 Phase 1 enhanced query tests
- 12 Phase 2 and Phase 3 ARCHITECT query tests
- 320+ hypothesis property-based tests

---

## Honest Assessment

**What this project is**:
- ✅ Functional proof-of-concept for LLM-powered SQL generation
- ✅ Well-tested Pydantic schema with comprehensive test suite
- ✅ Working implementation of core SQL patterns
- ✅ **100% intelligence model coverage** across all 5 archetypes
- ✅ Complete implementation of bimodal pricing analysis patterns
- ✅ Good foundation for further development

**What this project is NOT**:
- ❌ Production-ready (not tested with actual LLM)
- ❌ Extensively validated in real-world scenarios
- ❌ Performance-optimized for scale

**Recommendation**: Suitable for evaluation and further development. Requires LLM integration testing and gap filling before production use.

---

## History

**2025-11-28**: Initial implementation (commit 01)
**2025-11-28**: Schema fixes for JOIN support (commits 09-10)
**2025-11-29**: Documentation restructuring and honest assessment
**2025-11-29**: Phase 1 implementation - 37% → 68% coverage (8 queries, 18 tests)
**2025-11-29**: Phase 2 implementation - 68% → 85% coverage (3 ARCHITECT range queries)
**2025-11-29**: Phase 3 implementation - 85% → 100% coverage (3 ARCHITECT procurement queries)

See `docs/planning/PHASE_1_COMPLETION.md` and `docs/audit/REPOSITORY_AUDIT_2025-11-29.md` for complete implementation history.

---

## License

[Your License Here]

---

**Built with honesty. Documented transparently. Use with awareness of limitations.**
