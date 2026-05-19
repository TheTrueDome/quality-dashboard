#!/bin/bash
source ~/miniconda3/etc/profile.d/conda.sh
conda activate qualitydash
cd ~/quality-dashboard
code .
streamlit run app.py

