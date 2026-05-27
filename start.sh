#!/bin/bash
source /run/media/deck/1d979ec9-f997-465f-9d38-8b32835ce1bf/miniconda3/etc/profile.d/conda.sh
conda activate qualitydash
cd ~/quality-dashboard
flatpak run com.visualstudio.code
streamlit run app.py
