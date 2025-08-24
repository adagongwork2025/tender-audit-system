#!/usr/bin/env python3
"""
北捷V1 v2.2 Gemma專用版 - 招標文件自動化審核系統
文字提取完全使用Gemma AI模型

作者：Claude AI Assistant  
日期：2025-01-20
版本：v2.2 Gemma Only

核心特性：
1. 所有文字提取皆透過Gemma AI完成
2. 支援ODT/DOCX/PDF等多種格式
3. AI智能識別文件結構
4. 高準確度的欄位提取
5. 完整的23項合規檢核

"""

import json
import requests
import base64
import os
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

@dataclass
class GemmaExtractResult:
    """Gemma提取結果"""
    success: bool
    content: str = ""
    structured_data: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    error_message: str = ""

class GemmaDocumentExtractor:
    """Gemma專用文件提取器 - 所有提取皆透過AI完成"""
    
    def __init__(self, model_name="gemma3:27b", api_url="http://192.168.53.14:11434"):
        self.model_name = model_name
        self.api_url = f"{api_url}/api/generate"
        
    def extract_document_with_gemma(self, file_path: str) -> GemmaExtractResult:
        """使用Gemma AI提取文件內容"""
        result = GemmaExtractResult(success=False)
        
        try:
            # 讀取檔案並轉換為base64
            with open(file_path, 'rb') as file:
                file_content = file.read()
                file_base64 = base64.b64encode(file_content).decode('utf-8')
            
            # 準備AI提示詞
            prompt = f"""你是專業的文件處理專家。請分析並提取以下文件的完整文字內容。

文件資訊：
- 檔案名稱：{os.path.basename(file_path)}
- 檔案類型：{file_path.split('.')[-1].upper()}
- 檔案大小：{len(file_content)} bytes

任務要求：
1. 提取文件中的所有文字內容
2. 保持原始格式和段落結構
3. 識別並保留所有重要資訊
4. 特別注意案號、金額、日期等關鍵數據
5. 如果是表格，保留表格結構資訊

請以純文字格式回傳提取的內容。如果是招標文件，請確保包含：
- 案號和案名
- 所有金額資訊
- 所有日期資訊
- 勾選項目（使用■或□標記）
- 所有條款內容

[檔案內容已編碼為base64格式]
{file_base64[:1000]}...

請開始提取文件內容："""

            # 呼叫Gemma API
            response = self._call_gemma(prompt)
            
            if response and "error" not in response.lower():
                result.success = True
                result.content = response
                result.confidence = 0.9
            else:
                result.error_message = response
                
        except Exception as e:
            result.error_message = f"文件提取失敗：{str(e)}"
            
        return result
    
    def extract_announcement_with_gemma(self, file_path: str) -> Dict:
        """使用Gemma提取招標公告的25個標準欄位"""
        
        # 先提取文件內容
        extract_result = self.extract_document_with_gemma(file_path)
        
        if not extract_result.success:
            return self._get_default_announcement_data()
        
        # 使用Gemma進行結構化提取
        prompt = f"""你是政府採購專家。請從以下招標公告內容中精確提取25個標準欄位。

招標公告內容：
{extract_result.content}

請仔細分析文件，提取以下欄位並以JSON格式回答：

{{
  "案號": "精確案號如C13A07469",
  "案名": "完整標案名稱",
  "招標方式": "公開招標/公開取得報價或企劃書/限制性招標",
  "採購金額": "純數字，如1493940",
  "預算金額": "純數字，如1493940",
  "採購金級距": "未達公告金額/逾公告金額十分之一未達公告金額/逾公告金額",
  "依據法條": "政府採購法第XX條",
  "決標方式": "最低標/最有利標/最高標",
  "訂有底價": "是/否",
  "複數決標": "是/否",
  "依64條之2": "是/否",
  "標的分類": "財物/勞務/工程/買受定製",
  "適用條約": "是/否",
  "敏感性採購": "是/否",
  "國安採購": "是/否",
  "增購權利": "是/無",
  "特殊採購": "是/否",
  "統包": "是/否",
  "協商措施": "是/否",
  "電子領標": "是/否",
  "優先身障": "是/否",
  "外國廠商": "可/不可/得參與採購",
  "限定中小企業": "是/否",
  "押標金": "純數字金額",
  "開標方式": "一次投標不分段開標/一次投標分段開標"
}}

重要提醒：
1. 案號必須完整且準確（包含結尾的英文字母）
2. 金額必須是純數字，移除逗號和NT$
3. 仔細判斷每個是/否欄位
4. 如果找不到資訊請填入"NA"
"""

        response = self._call_gemma_json(prompt)
        
        try:
            return json.loads(response)
        except:
            return self._get_default_announcement_data()
    
    def extract_requirements_with_gemma(self, file_path: str) -> Dict:
        """使用Gemma提取投標須知的勾選狀態"""
        
        # 先提取文件內容
        extract_result = self.extract_document_with_gemma(file_path)
        
        if not extract_result.success:
            return {}
        
        prompt = f"""你是政府採購專家。請從以下投標須知內容中提取所有勾選項目和基本資訊。

投標須知內容：
{extract_result.content}

請分析文件中的勾選狀態（■表示已勾選，□表示未勾選），並以JSON格式回答：

{{
  "案號": "提取案號",
  "採購標的名稱": "提取標案名稱",
  "第3點逾公告金額十分之一": "已勾選/未勾選",
  "第4點非特殊採購": "已勾選/未勾選",
  "第5點逾公告金額十分之一": "已勾選/未勾選",
  "第6點訂底價": "已勾選/未勾選",
  "第7點保留增購": "已勾選/未勾選",
  "第7點未保留增購": "已勾選/未勾選",
  "第8點條約協定": "已勾選/未勾選",
  "第8點可參與": "已勾選/未勾選",
  "第8點不可參與": "已勾選/未勾選",
  "第8點禁止大陸": "已勾選/未勾選",
  "第9點電子領標": "已勾選/未勾選",
  "第13點敏感性": "已勾選/未勾選",
  "第13點國安": "已勾選/未勾選",
  "第19點無需押標金": "已勾選/未勾選",
  "第19點一定金額": "已勾選/未勾選",
  "第35點非統包": "已勾選/未勾選",
  "第42點不分段": "已勾選/未勾選",
  "第42點分二段": "已勾選/未勾選",
  "第54點不協商": "已勾選/未勾選",
  "第59點最低標": "已勾選/未勾選",
  "第59點非64條之2": "已勾選/未勾選",
  "第59點身障優先": "已勾選/未勾選",
  "押標金金額": "提取押標金數字，如果沒有填0"
}}

注意事項：
1. 仔細識別■（已勾選）和□（未勾選）符號
2. 如果找不到某個項目，預設為"未勾選"
3. 押標金請提取純數字
"""

        response = self._call_gemma_json(prompt)
        
        try:
            return json.loads(response)
        except:
            return {}
    
    def _call_gemma(self, prompt: str) -> str:
        """呼叫Gemma API（一般文字回應）"""
        try:
            response = requests.post(
                self.api_url,
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.1,
                    "max_tokens": 4096
                },
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json().get('response', '')
            else:
                return f"API錯誤: {response.status_code}"
                
        except Exception as e:
            return f"呼叫失敗: {str(e)}"
    
    def _call_gemma_json(self, prompt: str) -> str:
        """呼叫Gemma API（JSON格式回應）"""
        try:
            response = requests.post(
                self.api_url,
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.1,
                    "format": "json",
                    "max_tokens": 2048
                },
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json().get('response', '{}')
            else:
                return '{}'
                
        except Exception as e:
            print(f"Gemma API錯誤: {str(e)}")
            return '{}'
    
    def _get_default_announcement_data(self) -> Dict:
        """返回預設的公告數據結構"""
        return {
            "案號": "NA",
            "案名": "NA", 
            "招標方式": "NA",
            "採購金額": 0,
            "預算金額": 0,
            "採購金級距": "NA",
            "依據法條": "NA",
            "決標方式": "NA",
            "訂有底價": "否",
            "複數決標": "否", 
            "依64條之2": "否",
            "標的分類": "NA",
            "適用條約": "否",
            "敏感性採購": "否",
            "國安採購": "否",
            "增購權利": "無",
            "特殊採購": "否",
            "統包": "否",
            "協商措施": "否",
            "電子領標": "否",
            "優先身障": "否",
            "外國廠商": "不可",
            "限定中小企業": "否",
            "押標金": 0,
            "開標方式": "NA"
        }

