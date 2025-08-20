import json
import requests
import re
from typing import Dict, List, Any
import pandas as pd
from pathlib import Path

class TenderDocumentProcessor:
    def __init__(self, model_name="gemma2:7b"):
        self.model_name = model_name
        self.ollama_url = "http://localhost:11434/api/generate"
        
    def create_extraction_prompt(self) -> str:
        """建立專為 Gemma 2 7B 優化的提示詞"""
        return """從招標公告中提取資訊，以JSON格式回應。

必須提取25個項目：
案號、案名、招標方式、採購金額、預算金額、採購金級距、依據法條、決標方式、訂有底價、複數決標、依64條之2、標的分類、適用條約、敏感性採購、國安採購、增購權利、特殊採購、統包、協商措施、電子領標、押標金、優先身障、外國廠商、限定中小企業、開標方式

規則：
- 找不到填"NA"
- 數字不加引號
- 文字加引號
- 金額去除逗號和元
- 是否類填"是"或"否"

只回應JSON，格式：
{"案號":"值","案名":"值","招標方式":"值","採購金額":數值,"預算金額":數值,"採購金級距":"值","依據法條":"值","決標方式":"值","訂有底價":"是/否","複數決標":"是/否","依64條之2":"是/否","標的分類":"值","適用條約":"是/否","敏感性採購":"是/否","國安採購":"是/否","增購權利":"有/無","特殊採購":"是/否","統包":"是/否","協商措施":"是/否","電子領標":"是/否","押標金":數值,"優先身障":"是/否","外國廠商":"可/不可","限定中小企業":"是/否","開標方式":"值"}

文件內容：
"""

    def call_ollama(self, prompt: str, document_content: str) -> Dict:
        """呼叫 Ollama API"""
        full_prompt = prompt + document_content
        
        payload = {
            "model": self.model_name,
            "prompt": full_prompt,
            "stream": False,
            "temperature": 0.1,  # 降低溫度以獲得更穩定的輸出
            "top_p": 0.9,
            "format": "json"  # 強制 JSON 格式輸出
        }
        
        try:
            response = requests.post(self.ollama_url, json=payload)
            response.raise_for_status()
            result = response.json()
            
            # 提取並解析 JSON
            response_text = result.get('response', '')
            return self.parse_json_response(response_text)
            
        except Exception as e:
            print(f"API 呼叫錯誤: {e}")
            return {}
    
    def parse_json_response(self, response_text: str) -> Dict:
        """解析模型回應的 JSON"""
        try:
            # 嘗試直接解析
            return json.loads(response_text)
        except:
            # 如果失敗，嘗試提取 JSON 部分
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except:
                    pass
            
            print(f"JSON 解析失敗: {response_text[:200]}")
            return {}
    
    def process_document_by_pages(self, document_path: str, pages: List[str]) -> List[Dict]:
        """分頁處理文件"""
        results = []
        prompt = self.create_extraction_prompt()
        
        for page_num, page_content in enumerate(pages, 1):
            print(f"處理第 {page_num} 頁...")
            
            # 限制每頁內容長度（Gemma 2 7B 的上下文限制）
            if len(page_content) > 3000:
                page_content = page_content[:3000]
            
            result = self.call_ollama(prompt, page_content)
            if result:
                result['頁碼'] = page_num
                results.append(result)
                
        return results
    
    def merge_results(self, results: List[Dict]) -> Dict:
        """合併多頁結果"""
        if not results:
            return {}
        
        merged = results[0].copy()
        
        for result in results[1:]:
            for key, value in result.items():
                if key != '頁碼' and value != "NA" and merged.get(key) == "NA":
                    merged[key] = value
                    
        return merged
    
    def validate_tender_requirements(self, data: Dict) -> Dict:
        """驗證23項審核要求"""
        validation_results = {
            "通過項目": [],
            "失敗項目": [],
            "警告項目": [],
            "詳細說明": []
        }
        
        # 項次1：案號案名一致性（需要投標須知資料才能驗證）
        if data.get("案號") == "NA":
            validation_results["警告項目"].append("項次1：缺少案號資訊")
        
        # 項次2：公開取得報價金額範圍
        if "公開取得報價" in data.get("招標方式", ""):
            採購金額 = data.get("採購金額", 0)
            if isinstance(採購金額, (int, float)):
                if 150000 <= 採購金額 < 1500000:
                    validation_results["通過項目"].append("項次2：採購金額符合範圍")
                else:
                    validation_results["失敗項目"].append(f"項次2：採購金額 {採購金額} 不在15萬-150萬範圍")
            
            if data.get("採購金級距") != "未達公告金額":
                validation_results["失敗項目"].append("項次2：採購金級距應為'未達公告金額'")
            
            if data.get("依據法條") != "政府採購法第49條":
                validation_results["失敗項目"].append("項次2：依據法條應為'政府採購法第49條'")
        
        # 項次4：最低標設定
        if data.get("決標方式") == "最低標":
            if data.get("依64條之2") == "否":
                validation_results["通過項目"].append("項次4,7：最低標且非依64條之2辦理")
            else:
                validation_results["失敗項目"].append("項次4,7：最低標應為非依64條之2辦理")
        
        # 項次5：底價設定
        if data.get("訂有底價") == "是":
            validation_results["通過項目"].append("項次5：已訂底價")
        
        # 項次6：非複數決標
        if data.get("複數決標") == "否":
            validation_results["通過項目"].append("項次6：非複數決標")
        
        # 項次10-11：敏感性或國安採購
        if data.get("敏感性採購") == "是" or data.get("國安採購") == "是":
            if data.get("外國廠商") == "不可":
                validation_results["通過項目"].append("項次10-11：敏感性/國安採購已限制外國廠商")
            else:
                validation_results["失敗項目"].append("項次10-11：敏感性/國安採購應限制外國廠商參與")
        
        # 項次13-16：標準設定檢查
        standard_checks = [
            ("特殊採購", "否", "項次13"),
            ("統包", "否", "項次14"),
            ("協商措施", "否", "項次15"),
            ("電子領標", "是", "項次16")
        ]
        
        for field, expected, item in standard_checks:
            if data.get(field) == expected:
                validation_results["通過項目"].append(f"{item}：{field}設定正確")
            else:
                validation_results["失敗項目"].append(f"{item}：{field}應為'{expected}'")
        
        # 項次17：押標金
        if data.get("押標金", "NA") != "NA":
            validation_results["通過項目"].append(f"項次17：押標金已設定 {data.get('押標金')}")
        
        # 項次21：中小企業限定
        if data.get("限定中小企業") == "是":
            if data.get("外國廠商") == "不可":
                validation_results["通過項目"].append("項次21：限定中小企業且已禁止外國廠商")
            else:
                validation_results["失敗項目"].append("項次21：限定中小企業時應禁止外國廠商參與")
        
        return validation_results

    def process_tender_document(self, file_path: str) -> Dict:
        """處理完整招標文件"""
        # 讀取文件內容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 分頁處理（每3000字一頁）
        pages = [content[i:i+3000] for i in range(0, len(content), 3000)]
        
        # 處理各頁
        results = self.process_document_by_pages(file_path, pages)
        
        # 合併結果
        merged_data = self.merge_results(results)
        
        # 驗證審核要求
        validation = self.validate_tender_requirements(merged_data)
        
        return {
            "提取資料": merged_data,
            "審核結果": validation,
            "處理頁數": len(pages)
        }

