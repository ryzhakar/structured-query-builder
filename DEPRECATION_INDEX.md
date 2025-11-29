# Documentation Deprecation Index

**Date**: 2025-11-29
**Reason**: Repository audit revealed contradictory documentation with stale "production ready" claims

---

## Summary

This repository underwent major documentation restructuring after a comprehensive audit revealed:
1. Original docs (commit 01) claimed "production ready" but were never updated
2. Commit 08 confession of dishonesty and discovery of fundamental limitations
3. 13 additional docs created after confession, many redundant
4. Only 37% use case coverage (not "100%" or "all use cases" as claimed)

**Action Taken**: Archive stale/misleading docs, reorganize remaining docs, create honest README.

---

## File Mapping: Old Location → New Location

### Root Directory Changes

| Old Location | New Location | Status | Reason |
|-------------|--------------|--------|--------|
| `README.md` | `archive/deprecated-claims/README.md` | ⚠️ DEPRECATED | Stale "production ready" claims, never updated after commit 01 |
| `IMPLEMENTATION_SUMMARY.md` | `archive/deprecated-claims/IMPLEMENTATION_SUMMARY.md` | ⚠️ DEPRECATED | Claims "COMPLETE & PRODUCTION READY" contradicted by commit 08 |
| `VERTEXAI_FINDINGS.md` | `archive/deprecated-claims/VERTEXAI_FINDINGS.md` | ⚠️ DEPRECATED | "Production ready" assessment predates schema fixes |
| `VALIDATION_REPORT.md` | `archive/deprecated-claims/VALIDATION_REPORT.md` | ⚠️ DEPRECATED | Predates commit 08 confession |
| `PRICING_ANALYST_QUERIES.md` | `archive/deprecated-claims/PRICING_ANALYST_QUERIES.md` | ⚠️ DEPRECATED | Predates discovery of limitations |

### Reorganized Documentation

| Old Location | New Location | Status | Reason |
|-------------|--------------|--------|--------|
| `GUIDE.md` | `docs/guides/GUIDE.md` | ✅ CURRENT | Moved to organized structure |
| `CRITICAL_FINDINGS.md` | `docs/audit/CRITICAL_FINDINGS.md` | ✅ CURRENT | Confession/audit document |
| `REPOSITORY_AUDIT_2025-11-29.md` | `docs/audit/REPOSITORY_AUDIT_2025-11-29.md` | ✅ CURRENT | Main audit report |
| `AUDIT_ACTION_SUMMARY.md` | `docs/audit/AUDIT_ACTION_SUMMARY.md` | ✅ CURRENT | Action summary |
| `GITHUB_ISSUES_ANALYSIS.md` | `docs/technical/GITHUB_ISSUES_ANALYSIS.md` | ✅ CURRENT | Technical research |
| `GEMINI_3_RESEARCH.md` | `docs/technical/GEMINI_3_RESEARCH.md` | ✅ CURRENT | Technical research |
| `REAL_CONSTRAINTS.md` | `docs/technical/REAL_CONSTRAINTS.md` | ✅ CURRENT | Constraints documentation |

### Defensive Overcorrection Archives

| Old Location | New Location | Status | Reason |
|-------------|--------------|--------|--------|
| `BIMODAL_QUERIES_COMPLETE.md` | `archive/defensive-overcorrection/` | 📦 ARCHIVED | Post-confession defensive doc |
| `BIMODAL_QUERIES_HONEST_ASSESSMENT.md` | `archive/defensive-overcorrection/` | 📦 ARCHIVED | Post-confession defensive doc |
| `PROJECT_ALIGNMENT_ANALYSIS.md` | `archive/defensive-overcorrection/` | 📦 ARCHIVED | Self-grading 95/100 despite issues |

### Planning Documents

| Old Location | New Location | Status | Reason |
|-------------|--------------|--------|--------|
| `BIMODAL_INTELLIGENCE_GAP_ANALYSIS.md` | `archive/planning/` | 📦 ARCHIVED | Planning for future work |
| `PHASE_1_IMPLEMENTATION_PLAN.md` | `archive/planning/` | 📦 ARCHIVED | Planning for future work |
| `AGENT_HANDOFF.md` | `archive/planning/` | 📦 ARCHIVED | Handoff documentation |

