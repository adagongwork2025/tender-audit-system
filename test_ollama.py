#!/usr/bin/env python3
"""測試 Ollama API 連線"""

import requests
import json

def test_ollama_connection():
    """測試 Ollama API 是否正常運作"""
    ollama_url = "http://192.168.53.14:11434"
    
    print(f"🔍 測試 Ollama API: {ollama_url}")
    print("="*50)
    
    # 1. 測試基本連線
    try:
        response = requests.get(f"{ollama_url}/")
        if response.status_code == 200:
            print("✅ Ollama 服務正在運行")
        else:
            print(f"❌ 連線失敗: HTTP {response.status_code}")
            return
    except Exception as e:
        print(f"❌ 無法連接到 Ollama: {e}")
        return
    
    # 2. 列出可用模型
    try:
        response = requests.get(f"{ollama_url}/api/tags")
        if response.status_code == 200:
            data = response.json()
            models = data.get('models', [])
            print(f"\n📋 可用模型數量: {len(models)}")
            for model in models:
                print(f"   - {model['name']} ({model['details']['parameter_size']})")
    except Exception as e:
        print(f"❌ 無法取得模型列表: {e}")
    
    # 3. 測試模型推理
    print("\n🤖 測試模型推理...")
    model_name = "gpt-oss:latest"
    prompt = "請用一句話說明什麼是招標文件檢核？"
    
    try:
        response = requests.post(
            f"{ollama_url}/api/generate",
            json={
                "model": model_name,
                "prompt": prompt,
                "stream": False
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 模型回應成功")
            print(f"📝 提問: {prompt}")
            print(f"💬 回答: {result.get('response', '無回應')}")
            print(f"⏱️  生成時間: {result.get('total_duration', 0) / 1e9:.2f} 秒")
        else:
            print(f"❌ 模型推理失敗: HTTP {response.status_code}")
            print(f"錯誤訊息: {response.text}")
    except Exception as e:
        print(f"❌ 模型推理錯誤: {e}")
    
    # 4. 測試對話功能
    print("\n💬 測試對話功能...")
    try:
        response = requests.post(
            f"{ollama_url}/api/chat",
            json={
                "model": model_name,
                "messages": [
                    {"role": "user", "content": "你好，請介紹你自己"}
                ],
                "stream": False
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            message = result.get('message', {})
            print(f"✅ 對話功能正常")
            print(f"🤖 助手回應: {message.get('content', '無回應')}")
        else:
            print(f"❌ 對話功能失敗: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ 對話功能錯誤: {e}")

if __name__ == "__main__":
    test_ollama_connection()