import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict

from pydantic import BaseModel


def parse_decoded_data_json(data: str) -> dict:
    """Parses the decoded data JSON string into a dictionary.

    Args:
        data: The decoded data JSON string.

    Returns:
        A dictionary with the parsed data.
    """
    data = json.loads(data)
    
    parsed_dict = {}
    for item in data:
        key = item['name']
        value = item['value']['value']
        
        # handle case {'type': 'BigNumber', 'hex': '0x0114'},
        # convert it to int
        if isinstance(value, dict) and 'type' in value and value["type"] == "BigNumber":
            value = int(value["hex"], 16)
        
        parsed_dict[key] = value
    return parsed_dict
    
    
class AttentationMetadata(BaseModel):
    uid: str
    created_at: datetime
    expiration: int = 0
    revoked: bool = False
    from_address: str
    to_address: str
    
    ipfs_hash: str
    

class WeekInterval(BaseModel):
    
    start_timestamp: int
    end_timestamp: int
    
    @property
    def formatted_interval(self) -> str:
        start_date = datetime.fromtimestamp(self.start_timestamp, timezone.utc)
        end_date = datetime.fromtimestamp(self.end_timestamp, timezone.utc)
        # Format the dates to "3 June - 9 June"
        formatted_start = start_date.strftime("%-d %B %Y")
        formatted_end = end_date.strftime("%-d %B %Y")
        return f"{formatted_start} - {formatted_end} (UTC)"
    
    @classmethod
    def get_current_interval(cls) -> "WeekInterval":
        now = datetime.now(timezone.utc)
        # Find the start of the week (Monday 00:00 UTC)
        start_of_week = now - timedelta(days=now.weekday())
        start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Find the end of the week (Sunday 23:59 UTC)
        end_of_week = start_of_week + timedelta(days=6, hours=23, minutes=59, seconds=59)
        
        start_timestamp = int(start_of_week.timestamp())
        end_timestamp = int(end_of_week.timestamp())
        
        return cls(
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp
        )
    