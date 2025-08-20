#!/usr/bin/env python3
"""
使用AI模型提取招標文件中的案號和案名
"""
import json
import requests
import zipfile
import re
import os

class AIDocumentExtractor:
    def __init__(self):
        self.ollama_url = "http://192.168.53.14:11434"
        self.model = "gpt-oss:latest"
    
    def extract_odt_content(self, file_path: str) -> str:
        """提取ODT內容"""
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_file:
                content_xml = zip_file.read('content.xml').decode('utf-8')
                # 移除XML標籤
                clean_text = re.sub(r'<[^>]+>', ' ', content_xml)
                clean_text = re.sub(r'\s+', ' ', clean_text).strip()
                return clean_text
        except Exception as e:
            print(f"❌ 讀取ODT檔案失敗：{e}")
            return ""
    
    def call_ai_model(self, prompt: str) -> str:
        """呼叫AI模型"""
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.1  # 降低溫度以提高準確性
                }
            )
            if response.status_code == 200:
                return response.json().get('response', '')
            else:
                return f"錯誤: {response.status_code}"
        except Exception as e:
            return f"呼叫失敗: {str(e)}"
    
    def extract_with_ai(self, document_content: str, doc_type: str) -> dict:
        """使用AI模型提取資訊"""
        
        # 分頁處理（每頁約2000字）
        page_size = 2000
        pages = [document_content[i:i+page_size] for i in range(0, len(document_content), page_size)]
        
        # 針對第一頁（通常包含案號案名）
        first_page = pages[0] if pages else document_content
        
        # 設計提示詞
        if doc_type == "招標公告":
            prompt = f"""請從以下招標公告內容中提取資訊，並以JSON格式回答。
如果找不到對應資料，請填入"NA"。

需要提取的資訊：
1. 案號 - 尋找"案號："後面的編號（格式通常為C開頭，如C14A00139）
2. 案名 - 尋找"案名："後面的名稱

文件內容：
{first_page}

請只回答以下JSON格式，不要有其他文字：
{{
  "案號": "編號或NA",
  "案名": "名稱或NA"
}}"""
        else:  # 投標須知
            prompt = f"""請從以下投標須知內容中提取資訊，並以JSON格式回答。
如果找不到對應資料，請填入"NA"。

需要提取的資訊：
1. 案號 - 尋找"採購標的名稱及案號"章節中的案號（格式通常為C開頭）
2. 案名 - 尋找"採購標的名稱及案號"章節中的採購標的名稱

文件內容：
{first_page}

請只回答以下JSON格式，不要有其他文字：
{{
  "案號": "編號或NA",
  "案名": "名稱或NA"
}}"""
        
        # 呼叫AI模型
        print(f"🤖 正在使用AI模型分析{doc_type}...")
        ai_response = self.call_ai_model(prompt)
        
        # 解析AI回應
        try:
            # 嘗試提取JSON部分
            json_match = re.search(r'\{[^}]+\}', ai_response)
            if json_match:
                result = json.loads(json_match.group())
            else:
                result = {"案號": "解析失敗", "案名": "解析失敗"}
        except:
            result = {"案號": "JSON解析錯誤", "案名": "JSON解析錯誤"}
        
        return result

def main():
    """主程式"""
    case_id = "C14A00139"
    case_folder = f"/Users/ada/Desktop/ollama/{case_id}"
    
    extractor = AIDocumentExtractor()
    
    # 讀取招標公告
    announcement_file = f"{case_folder}/附件1.公開取得報價或企劃書公告事項(財物)-1120504版_錯.odt"
    announcement_content = extractor.extract_odt_content(announcement_file)
    
    # 讀取投標須知
    instructions_file = f"{case_folder}/附件2.臺北大眾捷運股份有限公司投標須知(一般版)(不含投標須知範本附錄)_錯.odt"
    instructions_content = extractor.extract_odt_content(instructions_file)
    
    # 使用AI模型提取
    ann_result = extractor.extract_with_ai(announcement_content[:3000], "招標公告")
    ins_result = extractor.extract_with_ai(instructions_content[:3000], "投標須知")
    
    # 整合結果
    final_result = {
        "招標公告的案號": ann_result.get("案號", "NA"),
        "招標公告的案名": ann_result.get("案名", "NA"),
        "投標須知的案號": ins_result.get("案號", "NA"),
        "投標須知的案名": ins_result.get("案名", "NA")
    }
    
    print("\n📊 AI模型提取結果：")
    print(json.dumps(final_result, ensure_ascii=False, indent=2))
    
    # 顯示預期結果（基於規則的提取）
    expected_result = {
        "招標公告的案號": "C14A00139",
        "招標公告的案名": "攜帶式數位無線電綜合測試儀採購",
        "投標須知的案號": "C13A00139",
        "投標須知的案名": "攜帶式數位無線電綜合測試儀採購"
    }
    
    print("\n✅ 預期結果（規則提取）：")
    print(json.dumps(expected_result, ensure_ascii=False, indent=2))
    
    # 比較差異
    print("\n🔍 差異分析：")
    for key in expected_result:
        if final_result.get(key) != expected_result[key]:
            print(f"❌ {key}: AI提取'{final_result.get(key)}' vs 預期'{expected_result[key]}'")
        else:
            print(f"✅ {key}: 一致")

if __name__ == "__main__":
    main()