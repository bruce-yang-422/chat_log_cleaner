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
