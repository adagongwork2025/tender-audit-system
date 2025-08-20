import json
import requests

def create_item23_ai_prompt():
    """專門針對項次23的AI分析提示詞"""
    return """
你是招標開標方式審核專家。請分析開標方式的設定是否一致。

關鍵邏輯規則：
1. 開標方式只能二選一：
   - 不分段開標：所有文件一次開標審查
   - 分段開標：分階段審查（資格→規格→價格）

2. 對應關係必須一致：
   不分段 = 第42點(一)(一) + 第55點(一)
   分段 = 第42點(一)(二) + 第55點(二) + 子項目

3. 互斥規則：
   - 第55點(一)和(二)不能同時勾選
   - 第42點(一)(一)和(一)(二)不能同時勾選

請分析以下資料：
招標公告開標方式：{opening_method}
投標須知勾選情況：{requirements}

判斷：
1. 是否有矛盾勾選？
2. 是否有遺漏勾選？
3. 邏輯是否一致？

回應格式：
{{
  "開標方式判定": "不分段/分段",
  "第42點正確性": "正確/錯誤",
  "第55點正確性": "正確/錯誤",
  "矛盾項目": [],
  "修正建議": "",
  "風險評估": "高/中/低"
}}
"""

def call_ai_model(prompt):
    """呼叫AI模型"""
    try:
        response = requests.post(
            "http://192.168.53.14:11434/api/generate",
            json={
                "model": "gemma3:27b",
                "prompt": prompt,
                "stream": False,
                "temperature": 0.1,
                "format": "json"
            }
        )
        if response.status_code == 200:
            return response.json().get('response', '')
        return f"錯誤: {response.status_code}"
    except Exception as e:
        return f"失敗: {str(e)}"

def test_item23_validation():
    """測試項次23的AI驗證"""
    
    # 測試案例1：實際的C13A07469案例
    test_case_1 = {
        "opening_method": "一次投標不分段開標",
        "requirements": {
            "第42點不分段": "未勾選",
            "第42點分二段": "已勾選",
            "第55點(一)": "未知",  # 沒有這個資料
            "第55點(二)": "未知"   # 沒有這個資料
        }
    }
    
    prompt_template = create_item23_ai_prompt()
    prompt = prompt_template.format(
        opening_method=test_case_1["opening_method"],
        requirements=json.dumps(test_case_1["requirements"], ensure_ascii=False)
    )
    
    print("🔍 測試項次23 AI驗證 - 案例1")
    print(f"公告開標方式: {test_case_1['opening_method']}")
    print(f"須知勾選: {test_case_1['requirements']}")
    print("\n🤖 AI分析中...")
    
    result = call_ai_model(prompt)
    print("\n📊 AI分析結果:")
    print(result)
    
    # 嘗試解析JSON
    try:
        json_result = json.loads(result)
        print("\n✅ 結構化結果:")
        print(json.dumps(json_result, ensure_ascii=False, indent=2))
    except:
        print("\n⚠️ JSON解析失敗，但AI回應已顯示")
    
    # 測試案例2：正確的不分段設定
    print("\n" + "="*60)
    print("🔍 測試項次23 AI驗證 - 案例2（正確設定）")
    
    test_case_2 = {
        "opening_method": "一次投標不分段開標", 
        "requirements": {
            "第42點不分段": "已勾選",
            "第42點分二段": "未勾選",
            "第55點(一)": "已勾選",
            "第55點(二)": "未勾選"
        }
    }
    
    prompt2 = prompt_template.format(
        opening_method=test_case_2["opening_method"],
        requirements=json.dumps(test_case_2["requirements"], ensure_ascii=False)
    )
    
    result2 = call_ai_model(prompt2)
    print("📊 AI分析結果 (正確設定):")
    print(result2)

def main():
    test_item23_validation()

if __name__ == "__main__":
    main()