#!/bin/bash
source /run/media/deck/1d979ec9-f997-465f-9d38-8b32835ce1bf/miniconda3/etc/profile.d/conda.sh
cd ~/quality-dashboard

echo "Was wurde geändert? (Commit-Nachricht eingeben):"
read commit_msg

git add .
git commit -m "$commit_msg"
git push

echo ""
echo "✅ Fertig – Code ist auf GitHub."
read -p "Enter drücken zum Schließen..."
