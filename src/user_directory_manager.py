#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
from typing import Dict, List, Optional, Tuple
from difflib import SequenceMatcher

class UserDirectoryManager:
    """
    簡化版使用者名冊管理器
    
    用於載入和管理簡化版使用者名冊 JSON 檔案，提供完全比對功能
    """
    
    def __init__(self, directory_path: str = "data/user_directory.json"):
        """
        初始化使用者名冊管理器
        
        Args:
            directory_path: 使用者名冊 JSON 檔案路徑
        """
        self.directory_path = directory_path
        self.users = []
        self.metadata = {}
        self.load_directory()
    
    def load_directory(self) -> bool:
        """
        載入使用者名冊
        
        Returns:
            是否成功載入
        """
        try:
            if not os.path.exists(self.directory_path):
                print(f"警告：使用者名冊檔案不存在：{self.directory_path}")
                return False
            
            with open(self.directory_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            self.users = data.get("users", [])
            self.metadata = data.get("metadata", {})
            
            print(f"成功載入使用者名冊，包含 {len(self.users)} 個使用者")
            return True
            
        except Exception as e:
            print(f"載入使用者名冊失敗：{e}")
            return False
    
    def find_user_by_name(self, name: str, max_length: int = 50) -> Optional[str]:
        """
        根據使用者名稱進行完全比對查找
        
        Args:
            name: 要查找的使用者名稱
            max_length: 最大比對長度
            
        Returns:
            匹配的完整使用者名稱或 None
        """
        # 限制比對長度
        name_to_check = name[:max_length]
        
        # 完全比對
        for full_name in self.users:
            if name_to_check == full_name:
                return full_name
        
        return None
    
    def is_known_user(self, name: str) -> bool:
        """
        檢查是否為已知使用者
        
        Args:
            name: 使用者名稱
            
        Returns:
            是否為已知使用者
        """
        return self.find_user_by_name(name) is not None
    
    def get_all_users(self) -> List[str]:
        """
        獲取所有使用者列表
        
        Returns:
            使用者名稱列表
        """
        return self.users.copy()
    
    def add_user(self, full_name: str) -> bool:
        """
        添加新使用者到名冊
        
        Args:
            full_name: 完整使用者名稱
            
        Returns:
            是否成功添加
        """
        try:
            if full_name not in self.users:
                self.users.append(full_name)
            return True
        except Exception as e:
            print(f"添加使用者失敗：{e}")
            return False
    
    def save_directory(self) -> bool:
        """
        保存使用者名冊到檔案
        
        Returns:
            是否成功保存
        """
        try:
            data = {
                "users": self.users,
                "metadata": self.metadata
            }
            
            os.makedirs(os.path.dirname(self.directory_path), exist_ok=True)
            
            with open(self.directory_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"使用者名冊已保存到：{self.directory_path}")
            return True
            
        except Exception as e:
            print(f"保存使用者名冊失敗：{e}")
            return False
    
    def get_statistics(self) -> Dict:
        """
        獲取使用者名冊統計資訊
        
        Returns:
            統計資訊字典
        """
        return {
            "total_users": len(self.users),
            "metadata": self.metadata
        }

# 全域實例
user_directory_manager = UserDirectoryManager()

if __name__ == "__main__":
    # 測試功能
    manager = UserDirectoryManager()
    
    # 測試查找功能
    test_names = [
        "楊翔志 Bruce",
        "楊翔志",
        "Bruce",
        "聖伯納_Peggy 林佩萱",
        "聖伯納_Peggy",
        "王玫雅",
        "Unknown",
        "未知使用者"
    ]
    
    print("=== 使用者名冊測試 ===")
    for name in test_names:
        result = manager.find_user_by_name(name)
        if result:
            print(f"'{name}' -> '{result}' (完全匹配)")
        else:
            print(f"'{name}' -> 未找到匹配")
    
    print("\n=== 統計資訊 ===")
    stats = manager.get_statistics()
    for key, value in stats.items():
        print(f"{key}: {value}") 