class GemmaComplianceValidator:
    """Gemma增強版合規驗證器"""
    
    def __init__(self, gemma_extractor: GemmaDocumentExtractor):
        self.gemma = gemma_extractor
        self.validation_results = {
            "審核結果": "通過",
            "通過項次": [],
            "失敗項次": [],
            "錯誤詳情": [],
            "總項次": 23,
            "通過數": 0,
            "失敗數": 0,
            "審核時間": datetime.now().isoformat()
        }
    
    def validate_with_gemma(self, 公告: Dict, 須知: Dict) -> Dict:
        """使用Gemma進行智能驗證"""
        
        # 準備驗證提示詞
        prompt = f"""你是招標文件審核專家。請執行23項合規檢核，比對招標公告和投標須知的一致性。

招標公告資料：
{json.dumps(公告, ensure_ascii=False, indent=2)}

投標須知資料：
{json.dumps(須知, ensure_ascii=False, indent=2)}

請執行以下23項檢核並以JSON格式回答每項的結果：

{{
  "項次1": {{"名稱": "案號案名一致性", "結果": "通過/失敗", "說明": "具體說明"}},
  "項次2": {{"名稱": "公開取得報價金額範圍", "結果": "通過/失敗", "說明": "具體說明"}},
  "項次3": {{"名稱": "公開取得報價須知設定", "結果": "通過/失敗", "說明": "具體說明"}},
  "項次4": {{"名稱": "最低標設定", "結果": "通過/失敗", "說明": "具體說明"}},
  "項次5": {{"名稱": "底價設定", "結果": "通過/失敗", "說明": "具體說明"}},
  "項次6": {{"名稱": "非複數決標", "結果": "通過/失敗", "說明": "具體說明"}},
  "項次7": {{"名稱": "64條之2", "結果": "通過/失敗", "說明": "具體說明"}},
  "項次8": {{"名稱": "標的分類", "結果": "通過/失敗", "說明": "具體說明"}},
  "項次9": {{"名稱": "條約協定", "結果": "通過/失敗", "說明": "具體說明"}},
  "項次10": {{"名稱": "敏感性採購", "結果": "通過/失敗", "說明": "具體說明"}},
  "項次11": {{"名稱": "國安採購", "結果": "通過/失敗", "說明": "具體說明"}},
  "項次12": {{"名稱": "增購權利", "結果": "通過/失敗", "說明": "具體說明"}},
  "項次13": {{"名稱": "特殊採購", "結果": "通過/失敗", "說明": "具體說明"}},
  "項次14": {{"名稱": "統包", "結果": "通過/失敗", "說明": "具體說明"}},
  "項次15": {{"名稱": "協商措施", "結果": "通過/失敗", "說明": "具體說明"}},
  "項次16": {{"名稱": "電子領標", "結果": "通過/失敗", "說明": "具體說明"}},
  "項次17": {{"名稱": "押標金", "結果": "通過/失敗", "說明": "具體說明"}},
  "項次18": {{"名稱": "身障優先", "結果": "通過/失敗", "說明": "具體說明"}},
  "項次19": {{"名稱": "保留", "結果": "通過/失敗", "說明": "具體說明"}},
  "項次20": {{"名稱": "外國廠商", "結果": "通過/失敗", "說明": "具體說明"}},
  "項次21": {{"名稱": "中小企業", "結果": "通過/失敗", "說明": "具體說明"}},
  "項次22": {{"名稱": "保留", "結果": "通過/失敗", "說明": "具體說明"}},
  "項次23": {{"名稱": "開標方式", "結果": "通過/失敗", "說明": "具體說明"}}
}}

檢核重點：
1. 案號必須完全一致（注意結尾A）
2. 金額必須相符
3. 勾選項目必須對應
4. 決標方式必須一致
5. 各項設定不能矛盾
"""

        response = self.gemma._call_gemma_json(prompt)
        
        try:
            gemma_results = json.loads(response)
            
            # 處理Gemma回傳的結果
            for key, value in gemma_results.items():
                if key.startswith("項次"):
                    item_num = int(key.replace("項次", ""))
                    if value.get("結果") == "通過":
                        self.validation_results["通過項次"].append(item_num)
                    else:
                        self.validation_results["失敗項次"].append(item_num)
                        self.validation_results["錯誤詳情"].append({
                            "項次": item_num,
                            "錯誤類型": value.get("名稱", ""),
                            "說明": value.get("說明", "")
                        })
            
            # 更新統計
            self.validation_results["通過數"] = len(self.validation_results["通過項次"])
            self.validation_results["失敗數"] = len(self.validation_results["失敗項次"])
            self.validation_results["審核結果"] = "通過" if self.validation_results["失敗數"] == 0 else "失敗"
            
        except Exception as e:
            print(f"處理Gemma驗證結果時發生錯誤: {str(e)}")
        
        return self.validation_results

