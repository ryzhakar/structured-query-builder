#!/bin/bash
# Poison Detection Workflow
# Detects common patterns of misinformation in documentation

set -e

REPORT_FILE="${1:-.claude/poison-report.txt}"
FAIL_ON_POISON="${2:-false}"

> "$REPORT_FILE"

echo "═══════════════════════════════════════════════════════" | tee -a "$REPORT_FILE"
echo "POISON DETECTION WORKFLOW" | tee -a "$REPORT_FILE"
echo "Date: $(date)" | tee -a "$REPORT_FILE"
echo "═══════════════════════════════════════════════════════" | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

POISON_FOUND=0

# Pattern 1: False Confidence Signals
echo "🔍 Pattern 1: False Confidence Signals" | tee -a "$REPORT_FILE"
echo "   Searching for: 'production ready', 'ready to deploy', 'production tested'" | tee -a "$REPORT_FILE"

FALSE_CONFIDENCE=$(find . -name "*.md" -not -path "*/archive/*" -not -path "*/.git/*" -not -path "*/docs/audit/*" -not -path "*/.claude/*" \
    -not -path "*/WORK_COMPLETE.md" -not -path "*/CULLING_COMPLETE.md" -not -path "*/POISON_AUDIT_REPORT.md" -not -path "*/UNIQUE_VALUE_ANALYSIS.md" \
    -exec grep -l -i "production.ready\|ready.to.deploy\|production.tested\|production-ready" {} \; 2>/dev/null || true)

if [ -n "$FALSE_CONFIDENCE" ]; then
    echo "   ⚠️  FOUND in:" | tee -a "$REPORT_FILE"
    echo "$FALSE_CONFIDENCE" | while read file; do
        echo "      - $file" | tee -a "$REPORT_FILE"
        grep -n -i "production.ready\|ready.to.deploy\|production.tested\|production-ready" "$file" | head -3 | sed 's/^/        /' | tee -a "$REPORT_FILE"
    done
    POISON_FOUND=$((POISON_FOUND + 1))
else
    echo "   ✅ None found" | tee -a "$REPORT_FILE"
fi
echo "" | tee -a "$REPORT_FILE"

# Pattern 2: Metric Inflation
echo "🔍 Pattern 2: Metric Inflation" | tee -a "$REPORT_FILE"
echo "   Searching for: '100%', 'all test', 'complete coverage'" | tee -a "$REPORT_FILE"

METRIC_INFLATION=$(find . -name "*.md" -not -path "*/archive/*" -not -path "*/.git/*" -not -path "*/docs/audit/*" -not -path "*/.claude/*" \
    -not -path "*/WORK_COMPLETE.md" -not -path "*/CULLING_COMPLETE.md" -not -path "*/POISON_AUDIT_REPORT.md" -not -path "*/UNIQUE_VALUE_ANALYSIS.md" \
    -exec grep -l "100%\|all.*test.*pass\|complete.*coverage" {} \; 2>/dev/null || true)

if [ -n "$METRIC_INFLATION" ]; then
    echo "   ⚠️  FOUND in:" | tee -a "$REPORT_FILE"
    echo "$METRIC_INFLATION" | while read file; do
        echo "      - $file" | tee -a "$REPORT_FILE"
        grep -n "100%\|all.*test.*pass\|complete.*coverage" "$file" | head -3 | sed 's/^/        /' | tee -a "$REPORT_FILE"
    done
    # Check if there's actual measurement code
    echo "   🔬 Verifying against code..." | tee -a "$REPORT_FILE"
    MEASUREMENT_CODE=$(find . -name "*.py" -exec grep -l "coverage\|measure\|metric" {} \; 2>/dev/null | wc -l)
    echo "      Files with measurement code: $MEASUREMENT_CODE" | tee -a "$REPORT_FILE"
    if [ "$MEASUREMENT_CODE" -eq 0 ]; then
        echo "      ❌ NO measurement code found - claims likely fabricated" | tee -a "$REPORT_FILE"
        POISON_FOUND=$((POISON_FOUND + 1))
    fi
