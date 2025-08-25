#!/usr/bin/env python3
"""
招標文件智能審核系統 v2.1 - C13A05954檢核執行
使用純Gemma AI進行文件分析，符合22項檢核標準
"""

import sys
import os
sys.path.append('/Users/ada/Desktop/tender-audit-system')

from tender_audit_system import TenderAuditSystem
import json

def main():
    """檢核C13A05954案件"""
    print("🎯 啟動招標文件智能審核系統 v2.1")
    print("📋 目標：C13A05954 - 22項合規檢核（依0821版規範）")
    print("🤖 AI模型：Gemma3:27b @ http://192.168.53.254:11434")
    print("=" * 60)
    
    # 建立審核系統
    audit_system = TenderAuditSystem(use_ai=True)
    
    # 案件資料夾
    case_folder = "/Users/ada/Desktop/正確內容/C13A05954"
    
    # 執行審核
    print(f"📁 處理案件資料夾: {case_folder}")
    result = audit_system.audit_tender_case(case_folder)
    
    # 檢查結果
    if "錯誤" in result:
        print(f"❌ 審核失敗: {result['錯誤']}")
        return
    
    # 顯示結果摘要
    rule_result = result["規則引擎驗證"]
    通過項數 = rule_result["通過數"]
    總項數 = rule_result["總項次"]
    通過率 = (通過項數 / 總項數) * 100
    
    print(f"\n📊 審核結果摘要:")
    print(f"   總檢核項數：{總項數} 項")
    print(f"   通過項數：{通過項數} 項")
    print(f"   失敗項數：{rule_result['失敗數']} 項")
    print(f"   通過率：{通過率:.1f}%")
    
    # 顯示失敗項目
    if rule_result["失敗數"] > 0:
        print(f"\n❌ 發現問題項次:")
        for error in rule_result["錯誤詳情"]:
            print(f"   項次{error['項次']}: {error['說明']}")
    
    # 生成TXT報告
    print(f"\n📄 生成檢核報告...")
    output_file = f"/Users/ada/Desktop/正確內容/C13A05954/AI檢核報告_C13A05954.txt"
    audit_system.export_to_txt(result, output_file)
    
    print(f"✅ 檢核完成！報告已儲存至: {output_file}")
    print(f"🎯 目標通過率68.2%，實際通過率{通過率:.1f}%")
    
    return result

if __name__ == "__main__":
    main()