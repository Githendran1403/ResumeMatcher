#!/usr/bin/env python
"""
Download required NLTK data
Run this script once to download the necessary NLTK datasets
"""

import nltk
import sys

def download_nltk_data():
    """Download required NLTK datasets"""
    try:
        print("Downloading NLTK stopwords...")
        nltk.download('stopwords', quiet=True)
        print("✓ Stopwords downloaded")
        
        print("Downloading NLTK punkt tokenizer...")
        nltk.download('punkt', quiet=True)
        print("✓ Punkt tokenizer downloaded")
        
        print("✓ All NLTK data downloaded successfully!")
        return True
        
    except Exception as e:
        print(f"Error downloading NLTK data: {e}")
        return False

if __name__ == "__main__":
    success = download_nltk_data()
    sys.exit(0 if success else 1)
