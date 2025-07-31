# Chat Log Cleaner 🗂️

一個功能強大的聊天記錄清洗工具，專門處理 LINE 等通訊軟體的匯出記錄，將其轉換為結構化的 CSV 和 JSONL 格式，支援多種過濾和處理功能。

## ✨ 主要功能

- 🔍 **智能解析**：自動識別聊天記錄的日期、時間、使用者和訊息內容
- 📅 **日期範圍過濾**：可設定特定日期區間進行資料篩選
- 👥 **關注名單**：標記特定使用者的訊息為關注對象
- 🚫 **關鍵字過濾**：自動排除包含特定關鍵字的訊息
- 📊 **多格式輸出**：支援 CSV 和 JSONL 兩種輸出格式
- 🌳 **專案結構生成**：內建目錄樹生成工具

## 📂 專案結構

```
chat_log_cleaner/
├── 📁 data/
│   ├── 📁 raw/              # 原始聊天記錄 TXT 檔案
│   ├── 📁 output/           # 清洗後的 CSV 檔案
│   └── 📁 output_jsonl/     # JSONL 格式輸出
├── 📁 src/
│   ├── 🐍 main.py           # 主執行腳本
│   ├── 🐍 chat_parser.py    # 聊天記錄解析核心邏輯
│   ├── 🐍 utils.py          # 通用工具函數
│   ├── 🐍 csv_to_jsonl.py   # CSV 轉 JSONL 轉換器
│   └── 🐍 TreeMaker.py      # 目錄樹生成工具
├── ⚙️ config.json           # 配置檔案
├── 📋 requirements.txt      # Python 依賴套件
├── 📖 README.md             # 專案說明文件
└── 🌳 tree.txt              # 專案結構樹狀圖
```

## 🚀 快速開始

### 1. 環境準備

```bash
# 克隆專案
git clone <repository-url>
cd chat_log_cleaner

# 安裝依賴套件
pip install -r requirements.txt
```

### 2. 配置設定

編輯 `config.json` 檔案：

```json
{
  "date_range": {
    "start": "2025-07-15",
    "end": "2025-07-31"
  },
  "watchlist_users": [
    "俏闆娘",
    "重要聯絡人"
  ],
  "exclude_keywords": [
    "加入聊天",
    "退出社群",
    "退出群組",
    "封鎖",
    "解除封鎖"
  ]
}
```

### 3. 放置原始檔案

將聊天記錄 TXT 檔案放入 `data/raw/` 資料夾：

```
data/raw/
├── chat_20250715.txt
├── chat_20250716.txt
└── ...
```

### 4. 執行清洗

```bash
# 執行主要清洗流程
python src/main.py

# 轉換為 JSONL 格式（可選）
python src/csv_to_jsonl.py
```

## 📊 輸出格式

### CSV 格式
```csv
日期,時間,使用者,訊息內容,是否關注對象
2025-07-15,14:30,俏闆娘,你好！,True
2025-07-15,14:35,其他使用者,回覆訊息,False
```

### JSONL 格式
```jsonl
{"date": "2025-07-15", "time": "14:30", "user": "俏闆娘", "text": "你好！", "is_watchlist": true}
{"date": "2025-07-15", "time": "14:35", "user": "其他使用者", "text": "回覆訊息", "is_watchlist": false}
```

## ⚙️ 配置說明

### 日期範圍設定
- `start`: 開始日期（YYYY-MM-DD 格式）
- `end`: 結束日期（YYYY-MM-DD 格式）

### 關注名單
- `watchlist_users`: 需要特別標記的使用者清單
- 這些使用者的訊息會在輸出中標記為 `True`

### 排除關鍵字
- `exclude_keywords`: 包含這些關鍵字的訊息會被自動過濾
- 支援使用者名稱和訊息內容的關鍵字過濾

## 🛠️ 進階功能

### 目錄樹生成

```bash
# 生成專案結構樹狀圖
python src/TreeMaker.py

# 包含檔案大小資訊
python src/TreeMaker.py --size

# 限制深度
python src/TreeMaker.py --depth 3

# 顯示統計資訊
python src/TreeMaker.py --stats
```

### 批次處理

工具會自動處理 `data/raw/` 資料夾中的所有 `.txt` 檔案，並在 `data/output/` 中生成對應的 CSV 檔案。

## 📋 支援的聊天記錄格式

目前支援以下格式的聊天記錄：

1. **日期格式**：
   - `2025.07.15 星期三`
   - `2025/7/15（週三）`

2. **訊息格式**：
   - `14:30	使用者名稱	訊息內容`
   - `14:30 使用者名稱 訊息內容`

## 🔧 技術細節

- **編碼處理**：自動處理 UTF-8 編碼，輸出使用 `utf-8-sig` 確保 Excel 相容性
- **多行訊息**：自動合併跨行的訊息內容
- **記憶體優化**：逐行處理，適合大型聊天記錄檔案
- **錯誤處理**：優雅的錯誤處理和日誌輸出

## 📦 依賴套件

- `chardet`: 字元編碼檢測
- `colorama`: 終端彩色輸出
- `numpy`: 數值計算
- `pandas`: 資料處理
- `python-dateutil`: 日期處理
- `pytz`: 時區處理
- `tqdm`: 進度條顯示

## 🤝 貢獻指南

1. Fork 本專案
2. 建立功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交變更 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

## 📄 授權條款

本專案採用 MIT 授權條款 - 詳見 [LICENSE](LICENSE) 檔案

## 📞 聯絡資訊

如有問題或建議，請透過以下方式聯絡：

- 建立 Issue
- 發送 Pull Request
- 電子郵件：[your-email@example.com]

---

**注意**：使用本工具時請確保遵守相關的隱私政策和資料保護法規。
