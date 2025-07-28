#!/usr/bin/env python3
"""
重建向量数据库脚本
包含中英文内容
"""

import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from app.rag_engine import RAGEngine

def main():
    print("🔄 重建向量数据库...")
    print("=" * 50)
    
    # 删除现有向量数据库
    vectordb_path = Path("data/vectordb")
    if vectordb_path.exists():
        import shutil
        shutil.rmtree(vectordb_path)
        print("✅ 已删除现有向量数据库")
    
    # 初始化RAG引擎
    try:
        rag_engine = RAGEngine()
        data_dirs = ["data/knowledge", "data/faq", "data/ebook_summary"]
        
        print("📚 加载知识库文件...")
        success = rag_engine.initialize_rag(data_dirs, force_rebuild=True)
        
        if success:
            print("✅ 向量数据库重建成功！")
            print("📊 数据库包含中英文内容")
            
            # 测试检索
            print("\n🔍 测试检索功能...")
            
            # 测试中文检索
            chinese_docs = rag_engine.retrieve_documents("新生儿喂养")
            print(f"中文检索结果: {len(chinese_docs)} 个文档")
            
            # 测试英文检索
            english_docs = rag_engine.retrieve_documents("newborn feeding")
            print(f"英文检索结果: {len(english_docs)} 个文档")
            
            print("\n🎉 向量数据库重建完成！")
            print("💡 现在可以重启系统: python start.py")
            
        else:
            print("❌ 向量数据库重建失败")
            return False
            
    except Exception as e:
        print(f"❌ 重建过程出错: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    main()