import json
import requests
import re
import zipfile
from typing import Dict, List

class C14A00139Processor:
    def __init__(self):
        self.model_name = "gemma2:7b"  # 可改為 "gpt-oss:latest" 或其他模型
        self.ollama_url = "http://192.168.53.14:11434/api/generate"
        
    def extract_odt_content(self, file_path: str) -> str:
        """提取ODT內容"""
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_file:
                content_xml = zip_file.read('content.xml').decode('utf-8')
                clean_text = re.sub(r'<[^>]+>', ' ', content_xml)
                clean_text = re.sub(r'\s+', ' ', clean_text).strip()
                return clean_text
        except Exception as e:
            print(f"❌ 讀取ODT檔案失敗：{e}")
            return ""
    
    def create_simple_prompt(self) -> str:
        """簡化的提示詞，只提取案號案名"""
        return """從文件中找出案號和案名。
案號格式：C開頭後接數字（如C14A00139）
案名：通常在案號附近

只回應JSON格式：
{"案號":"找到的案號","案名":"找到的案名"}

文件內容：
"""
    
    def call_ollama(self, prompt: str, content: str) -> Dict:
        """呼叫 Ollama API"""
        # 限制內容長度
        if len(content) > 2000:
            content = content[:2000]
            
        full_prompt = prompt + content
        
        payload = {
            "model": self.model_name,
            "prompt": full_prompt,
            "stream": False,
            "temperature": 0.1,
            "format": "json"
        }
        
        try:
            print(f"🤖 呼叫 {self.model_name} 模型...")
            response = requests.post(self.ollama_url, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            response_text = result.get('response', '')
            print(f"📝 模型回應: {response_text[:100]}...")
            
            # 解析JSON
            try:
                return json.loads(response_text)
            except:
                # 嘗試提取JSON部分
                json_match = re.search(r'\{[^}]+\}', response_text)
                if json_match:
                    return json.loads(json_match.group())
                return {"錯誤": "無法解析JSON"}
                
        except requests.exceptions.Timeout:
            return {"錯誤": "API 超時"}
        except requests.exceptions.ConnectionError:
            return {"錯誤": "無法連接到 Ollama"}
        except Exception as e:
            return {"錯誤": str(e)}
    
    def process_c14a00139(self):
        """處理 C14A00139 案例"""
        case_folder = "/Users/ada/Desktop/ollama/C14A00139"
        
        # 1. 處理招標公告
        print("\n=== 處理招標公告 ===")
        ann_file = f"{case_folder}/附件1.公開取得報價或企劃書公告事項(財物)-1120504版_錯.odt"
        ann_content = self.extract_odt_content(ann_file)
        
        if ann_content:
            print(f"✅ 成功讀取招標公告 ({len(ann_content)} 字元)")
            ann_result = self.call_ollama(self.create_simple_prompt(), ann_content)
            print(f"招標公告提取結果: {json.dumps(ann_result, ensure_ascii=False)}")
        else:
            ann_result = {"錯誤": "無法讀取檔案"}
        
        # 2. 處理投標須知
        print("\n=== 處理投標須知 ===")
        ins_file = f"{case_folder}/附件2.臺北大眾捷運股份有限公司投標須知(一般版)(不含投標須知範本附錄)_錯.odt"
        ins_content = self.extract_odt_content(ins_file)
        
        if ins_content:
            print(f"✅ 成功讀取投標須知 ({len(ins_content)} 字元)")
            # 找到"採購標的名稱及案號"部分
            pattern = r'採購標的名稱及案號[：:](.*?)(?:三、|$)'
            match = re.search(pattern, ins_content[:5000], re.DOTALL)
            if match:
                relevant_content = match.group(0)
                print(f"📍 找到相關段落: {relevant_content[:100]}...")
            else:
                relevant_content = ins_content[:2000]
            
            ins_result = self.call_ollama(self.create_simple_prompt(), relevant_content)
            print(f"投標須知提取結果: {json.dumps(ins_result, ensure_ascii=False)}")
        else:
            ins_result = {"錯誤": "無法讀取檔案"}
        
        # 3. 整合結果
        print("\n=== 最終結果 ===")
        final_result = {
            "招標公告的案號": ann_result.get("案號", "NA"),
            "招標公告的案名": ann_result.get("案名", "NA"),
            "投標須知的案號": ins_result.get("案號", "NA"),
            "投標須知的案名": ins_result.get("案名", "NA")
        }
        
        print(json.dumps(final_result, ensure_ascii=False, indent=2))
        
        # 4. 與預期結果比較
        print("\n=== 預期結果（基於文件解析）===")
        expected = {
            "招標公告的案號": "C14A00139",
            "招標公告的案名": "攜帶式數位無線電綜合測試儀採購",
            "投標須知的案號": "C13A00139",  # 注意：文件中是 C13A00139
            "投標須知的案名": "攜帶式數位無線電綜合測試儀採購"
        }
        print(json.dumps(expected, ensure_ascii=False, indent=2))
        
        # 5. 差異分析
        print("\n=== 差異分析 ===")
        for key in expected:
            if final_result[key] != expected[key]:
                print(f"❌ {key}: AI='{final_result[key]}' vs 預期='{expected[key]}'")
            else:
                print(f"✅ {key}: 正確")
        
        return final_result

def main():
    processor = C14A00139Processor()
    
    # 測試連線
    print("測試 Ollama 連線...")
    test_result = processor.call_ollama("回答OK", "測試")
    if "錯誤" in test_result:
        print(f"❌ Ollama 連線失敗: {test_result['錯誤']}")
        print("\n請確認:")
        print("1. Ollama 是否已啟動")
        print("2. 模型是否已下載 (ollama pull gemma2:7b)")
        print("3. API 地址是否正確")
        return
    
    # 處理文件
    processor.process_c14a00139()

if __name__ == "__main__":
    main()