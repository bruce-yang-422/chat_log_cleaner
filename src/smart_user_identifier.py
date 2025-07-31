#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from collections import Counter, defaultdict
from typing import List, Dict, Tuple, Set
import os

def extract_message_samples(file_path: str, sample_count: int = 50) -> List[Tuple[str, str, str]]:
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
    
    # 支援多種訊息格式（社群環境更複雜）
    message_patterns = [
        # 製表符分隔格式
        re.compile(r"^(\d{2}:\d{2})\t(.+?)\t(.+)"),
        # 標準空格分隔格式
        re.compile(r"^(\d{2}:\d{2})\s+(.+?)\s+(.+)"),
        # 社群格式：時間 + 使用者 + 內容（可能包含特殊字符）
        re.compile(r"^(\d{2}:\d{2})\s+([^～？！，。\s]+(?:\s+[^～？！，。\s]+)*)\s+(.+)"),
        # 寬鬆格式：時間 + 任意使用者名稱 + 內容
        re.compile(r"^(\d{2}:\d{2})\s+([^\s]+(?:\s+[^\s]+)*?)\s+(.+)"),
    ]
    
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
            
            # 嘗試匹配訊息格式
            message_match = None
            for pattern in message_patterns:
                message_match = pattern.match(line)
                if message_match:
                    break
            
            if message_match:
                time, user, content = message_match.groups()
                samples.append((time, user, content))
    
    return samples

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
        user_content_patterns[user].append(content[:50])  # 只取前50個字符
    
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

def identify_real_users(analysis: Dict[str, Dict], min_frequency: float = 0.02) -> List[str]:
    """
    根據分析結果識別真正的使用者名稱（社群環境優化）
    
    Args:
        analysis: 使用者分析結果
        min_frequency: 最小出現頻率閾值
        
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
        
        # 排除過短或過長的名稱
        if stats['length'] < 2 or stats['length'] > 50:
            continue
        
        # 檢查出現頻率（社群環境中降低閾值）
        if stats['frequency'] < min_frequency:
            continue
        
        # 檢查內容多樣性（社群環境中降低要求）
        if stats['content_diversity'] < 0.05:  # 降低到5%
            continue
        
        # 社群環境特殊檢查：檢查是否為有意義的使用者名稱
        # 排除純數字、純符號等
        if user.isdigit() or all(not char.isalnum() for char in user):
            continue
        
        # 如果通過所有檢查，認為是真正使用者
        real_users.append(user)
    
    # 按出現頻率排序
    real_users.sort(key=lambda u: analysis[u]['count'], reverse=True)
    
    return real_users

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
    
    # 對於每個識別出的真正使用者，創建標準化映射
    for real_user in real_users:
        # 檢查是否有相似的使用者名稱（可能是變體）
        for user in analysis.keys():
            if user != real_user:
                # 簡單的相似度檢查（可以根據需要改進）
                if real_user in user or user in real_user:
                    mapping[user] = real_user
                elif real_user.split('_')[0] == user.split('_')[0]:
                    # 如果下劃線前的部分相同，認為是變體
                    mapping[user] = real_user
    
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

def smart_identify_users(file_path: str, sample_count: int = 50) -> Tuple[List[str], Dict[str, str]]:
    """
    智能識別聊天記錄中的使用者名稱
    
    Args:
        file_path: 聊天記錄檔案路徑
        sample_count: 分析樣本數量
        
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
    
    # 根據格式調整識別參數
    if chat_format == 'group':
        min_frequency = 0.02  # 社群環境降低頻率要求
        print("使用社群模式識別（降低頻率要求）")
    else:
        min_frequency = 0.05  # 私聊環境保持較高要求
        print("使用私聊模式識別")
    
    # 識別真正使用者
    real_users = identify_real_users(analysis, min_frequency)
    
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
    test_file = "data/raw/[LINE]測試檔案.txt"
    if os.path.exists(test_file):
        real_users, mapping = smart_identify_users(test_file)
        print(f"\n測試結果：")
        print(f"真正使用者：{real_users}")
        print(f"映射關係：{mapping}")
    else:
        print(f"測試檔案不存在：{test_file}") 