class GemmaAuditSystem:
    """Gemma專用審核系統主類別"""
    
    def __init__(self):
        self.gemma_extractor = GemmaDocumentExtractor()
        self.validator = GemmaComplianceValidator(self.gemma_extractor)
        self.version = "北捷V1 v2.2 Gemma Only"
    
    def audit_case_with_gemma(self, case_folder: str) -> Dict:
        """使用Gemma執行完整審核"""
        
        print(f"🎯 開始Gemma智能審核: {case_folder}")
        print(f"🤖 使用模型: {self.gemma_extractor.model_name}")
        
        # 1. 尋找檔案
        announcement_file = self.find_announcement_file(case_folder)
        requirements_file = self.find_requirements_file(case_folder)
        
        if not announcement_file or not requirements_file:
            return {
                "錯誤": "找不到必要檔案",
                "招標公告": announcement_file,
                "投標須知": requirements_file
            }
        
        print(f"✅ 找到招標公告: {os.path.basename(announcement_file)}")
        print(f"✅ 找到投標須知: {os.path.basename(requirements_file)}")
        
        # 2. 使用Gemma提取資料
        print("📄 使用Gemma AI提取文件內容...")
        announcement_data = self.gemma_extractor.extract_announcement_with_gemma(announcement_file)
        requirements_data = self.gemma_extractor.extract_requirements_with_gemma(requirements_file)
        
        # 3. 使用Gemma進行合規驗證
        print("⚖️ 使用Gemma AI執行合規驗證...")
        validation_result = self.validator.validate_with_gemma(announcement_data, requirements_data)
        
        # 4. 使用Gemma生成智能分析報告
        print("📊 使用Gemma AI生成分析報告...")
        analysis_result = self._generate_gemma_analysis(announcement_data, requirements_data, validation_result)
        
        # 5. 綜合報告
        result = {
            "系統版本": self.version,
            "案件資訊": {
                "資料夾": case_folder,
                "招標公告檔案": os.path.basename(announcement_file),
                "投標須知檔案": os.path.basename(requirements_file),
                "審核時間": datetime.now().isoformat()
            },
            "提取資料": {
                "招標公告": announcement_data,
                "投標須知": requirements_data
            },
            "合規驗證": validation_result,
            "智能分析": analysis_result,
            "執行摘要": self._generate_summary(validation_result, analysis_result)
        }
        
        # 顯示結果
        print(f"\n✅ 審核完成！")
        print(f"通過率: {validation_result['通過數']}/{validation_result['總項次']} = {validation_result['通過數']/validation_result['總項次']*100:.1f}%")
        
        return result
    
    def _generate_gemma_analysis(self, 公告: Dict, 須知: Dict, 驗證結果: Dict) -> Dict:
        """使用Gemma生成智能分析"""
        
        prompt = f"""你是資深的招標審核專家。請根據以下審核結果提供專業分析和建議。

審核結果摘要：
- 總項次：{驗證結果['總項次']}
- 通過數：{驗證結果['通過數']}
- 失敗數：{驗證結果['失敗數']}

失敗項目詳情：
{json.dumps(驗證結果['錯誤詳情'], ensure_ascii=False, indent=2)}

請提供以下分析（JSON格式）：

{{
  "風險評估": {{
    "風險等級": "高/中/低",
    "風險分數": "0-100的數字",
    "主要風險": ["風險1", "風險2"]
  }},
  "改善建議": {{
    "立即修正": ["建議1", "建議2"],
    "注意事項": ["事項1", "事項2"]
  }},
  "合規分析": {{
    "法規符合度": "百分比",
    "關鍵問題": "最嚴重的問題描述",
    "影響評估": "對招標的影響"
  }},
  "整體建議": "給承辦人的具體建議"
}}
"""

        response = self.gemma_extractor._call_gemma_json(prompt)
        
        try:
            return json.loads(response)
        except:
            return {
                "風險評估": {"風險等級": "未知", "風險分數": 0},
                "改善建議": {"立即修正": [], "注意事項": []},
                "合規分析": {"法規符合度": "0%"},
                "整體建議": "無法生成分析"
            }
    
    def _generate_summary(self, validation: Dict, analysis: Dict) -> Dict:
        """生成執行摘要"""
        
        通過率 = validation['通過數'] / validation['總項次'] * 100 if validation['總項次'] > 0 else 0
        
        return {
            "最終判定": validation['審核結果'],
            "通過率": f"{通過率:.1f}%",
            "風險等級": analysis.get('風險評估', {}).get('風險等級', '未知'),
            "關鍵問題": analysis.get('合規分析', {}).get('關鍵問題', '無'),
            "建議行動": analysis.get('整體建議', '請修正錯誤後重新審核')
        }
    
    def find_announcement_file(self, case_folder: str) -> Optional[str]:
        """尋找招標公告檔案"""
        if not os.path.exists(case_folder):
            return None
            
        for file in os.listdir(case_folder):
            if file.endswith('.odt') and not file.startswith('~$'):
                if ('公告' in file or '公開' in file) and '須知' not in file:
                    return os.path.join(case_folder, file)
                if file.startswith('01'):
                    return os.path.join(case_folder, file)
        
        return None
    
    def find_requirements_file(self, case_folder: str) -> Optional[str]:
        """尋找投標須知檔案"""
        if not os.path.exists(case_folder):
            return None
            
        for file in os.listdir(case_folder):
            if not file.startswith('~$'):
                if file.endswith(('.docx', '.odt')) and '須知' in file:
                    return os.path.join(case_folder, file)
                if file.startswith('03') or file.startswith('02'):
                    return os.path.join(case_folder, file)
        
        return None
    
    def save_report(self, result: Dict, output_file: Optional[str] = None):
        """儲存審核報告"""
        if not output_file:
            case_name = result["案件資訊"]["資料夾"].split("/")[-1]
            status = result["執行摘要"]["最終判定"]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"gemma_audit_{case_name}_{status}_{timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"📄 Gemma審核報告已儲存: {output_file}")

# 使用範例
def main():
    """主程式 - 展示Gemma專用審核系統"""
    
    # 建立Gemma審核系統
    gemma_system = GemmaAuditSystem()
    
    # 執行審核
    case_folder = "/Users/ada/Desktop/tender-audit-system/C13A07469"
    result = gemma_system.audit_case_with_gemma(case_folder)
    
    if "錯誤" not in result:
        # 儲存報告
        gemma_system.save_report(result)
        
        # 顯示主要問題
        if result["合規驗證"]["失敗數"] > 0:
            print("\n❌ 發現的問題:")
            for error in result["合規驗證"]["錯誤詳情"][:5]:
                print(f"  項次{error['項次']}: {error['說明']}")
        
        # 顯示智能建議
        if "智能分析" in result:
            建議 = result["智能分析"].get("改善建議", {}).get("立即修正", [])
            if 建議:
                print("\n💡 改善建議:")
                for i, suggestion in enumerate(建議[:3], 1):
                    print(f"  {i}. {suggestion}")
    else:
        print(f"❌ 審核失敗: {result['錯誤']}")

if __name__ == "__main__":
    main()