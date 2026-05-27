#!/bin/bash
source /run/media/deck/1d979ec9-f997-465f-9d38-8b32835ce1bf/miniconda3/etc/profile.d/conda.sh

cd /home/deck/quality-dashboard || { echo "❌ Verzeichnis nicht gefunden."; read -p "Enter drücken..."; exit 1; }

echo "Was wurde geändert? (Commit-Nachricht eingeben):"
read commit_msg

if [ -z "$commit_msg" ]; then
    echo "❌ Keine Commit-Nachricht eingegeben – abgebrochen."
    read -p "Alt+F4 drücken zum Schließen..."
    exit 1
fi

git add .
git commit -m "$commit_msg"

if git push; then
    echo ""
    echo "✅ Fertig – Code ist auf GitHub."
else
    echo ""
    echo "❌ Push fehlgeschlagen – Token prüfen."
fi

read -p "Alt+F4 drücken zum Schließen..."