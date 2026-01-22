#!/bin/bash

SKILLS_DIR="$HOME/.snowflake/cortex/skills"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

mkdir -p "$SKILLS_DIR"

for skill in "$SCRIPT_DIR"/skills/*/; do
    skill_name=$(basename "$skill")
    echo "Installing skill: $skill_name"
    cp -r "$skill" "$SKILLS_DIR/"
done

echo ""
echo "Installed skills to: $SKILLS_DIR"
echo "Reload Cortex Code (Cmd+Shift+P -> 'Reload Window') to use the new skills."