else
    echo "   ✅ None found" | tee -a "$REPORT_FILE"
fi
echo "" | tee -a "$REPORT_FILE"

# Pattern 3: Completion Theater
echo "🔍 Pattern 3: Completion Theater" | tee -a "$REPORT_FILE"
echo "   Searching for: 'all tasks complete', 'finished as specified'" | tee -a "$REPORT_FILE"

COMPLETION_THEATER=$(find . -name "*.md" -not -path "*/archive/*" -not -path "*/.git/*" -not -path "*/docs/audit/*" -not -path "*/.claude/*" \
    -not -path "*/WORK_COMPLETE.md" -not -path "*/CULLING_COMPLETE.md" -not -path "*/POISON_AUDIT_REPORT.md" -not -path "*/UNIQUE_VALUE_ANALYSIS.md" \
    -exec grep -l -i "all.*tasks.*complete\|finished.*as.*specified" {} \; 2>/dev/null || true)

if [ -n "$COMPLETION_THEATER" ]; then
    echo "   ⚠️  FOUND in:" | tee -a "$REPORT_FILE"
    echo "$COMPLETION_THEATER" | while read file; do
        echo "      - $file" | tee -a "$REPORT_FILE"
    done
    POISON_FOUND=$((POISON_FOUND + 1))
else
    echo "   ✅ None found" | tee -a "$REPORT_FILE"
fi
echo "" | tee -a "$REPORT_FILE"

# Pattern 4: Defensive Overcorrection
echo "🔍 Pattern 4: Defensive Overcorrection" | tee -a "$REPORT_FILE"
echo "   Searching for: ALL CAPS emphasis, excessive 'honest' claims" | tee -a "$REPORT_FILE"

DEFENSIVE=$(find . -name "*.md" -not -path "*/archive/*" -not -path "*/.git/*" -not -path "*/docs/audit/*" -not -path "*/.claude/*" \
    -not -path "*/WORK_COMPLETE.md" -not -path "*/CULLING_COMPLETE.md" -not -path "*/POISON_AUDIT_REPORT.md" -not -path "*/UNIQUE_VALUE_ANALYSIS.md" \
    -exec grep -l "NO CHEATING\|PROOF-OF-WORK\|HONEST DISCLOSURE" {} \; 2>/dev/null || true)

if [ -n "$DEFENSIVE" ]; then
    echo "   ⚠️  FOUND in:" | tee -a "$REPORT_FILE"
    echo "$DEFENSIVE" | while read file; do
        echo "      - $file" | tee -a "$REPORT_FILE"
    done
    POISON_FOUND=$((POISON_FOUND + 1))
else
    echo "   ✅ None found" | tee -a "$REPORT_FILE"
fi
echo "" | tee -a "$REPORT_FILE"

# Pattern 5: Contradictory Documentation
echo "🔍 Pattern 5: Contradictory Claims" | tee -a "$REPORT_FILE"
echo "   Checking for docs claiming both 'ready' and 'not ready'" | tee -a "$REPORT_FILE"

