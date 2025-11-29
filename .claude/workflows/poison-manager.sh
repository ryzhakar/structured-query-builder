#!/bin/bash
# Full Lifecycle Poison Management System
# Detect → Assess → Remediate → Verify

set -e

REPORT_FILE="${1:-.claude/poison-management-report.txt}"
MODE="${2:-assess}"  # detect | assess | remediate | verify

> "$REPORT_FILE"

echo "═══════════════════════════════════════════════════════" | tee -a "$REPORT_FILE"
echo "POISON MANAGEMENT LIFECYCLE" | tee -a "$REPORT_FILE"
echo "Date: $(date)" | tee -a "$REPORT_FILE"
echo "Mode: $MODE" | tee -a "$REPORT_FILE"
echo "═══════════════════════════════════════════════════════" | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

# Phase 1: DETECT - Run poison detector
echo "📡 PHASE 1: DETECTION" | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

.claude/workflows/poison-detector.sh "$REPORT_FILE.detection" false

# Check if poison was actually found (grep for "Poison patterns detected")
if grep -q "✅ No poison detected" "$REPORT_FILE.detection"; then
    echo "✅ No poison detected - repository is clean" | tee -a "$REPORT_FILE"
    exit 0
fi

echo "⚠️  Poison patterns detected - proceeding to assessment" | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

if [ "$MODE" = "detect" ]; then
    cat "$REPORT_FILE.detection" >> "$REPORT_FILE"
    exit 0
fi

# Phase 2: ASSESS - Classify detections
echo "🔍 PHASE 2: ASSESSMENT" | tee -a "$REPORT_FILE"
echo "Classifying detections as: REAL POISON vs FALSE POSITIVE" | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

REAL_POISON=()
FALSE_POSITIVES=()

# Analyze Pattern 1: False Confidence - Check context
echo "Analyzing Pattern 1 detections..." | tee -a "$REPORT_FILE"
while IFS= read -r file; do
    # Check if mentions are in historical/warning context
    HISTORICAL=$(grep -c "Previous.*production ready.*deprecated\|Status.*outdated\|NOT.*production" "$file" 2>/dev/null || echo 0)
    CLAIMS=$(grep -c "production.ready\|production-ready" "$file" 2>/dev/null || echo 0)

    if [ "$HISTORICAL" -gt 0 ] && [ "$CLAIMS" -eq "$HISTORICAL" ]; then
        FALSE_POSITIVES+=("$file (historical reference)")
        echo "  ✓ $file - FALSE POSITIVE (historical/warning context)" | tee -a "$REPORT_FILE"
    else
        # Check for unqualified claims
        UNQUALIFIED=$(grep -i "production.ready\|production-ready" "$file" | grep -v "Previous\|outdated\|deprecated\|NOT\|⚠️\|Status.*:" || true)
        if [ -n "$UNQUALIFIED" ]; then
            REAL_POISON+=("$file")
            echo "  ⚠️  $file - REAL POISON (unqualified claims)" | tee -a "$REPORT_FILE"
            echo "$UNQUALIFIED" | head -2 | sed 's/^/      /' | tee -a "$REPORT_FILE"
        else
            FALSE_POSITIVES+=("$file (qualified reference)")
            echo "  ✓ $file - FALSE POSITIVE (qualified/annotated)" | tee -a "$REPORT_FILE"
        fi
    fi
done < <(grep "⚠️  FOUND in:" "$REPORT_FILE.detection" -A 100 | grep "^      - " | sed 's/^      - //' | sed 's/:.*$//' || true)

echo "" | tee -a "$REPORT_FILE"

