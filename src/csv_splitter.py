#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSV結果拆解器 (CSV Result Splitter)

此腳本負責將聊天記錄清理後的CSV結果檔案拆解成多個Markdown檔案：
1. 讀取CSV結果檔案
2. 智能分配檔案數量，避免檔案筆數過少
3. 輸出為Markdown格式，便於閱讀
4. 自動創建輸出目錄和檔案命名

主要功能：
- CSV讀取：支援UTF-8-BOM編碼的CSV檔案
- 智能拆解：基於最少筆數標準智能分配檔案數量
- Markdown格式：美觀的表格和訊息顯示
- 自動命名：按序號和日期範圍命名檔案
- 統計資訊：顯示拆解結果和統計數據
- 品質控制：確保每個檔案都有足夠的內容

輸出格式：
- 檔案命名：chat_part_001_YYYY-MM-DD_to_YYYY-MM-DD.md
- Markdown表格：包含日期、時間、使用者、內容
- 關注標記：高亮顯示關注對象的訊息

適用場景：
- 大量聊天記錄的分頁顯示
- 便於閱讀的Markdown格式輸出
- 按時間段或數量分割聊天記錄
- 生成報告和文檔

Authors: 楊翔志 & AI Collective
Studio: tranquility-base
版本: 1.0
"""

import csv
import os
import glob
from datetime import datetime
from typing import List, Dict, Tuple
import argparse

def read_csv_file(csv_path: str) -> List[List[str]]:
    """
    讀取CSV檔案
    
    Args:
        csv_path: CSV檔案路徑
        
    Returns:
        CSV資料列表
    """
    data = []
    try:
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            # 跳過標題行
            next(reader)
            for row in reader:
                if len(row) >= 5:  # 確保有足夠的欄位
                    data.append(row)
        print(f"成功讀取 {len(data)} 筆資料")
        return data
    except Exception as e:
        print(f"讀取CSV檔案失敗：{e}")
        return []

def format_message_content(content: str, max_length: int = 100) -> str:
    """
    格式化訊息內容，處理換行和長度限制
    
    Args:
        content: 原始訊息內容
        max_length: 最大顯示長度
        
    Returns:
        格式化後的內容
    """
    if not content:
        return ""
    
    # 替換換行符號
    formatted = content.replace('\n', '<br>')
    
    # 限制長度
    if len(formatted) > max_length:
        formatted = formatted[:max_length] + "..."
    
    return formatted

def create_markdown_table(data: List[List[str]], part_number: int, start_date: str, end_date: str, total_parts: int) -> str:
    """
    創建Markdown格式的表格
    
    Args:
        data: 資料列表
        part_number: 部分編號
        start_date: 開始日期
        end_date: 結束日期
        total_parts: 總部分數
        
    Returns:
        Markdown格式的字串
    """
    md_content = f"""<!-- CHAT_LOG_START:PART_{part_number:03d}_OF_{total_parts:03d} -->
<!-- FILE_INFO:START_DATE={start_date},END_DATE={end_date},MESSAGE_COUNT={len(data)} -->
<!-- GENERATED_TIME:{datetime.now().strftime('%Y-%m-%d_%H:%M:%S')} -->

# 聊天記錄 - 第 {part_number} 部分

**日期範圍**: {start_date} 至 {end_date}  
**訊息數量**: {len(data)} 筆  
**生成時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**檔案順序**: 第 {part_number} 部分，共 {total_parts} 部分

---

| 日期 | 時間 | 使用者 | 訊息內容 | 關注對象 |
|------|------|--------|----------|----------|
"""
    
    for row in data:
        date, time, user, content, is_watchlist = row
        formatted_content = format_message_content(content)
        
        # 標記關注對象
        watchlist_mark = "⭐" if is_watchlist == "True" else ""
        
        md_content += f"| {date} | {time} | {user} | {formatted_content} | {watchlist_mark} |\n"
    
    md_content += f"""
---

*此檔案包含 {len(data)} 筆訊息記錄*

