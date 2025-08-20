import json
import requests

def call_ai(prompt):
    try:
        response = requests.post(
            "http://192.168.53.14:11434/api/generate",
            json={
                "model": "gpt-oss:latest",
                "prompt": prompt,
                "stream": False,
                "temperature": 0.1
            }
        )
        if response.status_code == 200:
            return response.json().get('response', '')
        return f"錯誤: {response.status_code}"
    except Exception as e:
        return f"失敗: {str(e)}"

def main():
    # 簡化測試
    prompt = """檢查這兩個案號是否一致：
公告案號: C13A07469
須知案號: C13A07469A

只回答: 一致 或 不一致"""
    
    print("測試AI模型分析...")
    result = call_ai(prompt)
    print(f"AI回答: {result}")
    
    # 測試2: 敏感性採購邏輯
    prompt2 = """敏感性採購設為"是"，但須知未勾選敏感性選項且允許大陸廠商參與。這樣對嗎？
只回答: 對 或 錯"""
    
    result2 = call_ai(prompt2)
    print(f"敏感性採購檢查: {result2}")
    
    # 測試3: 開標方式
    prompt3 = """公告說"一次投標不分段開標"，須知勾選"分二段開標"。一致嗎？
只回答: 一致 或 不一致"""
    
    result3 = call_ai(prompt3)
    print(f"開標方式檢查: {result3}")

if __name__ == "__main__":
    main()