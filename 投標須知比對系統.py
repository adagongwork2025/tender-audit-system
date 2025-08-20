#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
投標須知文件比對系統
比較問題版本(ODT)與機關正確版本(PDF)的差異
"""

import zipfile
import xml.etree.ElementTree as ET
import re
import difflib
from datetime import datetime
import os
import PyPDF2
import pdfplumber

class TenderDocumentComparator:
    def __init__(self):
        self.problem_file = '/Users/ada/Desktop/ollama/C13A07982/03投標須知(一般版)-公告以下1025.odt'
        self.correct_file = '/Users/ada/Desktop/ollama/C13A07982/機關版-03投標須知(一般版)-公告以下1025 (1).pdf'
        self.output_file = '/Users/ada/Desktop/ollama/C13A07982/投標須知交叉比對報告.html'
    
    def extract_odt_content(self, file_path):
        """提取ODT文件內容"""
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_file:
                content_xml = zip_file.read('content.xml').decode('utf-8')
                # 移除XML標籤，保留純文字
                clean_text = re.sub(r'<[^>]+>', ' ', content_xml)
                clean_text = re.sub(r'\s+', ' ', clean_text).strip()
                return clean_text
        except Exception as e:
            print(f"❌ 讀取ODT檔案失敗：{e}")
            return ""
    
    def extract_pdf_content(self, file_path):
        """提取PDF文件內容"""
        try:
            text = ""
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text
        except Exception as e:
            print(f"⚠️ pdfplumber失敗，嘗試PyPDF2：{e}")
            try:
                text = ""
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
                return text
            except Exception as e2:
                print(f"❌ 讀取PDF檔案失敗：{e2}")
                return ""
    
    def extract_key_sections(self, content):
        """提取關鍵段落用於比對"""
        sections = {}
        
        # 案號和案名
        case_match = re.search(r'採購標的名稱及案號[：:：]([^。\n]+)', content)
        if case_match:
            sections['案號案名'] = case_match.group(1).strip()
        
        # 採購金額級距
        amount_patterns = [
            r'■\s*\(\s*一\s*\)\s*公告金額十分之一以下',
            r'■\s*\(\s*二\s*\)\s*逾公告金額十分之一未達公告金額',
            r'■\s*\(\s*三\s*\)\s*公告金額以上未達查核金額',
            r'■\s*\(\s*四\s*\)\s*查核金額以上'
        ]
        for pattern in amount_patterns:
            if re.search(pattern, content):
                sections['採購金額級距'] = pattern
        
        # 外國廠商參與
        if '■不可參與投標' in content:
            sections['外國廠商'] = '不可參與投標'
        elif '■可以參與投標' in content:
            sections['外國廠商'] = '可以參與投標'
        
        # 押標金
        deposit_match = re.search(r'押標金[：:：].*?新臺幣([0-9,]+)元', content)
        if deposit_match:
            sections['押標金'] = deposit_match.group(1)
        
        # 決標方式
        if '■1.最低標' in content or '■最低標' in content:
            sections['決標方式'] = '最低標'
        elif '■2.最有利標' in content:
            sections['決標方式'] = '最有利標'
        
        # 開標方式
        if '■(一)採一次投標不分段開標' in content:
            sections['開標方式'] = '一次投標不分段開標'
        elif '■(二)採一次投標分段開標' in content:
            sections['開標方式'] = '一次投標分段開標'
        
        return sections
    
    def find_differences(self, problem_text, correct_text):
        """找出具體差異"""
        differences = []
        
        # 提取關鍵段落
        problem_sections = self.extract_key_sections(problem_text)
        correct_sections = self.extract_key_sections(correct_text)
        
        # 比對關鍵項目
        all_keys = set(problem_sections.keys()) | set(correct_sections.keys())
        for key in all_keys:
            problem_value = problem_sections.get(key, '未找到')
            correct_value = correct_sections.get(key, '未找到')
            if problem_value != correct_value:
                differences.append({
                    'item': key,
                    'problem': problem_value,
                    'correct': correct_value,
                    'severity': self.assess_severity(key)
                })
        
        # 進行文字差異比對（找出其他細節差異）
        problem_lines = problem_text.split('\n')
        correct_lines = correct_text.split('\n')
        
        # 使用difflib找出差異
        differ = difflib.unified_diff(
            problem_lines[:100],  # 只比對前100行避免太長
            correct_lines[:100],
            fromfile='問題版本',
            tofile='正確版本',
            lineterm=''
        )
        
        detailed_diffs = list(differ)
        
        return differences, detailed_diffs
    
    def assess_severity(self, item):
        """評估差異嚴重程度"""
        high_risk = ['案號案名', '採購金額級距', '決標方式', '開標方式']
        medium_risk = ['外國廠商', '押標金']
        
        if item in high_risk:
            return '高'
        elif item in medium_risk:
            return '中'
        else:
            return '低'
    
    def generate_html_report(self, differences, detailed_diffs):
        """生成HTML比對報告"""
        html = """<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>投標須知交叉比對報告 - C13A07982</title>
    <style>
        body {
            font-family: "Microsoft JhengHei", Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            text-align: center;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }
        h2 {
            color: #34495e;
            border-left: 4px solid #3498db;
            padding-left: 15px;
            margin-top: 30px;
        }
        .summary {
            background-color: #ecf0f1;
            padding: 20px;
            border-radius: 5px;
            margin: 20px 0;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            font-size: 14px;
        }
        th, td {
            border: 1px solid #bdc3c7;
            padding: 10px;
            text-align: left;
        }
        th {
            background-color: #3498db;
            color: white;
            font-weight: bold;
        }
        tr:nth-child(even) {
            background-color: #f8f9fa;
        }
        .high {
            background-color: #ffebee !important;
        }
        .medium {
            background-color: #fff3e0 !important;
        }
        .low {
            background-color: #e8f5e9 !important;
        }
        .diff-add {
            background-color: #d4edda;
            color: #155724;
        }
        .diff-remove {
            background-color: #f8d7da;
            color: #721c24;
        }
        .code-block {
            background-color: #f4f4f4;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 10px;
            font-family: monospace;
            font-size: 12px;
            overflow-x: auto;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>投標須知交叉比對報告</h1>
        
        <div class="summary">
            <p><strong>案號：</strong>C13A07982</p>
            <p><strong>比對日期：</strong>""" + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
            <p><strong>問題文件：</strong>03投標須知(一般版)-公告以下1025.odt</p>
            <p><strong>正確文件：</strong>機關版-03投標須知(一般版)-公告以下1025 (1).pdf</p>
        </div>
        
        <h2>執行摘要</h2>
        <div class="summary">
            <p><strong>發現差異項目：</strong>""" + str(len(differences)) + """項</p>
            <p><strong>高風險差異：</strong>""" + str(len([d for d in differences if d['severity'] == '高'])) + """項</p>
            <p><strong>中風險差異：</strong>""" + str(len([d for d in differences if d['severity'] == '中'])) + """項</p>
            <p><strong>低風險差異：</strong>""" + str(len([d for d in differences if d['severity'] == '低'])) + """項</p>
        </div>
        
        <h2>關鍵差異對照表</h2>
        <table>
            <thead>
                <tr>
                    <th width="20%">檢核項目</th>
                    <th width="35%">問題版本內容</th>
                    <th width="35%">正確版本內容</th>
                    <th width="10%">風險等級</th>
                </tr>
            </thead>
            <tbody>
"""
        
        # 添加差異項目
        for diff in sorted(differences, key=lambda x: {'高': 0, '中': 1, '低': 2}[x['severity']]):
            risk_class = diff['severity'].lower() if diff['severity'] in ['高', '中', '低'] else ''
            html += f"""
                <tr class="{risk_class}">
                    <td>{diff['item']}</td>
                    <td>{diff['problem']}</td>
                    <td>{diff['correct']}</td>
                    <td>{diff['severity']}風險</td>
                </tr>
"""
        
        html += """
            </tbody>
        </table>
        
        <h2>詳細差異分析</h2>
        <div class="summary">
            <p>以下為兩份文件的逐行比對結果（僅顯示有差異的部分）：</p>
        </div>
        
        <div class="code-block">
"""
        
        # 添加詳細差異（限制顯示行數）
        diff_count = 0
        for line in detailed_diffs[:50]:  # 只顯示前50行差異
            if line.startswith('+'):
                html += f'<div class="diff-add">{line}</div>'
                diff_count += 1
            elif line.startswith('-'):
                html += f'<div class="diff-remove">{line}</div>'
                diff_count += 1
            elif line.startswith('@'):
                html += f'<div style="color: #6c757d;">{line}</div>'
        
        if diff_count == 0:
            html += '<div>未發現顯著的文字差異</div>'
        
        html += """
        </div>
        
        <h2>修正建議</h2>
        <div class="summary">
            <ol>
"""
        
        # 添加修正建議
        for diff in sorted(differences, key=lambda x: {'高': 0, '中': 1, '低': 2}[x['severity']]):
            if diff['severity'] == '高':
                html += f"<li><strong>{diff['item']}：</strong>必須立即修正為「{diff['correct']}」</li>"
            else:
                html += f"<li><strong>{diff['item']}：</strong>建議修正為「{diff['correct']}」</li>"
        
        html += """
            </ol>
        </div>
        
        <div class="summary" style="margin-top: 40px;">
            <p><strong>比對完成</strong></p>
            <p>本報告詳細比對了問題版本與機關正確版本的差異，請依照風險等級優先修正高風險項目。</p>
        </div>
    </div>
</body>
</html>
"""
        
        return html
    
    def compare_documents(self):
        """執行文件比對"""
        print("📋 開始比對投標須知文件...")
        print(f"問題版本：{os.path.basename(self.problem_file)}")
        print(f"正確版本：{os.path.basename(self.correct_file)}")
        
        # 提取文件內容
        print("\n📖 讀取文件內容...")
        problem_content = self.extract_odt_content(self.problem_file)
        correct_content = self.extract_pdf_content(self.correct_file)
        
        if not problem_content:
            print("❌ 無法讀取問題版本文件")
            return
        if not correct_content:
            print("❌ 無法讀取正確版本文件")
            return
        
        print(f"✅ 問題版本長度：{len(problem_content)} 字元")
        print(f"✅ 正確版本長度：{len(correct_content)} 字元")
        
        # 執行比對
        print("\n🔍 分析差異...")
        differences, detailed_diffs = self.find_differences(problem_content, correct_content)
        
        print(f"\n📊 發現 {len(differences)} 項關鍵差異：")
        for diff in differences:
            print(f"   - {diff['item']}: {diff['problem']} → {diff['correct']} ({diff['severity']}風險)")
        
        # 生成報告
        print("\n📄 生成比對報告...")
        html_content = self.generate_html_report(differences, detailed_diffs)
        
        # 寫入檔案
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ 報告已生成：{self.output_file}")
        return self.output_file

def main():
    comparator = TenderDocumentComparator()
    comparator.compare_documents()

if __name__ == "__main__":
    main()