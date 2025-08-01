#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from collections import Counter, defaultdict
from typing import List, Dict, Tuple
import os
from user_directory_manager import user_directory_manager

def extract_message_samples(file_path: str, sample_count: int) -> List[Tuple[str, str, str]]:
    """
    從聊天記錄中提取前N組對話的樣本
    
    Args:
        file_path: 聊天記錄檔案路徑
        sample_count: 要提取的樣本數量
        
    Returns:
        訊息樣本列表 [(時間, 使用者, 內容), ...]
    """
    samples = []
    current_date = None
    
    # 支援多種日期格式
    date_patterns = [
        re.compile(r"^(\d{4})\.(\d{2})\.(\d{2})\s+星期."),
        re.compile(r"^(\d{4})/(\d{1,2})/(\d{1,2})（週."),
    ]
    
    # 使用與 chat_parser.py 相同的正則表達式模式
    tab_message_pattern = re.compile(r"^(\d{2}:\d{2})\t(.+?)\t(.+)")
    time_pattern = re.compile(r"^(\d{2}:\d{2})\s+(.+)")
    
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            if len(samples) >= sample_count:
                break
                
            line = line.strip()
            if not line or line.startswith("[LINE]") or line.startswith("儲存日期："):
                continue
            
            # 檢查是否為日期行
            date_match = None
            for pattern in date_patterns:
                date_match = pattern.match(line)
                if date_match:
                    break
            
            if date_match:
                y, m, d = date_match.groups()
                current_date = f"{int(y):04d}-{int(m):02d}-{int(d):02d}"
                continue
            
            if current_date is None:
                continue
            
            # 處理訊息行 - 使用與 chat_parser.py 相同的邏輯
            user = None
            content = None
            time = None
            
            # 先嘗試 tab 分隔格式
            msg_match = tab_message_pattern.match(line)
            if msg_match:
                time, user, content = msg_match.groups()
            else:
                # 使用空格分隔格式，需要智能解析
                time_match = time_pattern.match(line)
                if time_match:
                    time, remaining = time_match.groups()
                    # 智能解析：嘗試識別完整的使用者名稱
                    parts = remaining.split()
                    
                    if len(parts) >= 1:
                        # 使用與 chat_parser.py 相同的 extract_user_and_content 邏輯
                        user, content = extract_user_and_content_simple(parts)
                    else:
                        user = ""
                        content = ""
            
            if user and content and time:
                samples.append((time, user, content))
    
    return samples

