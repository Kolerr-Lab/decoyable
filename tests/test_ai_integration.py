"""
Test script for AI integration with all providers.
Tests: Ollama (Gemma 3:12b), OpenAI, Phi-3, Pattern-based
"""

import asyncio
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from decoyable.llm.model_router import get_router

# Test vulnerable code sample
VULNERABLE_CODE = '''
import os
import sqlite3

def get_user_data(user_id):
    # SQL Injection vulnerability
    query = f"SELECT * FROM users WHERE id = {user_id}"
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

def run_command(cmd):
    # Command injection vulnerability
    os.system(f"ping -c 1 {cmd}")
    
def get_api_key():
    # Hardcoded secret
    api_key = "sk-1234567890abcdef"
    return api_key
'''


async def test_ai_providers():
    """Test all AI providers."""
    print("\n" + "="*60)
    print("🤖 TESTING DECOYABLE AI INTEGRATION")
    print("="*60 + "\n")
    
    # Get router instance
    router = get_router()
    
    # Print status
    print("📊 AVAILABLE PROVIDERS:")
    router.print_status()
    
    print("\n" + "="*60)
    print("🧪 TESTING AI ANALYSIS ON VULNERABLE CODE")
    print("="*60 + "\n")
    
    print("📝 Test Code:")
    print("-" * 40)
    print(VULNERABLE_CODE[:200] + "...")
    print("-" * 40 + "\n")
    
    # Test analysis
    print("🔍 Running AI analysis...")
    
    try:
        result = await router.analyze(
            code=VULNERABLE_CODE,
            context={
                "file": "test.py",
                "framework": "flask"
            },
            task="security_analysis"
        )
        
        if result:
            print("\n✅ AI ANALYSIS COMPLETE!")
            print("="*60)
            
            # Show provider used
            provider = result.get("_provider", "unknown")
            cost = result.get("_cost", 0.0)
            local = result.get("_local", False)
            
            print(f"\n🤖 Provider Used: {provider.upper()}")
            print(f"💰 Cost: ${cost:.4f}")
            print(f"🔒 Local: {'Yes' if local else 'No'}")
            
            # Show vulnerabilities found
            vulns = result.get("vulnerabilities", [])
            print(f"\n🎯 Vulnerabilities Found: {len(vulns)}")
            
            for i, vuln in enumerate(vulns, 1):
                print(f"\n  {i}. {vuln.get('type', 'Unknown')}")
                print(f"     Severity: {vuln.get('severity', 'Unknown')}")
                print(f"     Confidence: {vuln.get('confidence', 0)*100:.0f}%")
                desc = vuln.get('description', 'No description')
                print(f"     Description: {desc[:100]}...")
            
            # Show risk score
            risk = result.get("risk_score", 0)
            print(f"\n📊 Overall Risk Score: {risk}/100")
            
            # Show summary
            summary = result.get("summary", "No summary available")
            print(f"\n📝 Summary:")
            print(f"   {summary[:200]}...")
            
            # Show recommendations
            recs = result.get("recommendations", [])
            if recs:
                print(f"\n💡 Recommendations:")
                for i, rec in enumerate(recs[:3], 1):
                    print(f"   {i}. {rec[:100]}...")
            
            print("\n" + "="*60)
            print("✅ TEST SUCCESSFUL!")
            print("="*60)
            
        else:
            print("\n❌ Analysis returned no results")
            
    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()


async def test_ollama_direct():
    """Test Ollama directly."""
    print("\n" + "="*60)
    print("🦙 TESTING OLLAMA + GEMMA 3:12B DIRECTLY")
    print("="*60 + "\n")
    
    from decoyable.llm.ollama_client import OllamaClient
    
    client = OllamaClient()
    
    print(f"Model: {client.model}")
    print(f"Available: {client.available}")
    print(f"Base URL: {client.base_url}\n")
    
    if client.available:
        print("✅ Ollama is running!")
        
        # Get available models
        models = client.get_available_models()
        print(f"\n📦 Available Models ({len(models) if isinstance(models, list) else 0}):")
        if isinstance(models, list):
            for model in models:
                if isinstance(model, dict):
                    name = model.get('name', 'Unknown')
                    size = model.get('size', 0) / (1024**3)  # Convert to GB
                    params = model.get('details', {}).get('parameter_size', 'Unknown')
                    print(f"  - {name} ({size:.1f}GB, {params})")
                else:
                    print(f"  - {model}")
        
        print("\n🧪 Testing quick analysis...")
        result = await client.analyze_security(
            code="password = '123456'  # Hardcoded password",
            task="security_analysis"
        )
        
        if result:
            print("✅ Analysis successful!")
            print(f"Found {len(result.get('vulnerabilities', []))} issues")
        else:
            print("❌ Analysis failed")
    else:
        print("❌ Ollama is not available")


if __name__ == "__main__":
    print("\n🚀 DECOYABLE v1.2.0 - AI Integration Test\n")
    
    # Run tests
    asyncio.run(test_ollama_direct())
    asyncio.run(test_ai_providers())
    
    print("\n✅ All tests complete!\n")
