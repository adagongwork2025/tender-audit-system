# 招標文件自動化審核系統

智能化招標文件合規性檢核工具，專為政府採購案件設計，提供完整的23項合規檢核標準。

## 🚀 系統特色

- **AI智能提取**：使用Gemma AI模型自動提取招標文件關鍵資訊
- **23項合規檢核**：完整實施政府採購法規定的檢核項目
- **智能容錯機制**：自動處理文件格式變異和常見錯誤
- **多版本支援**：提供標準版、智能容錯版、Gemma專用版

## 📋 版本說明

### 1. 標準版 (tender_audit_system.py)
- 基礎23項檢核功能
- XML解析提取文件內容
- 規則引擎驗證
- 支援AI輔助驗證（可選）

### 2. 智能容錯優化版 (tender_audit_system_v2.1.py)
- **模糊比對技術**：處理案號結尾A問題
- **智能文字匹配**：相似度計算
- **自動修復功能**：常見錯誤自動修正
- **信心度評分**：每項檢核都有信心度
- **多狀態分類**：通過/失敗/警告/跳過/自動修復

### 3. Gemma專用版 (tender_audit_gemma_only.py)
- **純AI提取**：所有文字提取使用Gemma完成
- **無需XML解析**：直接處理原始文件
- **智能結構化**：AI自動識別25個標準欄位

## 🛠️ 安裝需求

```bash
# Python 3.8+
pip install requests
pip install python-docx  # 可選，用於Word報告輸出
```

## 📖 使用方法

### 基本使用
```python
from tender_audit_system import TenderAuditSystem

# 建立審核系統
audit_system = TenderAuditSystem(use_ai=True)

# 執行審核
result = audit_system.audit_tender_case("/path/to/case/folder")

# 儲存報告
audit_system.save_report(result)
```

### 智能容錯版
```python
from tender_audit_system_v2_1 import IntelligentAuditSystem

# 使用智能容錯系統
smart_system = IntelligentAuditSystem(use_ai=True)
result = smart_system.audit_case_smart("/path/to/case/folder")
```

### Gemma專用版
```python
from tender_audit_gemma_only import GemmaAuditSystem

# 使用純AI系統
gemma_system = GemmaAuditSystem()
result = gemma_system.audit_case_with_gemma("/path/to/case/folder")
```

## 📊 23項檢核標準

1. **案號案名一致性**
2. **公開取得報價金額範圍**（15-150萬）
3. **公開取得報價須知設定**
4. **最低標設定**
5. **底價設定**
6. **非複數決標**
7. **64條之2設定**
8. **標的分類一致性**
9. **條約協定適用**
10. **敏感性採購**
11. **國安採購**
12. **增購權利**
13. **特殊採購認定**
14. **統包認定**
15. **協商措施**
16. **電子領標**
17. **押標金一致性**
18. **身障優先採購**
19. **外國廠商文件要求**（部分版本跳過）
20. **外國廠商參與規定**
21. **中小企業參與限制**
22. **廠商資格摘要**（部分版本跳過）
23. **開標程序一致性**

## 🔧 改進的AI提示詞

系統包含改進版的AI提示詞（improved_ai_prompts.py），解決了：
- 金額單位混淆（萬元vs元）
- 案名數量識別（3項vs5項）
- 押標金額錯誤（39,000 vs 390,000）
- 特殊採購設定
- 第十五點刪除檢測

## 📁 檔案結構

```
tender-audit-system/
├── tender_audit_system.py          # 標準版主程式
├── tender_audit_system_v2.1.py     # 智能容錯優化版
├── tender_audit_gemma_only.py      # Gemma專用版
├── improved_ai_prompts.py          # 改進的AI提示詞
├── manual_audit_C13A05954.py       # 手動修正範例
└── README_zh.md                    # 本說明文件
```

## ⚠️ 注意事項

1. **AI模型需求**：需要連接到Gemma AI服務（預設：http://192.168.53.14:11434）
2. **文件格式**：支援ODT和DOCX格式的招標文件
3. **檔案命名**：建議使用標準命名規則
   - 招標公告：包含「公告」或「公開」關鍵字
   - 投標須知：包含「須知」關鍵字

## 🚨 已知問題

1. 項次19和22在部分版本中未實作，會顯示為「跳過」
2. AI提取可能因網路或服務問題失敗，建議實施重試機制
3. 複雜表格內容可能需要人工確認

## 📈 效能優化建議

1. 批次處理多個案件時，考慮使用並行處理
2. 快取AI回應結果以減少重複呼叫
3. 定期更新AI提示詞以提升準確度

## 🤝 貢獻指南

歡迎提交Issue和Pull Request來改進系統。建議重點：
- 補充缺失的檢核項目
- 優化AI提示詞
- 增加更多文件格式支援
- 改進錯誤處理機制

## 📄 授權

本專案採用 MIT 授權條款。

---

💡 **提示**：使用前請確保已正確設定AI服務連接，並準備好符合格式要求的招標文件。