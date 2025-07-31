import re
from datetime import datetime

def parse_chat_log(file_path, config):
    messages = []
    current_date = None
    last_entry = None

    date_start = datetime.strptime(config["date_range"]["start"], "%Y-%m-%d")
    date_end = datetime.strptime(config["date_range"]["end"], "%Y-%m-%d")
    watchlist = set(config["watchlist_users"])
    exclude_keywords = set(config["exclude_keywords"])

    date_pattern_dot = re.compile(r"^(\d{4})\.(\d{2})\.(\d{2})\s+星期.")
    date_pattern_slash = re.compile(r"^(\d{4})/(\d{1,2})/(\d{1,2})（週.")
    tab_message_pattern = re.compile(r"^(\d{2}:\d{2})\t(.+?)\t(.+)")
    space_message_pattern = re.compile(r"^(\d{2}:\d{2})\s+(.+?)\s+(.+)")

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("[LINE]") or line.startswith("儲存日期："):
                continue

            # 日期解析
            date_match = date_pattern_dot.match(line) or date_pattern_slash.match(line)
            if date_match:
                y, m, d = date_match.groups()
                current_date = f"{int(y):04d}-{int(m):02d}-{int(d):02d}"
                continue

            if current_date is None:
                continue

            msg_match = tab_message_pattern.match(line) or space_message_pattern.match(line)
            if msg_match:
                time, user, content = msg_match.groups()

                # 過濾關鍵字
                if any(kw in user or kw in content for kw in exclude_keywords):
                    last_entry = None
                    continue

                # 過濾日期區間
                dt = datetime.strptime(current_date, "%Y-%m-%d")
                if not (date_start <= dt <= date_end):
                    last_entry = None
                    continue

                is_watchlist = user in watchlist
                last_entry = [current_date, time, user, content, is_watchlist]
                messages.append(last_entry)
            elif last_entry:
                if any(kw in line for kw in exclude_keywords):
                    continue
                last_entry[3] += "\n" + line

    return messages
