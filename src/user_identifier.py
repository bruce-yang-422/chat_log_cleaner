import re
from collections import Counter, defaultdict
from typing import List, Dict, Tuple

def extract_user_samples(file_path: str, sample_count: int = 20) -> List[str]:
    """
    從聊天記錄中提取前N組對話的使用者名稱樣本
    
    Args:
        file_path: 聊天記錄檔案路徑
        sample_count: 要提取的樣本數量
        
    Returns:
        使用者名稱樣本列表
    """
    user_samples = []
    current_date = None
    
    # 日期和訊息模式
    date_pattern_dot = re.compile(r"^(\d{4})\.(\d{2})\.(\d{2})\s+星期.")
    date_pattern_slash = re.compile(r"^(\d{4})/(\d{1,2})/(\d{1,2})（週.")
    tab_message_pattern = re.compile(r"^(\d{2}:\d{2})\t(.+?)\t(.+)")
    # 使用與 chat_parser.py 相同的邏輯
    time_pattern = re.compile(r"^(\d{2}:\d{2})\s+(.+)")
    
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
            
            # 訊息解析
            msg_match = tab_message_pattern.match(line)
            if msg_match:
                time, user, content = msg_match.groups()
                user_samples.append(user)
                
                if len(user_samples) >= sample_count:
                    break
            else:
                # 使用與 chat_parser.py 相同的邏輯
                time_match = time_pattern.match(line)
                if time_match:
                    time, remaining = time_match.groups()
                    parts = remaining.split()
                    
                    if len(parts) >= 1:
                        # 簡化邏輯：第一個部分是用戶名
                        user = parts[0]
                        
                        user_samples.append(user)
                        
                        if len(user_samples) >= sample_count:
                            break
    
    return user_samples

def analyze_user_patterns(user_samples: List[str]) -> Dict[str, str]:
    """
    分析使用者名稱模式，找出重複的開頭部分並建立標準化映射
    
    Args:
        user_samples: 使用者名稱樣本列表
        
    Returns:
        標準化映射字典 {短名稱: 完整名稱}
    """
    if not user_samples:
        return {}
    
    # 統計每個完整名稱的出現次數
    name_counter = Counter(user_samples)
    
    # 基於對話模式分析，識別完整的使用者名稱
    # 這裡可以根據實際聊天記錄格式自定義映射規則
    # 例如：短名稱 -> 完整名稱
    
    # 常見的完整使用者名稱模式（請根據實際情況修改）
    full_name_patterns = {
        # 範例：'短名稱': '完整名稱'
        # 'User1': 'User1 FullName',
        # 'User2': 'User2 CompleteName',
    }
    
    # 創建標準化映射
    normalized_patterns = {}
    
    for short_name, full_name in full_name_patterns.items():
        if short_name in name_counter:
            normalized_patterns[short_name] = full_name
    
    return normalized_patterns

def normalize_user_name(user_name: str, user_patterns: Dict[str, str]) -> str:
    """
    使用識別出的模式來標準化使用者名稱
    
    Args:
        user_name: 原始使用者名稱
        user_patterns: 標準化映射字典
        
    Returns:
        標準化後的使用者名稱
    """
    # 檢查是否有匹配的前綴模式
    for prefix, full_name in user_patterns.items():
        if user_name.startswith(prefix):
            return full_name
    
    # 如果沒有匹配的模式，返回原始名稱
    return user_name

def identify_users_from_file(file_path: str, sample_count: int = 20) -> Dict[str, str]:
    """
    從檔案中識別使用者模式
    
    Args:
        file_path: 聊天記錄檔案路徑
        sample_count: 要提取的樣本數量
        
    Returns:
        使用者模式映射字典
    """
    user_samples = extract_user_samples(file_path, sample_count)
    user_patterns = analyze_user_patterns(user_samples)
    return user_patterns

def print_user_analysis(file_path: str, sample_count: int = 20):
    """
    印出使用者分析結果（用於調試）
    
    Args:
        file_path: 聊天記錄檔案路徑
        sample_count: 要提取的樣本數量
        
    Returns:
        使用者模式映射字典
    """
    print(f"分析檔案：{file_path}")
    print(f"取樣數量：{sample_count}")
    print("-" * 50)
    
    user_samples = extract_user_samples(file_path, sample_count)
    print(f"原始使用者樣本：")
    for i, user in enumerate(user_samples, 1):
        print(f"  {i:2d}. {user}")
    
    print(f"\n使用者統計：")
    name_counter = Counter(user_samples)
    for name, count in name_counter.most_common():
        print(f"  {name}: {count} 次")
    
    user_patterns = analyze_user_patterns(user_samples)
    print(f"\n識別出的模式：")
    for prefix, full_name in user_patterns.items():
        print(f"  '{prefix}' -> '{full_name}'")
    
    return user_patterns 