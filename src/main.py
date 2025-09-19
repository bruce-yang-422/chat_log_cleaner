#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
聊天記錄清理器主程式 (Chat Log Cleaner Main)

此腳本為聊天記錄清理系統的主入口點，負責：
1. 載入配置文件
2. 掃描原始聊天記錄檔案
3. 批量處理多個聊天記錄檔案
4. 將解析結果輸出為CSV格式

工作流程：
1. 讀取 config.json 配置文件
2. 掃描 data/raw/ 目錄下的所有 .txt 檔案
3. 對每個檔案調用 chat_parser.py 進行解析
4. 將結果保存到 data/output/ 目錄

輸入：data/raw/*.txt（原始聊天記錄檔案）
輸出：data/output/*.csv（清理後的CSV檔案）

Authors: 楊翔志 & AI Collective
Studio: tranquility-base
版本: 1.0
"""

import os
import glob
from chat_parser import parse_chat_log
from utils import load_config
from utils import write_to_csv  # 請確認 utils 中已有此函數

RAW_DIR = os.path.join("data", "raw")
OUTPUT_DIR = os.path.join("data", "output")
CONFIG_PATH = "config.json"

def main():
    config = load_config(CONFIG_PATH)
    txt_files = glob.glob(os.path.join(RAW_DIR, "*.txt"))

    if not txt_files:
        print(f"找不到 .txt 檔案於 {RAW_DIR}")
        return

    for txt_file in txt_files:
        filename = os.path.basename(txt_file)
        name_without_ext = os.path.splitext(filename)[0]
        output_path = os.path.join(OUTPUT_DIR, f"{name_without_ext}.csv")

        print(f"處理：{filename}")
        messages = parse_chat_log(txt_file, config)
        write_to_csv(messages, output_path)
        print(f"→ 輸出：{output_path}")

if __name__ == "__main__":
    main()
