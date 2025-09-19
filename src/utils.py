#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具函數庫 (Utilities)

此腳本提供聊天記錄清理系統的通用工具函數：
1. 配置文件載入和解析
2. CSV檔案寫入和格式化
3. 檔案操作和錯誤處理
4. 通用輔助功能

主要功能：
- 配置載入：從JSON檔案載入系統配置
- CSV輸出：將解析結果寫入CSV檔案
- 錯誤處理：提供重試機制和錯誤提示
- 檔案管理：自動創建目錄和處理檔案權限

支援的檔案格式：
- 輸入：config.json（JSON格式配置文件）
- 輸出：*.csv（UTF-8-BOM編碼的CSV檔案）

錯誤處理：
- 檔案權限錯誤自動重試
- 目錄不存在自動創建
- 詳細的錯誤訊息和建議

適用場景：
- 配置文件管理
- 資料匯出和格式化
- 檔案操作輔助
- 系統工具函數

Authors: 楊翔志 & AI Collective
Studio: tranquility-base
版本: 1.0
"""

import json
import csv
import os

def load_config(config_path):
    """
    載入配置文件
    
    Args:
        config_path: 配置文件路徑
        
    Returns:
        配置字典
    """
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def write_to_csv(data, output_path):
    """
    將資料寫入CSV檔案
    
    Args:
        data: 要寫入的資料列表
        output_path: 輸出檔案路徑
    """
    # 確保輸出目錄存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 嘗試寫入檔案，如果失敗則重試
    max_retries = 3
    for attempt in range(max_retries):
        try:
            with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                # 寫入標題行
                writer.writerow(["日期", "時間", "使用者", "訊息內容", "是否關注對象"])
                # 寫入資料行
                writer.writerows(data)
            print(f"成功寫入檔案：{output_path}")
            return
        except PermissionError as e:
            if attempt < max_retries - 1:
                print(f"檔案被鎖定，等待重試... (嘗試 {attempt + 1}/{max_retries})")
                import time
                time.sleep(2)  # 等待2秒後重試
            else:
                print(f"無法寫入檔案 {output_path}：{e}")
                print("請關閉可能開啟該檔案的程式（如Excel、記事本等）")
                raise
        except Exception as e:
            print(f"寫入檔案時發生錯誤：{e}")
            raise
