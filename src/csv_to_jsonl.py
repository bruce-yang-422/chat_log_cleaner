import csv
import json
from pathlib import Path

def csv_to_jsonl(csv_path, jsonl_path):
    with open(csv_path, 'r', encoding='utf-8-sig') as f_in, open(jsonl_path, 'w', encoding='utf-8') as f_out:
        reader = csv.DictReader(f_in)
        for row in reader:
            # 欄位標準化（移除多餘空白）
            obj = {
                "date": row["日期"].strip(),
                "time": row["時間"].strip(),
                "user": row["使用者"].strip(),
                "text": row["訊息內容"].strip(),
                "is_watchlist": row.get("是否關注對象", "").strip().lower() in ["true", "1"]
            }
            f_out.write(json.dumps(obj, ensure_ascii=False) + '\n')

def batch_convert(input_dir, output_dir):
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    for csv_file in input_path.glob("*.csv"):
        jsonl_file = output_path / (csv_file.stem + ".jsonl")
        print(f"轉換：{csv_file.name} → {jsonl_file.name}")
        csv_to_jsonl(csv_file, jsonl_file)

if __name__ == "__main__":
    batch_convert("data/output", "data/output_jsonl")