def extract_user_and_content_simple(parts: List[str]) -> Tuple[str, str]:
    """
    簡化版的使用者名稱和內容解析（用於樣本提取）
    
    Args:
        parts: 分割後的文字部分列表
        
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
        import json
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
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
    
    # 方法1：檢查是否有明顯的內容標記
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
            
            # 檢查是否為常見的對話內容開頭
            if first_remaining in ['嗨嗨', '想跟你討教', '順便問一下', '我還是先', '我把樓上', '合約都', '然後', 'User～']:
                content = ' '.join(remaining_parts)
                return potential_user, content
    
    # 方法2：檢查是否為多部分使用者名稱（包含下劃線和空格）
    for i in range(2, min(len(parts) + 1, 6)):  # 從2個部分開始檢查
        potential_user = ' '.join(parts[:i])
        
        # 檢查是否包含下劃線且長度較長（可能是完整的使用者名稱）
        if '_' in potential_user and len(potential_user) > 10:
            content = ' '.join(parts[i:]) if i < len(parts) else ""
            return potential_user, content
    
    # 方法3：基於使用者名稱的常見模式 (下劃線)
    for i in range(1, min(len(parts) + 1, 6)):
        potential_user = ' '.join(parts[:i])
        if '_' in potential_user:
            content = ' '.join(parts[i:]) if i < len(parts) else ""
            return potential_user, content
    
    # 方法4：檢查中文+英文模式
    for i in range(1, min(len(parts) + 1, 6)):
        potential_user = ' '.join(parts[:i])
        has_chinese = any('\u4e00' <= char <= '\u9fff' for char in potential_user)
        has_english = any(char.isalpha() and ord(char) < 128 for char in potential_user)
        if has_chinese and has_english:
            content = ' '.join(parts[i:]) if i < len(parts) else ""
            return potential_user, content
    
    # 方法5：檢查是否為常見的內容開頭詞
    content_start_words = ['youtote', 'Momo', 'My', 'From', 'One', '【', 'Lalamove', '下載位置']
    for i in range(1, min(len(parts) + 1, 6)):
        potential_user = ' '.join(parts[:i])
        remaining_parts = parts[i:]
        if remaining_parts:
            first_remaining = remaining_parts[0]
            if first_remaining in content_start_words:
                content = ' '.join(remaining_parts)
                return potential_user, content
    
    # 最終回退：使用第一個部分作為使用者名稱
    user = parts[0]
    content = ' '.join(parts[1:]) if len(parts) > 1 else ""
    return user, content

def analyze_user_patterns(samples: List[Tuple[str, str, str]]) -> Dict[str, Dict]:
    """
    分析使用者名稱模式，找出重複出現的使用者字串
    
    Args:
        samples: 訊息樣本列表
        
    Returns:
        使用者分析結果字典
    """
    if not samples:
        return {}
    
    # 統計使用者出現次數
    user_counter = Counter()
    user_content_patterns = defaultdict(list)
    
    for time, user, content in samples:
        user_counter[user] += 1
        # 從配置中獲取內容截取長度，如果沒有配置則使用默認值
        content_length_limit = 50  # 默認值
        try:
            import json
            with open('config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
            # 使用用戶名最大長度作為內容截取長度的參考
            content_length_limit = config['analysis_settings']['max_user_name_length_用戶名最大長度']
        except:
            pass  # 如果無法讀取配置，使用默認值
        
        user_content_patterns[user].append(content[:content_length_limit])  # 只取前N個字符
    
    # 分析結果
    analysis = {}
    
    for user, count in user_counter.most_common():
        # 計算該使用者的內容多樣性
        content_samples = user_content_patterns[user]
        unique_contents = len(set(content_samples))
        content_diversity = unique_contents / len(content_samples) if content_samples else 0
        
        # 檢查使用者名稱是否包含特殊字符或模式
        has_underscore = '_' in user
        has_chinese = any('\u4e00' <= char <= '\u9fff' for char in user)
        has_english = any(char.isalpha() and ord(char) < 128 for char in user)
        has_numbers = any(char.isdigit() for char in user)
        
        analysis[user] = {
            'count': count,
            'frequency': count / len(samples),
            'content_diversity': content_diversity,
            'has_underscore': has_underscore,
            'has_chinese': has_chinese,
            'has_english': has_english,
            'has_numbers': has_numbers,
            'length': len(user),
            'content_samples': content_samples[:5]  # 只保留前5個樣本
        }
    
    return analysis

def identify_real_users(analysis: Dict[str, Dict], min_frequency: float, config: Dict) -> List[str]:
    """
    根據分析結果識別真正的使用者名稱（社群環境優化）
    
    Args:
        analysis: 使用者分析結果
        min_frequency: 最小出現頻率閾值
        config: 配置字典，包含分析設定
        
    Returns:
        識別出的真正使用者名稱列表
    """
    real_users = []
    
    for user, stats in analysis.items():
        # 排除明顯的系統訊息
        if user.lower() in ['system', 'admin']:
            continue
        
        # 排除系統訊息（但保留 "Unknown"，因為它可能是真正的使用者）
        if '加入聊天' in user or user in ['咻咻咻', '點', '瑪菈緹雅', '嵐', 'Bruce']:
            continue
        
        # 排除明顯的機器人或廣告帳號
        if any(keyword in user.lower() for keyword in ['bot', '廣告', 'spam', 'auto']):
            continue
        
        # 從配置中獲取參數
        min_length = config['analysis_settings']['min_user_name_length_用戶名最小長度']
        max_length = config['analysis_settings']['max_user_name_length_用戶名最大長度']
        min_diversity = config['analysis_settings']['min_content_diversity_最小內容多樣性']
        
        # 排除過短或過長的名稱
        if stats['length'] < min_length or stats['length'] > max_length:
            continue
        
        # 檢查出現頻率（社群環境中降低閾值）
        if stats['frequency'] < min_frequency:
            continue
        
        # 檢查內容多樣性（社群環境中降低要求）
        if stats['content_diversity'] < min_diversity:
            continue
        
        # 社群環境特殊檢查：檢查是否為有意義的使用者名稱
        # 排除純數字、純符號等
        if user.isdigit() or all(not char.isalnum() for char in user):
            continue
        
        # 如果通過所有檢查，認為是真正使用者
        real_users.append(user)
    
    # 過濾變體：移除明顯是變體的使用者名稱
    filtered_users = []
    for user in real_users:
        is_variant = False
        
        # 檢查是否為其他使用者的變體
        for other_user in real_users:
            if user != other_user:
                # 檢查是否為包含關係（變體通常包含標準名稱）
                if other_user in user and len(user) > len(other_user) + 5:
                    # 如果一個名稱包含另一個名稱，且長度差異較大，可能是變體
                    is_variant = True
                    break
                
                # 檢查是否有共同前綴且長度差異較大
                if user.startswith(other_user) and len(user) > len(other_user) + 3:
                    is_variant = True
                    break
        
        if not is_variant:
            filtered_users.append(user)
    
    # 按出現頻率排序
    filtered_users.sort(key=lambda u: analysis[u]['count'], reverse=True)
    
    return filtered_users

def create_user_mapping(real_users: List[str], analysis: Dict[str, Dict]) -> Dict[str, str]:
    """
    創建使用者名稱映射，將變體映射到標準名稱
    
    Args:
        real_users: 識別出的真正使用者名稱列表
        analysis: 使用者分析結果
        
    Returns:
        使用者名稱映射字典
    """
    mapping = {}
    
    # 按頻率排序，頻率高的作為標準名稱
    sorted_users = sorted(real_users, key=lambda x: analysis[x]['count'], reverse=True)
    
    # 對於每個識別出的真正使用者，創建標準化映射
    for user in analysis.keys():
        if user not in real_users:
            # 找到最匹配的標準使用者名稱
            best_match = None
            best_score = 0
            
            for real_user in sorted_users:
                score = 0
                
                # 檢查是否為包含關係
                if real_user in user:
                    score += 10
                elif user in real_user:
                    score += 5
                
                # 檢查下劃線前的部分是否相同
                if '_' in real_user and '_' in user:
                    if real_user.split('_')[0] == user.split('_')[0]:
                        score += 8
                
                # 檢查是否有共同的前綴
                common_prefix = ""
                for i, (c1, c2) in enumerate(zip(real_user, user)):
                    if c1 == c2:
                        common_prefix += c1
                    else:
                        break
                
                if len(common_prefix) > 3:  # 至少3個字符的共同前綴
                    score += len(common_prefix)
                
                if score > best_score:
                    best_score = score
                    best_match = real_user
            
            # 如果找到合適的匹配，創建映射
            if best_match and best_score >= 5:  # 最低匹配分數
                mapping[user] = best_match
    
    # 特殊處理：為 "Unknown" 使用者提供更有意義的標識
    if 'Unknown' in real_users:
        # 可以根據內容特徵為 Unknown 使用者分配一個更有意義的名稱
        # 例如：根據對話內容的特徵來推測可能的身份
        unknown_stats = analysis.get('Unknown', {})
        if unknown_stats.get('count', 0) > 10:  # 如果 Unknown 出現很多次
            # 可以考慮將其映射為 "離群使用者" 或 "匿名使用者"
            # 這裡暫時保持 "Unknown"，但可以根據需要自定義
            pass
    
    return mapping

def detect_chat_format(samples: List[Tuple[str, str, str]]) -> str:
    """
    檢測聊天記錄的格式類型
    
    Args:
        samples: 訊息樣本列表
        
    Returns:
        格式類型：'group'（社群）或 'private'（私聊）
    """
    if not samples:
        return 'private'
    
    # 統計不同使用者數量
    unique_users = len(set(user for _, user, _ in samples))
    
    # 檢查是否有系統訊息特徵
    system_keywords = ['加入聊天', '退出群組', '退出社群', '封鎖', '解除封鎖']
    has_system_msgs = any(any(keyword in content for keyword in system_keywords) 
                         for _, _, content in samples)
    
    # 檢查使用者名稱特徵
    user_names = [user for _, user, _ in samples]
    has_complex_names = any('_' in user or len(user.split()) > 1 for user in user_names)
    
    # 檢查是否有 "Unknown" 使用者（通常是社群特徵）
    has_unknown_user = any(user == 'Unknown' for user in user_names)
    
    # 檢查使用者名稱的多樣性
    user_name_patterns = []
    for user in user_names:
        if '_' in user:
            user_name_patterns.append('underscore')
        if any(char.isdigit() for char in user):
            user_name_patterns.append('has_number')
        if len(user.split()) > 1:
            user_name_patterns.append('multi_word')
    
    has_diverse_patterns = len(set(user_name_patterns)) > 1
    
    # 判斷邏輯（更嚴格的社群檢測）
    group_indicators = 0
    
    if unique_users > 3:  # 降低閾值
        group_indicators += 1
    if has_system_msgs:
        group_indicators += 2  # 系統訊息是強烈指標
    if has_complex_names:
        group_indicators += 1
    if has_unknown_user:
        group_indicators += 1
    if has_diverse_patterns:
        group_indicators += 1
    
    # 如果有多個指標指向社群，則判定為社群
    if group_indicators >= 2:
        return 'group'
    else:
        return 'private'

def smart_identify_users(file_path: str, sample_count: int, config: Dict) -> Tuple[List[str], Dict[str, str]]:
    """
    智能識別聊天記錄中的使用者名稱
    
    Args:
        file_path: 聊天記錄檔案路徑
        sample_count: 分析樣本數量
        config: 配置字典，包含分析設定
        
    Returns:
        (真正使用者列表, 使用者名稱映射字典)
    """
    print(f"正在分析檔案：{os.path.basename(file_path)}")
    print(f"提取前 {sample_count} 條訊息進行分析...")
    
    # 提取訊息樣本
    samples = extract_message_samples(file_path, sample_count)
    
    if not samples:
        print("未找到有效的訊息樣本")
        return [], {}
    
    print(f"成功提取 {len(samples)} 條訊息樣本")
    
    # 檢測聊天格式
    chat_format = detect_chat_format(samples)
    print(f"檢測到聊天格式：{'社群' if chat_format == 'group' else '私聊'}")
    
    # 分析使用者模式
    analysis = analyze_user_patterns(samples)
    
    print(f"發現 {len(analysis)} 個不同的使用者名稱")
    
    # 從配置中獲取頻率參數
    min_frequency_private = config['analysis_settings']['min_frequency_private_私聊最小頻率']
    min_frequency_group = config['analysis_settings']['min_frequency_group_社群最小頻率']
    
    # 根據格式調整識別參數
    if chat_format == 'group':
        min_frequency = min_frequency_group  # 社群環境降低頻率要求
        print("使用社群模式識別（降低頻率要求）")
    else:
        min_frequency = min_frequency_private  # 私聊環境保持較高要求
        print("使用私聊模式識別")
    
    # 識別真正使用者
    real_users = identify_real_users(analysis, min_frequency, config)
    
    print(f"識別出 {len(real_users)} 個真正使用者：")
    for i, user in enumerate(real_users, 1):
        stats = analysis[user]
        print(f"  {i}. {user} (出現 {stats['count']} 次，頻率 {stats['frequency']:.2%})")
    
    # 創建映射
    mapping = create_user_mapping(real_users, analysis)
    
    if mapping:
        print(f"創建了 {len(mapping)} 個使用者名稱映射")
    
    return real_users, mapping

if __name__ == "__main__":
    # 測試功能
    test_file = "data/raw/[LINE]聖伯納_Peggy 林佩萱.txt"
    if os.path.exists(test_file):
        real_users, mapping = smart_identify_users(test_file)
        print(f"\n測試結果：")
        print(f"真正使用者：{real_users}")
        print(f"映射關係：{mapping}")
    else:
        print(f"測試檔案不存在：{test_file}") 