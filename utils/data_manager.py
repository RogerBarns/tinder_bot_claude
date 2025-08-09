"""
Data persistence management
"""
import json
from typing import Set, Dict, Any, List
from pathlib import Path
from threading import Lock


class DataManager:
    """Manages persistent data with thread safety"""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / "data"
        self.data_dir.mkdir(exist_ok=True)
        
        self.replied_file = self.data_dir / "replied_matches.json"
        self.rejected_file = self.data_dir / "rejected_matches.json"
        self.conversation_cache_file = self.data_dir / "conversation_cache.json"
        
        self.replied_messages = self._load_replied()
        self.rejected_matches = self._load_rejected()
        self.conversation_cache = self._load_conversation_cache()
        
        self._lock = Lock()
    
    def _load_replied(self) -> Dict[str, str]:
        """Load replied messages tracking"""
        if self.replied_file.exists():
            try:
                with open(self.replied_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def _load_rejected(self) -> Set[str]:
        """Load rejected matches"""
        if self.rejected_file.exists():
            try:
                with open(self.rejected_file, 'r') as f:
                    return set(json.load(f))
            except:
                pass
        return set()
    
    def _load_conversation_cache(self) -> Dict[str, List[Dict]]:
        """Load conversation cache"""
        if self.conversation_cache_file.exists():
            try:
                with open(self.conversation_cache_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def has_replied_to(self, match_id: str, message_time: str) -> bool:
        """Check if we've replied to a specific message"""
        with self._lock:
            return self.replied_messages.get(match_id) == message_time
    
    def has_ever_replied_to(self, match_id: str) -> bool:
        """Check if we've ever replied to this match"""
        with self._lock:
            return match_id in self.replied_messages
    
    def mark_replied(self, match_id: str, message_time: str):
        """Mark a message as replied"""
        with self._lock:
            self.replied_messages[match_id] = message_time
            
            with open(self.replied_file, 'w') as f:
                json.dump(self.replied_messages, f)
    
    def is_rejected(self, match_id: str) -> bool:
        """Check if match was rejected"""
        with self._lock:
            return match_id in self.rejected_matches
    
    def mark_rejected(self, match_id: str):
        """Mark match as rejected"""
        with self._lock:
            self.rejected_matches.add(match_id)
            
            with open(self.rejected_file, 'w') as f:
                json.dump(list(self.rejected_matches), f)
    
    def remove_rejected(self, match_id: str):
        """Remove match from rejected list"""
        with self._lock:
            self.rejected_matches.discard(match_id)
            
            with open(self.rejected_file, 'w') as f:
                json.dump(list(self.rejected_matches), f)
    
    def cache_conversation(self, match_id: str, messages: List[Dict]):
        """Cache a conversation"""
        with self._lock:
            self.conversation_cache[match_id] = messages
            
            # Keep cache size reasonable (max 100 conversations)
            if len(self.conversation_cache) > 100:
                # Remove oldest entries
                oldest = sorted(self.conversation_cache.keys())[:20]
                for key in oldest:
                    del self.conversation_cache[key]
            
            with open(self.conversation_cache_file, 'w') as f:
                json.dump(self.conversation_cache, f)
    
    def get_cached_conversation(self, match_id: str) -> List[Dict]:
        """Get cached conversation"""
        with self._lock:
            return self.conversation_cache.get(match_id, [])
    
    def clear_all_data(self):
        """Clear all persistent data (use with caution)"""
        with self._lock:
            self.replied_messages.clear()
            self.rejected_matches.clear()
            self.conversation_cache.clear()
            
            # Save empty files
            with open(self.replied_file, 'w') as f:
                json.dump({}, f)
            with open(self.rejected_file, 'w') as f:
                json.dump([], f)
            with open(self.conversation_cache_file, 'w') as f:
                json.dump({}, f)

