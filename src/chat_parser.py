#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
聊天記錄解析器 (Chat Log Parser)

此腳本負責解析聊天記錄檔案，提取訊息內容並進行智能過濾。
主要功能包括：
1. 解析多種聊天記錄格式（LINE、WhatsApp等）
2. 智能識別使用者名稱和訊息內容
3. 根據配置進行日期範圍和關鍵字過濾
4. 支援關注對象和關鍵字標記
5. 處理多行訊息和特殊格式

支援的輸入格式：
- Tab分隔格式：時間\t使用者\t內容
- 空格分隔格式：時間 使用者 內容
- 多種日期格式：YYYY.MM.DD 星期X 或 YYYY/MM/DD（週X）

輸出格式：
- CSV檔案，包含：日期、時間、使用者、訊息內容、是否關注對象

Authors: 楊翔志 & AI Collective
Studio: tranquility-base
版本: 1.0
"""

import re
from datetime import datetime
from user_identifier import identify_users_from_file, normalize_user_name
from smart_user_identifier import smart_identify_users
from user_directory_manager import user_directory_manager

def extract_user_and_content(parts, real_users=None, user_mapping=None, config=None):
    """
    智能解析使用者名稱和內容
    
    Args:
        parts: 分割後的文字部分列表
        real_users: 智能識別出的真正使用者列表
        user_mapping: 使用者名稱映射字典
        
    Returns:
        (user, content): 使用者名稱和內容的元組
    """
    if not parts:
        return "", ""
    
    # 如果只有一個部分，直接返回
    if len(parts) == 1:
        return parts[0], ""
    
    # 方法0：優先處理簡短明確的使用者名稱（如 "WhoAmI"）
    # 檢查第一個部分是否為明確的使用者名稱
    first_part = parts[0]
    
    # 簡短明確的使用者名稱特徵：
    # 1. 長度適中（可配置範圍）
    # 2. 不包含空格
    # 3. 不是表情符號或特殊符號
    # 4. 不是URL
    # 5. 不是明顯的內容詞
    min_username_length = 2
    max_username_length = 15
    
    # 從配置中獲取使用者名稱長度限制
    try:
        import json
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        min_username_length = config['analysis_settings']['min_user_name_length_用戶名最小長度']
        max_username_length = config['analysis_settings']['max_user_name_length_用戶名最大長度']
    except:
        pass  # 如果無法讀取配置，使用默認值
    
    # 從配置中獲取解析設置
    emoji_chars = ['😀', '😂', '😅', '🙏', '～']  # 默認值
    content_indicators = ['貼圖', '圖片', '影片', '語音訊息', '檔案', '位置']  # 默認值
    conversation_starters = ['嗨嗨', '想跟你討教', '順便問一下', '我還是先', '我把樓上', '合約都', '然後', 'User～']  # 默認值
    
    try:
        parsing_settings = config.get('parsing_settings', {})
        emoji_chars = parsing_settings.get('emoji_chars', emoji_chars)
        content_indicators = parsing_settings.get('content_indicators', content_indicators)
        conversation_starters = parsing_settings.get('conversation_starters', conversation_starters)
    except:
        pass  # 如果無法讀取配置，使用默認值
    
    if (min_username_length <= len(first_part) <= max_username_length and 
        ' ' not in first_part and 
        not any(char in first_part for char in emoji_chars) and
        not first_part.startswith('http') and
        first_part not in content_indicators and
        first_part not in conversation_starters):
        
        # 檢查是否為已知使用者
        result = user_directory_manager.find_user_by_name(first_part)
        if result:
            content = ' '.join(parts[1:]) if len(parts) > 1 else ""
            return result, content
        
        # 如果有智能識別結果，檢查是否匹配
        if real_users and first_part in real_users:
            content = ' '.join(parts[1:]) if len(parts) > 1 else ""
            return first_part, content
        
        # 檢查映射關係
        if user_mapping and first_part in user_mapping:
            mapped_user = user_mapping[first_part]
            content = ' '.join(parts[1:]) if len(parts) > 1 else ""
            return mapped_user, content
        
        # 如果第一個部分看起來像使用者名稱，直接使用
        content = ' '.join(parts[1:]) if len(parts) > 1 else ""
        return first_part, content
    
    # 方法1：使用使用者名冊（完全比對）
    for i in range(1, min(len(parts) + 1, 6)):
        potential_user = ' '.join(parts[:i])
        
        # 檢查是否為已知使用者（完全比對）
        result = user_directory_manager.find_user_by_name(potential_user)
        if result:
            content = ' '.join(parts[i:]) if i < len(parts) else ""
            return result, content
    
    # 如果有智能識別結果，優先使用
    if real_users:
        # 方法1：檢查是否匹配智能識別的使用者名稱
        for i in range(1, min(len(parts) + 1, 6)):
            potential_user = ' '.join(parts[:i])
            if potential_user in real_users:
                content = ' '.join(parts[i:]) if i < len(parts) else ""
                return potential_user, content
        
        # 檢查映射關係
        if user_mapping:
            for i in range(1, min(len(parts) + 1, 6)):
                potential_user = ' '.join(parts[:i])
                if potential_user in user_mapping:
                    mapped_user = user_mapping[potential_user]
                    content = ' '.join(parts[i:]) if i < len(parts) else ""
                    return mapped_user, content
    
    # 已知的完整使用者名稱模式（請根據實際情況修改）
    known_full_names = [
        # 範例格式，請替換為實際的使用者名稱
        # 'User1_Group User1_FullName',
        # 'User2_Group User2_FullName',
        # 'User3_Group User3_FullName',
        # 'User4_Group User4_FullName'
    ]
    
    # 方法1：檢查是否為已知的完整使用者名稱
    for i in range(1, min(len(parts) + 1, 6)):
        potential_user = ' '.join(parts[:i])
        if potential_user in known_full_names:
            content = ' '.join(parts[i:]) if i < len(parts) else ""
            return potential_user, content
    
    # 方法2：檢查是否有明顯的內容標記
    content_indicators = ['貼圖', '圖片', '影片', '語音訊息', '檔案', '位置']
    
    for i in range(1, min(len(parts) + 1, 6)):
        potential_user = ' '.join(parts[:i])
        remaining_parts = parts[i:]
        
        if remaining_parts:
            first_remaining = remaining_parts[0]
            
            # 檢查是否為內容標記
            if first_remaining in content_indicators:
                content = ' '.join(remaining_parts)
                return potential_user, content
            
            # 檢查是否為表情符號或特殊符號
            if any(char in first_remaining for char in ['😀', '😂', '😅', '🙏', '～', '～', '～']):
                content = ' '.join(remaining_parts)
                return potential_user, content
            
            # 檢查是否為URL
            if first_remaining.startswith('http'):
                content = ' '.join(remaining_parts)
                return potential_user, content
            
            # 檢查是否為常見的對話內容開頭（請根據實際情況修改）
            if first_remaining in ['嗨嗨', '想跟你討教', '順便問一下', '我還是先', '我把樓上', '合約都', '然後', 'User～']:
                content = ' '.join(remaining_parts)
                return potential_user, content
    
    # 方法3：檢查是否為多部分使用者名稱（包含下劃線和空格）
    # 這是針對複雜使用者名稱的特殊處理
    for i in range(2, min(len(parts) + 1, 6)):  # 從2個部分開始檢查
        potential_user = ' '.join(parts[:i])
        
        # 檢查是否包含下劃線且長度較長（可能是完整的使用者名稱）
        if '_' in potential_user and len(potential_user) > 10:
            content = ' '.join(parts[i:]) if i < len(parts) else ""
            return potential_user, content
    
    # 方法4：基於使用者名稱的常見模式
    # 檢查是否有下劃線模式（通常表示完整的使用者名稱）
    for i in range(1, min(len(parts) + 1, 6)):
        potential_user = ' '.join(parts[:i])
        
        # 如果包含下劃線，可能是完整的使用者名稱
        if '_' in potential_user:
            content = ' '.join(parts[i:]) if i < len(parts) else ""
            return potential_user, content
    
    # 方法5：檢查中文+英文模式
    for i in range(1, min(len(parts) + 1, 6)):
        potential_user = ' '.join(parts[:i])
        
        # 檢查是否包含中文和英文
        has_chinese = any('\u4e00' <= char <= '\u9fff' for char in potential_user)
        has_english = any(char.isalpha() and ord(char) < 128 for char in potential_user)
        
        if has_chinese and has_english:
            content = ' '.join(parts[i:]) if i < len(parts) else ""
            return potential_user, content
    
    # 方法6：檢查是否為常見的內容開頭詞
    # 這些詞通常不會是使用者名稱的一部分
    content_start_words = ['youtote', 'Momo', 'My', 'From', 'One', '【', 'Lalamove', '下載位置']
    
    for i in range(1, min(len(parts) + 1, 6)):
        potential_user = ' '.join(parts[:i])
        remaining_parts = parts[i:]
        
        if remaining_parts:
            first_remaining = remaining_parts[0]
            
            # 檢查是否為內容開頭詞
            if first_remaining in content_start_words:
                content = ' '.join(remaining_parts)
                return potential_user, content
    
    # 方法7：如果都沒有匹配，使用第一個部分作為使用者名稱
    user = parts[0]
    content = ' '.join(parts[1:]) if len(parts) > 1 else ""
    return user, content

def parse_chat_log(file_path, config):
    """
    解析聊天記錄檔案，提取訊息並進行過濾
    
    Args:
        file_path: 聊天記錄檔案路徑
        config: 配置字典，包含日期範圍、關注用戶列表、排除關鍵字等
        
    Returns:
        解析後的訊息列表，每個訊息包含 [日期, 時間, 使用者, 內容, 是否關注對象]
    """
    messages = []
    current_date = None
    last_entry = None

    # 從配置中提取設定
    date_start = datetime.strptime(config["date_range"]["start"], "%Y-%m-%d")
    date_end = datetime.strptime(config["date_range"]["end"], "%Y-%m-%d")
    watchlist = set(config["watchlist_users"])
    exclude_keywords = set(config["exclude_keywords"])
    watchlist_keywords = set(config.get("watchlist_keywords", []))
    
    # 從配置中獲取分析參數
    analysis_settings = config['analysis_settings']
    sample_count = analysis_settings['sample_count_智能識別樣本數量']
    traditional_sample_count = analysis_settings['traditional_sample_count_傳統識別樣本數量']
    
    # 智能使用者識別
    print(f"正在進行智能使用者識別...")
    try:
        real_users, user_mapping = smart_identify_users(file_path, sample_count=sample_count, config=config)
        print(f"智能識別結果：{real_users}")
        if user_mapping:
            print(f"使用者映射：{user_mapping}")
    except Exception as e:
        print(f"智能識別失敗：{e}")
        real_users, user_mapping = [], {}
    
    # 傳統使用者模式識別（作為備用）
    print(f"正在分析傳統使用者模式...")
    user_patterns = identify_users_from_file(file_path, sample_count=traditional_sample_count)
    if user_patterns:
        print(f"識別出 {len(user_patterns)} 個使用者模式：")
        for prefix, full_name in user_patterns.items():
            print(f"  '{prefix}' -> '{full_name}'")
    else:
        print("未識別出明確的使用者模式")

    # 正則表達式模式
    date_pattern_dot = re.compile(r"^(\d{4})\.(\d{2})\.(\d{2})\s+星期.")
    date_pattern_slash = re.compile(r"^(\d{4})/(\d{1,2})/(\d{1,2})（週.")
    tab_message_pattern = re.compile(r"^(\d{2}:\d{2})\t(.+?)\t(.+)")
    time_pattern = re.compile(r"^(\d{2}:\d{2})\s+(.+)")

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # 跳過空行和系統訊息
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

            # 處理訊息行
            user = None
            content = None
            time = None

            # 先嘗試 tab 分隔格式
            msg_match = tab_message_pattern.match(line)
            if msg_match:
                time, user, content = msg_match.groups()
            else:
                # 使用智能解析空格分隔格式
                time_match = time_pattern.match(line)
                if time_match:
                    time, remaining = time_match.groups()
                    # 智能解析：嘗試識別完整的使用者名稱
                    parts = remaining.split()
                    
                    if len(parts) >= 1:
                        # 嘗試識別完整的使用者名稱
                        user, content = extract_user_and_content(parts, real_users, user_mapping, config)
                    else:
                        user = ""
                        content = ""

            # 如果成功解析出訊息
            if user and content and time:
                # 智慧型使用者名稱標準化
                normalized_user = normalize_user_name(user, user_patterns)
                
                # 修正內容：移除可能包含在使用者名稱中的部分
                # 如果標準化後的使用者名稱比原始使用者名稱長，需要從內容中移除多餘的部分
                if len(normalized_user) > len(user):
                    # 計算需要從內容中移除的部分
                    extra_parts = normalized_user[len(user):].strip()
                    if content.startswith(extra_parts):
                        # 移除內容開頭的使用者名稱部分
                        content = content[len(extra_parts):].strip()
                
                # 過濾關鍵字
                if any(kw in normalized_user or kw in content for kw in exclude_keywords):
                    last_entry = None
                    continue

                # 過濾日期區間
                dt = datetime.strptime(current_date, "%Y-%m-%d")
                if not (date_start <= dt <= date_end):
                    last_entry = None
                    continue

                # 檢查是否為關注對象
                is_watchlist = normalized_user in watchlist
                
                # 檢查是否包含關注關鍵字
                contains_watchlist_keywords = any(kw in content for kw in watchlist_keywords)
                
                # 如果包含關注關鍵字，標記為關注對象
                if contains_watchlist_keywords:
                    is_watchlist = True
                
                last_entry = [current_date, time, normalized_user, content, is_watchlist]
                messages.append(last_entry)
            elif last_entry:
                # 處理多行訊息
                # 檢查這行是否為新的時間戳（新訊息）
                time_match = time_pattern.match(line)
                if time_match:
                    # 這是新的訊息，不應該附加到上一個訊息
                    continue
                
                # 過濾關鍵字
                if any(kw in line for kw in exclude_keywords):
                    continue
                # 將這行附加到上一個訊息的內容中
                last_entry[3] += "\n" + line

    return messages
