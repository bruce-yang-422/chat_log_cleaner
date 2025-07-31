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
