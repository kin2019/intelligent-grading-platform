#!/usr/bin/env python3
"""测试路由导入"""

import sys
import traceback

def test_imports():
    print("Testing individual module imports...")
    
    try:
        from app.api.v1 import auth
        print("[OK] auth module imported successfully")
    except Exception as e:
        print(f"[ERROR] auth module failed: {e}")
        traceback.print_exc()
    
    try:
        from app.api.v1 import homework
        print("[OK] homework module imported successfully")
    except Exception as e:
        print(f"[ERROR] homework module failed: {e}")
        traceback.print_exc()
    
    try:
        from app.api.v1 import student
        print("[OK] student module imported successfully")
    except Exception as e:
        print(f"[ERROR] student module failed: {e}")
        traceback.print_exc()
    
    try:
        from app.api.v1 import image
        print("[OK] image module imported successfully")
    except Exception as e:
        print(f"[ERROR] image module failed: {e}")
        traceback.print_exc()
    
    print("\nTesting router import...")
    try:
        from app.api.v1.router import api_router
        print(f"[OK] router imported successfully with {len(api_router.routes)} routes")
        
        print("\nAll routes:")
        for route in api_router.routes:
            print(f"  {route.path} {route.methods}")
            
    except Exception as e:
        print(f"[ERROR] router import failed: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_imports()