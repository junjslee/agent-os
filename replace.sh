#!/bin/bash
find . -type f \( -name "*.md" -o -name "*.py" -o -name "*.svg" -o -name "*.json" \) \
  -not -path "*/\.git/*" -not -path "*/\.venv/*" -not -path "*/backups/*" | while read -r file; do
  sed -i '' 's/epistemic-auditor/reasoning-auditor/g' "$file"
  sed -i '' 's/ontologist/domain-architect/g' "$file"
  sed -i '' 's/ontological/structural/g' "$file"
  sed -i '' 's/Ontological/Structural/g' "$file"
  sed -i '' 's/ontology/system structure/g' "$file"
  sed -i '' 's/Ontology/System Structure/g' "$file"
  sed -i '' 's/epistemic/reasoning/g' "$file"
  sed -i '' 's/Epistemic/Reasoning/g' "$file"
  sed -i '' 's/epistemics/reasoning principles/g' "$file"
  sed -i '' 's/Epistemics/Reasoning Principles/g' "$file"
  sed -i '' 's/canonical/authoritative/g' "$file"
  sed -i '' 's/Canonical/Authoritative/g' "$file"
  sed -i '' 's/PRD_EPISTEMIC_SYNTHESIS/PRD_REASONING_SYNTHESIS/g' "$file"
done
