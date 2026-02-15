
# 测试导入
try:
    from app.llm import engine
    print("✅ 导入成功")
except Exception as e:
    print(f"❌ 导入失败: {e}")
    import traceback
    traceback.print_exc()
