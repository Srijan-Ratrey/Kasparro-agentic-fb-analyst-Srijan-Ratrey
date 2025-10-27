"""
Memory systems for the Agentic Facebook Performance Analyst.
"""

import json
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from pathlib import Path
import asyncio
import threading
from collections import deque
import pickle

logger = logging.getLogger(__name__)


class MemorySystem:
    """Base class for memory systems."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize memory system."""
        self.config = config
        self.logger = logging.getLogger(f"memory.{self.__class__.__name__}")
    
    async def store(self, key: str, value: Any) -> bool:
        """Store a value in memory."""
        raise NotImplementedError
    
    async def retrieve(self, key: str, default: Any = None) -> Any:
        """Retrieve a value from memory."""
        raise NotImplementedError
    
    async def delete(self, key: str) -> bool:
        """Delete a value from memory."""
        raise NotImplementedError
    
    async def clear(self) -> bool:
        """Clear all values from memory."""
        raise NotImplementedError
    
    async def exists(self, key: str) -> bool:
        """Check if a key exists in memory."""
        raise NotImplementedError
    
    async def list_keys(self) -> List[str]:
        """List all keys in memory."""
        raise NotImplementedError


class ShortTermMemory(MemorySystem):
    """Short-term memory for session-based data."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize short-term memory."""
        super().__init__(config)
        self.max_items = config.get("max_items", 1000)
        self.ttl_seconds = config.get("ttl_seconds", 3600)
        
        # Use deque for efficient operations
        self.memory: Dict[str, Dict[str, Any]] = {}
        self.access_times: Dict[str, datetime] = {}
        self._lock = threading.RLock()
    
    async def store(self, key: str, value: Any) -> bool:
        """Store a value in short-term memory."""
        try:
            with self._lock:
                # Check if we need to evict old items
                await self._evict_expired()
                
                # Store the value with timestamp
                self.memory[key] = {
                    "value": value,
                    "timestamp": datetime.now(),
                    "access_count": 0
                }
                self.access_times[key] = datetime.now()
                
                self.logger.debug(f"Stored key '{key}' in short-term memory")
                return True
                
        except Exception as e:
            self.logger.error(f"Error storing key '{key}': {e}")
            return False
    
    async def retrieve(self, key: str, default: Any = None) -> Any:
        """Retrieve a value from short-term memory."""
        try:
            with self._lock:
                if key not in self.memory:
                    return default
                
                # Check if item has expired
                item = self.memory[key]
                if await self._is_expired(item["timestamp"]):
                    await self.delete(key)
                    return default
                
                # Update access information
                item["access_count"] += 1
                self.access_times[key] = datetime.now()
                
                self.logger.debug(f"Retrieved key '{key}' from short-term memory")
                return item["value"]
                
        except Exception as e:
            self.logger.error(f"Error retrieving key '{key}': {e}")
            return default
    
    async def delete(self, key: str) -> bool:
        """Delete a value from short-term memory."""
        try:
            with self._lock:
                if key in self.memory:
                    del self.memory[key]
                    if key in self.access_times:
                        del self.access_times[key]
                    self.logger.debug(f"Deleted key '{key}' from short-term memory")
                    return True
                return False
                
        except Exception as e:
            self.logger.error(f"Error deleting key '{key}': {e}")
            return False
    
    async def clear(self) -> bool:
        """Clear all values from short-term memory."""
        try:
            with self._lock:
                self.memory.clear()
                self.access_times.clear()
                self.logger.info("Cleared short-term memory")
                return True
                
        except Exception as e:
            self.logger.error(f"Error clearing short-term memory: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if a key exists in short-term memory."""
        try:
            with self._lock:
                if key not in self.memory:
                    return False
                
                # Check if item has expired
                item = self.memory[key]
                if await self._is_expired(item["timestamp"]):
                    await self.delete(key)
                    return False
                
                return True
                
        except Exception as e:
            self.logger.error(f"Error checking existence of key '{key}': {e}")
            return False
    
    async def list_keys(self) -> List[str]:
        """List all keys in short-term memory."""
        try:
            with self._lock:
                await self._evict_expired()
                return list(self.memory.keys())
                
        except Exception as e:
            self.logger.error(f"Error listing keys: {e}")
            return []
    
    async def _is_expired(self, timestamp: datetime) -> bool:
        """Check if a timestamp has expired."""
        return datetime.now() - timestamp > timedelta(seconds=self.ttl_seconds)
    
    async def _evict_expired(self) -> None:
        """Evict expired items from memory."""
        expired_keys = []
        
        for key, item in self.memory.items():
            if await self._is_expired(item["timestamp"]):
                expired_keys.append(key)
        
        for key in expired_keys:
            await self.delete(key)
        
        # If still over capacity, evict least recently used
        if len(self.memory) > self.max_items:
            await self._evict_lru()
    
    async def _evict_lru(self) -> None:
        """Evict least recently used items."""
        if not self.access_times:
            return
        
        # Sort by access time and remove oldest
        sorted_keys = sorted(self.access_times.items(), key=lambda x: x[1])
        keys_to_remove = len(self.memory) - self.max_items
        
        for key, _ in sorted_keys[:keys_to_remove]:
            await self.delete(key)


class LongTermMemory(MemorySystem):
    """Long-term memory for persistent data storage."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize long-term memory."""
        super().__init__(config)
        self.max_items = config.get("max_items", 10000)
        self.persistence_file = Path(config.get("persistence_file", "data/memory/long_term.json"))
        
        # Ensure directory exists
        self.persistence_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing data
        self.memory: Dict[str, Any] = {}
        self.metadata: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.RLock()
        
        asyncio.create_task(self._load_from_disk())
    
    async def store(self, key: str, value: Any) -> bool:
        """Store a value in long-term memory."""
        try:
            with self._lock:
                # Check capacity
                if len(self.memory) >= self.max_items:
                    await self._evict_oldest()
                
                # Store the value
                self.memory[key] = value
                self.metadata[key] = {
                    "timestamp": datetime.now().isoformat(),
                    "access_count": 0,
                    "last_accessed": datetime.now().isoformat()
                }
                
                # Persist to disk
                await self._save_to_disk()
                
                self.logger.debug(f"Stored key '{key}' in long-term memory")
                return True
                
        except Exception as e:
            self.logger.error(f"Error storing key '{key}': {e}")
            return False
    
    async def retrieve(self, key: str, default: Any = None) -> Any:
        """Retrieve a value from long-term memory."""
        try:
            with self._lock:
                if key not in self.memory:
                    return default
                
                # Update access information
                if key in self.metadata:
                    self.metadata[key]["access_count"] += 1
                    self.metadata[key]["last_accessed"] = datetime.now().isoformat()
                
                self.logger.debug(f"Retrieved key '{key}' from long-term memory")
                return self.memory[key]
                
        except Exception as e:
            self.logger.error(f"Error retrieving key '{key}': {e}")
            return default
    
    async def delete(self, key: str) -> bool:
        """Delete a value from long-term memory."""
        try:
            with self._lock:
                if key in self.memory:
                    del self.memory[key]
                    if key in self.metadata:
                        del self.metadata[key]
                    
                    # Persist to disk
                    await self._save_to_disk()
                    
                    self.logger.debug(f"Deleted key '{key}' from long-term memory")
                    return True
                return False
                
        except Exception as e:
            self.logger.error(f"Error deleting key '{key}': {e}")
            return False
    
    async def clear(self) -> bool:
        """Clear all values from long-term memory."""
        try:
            with self._lock:
                self.memory.clear()
                self.metadata.clear()
                
                # Persist to disk
                await self._save_to_disk()
                
                self.logger.info("Cleared long-term memory")
                return True
                
        except Exception as e:
            self.logger.error(f"Error clearing long-term memory: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if a key exists in long-term memory."""
        return key in self.memory
    
    async def list_keys(self) -> List[str]:
        """List all keys in long-term memory."""
        return list(self.memory.keys())
    
    async def _load_from_disk(self) -> None:
        """Load memory data from disk."""
        try:
            if self.persistence_file.exists():
                with open(self.persistence_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.memory = data.get("memory", {})
                    self.metadata = data.get("metadata", {})
                    self.logger.info(f"Loaded long-term memory from {self.persistence_file}")
        except Exception as e:
            self.logger.error(f"Error loading long-term memory: {e}")
    
    async def _save_to_disk(self) -> None:
        """Save memory data to disk."""
        try:
            data = {
                "memory": self.memory,
                "metadata": self.metadata,
                "last_saved": datetime.now().isoformat()
            }
            
            with open(self.persistence_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"Error saving long-term memory: {e}")
    
    async def _evict_oldest(self) -> None:
        """Evict oldest items from memory."""
        if not self.metadata:
            return
        
        # Sort by timestamp and remove oldest
        sorted_keys = sorted(self.metadata.items(), key=lambda x: x[1]["timestamp"])
        keys_to_remove = len(self.memory) - self.max_items + 1
        
        for key, _ in sorted_keys[:keys_to_remove]:
            await self.delete(key)


class EpisodicMemory(MemorySystem):
    """Episodic memory for session-based experiences."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize episodic memory."""
        super().__init__(config)
        self.max_sessions = config.get("max_sessions", 100)
        self.session_ttl_hours = config.get("session_ttl_hours", 24)
        
        # Store sessions with their events
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.session_events: Dict[str, List[Dict[str, Any]]] = {}
        self._lock = threading.RLock()
    
    async def store(self, key: str, value: Any) -> bool:
        """Store a value in episodic memory."""
        try:
            with self._lock:
                # Extract session ID from key (format: session_id:event_id)
                if ":" not in key:
                    return False
                
                session_id, event_id = key.split(":", 1)
                
                # Create session if it doesn't exist
                if session_id not in self.sessions:
                    self.sessions[session_id] = {
                        "created_at": datetime.now().isoformat(),
                        "last_accessed": datetime.now().isoformat(),
                        "event_count": 0
                    }
                    self.session_events[session_id] = []
                
                # Store the event
                event = {
                    "event_id": event_id,
                    "timestamp": datetime.now().isoformat(),
                    "data": value
                }
                
                self.session_events[session_id].append(event)
                self.sessions[session_id]["event_count"] += 1
                self.sessions[session_id]["last_accessed"] = datetime.now().isoformat()
                
                # Check capacity
                if len(self.sessions) > self.max_sessions:
                    await self._evict_oldest_session()
                
                self.logger.debug(f"Stored event '{event_id}' in session '{session_id}'")
                return True
                
        except Exception as e:
            self.logger.error(f"Error storing key '{key}': {e}")
            return False
    
    async def retrieve(self, key: str, default: Any = None) -> Any:
        """Retrieve a value from episodic memory."""
        try:
            with self._lock:
                if ":" not in key:
                    return default
                
                session_id, event_id = key.split(":", 1)
                
                if session_id not in self.sessions:
                    return default
                
                # Check if session has expired
                if await self._is_session_expired(session_id):
                    await self.delete_session(session_id)
                    return default
                
                # Find the event
                for event in self.session_events[session_id]:
                    if event["event_id"] == event_id:
                        self.sessions[session_id]["last_accessed"] = datetime.now().isoformat()
                        return event["data"]
                
                return default
                
        except Exception as e:
            self.logger.error(f"Error retrieving key '{key}': {e}")
            return default
    
    async def delete(self, key: str) -> bool:
        """Delete a value from episodic memory."""
        try:
            with self._lock:
                if ":" not in key:
                    return False
                
                session_id, event_id = key.split(":", 1)
                
                if session_id not in self.session_events:
                    return False
                
                # Remove the event
                self.session_events[session_id] = [
                    event for event in self.session_events[session_id]
                    if event["event_id"] != event_id
                ]
                
                # Update session metadata
                self.sessions[session_id]["event_count"] = len(self.session_events[session_id])
                
                # Remove session if empty
                if not self.session_events[session_id]:
                    await self.delete_session(session_id)
                
                return True
                
        except Exception as e:
            self.logger.error(f"Error deleting key '{key}': {e}")
            return False
    
    async def clear(self) -> bool:
        """Clear all values from episodic memory."""
        try:
            with self._lock:
                self.sessions.clear()
                self.session_events.clear()
                self.logger.info("Cleared episodic memory")
                return True
                
        except Exception as e:
            self.logger.error(f"Error clearing episodic memory: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if a key exists in episodic memory."""
        if ":" not in key:
            return False
        
        session_id, event_id = key.split(":", 1)
        
        if session_id not in self.sessions:
            return False
        
        if await self._is_session_expired(session_id):
            await self.delete_session(session_id)
            return False
        
        return any(event["event_id"] == event_id for event in self.session_events[session_id])
    
    async def list_keys(self) -> List[str]:
        """List all keys in episodic memory."""
        keys = []
        
        for session_id in self.sessions:
            if not await self._is_session_expired(session_id):
                for event in self.session_events[session_id]:
                    keys.append(f"{session_id}:{event['event_id']}")
        
        return keys
    
    async def get_session_events(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all events for a session."""
        if session_id not in self.session_events:
            return []
        
        if await self._is_session_expired(session_id):
            await self.delete_session(session_id)
            return []
        
        return self.session_events[session_id]
    
    async def delete_session(self, session_id: str) -> bool:
        """Delete an entire session."""
        try:
            with self._lock:
                if session_id in self.sessions:
                    del self.sessions[session_id]
                if session_id in self.session_events:
                    del self.session_events[session_id]
                return True
        except Exception as e:
            self.logger.error(f"Error deleting session '{session_id}': {e}")
            return False
    
    async def _is_session_expired(self, session_id: str) -> bool:
        """Check if a session has expired."""
        if session_id not in self.sessions:
            return True
        
        created_at = datetime.fromisoformat(self.sessions[session_id]["created_at"])
        return datetime.now() - created_at > timedelta(hours=self.session_ttl_hours)
    
    async def _evict_oldest_session(self) -> None:
        """Evict the oldest session."""
        if not self.sessions:
            return
        
        # Sort by creation time and remove oldest
        sorted_sessions = sorted(self.sessions.items(), key=lambda x: x[1]["created_at"])
        oldest_session_id = sorted_sessions[0][0]
        await self.delete_session(oldest_session_id)


class SemanticMemory(MemorySystem):
    """Semantic memory for knowledge and relationships."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize semantic memory."""
        super().__init__(config)
        self.max_nodes = config.get("max_nodes", 5000)
        self.knowledge_graph_file = Path(config.get("knowledge_graph_file", "data/memory/semantic_graph.json"))
        
        # Ensure directory exists
        self.knowledge_graph_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Knowledge graph structure
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.edges: Dict[str, List[Dict[str, Any]]] = {}
        self._lock = threading.RLock()
        
        asyncio.create_task(self._load_from_disk())
    
    async def store(self, key: str, value: Any) -> bool:
        """Store a value in semantic memory."""
        try:
            with self._lock:
                # Check capacity
                if len(self.nodes) >= self.max_nodes:
                    await self._evict_least_connected()
                
                # Store as a node
                self.nodes[key] = {
                    "value": value,
                    "timestamp": datetime.now().isoformat(),
                    "access_count": 0,
                    "last_accessed": datetime.now().isoformat(),
                    "connections": 0
                }
                
                # Initialize edges if not exists
                if key not in self.edges:
                    self.edges[key] = []
                
                # Persist to disk
                await self._save_to_disk()
                
                self.logger.debug(f"Stored key '{key}' in semantic memory")
                return True
                
        except Exception as e:
            self.logger.error(f"Error storing key '{key}': {e}")
            return False
    
    async def retrieve(self, key: str, default: Any = None) -> Any:
        """Retrieve a value from semantic memory."""
        try:
            with self._lock:
                if key not in self.nodes:
                    return default
                
                # Update access information
                self.nodes[key]["access_count"] += 1
                self.nodes[key]["last_accessed"] = datetime.now().isoformat()
                
                self.logger.debug(f"Retrieved key '{key}' from semantic memory")
                return self.nodes[key]["value"]
                
        except Exception as e:
            self.logger.error(f"Error retrieving key '{key}': {e}")
            return default
    
    async def delete(self, key: str) -> bool:
        """Delete a value from semantic memory."""
        try:
            with self._lock:
                if key in self.nodes:
                    # Remove all edges connected to this node
                    await self._remove_node_connections(key)
                    
                    del self.nodes[key]
                    if key in self.edges:
                        del self.edges[key]
                    
                    # Persist to disk
                    await self._save_to_disk()
                    
                    self.logger.debug(f"Deleted key '{key}' from semantic memory")
                    return True
                return False
                
        except Exception as e:
            self.logger.error(f"Error deleting key '{key}': {e}")
            return False
    
    async def clear(self) -> bool:
        """Clear all values from semantic memory."""
        try:
            with self._lock:
                self.nodes.clear()
                self.edges.clear()
                
                # Persist to disk
                await self._save_to_disk()
                
                self.logger.info("Cleared semantic memory")
                return True
                
        except Exception as e:
            self.logger.error(f"Error clearing semantic memory: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if a key exists in semantic memory."""
        return key in self.nodes
    
    async def list_keys(self) -> List[str]:
        """List all keys in semantic memory."""
        return list(self.nodes.keys())
    
    async def add_relationship(self, from_key: str, to_key: str, relationship_type: str, weight: float = 1.0) -> bool:
        """Add a relationship between two nodes."""
        try:
            with self._lock:
                if from_key not in self.nodes or to_key not in self.nodes:
                    return False
                
                # Add edge
                edge = {
                    "to": to_key,
                    "type": relationship_type,
                    "weight": weight,
                    "timestamp": datetime.now().isoformat()
                }
                
                self.edges[from_key].append(edge)
                
                # Update connection counts
                self.nodes[from_key]["connections"] += 1
                self.nodes[to_key]["connections"] += 1
                
                # Persist to disk
                await self._save_to_disk()
                
                self.logger.debug(f"Added relationship '{relationship_type}' from '{from_key}' to '{to_key}'")
                return True
                
        except Exception as e:
            self.logger.error(f"Error adding relationship: {e}")
            return False
    
    async def get_related_nodes(self, key: str, relationship_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get nodes related to a given node."""
        try:
            with self._lock:
                if key not in self.edges:
                    return []
                
                related = []
                for edge in self.edges[key]:
                    if relationship_type is None or edge["type"] == relationship_type:
                        related.append({
                            "node": edge["to"],
                            "type": edge["type"],
                            "weight": edge["weight"]
                        })
                
                return related
                
        except Exception as e:
            self.logger.error(f"Error getting related nodes: {e}")
            return []
    
    async def _load_from_disk(self) -> None:
        """Load knowledge graph from disk."""
        try:
            if self.knowledge_graph_file.exists():
                with open(self.knowledge_graph_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.nodes = data.get("nodes", {})
                    self.edges = data.get("edges", {})
                    self.logger.info(f"Loaded semantic memory from {self.knowledge_graph_file}")
        except Exception as e:
            self.logger.error(f"Error loading semantic memory: {e}")
    
    async def _save_to_disk(self) -> None:
        """Save knowledge graph to disk."""
        try:
            data = {
                "nodes": self.nodes,
                "edges": self.edges,
                "last_saved": datetime.now().isoformat()
            }
            
            with open(self.knowledge_graph_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"Error saving semantic memory: {e}")
    
    async def _remove_node_connections(self, key: str) -> None:
        """Remove all connections to a node."""
        # Remove outgoing edges
        if key in self.edges:
            del self.edges[key]
        
        # Remove incoming edges
        for node_key, edges in self.edges.items():
            self.edges[node_key] = [
                edge for edge in edges if edge["to"] != key
            ]
    
    async def _evict_least_connected(self) -> None:
        """Evict the least connected node."""
        if not self.nodes:
            return
        
        # Sort by connection count and remove least connected
        sorted_nodes = sorted(self.nodes.items(), key=lambda x: x[1]["connections"])
        least_connected_key = sorted_nodes[0][0]
        await self.delete(least_connected_key)


class AdaptiveMemoryManager:
    """Manages all memory systems and provides unified interface."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize adaptive memory manager."""
        self.config = config
        self.logger = logging.getLogger("memory_manager")
        
        # Initialize memory systems
        self.short_term = ShortTermMemory(config.get("short_term", {}))
        self.long_term = LongTermMemory(config.get("long_term", {}))
        self.episodic = EpisodicMemory(config.get("episodic", {}))
        self.semantic = SemanticMemory(config.get("semantic", {}))
        
        self.logger.info("Adaptive memory manager initialized")
    
    async def store(self, key: str, value: Any, memory_type: str = "short_term") -> bool:
        """Store a value in the specified memory system."""
        memory_system = getattr(self, memory_type, None)
        if not memory_system:
            self.logger.error(f"Unknown memory type: {memory_type}")
            return False
        
        return await memory_system.store(key, value)
    
    async def retrieve(self, key: str, default: Any = None, memory_type: str = "short_term") -> Any:
        """Retrieve a value from the specified memory system."""
        memory_system = getattr(self, memory_type, None)
        if not memory_system:
            self.logger.error(f"Unknown memory type: {memory_type}")
            return default
        
        return await memory_system.retrieve(key, default)
    
    async def delete(self, key: str, memory_type: str = "short_term") -> bool:
        """Delete a value from the specified memory system."""
        memory_system = getattr(self, memory_type, None)
        if not memory_system:
            self.logger.error(f"Unknown memory type: {memory_type}")
            return False
        
        return await memory_system.delete(key)
    
    async def clear(self, memory_type: str = "all") -> bool:
        """Clear the specified memory system."""
        if memory_type == "all":
            results = []
            for system_name in ["short_term", "long_term", "episodic", "semantic"]:
                system = getattr(self, system_name)
                result = await system.clear()
                results.append(result)
            return all(results)
        else:
            memory_system = getattr(self, memory_type, None)
            if not memory_system:
                self.logger.error(f"Unknown memory type: {memory_type}")
                return False
            return await memory_system.clear()
    
    async def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics for all memory systems."""
        stats = {}
        
        for system_name in ["short_term", "long_term", "episodic", "semantic"]:
            system = getattr(self, system_name)
            stats[system_name] = {
                "keys_count": len(await system.list_keys()),
                "type": system.__class__.__name__
            }
        
        return stats