# 主程式
def main():
    # 初始化處理器
    processor = TenderDocumentProcessor()
    
    # 測試單一提取
    test_content = """
    臺北大眾捷運股份有限公司公開取得報價或企劃書招標公告事項
    一、(一)案號：C14A01070
    (二)案名：束線帶等4項採購
    三、招標方式：公開取得報價或企劃書招標
    四、決標方式：(一)最低標 (二)訂有底價 (三)非複數決標
    九、(一)採購金額：NT$ 929,250
    (二)採購金額級距：未達公告金額
    十一、依據法條：政府採購法第49條
    三十四、(一)押標金：新臺幣 37,000 元
    """
    
    print("測試 Gemma 2 7B 模型提取...")
    prompt = processor.create_extraction_prompt()
    result = processor.call_ollama(prompt, test_content)
    
    print("\n提取結果:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # 驗證結果
    validation = processor.validate_tender_requirements(result)
    print("\n審核結果:")
    print(f"通過項目: {len(validation['通過項目'])} 項")
    print(f"失敗項目: {len(validation['失敗項目'])} 項")
    print(f"警告項目: {len(validation['警告項目'])} 項")
    
    for item in validation['失敗項目']:
        print(f"  ❌ {item}")
    
    for item in validation['通過項目']:
        print(f"  ✅ {item}")

if __name__ == "__main__":
    main()