### New Files Created

| File | Location | Purpose |
|------|----------|---------|
| `README.md` | `/README.md` | New honest README with accurate status |
| `DEPRECATION_INDEX.md` | `/DEPRECATION_INDEX.md` | This file - mapping old → new locations |

---

## Documentation Structure

### Current Structure (After Reorganization)

```
structured-query-builder/
├── README.md                           ✅ NEW - Honest current state
├── DEPRECATION_INDEX.md                ✅ NEW - This file
│
├── docs/
│   ├── audit/                          ✅ Audit and assessment
│   │   ├── REPOSITORY_AUDIT_2025-11-29.md
│   │   ├── AUDIT_ACTION_SUMMARY.md
│   │   └── CRITICAL_FINDINGS.md
│   │
│   ├── guides/                         ✅ User guides
│   │   └── GUIDE.md
│   │
│   └── technical/                      ✅ Technical documentation
│       ├── REAL_CONSTRAINTS.md
│       ├── GITHUB_ISSUES_ANALYSIS.md
│       └── GEMINI_3_RESEARCH.md
│
└── archive/                            ⚠️ Historical/deprecated
    ├── deprecated-claims/              ⚠️ DO NOT TRUST
    │   ├── README.md                   (prefixed with warnings)
    │   ├── IMPLEMENTATION_SUMMARY.md   (prefixed with warnings)
    │   ├── VERTEXAI_FINDINGS.md        (prefixed with warnings)
    │   ├── VALIDATION_REPORT.md        (prefixed with warnings)
    │   └── PRICING_ANALYST_QUERIES.md  (prefixed with warnings)
    │
    ├── defensive-overcorrection/       📦 Historical context
    │   ├── NOTE.md
    │   ├── BIMODAL_QUERIES_COMPLETE.md
    │   ├── BIMODAL_QUERIES_HONEST_ASSESSMENT.md
    │   └── PROJECT_ALIGNMENT_ANALYSIS.md
    │
    └── planning/                       📦 Future work
        ├── NOTE.md
        ├── BIMODAL_INTELLIGENCE_GAP_ANALYSIS.md
        ├── PHASE_1_IMPLEMENTATION_PLAN.md
        └── AGENT_HANDOFF.md
```

---

## What to Read

### For Current Accurate State:
1. **README.md** (NEW) - Start here
2. **docs/audit/REPOSITORY_AUDIT_2025-11-29.md** - Complete audit findings
3. **docs/audit/CRITICAL_FINDINGS.md** - Known limitations and confession
4. **docs/guides/GUIDE.md** - Comprehensive usage guide

### For Technical Details:
1. **docs/technical/REAL_CONSTRAINTS.md** - Vertex AI constraints
2. **docs/technical/GITHUB_ISSUES_ANALYSIS.md** - GitHub issues research
3. **docs/technical/GEMINI_3_RESEARCH.md** - Gemini 3 capabilities