<!-- CHAT_LOG_END:PART_{part_number:03d}_OF_{total_parts:03d} -->
<!-- FILE_INFO:START_DATE={start_date},END_DATE={end_date},MESSAGE_COUNT={len(data)} -->
<!-- GENERATED_TIME:{datetime.now().strftime('%Y-%m-%d_%H:%M:%S')} -->
"""
    
    return md_content

def split_csv_to_markdown(csv_path: str, output_dir: str = "data/markdown", max_files: int = 10, min_records_per_file: int = 100):
    """
    將CSV檔案拆解成多個Markdown檔案（智能分配，避免檔案筆數過少）
    
    Args:
        csv_path: CSV檔案路徑
        output_dir: 輸出目錄
        max_files: 最大檔案數量（預設10個）
        min_records_per_file: 每檔案最少筆數（預設100筆）
    """
    # 讀取CSV資料
    data = read_csv_file(csv_path)
    if not data:
        print("沒有資料可處理")
        return
    
    # 創建輸出目錄
    os.makedirs(output_dir, exist_ok=True)
    
    # 獲取檔案基本名稱
    base_name = os.path.splitext(os.path.basename(csv_path))[0]
    
    # 智能計算實際檔案數量
    total_records = len(data)
    
    # 計算理想的檔案數量（基於最少筆數限制）
    ideal_files = total_records // min_records_per_file
    
    # 確定實際檔案數量
    if ideal_files == 0:
        # 如果總筆數少於最少筆數，只生成1個檔案
        actual_files = 1
        print(f"⚠️  總筆數 {total_records} 少於最少筆數 {min_records_per_file}，將生成 1 個檔案")
    elif ideal_files > max_files:
        # 如果理想檔案數超過最大限制，使用最大限制
        actual_files = max_files
        print(f"⚠️  理想檔案數 {ideal_files} 超過最大限制 {max_files}，將生成 {max_files} 個檔案")
    else:
        # 使用理想檔案數
        actual_files = ideal_files
        print(f"✅ 使用理想檔案數 {actual_files}")
    
    # 計算每檔案的筆數（平均分配）
    records_per_file = total_records // actual_files
    remainder = total_records % actual_files  # 剩餘的筆數
    
    print(f"開始拆解 {total_records} 筆資料，分為 {actual_files} 個檔案...")
    print(f"每檔案約 {records_per_file} 筆，剩餘 {remainder} 筆將分配給前幾個檔案")
    
    # 檢查是否會產生過少的檔案
    if records_per_file < min_records_per_file:
        print(f"⚠️  警告：平均每檔案 {records_per_file} 筆少於最少標準 {min_records_per_file} 筆")
        print(f"建議減少檔案數量或降低最少筆數標準")
    
    current_idx = 0
    
    for i in range(actual_files):
        # 計算當前檔案的筆數（前幾個檔案多分配1筆剩餘的記錄）
        current_batch_size = records_per_file + (1 if i < remainder else 0)
        
        # 獲取當前檔案的資料
        end_idx = current_idx + current_batch_size
        batch_data = data[current_idx:end_idx]
        
        # 獲取日期範圍
        start_date = batch_data[0][0] if batch_data else "未知"
        end_date = batch_data[-1][0] if batch_data else "未知"
        
        # 生成Markdown內容
        md_content = create_markdown_table(batch_data, i + 1, start_date, end_date, actual_files)
        
        # 生成檔案名稱
        part_number = f"{i + 1:03d}"
        output_filename = f"{base_name}_part_{part_number}_{start_date}_to_{end_date}.md"
        output_path = os.path.join(output_dir, output_filename)
        
        # 寫入檔案
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(md_content)
            
            # 檢查檔案筆數是否符合標準
            record_count = len(batch_data)
            status = "✅" if record_count >= min_records_per_file else "⚠️"
            print(f"{status} 已生成: {output_filename} ({record_count} 筆)")
            
        except Exception as e:
            print(f"❌ 寫入檔案失敗 {output_filename}: {e}")
        
        # 更新下一個檔案的起始索引
        current_idx = end_idx
    
    print(f"\n🎉 拆解完成！共生成 {actual_files} 個Markdown檔案")
    print(f"📁 輸出目錄: {output_dir}")
    print(f"📊 平均每檔案: {total_records / actual_files:.1f} 筆")
    print(f"📋 最少筆數標準: {min_records_per_file} 筆")

def process_all_csv_files(input_dir: str = "data/output", output_dir: str = "data/markdown", max_files: int = 10, min_records_per_file: int = 100):
    """
    處理所有CSV檔案
    
    Args:
        input_dir: 輸入目錄
        output_dir: 輸出目錄
        max_files: 最大檔案數量
        min_records_per_file: 每檔案最少筆數
    """
    csv_files = glob.glob(os.path.join(input_dir, "*.csv"))
    
    if not csv_files:
        print(f"在 {input_dir} 目錄中找不到CSV檔案")
        return
    
    print(f"找到 {len(csv_files)} 個CSV檔案")
    
    for csv_file in csv_files:
        print(f"\n處理檔案: {os.path.basename(csv_file)}")
        split_csv_to_markdown(csv_file, output_dir, max_files, min_records_per_file)

def main():
    """
    主程式入口
    """
    parser = argparse.ArgumentParser(description='將CSV聊天記錄拆解成Markdown檔案（智能分配，避免檔案筆數過少）')
    parser.add_argument('--input', '-i', default='data/output', 
                       help='輸入CSV檔案目錄 (預設: data/output)')
    parser.add_argument('--output', '-o', default='data/markdown', 
                       help='輸出Markdown檔案目錄 (預設: data/markdown)')
    parser.add_argument('--max-files', '-m', type=int, default=10, 
                       help='最大檔案數量 (預設: 10)')
    parser.add_argument('--min-records', '-r', type=int, default=100, 
                       help='每檔案最少筆數 (預設: 100)')
    parser.add_argument('--file', '-f', 
                       help='指定單一CSV檔案路徑')
    
    args = parser.parse_args()
    
    print("=== CSV結果拆解器 ===")
    print(f"最大檔案數: {args.max_files}")
    print(f"最少筆數標準: {args.min_records}")
    print(f"輸出目錄: {args.output}")
    
    if args.file:
        # 處理單一檔案
        if os.path.exists(args.file):
            print(f"處理檔案: {args.file}")
            split_csv_to_markdown(args.file, args.output, args.max_files, args.min_records)
        else:
            print(f"檔案不存在: {args.file}")
    else:
        # 處理所有檔案
        process_all_csv_files(args.input, args.output, args.max_files, args.min_records)

if __name__ == "__main__":
    main()
