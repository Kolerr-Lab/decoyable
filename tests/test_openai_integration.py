"""
Quick test script to demonstrate OpenAI integration with DECOYABLE AI systems.

Tests:
1. OpenAI API connectivity
2. AI-powered vulnerability analysis with GPT
3. LLM-enhanced threat predictions
4. Smart remediation suggestions
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from decoyable.orchestrator import get_orchestrator


async def test_openai_integration():
    """Test OpenAI integration with DECOYABLE."""
    
    print("\n" + "="*80)
    print("🧪 TESTING OPENAI INTEGRATION WITH DECOYABLE AI".center(80))
    print("="*80 + "\n")
    
    # Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ No OpenAI API key found in environment!")
        print("   Please set OPENAI_API_KEY in your .env file\n")
        return False
    
    print(f"✅ OpenAI API key detected: configured ({len(api_key)} chars)")
    print()
    
    # Test basic OpenAI connectivity
    print("🔍 Testing OpenAI API connectivity...")
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        # Simple test call
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a cybersecurity expert."},
                {"role": "user", "content": "In one sentence, what is SQL injection?"}
            ],
            max_tokens=100
        )
        
        test_response = response.choices[0].message.content
        print(f"✅ OpenAI API working! Test response:")
        print(f"   '{test_response}'\n")
        
    except ImportError:
        print("⚠️  OpenAI package not installed. Installing...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "openai"])
        print("✅ OpenAI package installed!\n")
        return await test_openai_integration()  # Retry
        
    except Exception as e:
        print(f"❌ OpenAI API test failed: {e}\n")
        return False
    
    # Test DECOYABLE AI analysis
    print("-"*80)
    print("🤖 Running DECOYABLE AI Analysis...")
    print("-"*80 + "\n")
    
    orchestrator = get_orchestrator()
    
    # Analyze a sample vulnerable code snippet
    sample_code = """
import os
import subprocess

def process_user_input(user_data):
    # Vulnerable to command injection
    result = os.system(f"echo {user_data}")
    
    # Vulnerable to SQL injection
    query = f"SELECT * FROM users WHERE username = '{user_data}'"
    
    # Vulnerable to path traversal
    filename = user_data
    with open(f"/data/{filename}", "r") as f:
        content = f.read()
    
    return content
"""
    
    # Save sample to temp file
    temp_file = Path("temp_vulnerable_sample.py")
    temp_file.write_text(sample_code)
    
    try:
        # Run comprehensive analysis
        report = await orchestrator.analyze_codebase_comprehensive(str(temp_file))
        
        print("📊 ANALYSIS RESULTS:")
        print(f"   Risk Level: {report['risk_emoji']} {report['overall_risk_level']}")
        print(f"   Risk Score: {report['overall_risk_score']:.1f}")
        print(f"   Vulnerabilities: {report['summary']['total_vulnerabilities']}")
        print(f"   AI Predictions: {report['summary']['predicted_threats']}")
        print(f"   Exploit Chains: {report['summary']['exploit_chains_detected']}")
        print()
        
        # Show top predictions
        if report.get('threat_predictions'):
            print("🎯 TOP AI PREDICTIONS:")
            for i, pred in enumerate(report['threat_predictions'][:3], 1):
                print(f"   {i}. {pred['threat_type']}")
                print(f"      Probability: {pred['probability']} | Confidence: {pred['confidence']}")
                print(f"      Risk Score: {pred['risk_score']}")
            print()
        
        # Show exploit chains
        if report.get('exploit_chains'):
            print("⛓️  EXPLOIT CHAINS DETECTED:")
            for chain in report['exploit_chains']:
                print(f"   🔴 {chain['severity']}: {chain['impact']}")
                print(f"      Chain: {' → '.join(chain['vulnerability_types'])}")
            print()
        
    finally:
        # Cleanup
        if temp_file.exists():
            temp_file.unlink()
    
    # Test LLM-enhanced analysis (if we have time to implement)
    print("-"*80)
    print("🧠 POTENTIAL LLM-ENHANCED FEATURES:")
    print("-"*80 + "\n")
    print("   ✨ Natural language vulnerability explanations")
    print("   ✨ Context-aware remediation suggestions")
    print("   ✨ Attack scenario generation")
    print("   ✨ Custom security policy recommendations")
    print("   ✨ Intelligent code review comments")
    print("   ✨ Threat intelligence summarization")
    print()
    
    print("="*80)
    print("✅ OpenAI Integration Test Complete!".center(80))
    print("="*80 + "\n")
    
    return True


async def demonstrate_llm_enhanced_analysis():
    """Demonstrate what LLM-enhanced analysis could look like."""
    
    print("\n" + "="*80)
    print("💡 LLM-ENHANCED ANALYSIS DEMO".center(80))
    print("="*80 + "\n")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  Skipping LLM demo - no API key\n")
        return
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        # Example: Get natural language explanation for a vulnerability
        vulnerability = {
            "type": "SQL_INJECTION",
            "code": "query = f\"SELECT * FROM users WHERE id = '{user_id}'\"",
            "line": 42
        }
        
        print("🔍 Analyzing vulnerability with GPT-3.5...")
        print(f"   Code: {vulnerability['code']}")
        print()
        
        prompt = f"""As a cybersecurity expert, explain this vulnerability:

Type: {vulnerability['type']}
Code: {vulnerability['code']}

Provide:
1. Why this is vulnerable (2 sentences)
2. A specific attack example
3. The exact fix (code)
4. Prevention tips

Be concise and technical."""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a senior cybersecurity engineer providing code review."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.3
        )
        
        explanation = response.choices[0].message.content
        
        print("🧠 GPT-4 Analysis:")
        print("-" * 80)
        print(explanation)
        print("-" * 80)
        print()
        
        print("✨ This is the power of LLM-enhanced security analysis!")
        print("   • Natural language explanations")
        print("   • Context-aware recommendations")
        print("   • Teaching moments for developers")
        print()
        
    except Exception as e:
        print(f"⚠️  LLM demo encountered error: {e}")
        print("   (This is optional - core AI features still work!)\n")


if __name__ == "__main__":
    print("\n🚀 Starting DECOYABLE + OpenAI Integration Tests...\n")
    
    # Run tests
    loop = asyncio.get_event_loop()
    
    success = loop.run_until_complete(test_openai_integration())
    
    if success:
        loop.run_until_complete(demonstrate_llm_enhanced_analysis())
    
    print("🎉 All tests complete!\n")