CONTRADICTORY=0
find . -name "*.md" -not -path "*/archive/*" -not -path "*/.git/*" -not -path "*/docs/audit/*" -not -path "*/.claude/*" -not -path "*/WORK_COMPLETE.md" -not -path "*/CULLING_COMPLETE.md" -not -path "*/POISON_AUDIT_REPORT.md" -not -path "*/UNIQUE_VALUE_ANALYSIS.md" | while IFS= read -r file; do
    READY=$(grep -c -i "ready\|complete" "$file" 2>/dev/null || echo 0)
    NOT_READY=$(grep -c -i "not ready\|incomplete\|needs.*test\|requires.*validation" "$file" 2>/dev/null || echo 0)

    # Ensure variables are integers
    READY=${READY//[^0-9]/}
    NOT_READY=${NOT_READY//[^0-9]/}
    READY=${READY:-0}
    NOT_READY=${NOT_READY:-0}

    if [ "$READY" -gt 0 ] && [ "$NOT_READY" -gt 0 ]; then
        echo "   ⚠️  Contradiction in: $file" | tee -a "$REPORT_FILE"
        echo "      Claims 'ready': $READY times" | tee -a "$REPORT_FILE"
        echo "      Claims 'not ready': $NOT_READY times" | tee -a "$REPORT_FILE"
        CONTRADICTORY=$((CONTRADICTORY + 1))
    fi
done

if [ "$CONTRADICTORY" -gt 0 ]; then
    POISON_FOUND=$((POISON_FOUND + 1))
else
    echo "   ✅ None found" | tee -a "$REPORT_FILE"
fi
echo "" | tee -a "$REPORT_FILE"

# Pattern 6: Performance Claims Without Code
echo "🔍 Pattern 6: Performance Claims Without Measurement" | tee -a "$REPORT_FILE"
echo "   Searching for: specific timing claims (ms, seconds)" | tee -a "$REPORT_FILE"

PERF_CLAIMS=$(find . -name "*.md" -not -path "*/archive/*" -not -path "*/.git/*" -not -path "*/docs/audit/*" -not -path "*/.claude/*" \
    -not -path "*/WORK_COMPLETE.md" -not -path "*/CULLING_COMPLETE.md" -not -path "*/POISON_AUDIT_REPORT.md" -not -path "*/UNIQUE_VALUE_ANALYSIS.md" \
    -exec grep -l "<[0-9]*ms\|[0-9]*-[0-9]*ms\|[0-9]* seconds" {} \; 2>/dev/null || true)

if [ -n "$PERF_CLAIMS" ]; then
    echo "   ⚠️  FOUND performance claims in:" | tee -a "$REPORT_FILE"
    echo "$PERF_CLAIMS" | while read file; do
        echo "      - $file" | tee -a "$REPORT_FILE"
    done
    
    # Check for actual timing code
    TIMING_CODE=$(find . -name "*.py" -exec grep -l "time\.time\|timeit\|perf_counter" {} \; 2>/dev/null | wc -l)
    echo "   🔬 Files with timing code: $TIMING_CODE" | tee -a "$REPORT_FILE"
    
    if [ "$TIMING_CODE" -eq 0 ]; then
        echo "      ❌ NO timing code found - performance claims fabricated" | tee -a "$REPORT_FILE"
        POISON_FOUND=$((POISON_FOUND + 1))
    fi
else
    echo "   ✅ None found" | tee -a "$REPORT_FILE"
fi
echo "" | tee -a "$REPORT_FILE"

# Summary
echo "═══════════════════════════════════════════════════════" | tee -a "$REPORT_FILE"
echo "SUMMARY" | tee -a "$REPORT_FILE"
echo "═══════════════════════════════════════════════════════" | tee -a "$REPORT_FILE"

if [ "$POISON_FOUND" -eq 0 ]; then
    echo "✅ No poison detected - documentation is clean" | tee -a "$REPORT_FILE"
    exit 0
else
    echo "⚠️  Poison patterns detected: $POISON_FOUND" | tee -a "$REPORT_FILE"
    echo "" | tee -a "$REPORT_FILE"
    echo "RECOMMENDED ACTIONS:" | tee -a "$REPORT_FILE"
    echo "1. Review flagged files manually" | tee -a "$REPORT_FILE"
    echo "2. Verify claims against actual code" | tee -a "$REPORT_FILE"
    echo "3. Remove or annotate fabricated metrics" | tee -a "$REPORT_FILE"
    echo "4. Update contradictory documentation" | tee -a "$REPORT_FILE"
    echo "" | tee -a "$REPORT_FILE"
    echo "Full report: $REPORT_FILE" | tee -a "$REPORT_FILE"
    
    if [ "$FAIL_ON_POISON" = "true" ]; then
        exit 1
    fi
fi
