import json
import requests

def call_gemma(prompt):
    """呼叫Gemma 2 7B模型"""
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
        else:
            return f"錯誤: {response.status_code}"
    except Exception as e:
        return f"呼叫失敗: {str(e)}"

def test_ai_validation():
    """使用Gemma 2 7B測試招標驗證"""
    
    # 測試資料
    招標公告 = {
        "案號": "C13A07469",
        "案名": "進氣閥等4項採購",
        "招標方式": "公開取得報價或企劃書招標",
        "採購金額": 1493940,
        "敏感性採購": "是",
        "國安採購": "否",
        "增購權利": "是",
        "開標方式": "一次投標不分段開標",
        "外國廠商": "可",
        "適用條約": "否"
    }
    
    投標須知 = {
        "案號": "C13A07469A",
        "採購標的名稱": "進氣閥等4項採購",
        "第8點條約協定": "已勾選",
        "第13點敏感性": "未勾選",
        "第8點禁止大陸": "未勾選",
        "第7點保留增購": "未勾選",
        "第42點不分段": "未勾選",
        "第42點分二段": "已勾選"
    }
    
    prompt = f"""分析以下招標文件的一致性，找出所有問題並以JSON格式回答：

招標公告資料：
{json.dumps(招標公告, ensure_ascii=False)}

投標須知資料：
{json.dumps(投標須知, ensure_ascii=False)}

檢查規則：
1. 案號必須完全一致
2. 敏感性採購為"是"時，須知第13點敏感性應勾選，第8點應禁止大陸廠商
3. 適用條約為"否"時，須知第8點條約協定不應勾選
4. 增購權利為"是"時，須知第7點保留增購應勾選
5. 開標方式不分段時，須知第42點不分段應勾選

回答JSON格式：
{{
  "總檢查項目": 5,
  "通過項目": [],
  "失敗項目": [],
  "問題詳情": [
    {{"項次": 1, "問題": "具體問題描述"}}
  ],
  "整體結果": "通過/失敗"
}}"""
    
    print("🤖 呼叫Gemma 2 7B進行驗證分析...")
    result = call_gemma(prompt)
    
    print("\n📝 AI分析結果:")
    print(result)
    
    # 嘗試解析JSON
    try:
        json_result = json.loads(result)
        print("\n✅ JSON解析成功:")
        print(json.dumps(json_result, ensure_ascii=False, indent=2))
    except:
        print("\n❌ JSON解析失敗，嘗試提取...")
        import re
        json_match = re.search(r'\{.*\}', result, re.DOTALL)
        if json_match:
            try:
                json_result = json.loads(json_match.group())
                print("✅ 提取JSON成功:")
                print(json.dumps(json_result, ensure_ascii=False, indent=2))
            except:
                print("❌ 提取後仍無法解析JSON")

def main():
    test_ai_validation()

if __name__ == "__main__":
    main()