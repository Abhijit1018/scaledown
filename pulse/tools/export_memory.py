
import sqlite3
import json
import os
import argparse
from pathlib import Path
from pulse.config import PulseConfig
from pulse.core.memory import Memory

def export_to_jsonl(db_path: str, output_file: str):
    """
    Export conversation history to JSONL format.
    Format: {"role": "user", "content": "..."}
    """
    print(f"Exporting memory from {db_path} to {output_file}...")
    
    # Initialize Memory (handles decryption if key in env, but here we might need manual handling if encrypted)
    # Ideally should use the Memory class to handle decryption layer
    config = PulseConfig.from_env()
    mem = Memory(db_path, config.encryption_key)
    
    # Get all history
    # We increase limit to get everything
    messages = mem.get_history(limit=10000)
    
    count = 0
    with open(output_file, 'w', encoding='utf-8') as f:
        for msg in messages:
            record = {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp,
                "metadata": msg.metadata
            }
            f.write(json.dumps(record) + "\n")
            count += 1
            
    print(f"✅ Successfully exported {count} messages to {output_file}")

if __name__ == "__main__":
    if not os.path.exists("training_data"):
        os.makedirs("training_data")
        
    config = PulseConfig.from_env()
    db_path = config.db_path
    timestamp = int(os.path.getmtime(db_path)) if os.path.exists(db_path) else 0
    output_path = f"training_data/chat_history_export.jsonl"
    
    export_to_jsonl(db_path, output_path)
