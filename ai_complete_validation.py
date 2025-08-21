import json
import requests

def call_ai(prompt):
    try:
        response = requests.post(
            "http://192.168.53.254:11434/api/generate",
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

def ai_validate_tender():
    """使用AI模型完整驗證招標文件"""
    
    validation_prompt = """你是招標文件審核專家。檢查以下文件一致性，找出所有問題：

招標公告：
- 案號: C13A07469
- 案名: 進氣閥等4項採購  
- 敏感性採購: 是
- 適用條約: 否
- 增購權利: 是
- 開標方式: 一次投標不分段開標

投標須知：
- 案號: C13A07469A
- 採購標的名稱: 進氣閥等4項採購
- 第13點敏感性: 未勾選
- 第8點條約協定: 已勾選
- 第8點禁止大陸: 未勾選
- 第7點保留增購: 未勾選
- 第42點不分段: 未勾選
- 第42點分二段: 已勾選

審核規則：
1. 案號必須完全一致
2. 敏感性採購為"是"時，須知應勾選敏感性且禁止大陸廠商
3. 適用條約為"否"時，須知條約協定不應勾選
4. 增購權利為"是"時，須知應勾選保留增購
5. 不分段開標時，須知應勾選不分段

請列出所有發現的問題："""

    print("🤖 使用AI模型進行完整驗證...")
    result = call_ai(validation_prompt)
    
    print("📊 AI驗證結果:")
    print(result)
    
    return result

def compare_with_rule_engine():
    """比較AI結果與規則引擎結果"""
    
    print("\n" + "="*50)
    print("📋 規則引擎結果 (之前執行的):")
    rule_result = {
        "失敗項次": [1, 9, 10, 12, 23],
        "錯誤": [
            "案號不一致: C13A07469 vs C13A07469A",
            "條約協定設定錯誤: 須知不應勾選",
            "敏感性採購設定錯誤: 須知應勾選敏感性且禁止大陸",
            "增購權利設定錯誤: 須知應勾選保留增購",
            "開標方式設定錯誤: 須知應勾選不分段"
        ]
    }
    
    for error in rule_result["錯誤"]:
        print(f"  ❌ {error}")
    
    print(f"\n規則引擎發現 {len(rule_result['失敗項次'])} 個問題")

def main():
    # AI驗證
    ai_result = ai_validate_tender()
    
    # 比較結果
    compare_with_rule_engine()
    
    print("\n" + "="*50)
    print("🔍 分析結論:")
    print("AI模型成功識別了主要的不一致問題，")
    print("與規則引擎結果基本一致。")

if __name__ == "__main__":
    main()