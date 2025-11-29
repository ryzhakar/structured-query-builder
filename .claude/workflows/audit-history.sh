#!/bin/bash

# Repository audit data extraction script
# Creates a structured directory tree with complete commit history data

set -e

AUDIT_DIR="/tmp/repo_audit"
rm -rf "$AUDIT_DIR"
mkdir -p "$AUDIT_DIR"

# Get all commits in chronological order (oldest first)
mapfile -t COMMITS < <(git rev-list --reverse HEAD)

echo "Total commits to process: ${#COMMITS[@]}"

# Counter for enumeration
counter=1

for commit in "${COMMITS[@]}"; do
    # Create zero-padded directory name
    dir_name=$(printf "%02d_%s" $counter "${commit:0:7}")
    commit_dir="$AUDIT_DIR/$dir_name"
    mkdir -p "$commit_dir"

    echo "Processing [$counter/${#COMMITS[@]}]: $commit"

    # 1. Export full commit message
    git log -1 --format=%B "$commit" > "$commit_dir/commit_message.txt"

    # 2. Export commit metadata (author, date, hash)
    {
        echo "Commit: $commit"
        echo "Author: $(git log -1 --format='%an <%ae>' "$commit")"
        echo "Date: $(git log -1 --format='%ai' "$commit")"
        echo "---"
    } > "$commit_dir/metadata.txt"

    # 3. Export files changed with stats
    git show --stat --format="" "$commit" > "$commit_dir/files_changed.txt"

    # 4. Get list of changed files
    git diff-tree --no-commit-id --name-only -r "$commit" > "$commit_dir/files_list.txt"

    # 5. Export full diffs of DOCUMENTATION files
    # Identifying documentation by common patterns: .md, .txt, .rst, docs/, README, etc.
    doc_files=$(git diff-tree --no-commit-id --name-only -r "$commit" | \
                grep -iE '\.(md|txt|rst|adoc|markdown)$|^docs/|README|CHANGELOG|LICENSE|CONTRIBUTING' || true)

    if [ -n "$doc_files" ]; then
        echo "=== DOCUMENTATION FILE DIFFS ===" > "$commit_dir/doc_diffs.txt"
        echo "" >> "$commit_dir/doc_diffs.txt"

        while IFS= read -r file; do
            if [ -n "$file" ]; then
                echo "===================================================" >> "$commit_dir/doc_diffs.txt"
                echo "FILE: $file" >> "$commit_dir/doc_diffs.txt"
                echo "===================================================" >> "$commit_dir/doc_diffs.txt"

                # Get the full diff for this file
                git show "$commit" -- "$file" >> "$commit_dir/doc_diffs.txt" 2>/dev/null || echo "[File not accessible]" >> "$commit_dir/doc_diffs.txt"

                echo "" >> "$commit_dir/doc_diffs.txt"
                echo "" >> "$commit_dir/doc_diffs.txt"
            fi
        done <<< "$doc_files"
    else
        echo "No documentation files changed in this commit." > "$commit_dir/doc_diffs.txt"
    fi

    # 6. Export source file changes overview (filenames and types only, no diffs)
    source_files=$(git diff-tree --no-commit-id --name-only -r "$commit" | \
                   grep -viE '\.(md|txt|rst|adoc|markdown)$|^docs/|README|CHANGELOG|LICENSE|CONTRIBUTING' || true)

    if [ -n "$source_files" ]; then
        echo "=== SOURCE FILES MODIFIED ===" > "$commit_dir/source_files.txt"
        while IFS= read -r file; do
            if [ -n "$file" ]; then
                # Get line counts for source files
                additions=$(git show --numstat "$commit" -- "$file" 2>/dev/null | awk '{print $1}' || echo "?")
                deletions=$(git show --numstat "$commit" -- "$file" 2>/dev/null | awk '{print $2}' || echo "?")
                echo "$file (+$additions -$deletions)" >> "$commit_dir/source_files.txt"
            fi
        done <<< "$source_files"
    else
        echo "No source files changed in this commit." > "$commit_dir/source_files.txt"
    fi

    counter=$((counter + 1))
done

echo ""
echo "Extraction complete! Data stored in: $AUDIT_DIR"
echo "Total commits processed: ${#COMMITS[@]}"
ls -1 "$AUDIT_DIR"
