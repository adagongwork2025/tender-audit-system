#!/usr/bin/env python3
"""
北捷V1 檢核 C14A01072
"""

import json
import os
from ai_tender_audit_v2 import AITenderAuditSystemV2

def main():
    print('🚇 北捷V1 檢核 C14A01072')
    print('=' * 40)
    
    # 建立AI審核系統
    ai_system = AITenderAuditSystemV2()
    
    # 指定案件資料夾
    case_folder = "/Users/ada/Desktop/ollama/C14A01072"
    
    try:
        # 審核案件
        result = ai_system.audit_tender_case(case_folder)
        
        # 輸出結果
        if "錯誤" not in result:
            # 存回原資料夾
            report_filename = 'AI檢核報告_C14A01072.txt'
            report_path = os.path.join(case_folder, report_filename)
            ai_system.export_ai_report(result, report_path)
            
            # 同時儲存JSON
            json_filename = 'AI檢核結果_C14A01072.json'
            json_path = os.path.join(case_folder, json_filename)
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            # 顯示結果
            summary = result.get('總結', {})
            print(f"✅ 檢核完成")
            print(f"📊 通過項數：{summary.get('通過項數', 0)}")
            print(f"📊 失敗項數：{summary.get('失敗項數', 0)}")
            print(f"📊 通過率：{summary.get('通過率', '未知')}")
            print(f"📊 風險等級：{summary.get('風險等級', '未知')}")
            print(f"📄 報告已存回資料夾：{case_folder}")
        else:
            print(f"❌ 審核失敗: {result['錯誤']}")
            
    except Exception as e:
        print(f"❌ 執行失敗: {e}")

if __name__ == "__main__":
    main()