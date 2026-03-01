"""Test script to verify Gemini API is working."""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Test Gemini API
try:
    import google.generativeai as genai
    
    api_key = os.environ.get('GEMINI_API_KEY')
    model_name = os.environ.get('GEMINI_MODEL', 'gemini-2.5-flash')
    
    print(f"API Key: {api_key[:10]}..." if api_key else "No API key found")
    print(f"Model: {model_name}")
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)
    
    print("\nTesting API call...")
    response = model.generate_content("Say hello in one word")
    print(f"Response: {response.text}")
    print("\n✓ Gemini API is working!")
    
except Exception as e:
    print(f"\n✗ Error: {str(e)}")
    print(f"Error type: {type(e).__name__}")
