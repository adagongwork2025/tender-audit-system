#!/usr/bin/env python3
"""
北捷V1 專用檢核程式 - C14A01072
"""

import json
import os
from datetime import datetime
from ai_tender_audit_v2 import AITenderAuditSystemV2

def main():
    print('🚇 北捷V1 檢核系統 - C14A01072')
    print('=' * 50)
    
    case_folder = '/Users/ada/Desktop/ollama/C14A01072'
    
    # 使用AI系統
    ai_system = AITenderAuditSystemV2()
    
    try:
        # 檢核案件
        result = ai_system.audit_case(case_folder)
        
        print(f'✅ 檢核完成：通過率 {result["通過率"]}')
        print(f'📊 風險等級：{result["風險等級"]}')
        
        # 檢查報告是否已存在於正確位置
        report_path = os.path.join(case_folder, f'AI檢核報告_C14A01072.txt')
        if os.path.exists(report_path):
            print(f'✅ 報告已儲存：{report_path}')
        else:
            print('❌ 報告未正確儲存')
            
    except Exception as e:
        print(f'❌ 檢核失敗：{e}')

if __name__ == "__main__":
    main()