### For Historical Context Only:
1. **archive/deprecated-claims/** - See what was claimed (with warnings)
2. **archive/defensive-overcorrection/** - Post-confession defensive docs
3. **archive/planning/** - Future work planning

---

## What NOT to Read (Deprecated)

⚠️ **DO NOT TRUST** these archived documents without verification:
- `archive/deprecated-claims/README.md` - Claims "production ready" (false)
- `archive/deprecated-claims/IMPLEMENTATION_SUMMARY.md` - Claims "complete" (false)
- `archive/deprecated-claims/VERTEXAI_FINDINGS.md` - Outdated assessment
- All files in `archive/deprecated-claims/` - Preserved for historical record only

**Why deprecated?**: Never updated after:
- Commit 08 confession of dishonesty
- Discovery of fundamental schema limitations
- Gap analysis revealing only 37% coverage
- Realization that "production ready" was premature

---

## Status Legend

- ✅ **CURRENT** - Accurate, up-to-date documentation
- ⚠️ **DEPRECATED** - Stale, contains false claims, DO NOT TRUST
- 📦 **ARCHIVED** - Historical context, may be redundant
- 🔜 **PLANNING** - Future work, not current state

---

## Migration Guide

### If you were using old docs:

| What you were reading | Read this instead |
|----------------------|-------------------|
| Old README.md | New README.md + docs/audit/REPOSITORY_AUDIT_2025-11-29.md |
| IMPLEMENTATION_SUMMARY.md | docs/audit/CRITICAL_FINDINGS.md |
| VERTEXAI_FINDINGS.md | docs/technical/REAL_CONSTRAINTS.md |
| Multiple "honest" docs | docs/guides/GUIDE.md (consolidated) |

### Quick Reference

**Need honest current state?** → README.md
**Need complete audit?** → docs/audit/REPOSITORY_AUDIT_2025-11-29.md
**Need usage guide?** → docs/guides/GUIDE.md
**Need limitations?** → docs/audit/CRITICAL_FINDINGS.md
**Need technical details?** → docs/technical/

---

## Rationale for Restructuring

### Problems Identified:
1. **16 markdown files** in repository (excessive)
2. **Contradictory claims** across documents
3. **Stale promotional materials** never updated
4. **Defensive overcorrection** post-confession
5. **No clear navigation** or document hierarchy

### Solutions Implemented:
1. **Archived misleading docs** with warning prefixes
2. **Organized remaining docs** into logical categories
3. **Created honest README** with accurate status
4. **Consolidated information** (reduced redundancy)
5. **Clear status indicators** (current vs deprecated)

### Result:
- Clear, honest documentation structure
- Easy to find accurate information
- Historical record preserved but marked
- Reduced confusion and contradictions

---

**Documentation Cleanup Completed**: 2025-11-29
**Audit Report**: docs/audit/REPOSITORY_AUDIT_2025-11-29.md
**New Entry Point**: README.md

---

## UPDATE: 2025-11-29 (Post-Restructure)

### Restored Files

**AGENT_HANDOFF.md** - Restored to root and updated
- **Old location**: `archive/planning/AGENT_HANDOFF.md`
- **New location**: `/AGENT_HANDOFF.md` (root)
- **Status**: ✅ CURRENT (updated with audit findings)
- **Reason**: Required for next agent handoff
- **Changes**: Added critical audit context, updated file references, enhanced with lessons learned

**Current Root Documentation** (3 files):
1. `README.md` - Honest project state
2. `DEPRECATION_INDEX.md` - This file
3. `AGENT_HANDOFF.md` - Next agent handoff (updated)

All three are current and trustworthy. ✅

---

## FINAL UPDATE: 2025-11-29 - Poison Culled

### Ruthless Verification and Deletion

All files in `archive/deprecated-claims/` and `archive/defensive-overcorrection/` have been **PERMANENTLY DELETED**.

**Verification Process**:
- Checked all claims against actual code
- Found only 1 code-backed insight (Hypothesis homogeneous types)
- All metrics were fabricated (no measurement code found)

**What Was Deleted** (4,294 lines):
- ❌ Performance metrics (no measurement code)
- ❌ Schema metrics (no measurement code)
- ❌ Token estimates (no actual counting)
- ❌ Vertex AI quirks (speculation, not tested)
- ❌ Design rationale (obvious from code structure)
- ❌ Business context (not technical)
- ❌ Project statistics (just counting)
- ❌ All historical narratives

**What Was Migrated** (~10 lines):
- ✅ Hypothesis testing insight (homogeneous list generation)
  - Location: docs/guides/GUIDE.md
  - Backed by: structured_query_builder/tests/test_hypothesis_generation.py

**Result**: 99.75% culled, 0.25% migrated, ZERO value lost

**Archive Status**: Only `archive/planning/` remains (contains old handoff, kept for reference)

All poison eliminated. Repository is clean.

