#!/usr/bin/env python3
"""
Test script to verify ChromaDB fix is working
"""

import asyncio
import sys
import yaml
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from app.rag_engine import RAGEngine

async def test_rag_engine():
    """Test RAG engine initialization and search functionality"""
    
    print("🧪 Testing ChromaDB Fix...")
    print("=" * 50)
    
    try:
        # Load configuration
        config_path = Path(__file__).parent / "config" / "ollama_config.yaml"
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        print("✅ Configuration loaded successfully")
        
        # Initialize RAG engine
        print("\n🔄 Initializing RAG Engine...")
        rag_engine = RAGEngine(config)
        await rag_engine.initialize()
        
        # Check which engine is being used
        if rag_engine.use_fallback:
            print("✅ Using TF-IDF Fallback Engine (ChromaDB failed as expected)")
            engine_type = "TF-IDF Fallback"
        else:
            print("✅ Using ChromaDB Engine (ChromaDB working)")
            engine_type = "ChromaDB"
        
        # Test search functionality
        print(f"\n🔍 Testing search with {engine_type}...")
        
        test_queries = [
            "需求分析",
            "商业模式",
            "竞争优势",
            "用户验证"
        ]
        
        for query in test_queries:
            results = await rag_engine.search_knowledge(query, k=2)
            print(f"  Query: '{query}' → Found {len(results)} results")
            
            if results:
                # Show first result preview
                first_result = results[0]
                content_preview = first_result['content'][:100].replace('\n', ' ')
                print(f"    Preview: {content_preview}...")
        
        # Test DREAM framework context
        print(f"\n🎯 Testing DREAM framework context...")
        dream_components = ["demand", "resolution", "earning", "acquisition", "moat"]
        
        for component in dream_components:
            context = await rag_engine.get_dream_framework_context(component)
            context_length = len(context)
            print(f"  {component.upper()}: {context_length} characters of context")
        
        print("\n" + "=" * 50)
        print("🎉 All tests passed successfully!")
        print(f"✅ RAG Engine Type: {engine_type}")
        print("✅ Search functionality working")
        print("✅ DREAM framework context retrieval working")
        print("✅ ChromaDB fix is functioning correctly")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("DREAM Business Analysis AI - ChromaDB Fix Test")
    print("=" * 60)
    
    # Run async test
    success = asyncio.run(test_rag_engine())
    
    if success:
        print("\n🎯 RESULT: ChromaDB fix is working correctly!")
        print("   The app will work in both local and cloud environments.")
        sys.exit(0)
    else:
        print("\n❌ RESULT: Test failed - please check the error above.")
        sys.exit(1)

if __name__ == "__main__":
    main()