# Analyze Pattern 6: Performance Claims
echo "Analyzing Pattern 6 detections..." | tee -a "$REPORT_FILE"
PERF_FILES=$(grep -A 20 "Pattern 6: Performance Claims" "$REPORT_FILE.detection" | grep "^      - " | sed 's/^      - //' || true)
if [ -n "$PERF_FILES" ]; then
    while IFS= read -r file; do
        # Check if timing code exists
        TIMING_CODE=$(find . -name "*.py" -exec grep -l "time\.time\|timeit\|perf_counter" {} \; 2>/dev/null | wc -l)
        if [ "$TIMING_CODE" -eq 0 ]; then
            REAL_POISON+=("$file")
            echo "  ⚠️  $file - REAL POISON (no measurement code)" | tee -a "$REPORT_FILE"
        else
            FALSE_POSITIVES+=("$file (has measurement code)")
            echo "  ✓ $file - FALSE POSITIVE (measurement code exists)" | tee -a "$REPORT_FILE"
        fi
    done <<< "$PERF_FILES"
fi

echo "" | tee -a "$REPORT_FILE"
echo "Assessment Summary:" | tee -a "$REPORT_FILE"
echo "  Real poison items: ${#REAL_POISON[@]}" | tee -a "$REPORT_FILE"
echo "  False positives: ${#FALSE_POSITIVES[@]}" | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

if [ ${#REAL_POISON[@]} -eq 0 ]; then
    echo "✅ All detections are false positives - repository is functionally clean" | tee -a "$REPORT_FILE"
    exit 0
fi

if [ "$MODE" = "assess" ]; then
    echo "" | tee -a "$REPORT_FILE"
    echo "To remediate, run: $0 $REPORT_FILE remediate" | tee -a "$REPORT_FILE"
    exit 1
fi

# Phase 3: REMEDIATE - Fix real poison
echo "🔧 PHASE 3: REMEDIATION" | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

for item in "${REAL_POISON[@]}"; do
    file=$(echo "$item" | cut -d' ' -f1)
    echo "Remediating: $file" | tee -a "$REPORT_FILE"

    # Strategy: Remove unqualified claims or add annotations
    if grep -q "performance.*<.*ms\|[0-9]-[0-9]ms" "$file"; then
        echo "  → Removing fabricated performance metrics" | tee -a "$REPORT_FILE"
        # Create backup
        cp "$file" "$file.backup"
        # Remove lines with specific timing claims
        sed -i '/performance.*<.*ms\|[0-9]-[0-9]ms/d' "$file"
    fi

    # Add warning annotation if unqualified "production ready" found
    if grep -qi "^.*production.ready" "$file" | grep -qv "Previous\|outdated\|NOT"; then
        echo "  → Adding deprecation warning" | tee -a "$REPORT_FILE"
        # Prepend warning to file
        echo "> ⚠️ **Status Claims Deprecated**: Any 'production ready' claims in this file are outdated." > "$file.tmp"
        echo "> See AGENT_HANDOFF.md for current accurate status." >> "$file.tmp"
        echo "" >> "$file.tmp"
        cat "$file" >> "$file.tmp"
        mv "$file.tmp" "$file"
    fi
done

echo "" | tee -a "$REPORT_FILE"
echo "Remediation complete. Backed up files to *.backup" | tee -a "$REPORT_FILE"

if [ "$MODE" = "remediate" ]; then
    echo "" | tee -a "$REPORT_FILE"
    echo "To verify cleanup, run: $0 $REPORT_FILE verify" | tee -a "$REPORT_FILE"
    exit 0
fi

# Phase 4: VERIFY - Confirm cleanup
echo "" | tee -a "$REPORT_FILE"
echo "🔬 PHASE 4: VERIFICATION" | tee -a "$REPORT_FILE"
echo "" | tee -a "$REPORT_FILE"

# Re-run detector
.claude/workflows/poison-detector.sh "$REPORT_FILE.verification" false
VERIFY_RESULT=$?

if [ "$VERIFY_RESULT" -eq 0 ]; then
    echo "✅ VERIFICATION PASSED - Repository is clean" | tee -a "$REPORT_FILE"
    # Clean up backups
    find . -name "*.backup" -delete 2>/dev/null || true
    exit 0
else
    echo "⚠️  VERIFICATION FAILED - Poison still detected" | tee -a "$REPORT_FILE"
    echo "Manual intervention required" | tee -a "$REPORT_FILE"
    cat "$REPORT_FILE.verification" >> "$REPORT_FILE"
    exit 1
fi
