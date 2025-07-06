#!/usr/bin/env python3
"""
Startup script to preload heavy dependencies
"""
import os
import sys

print("Preloading dependencies...")

# Set environment variables to reduce memory usage
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['MKL_NUM_THREADS'] = '1'
os.environ['OPENBLAS_NUM_THREADS'] = '1'

# Import heavy libraries during startup
try:
    print("Loading PyTorch...")
    import torch
    torch.set_num_threads(1)
    print("PyTorch loaded successfully")
except Exception as e:
    print(f"Warning: Could not load PyTorch: {e}")

try:
    print("Loading transformers...")
    import transformers
    print("Transformers loaded successfully")
except Exception as e:
    print(f"Warning: Could not load transformers: {e}")

print("Preloading complete!")