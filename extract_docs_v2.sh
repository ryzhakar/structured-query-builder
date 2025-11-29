#!/bin/bash
# Extract all documentation files from each commit

OUTPUT_DIR="/tmp/audit_docs_v2"
rm -rf "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR"

# Get all commits in chronological order
COMMITS=$(git log --all --oneline --reverse | awk '{print $1}')

commit_num=0
for commit in $COMMITS; do
  commit_num=$((commit_num + 1))
  commit_short=$(echo "$commit" | cut -c1-7)
  commit_dir="$OUTPUT_DIR/commit_$(printf '%02d' $commit_num)_$commit_short"
  mkdir -p "$commit_dir"

  # Save commit message
  git log -1 --format="Commit: %H%nAuthor: %an <%ae>%nDate: %ai%nSubject: %s%n%nMessage:%n%b" "$commit" > "$commit_dir/00_COMMIT_INFO.txt"

  # Get all files that exist in this commit (not just changed)
  doc_files=$(git ls-tree -r --name-only "$commit" | grep -E '\.(md|txt|yaml|yml|rst|json)$' | grep -v node_modules | grep -v '.venv' || true)

  if [ -z "$doc_files" ]; then
    echo "No documentation files in this commit" > "$commit_dir/01_NO_DOCS.txt"
    continue
  fi

  # Save list of doc files
  echo "$doc_files" > "$commit_dir/01_DOC_FILES_LIST.txt"

  # Extract each doc file
  file_num=1
  echo "$doc_files" | while read -r filepath; do
    if [ -n "$filepath" ]; then
      safe_name=$(echo "$filepath" | tr '/' '_')
      padded_num=$(printf '%02d' $file_num)
      git show "$commit:$filepath" > "$commit_dir/${padded_num}_${safe_name}" 2>/dev/null || echo "Error extracting" > "$commit_dir/${padded_num}_${safe_name}.error"
      file_num=$((file_num + 1))
    fi
  done
done

echo "==== EXTRACTION COMPLETE ===="
echo "Output directory: $OUTPUT_DIR"
echo ""
echo "Commits processed:"
ls -1d "$OUTPUT_DIR"/commit_* | wc -l
echo ""
echo "Total files extracted:"
find "$OUTPUT_DIR" -type f -name "*.md" -o -name "*.txt" -o -name "*.yaml" -o -name "*.yml" | wc -l
