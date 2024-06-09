import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict

from pydantic import BaseModel, validator

from .api import ReceiptsXYZGraphQLAPI
from .exception import ParsingFailException
from .utils import parse_decoded_data_json


class Attestation(BaseModel):
    """
    Attestation
        id: String
        data: String
        decodedDataJson: String
    """
    id: str
    data: Dict  # Change the type to Dict to reflect the parsed data
    decodedDataJson: str
    revoked: bool
    ipfsHash: str
    txid: str
    
    @property
    def eas_url(self) -> str:
        return f"https://base.easscan.org/attestation/{self.id}"
    
    @property
    def mint_url(self) -> str:
        return f"https://basescan.org/tx/{self.txid}"
    
    @property
    def ipfs_url(self) -> str:
        return f"ipfs://{self.ipfsHash}"

    @classmethod
    def from_dict(cls, attestation_data: dict) -> "Attestation":
        # Extract the attestation data from the response
        
        # Parse the "data" field from JSON string to dictionary
        if isinstance(attestation_data["data"], str):
            if attestation_data["data"].startswith("0x"):
                raise ParsingFailException(f"Failed to parse attestation data: {attestation_data['data']}")
            attestation_data["data"] = json.loads(attestation_data["data"])
        
        # Extract schema fields
        schema = attestation_data.get("schema", {})
        txid = schema.get("txid")
        
        # Create an instance of Attestation
        attestation = cls(
            **attestation_data,
            txid=txid,
        )
        
        return attestation
    
    @classmethod
    def from_uid(cls, uid: str) -> "Attestation":
        api = ReceiptsXYZGraphQLAPI()
        
        attestations = api.query_attestation(uid)["data"]["attestations"]
        if len(attestations) == 0:
            raise ValueError(f"UID {uid} not found in GraphQL API")
        elif len(attestations) > 1:
            raise ValueError(f"UID {uid} found more than once in GraphQL API")
        
        attestation = attestations[0]
        return cls.from_dict(attestation)
    
    def to_metadata(self) -> "AttentationMetadata":
        return AttentationMetadata(
            uid=self.id,
            created_at=datetime.fromtimestamp(self.data["sig"]["message"]["time"]),
            expiration=self.data["sig"]["message"]["expirationTime"],
            revoked=self.revoked,
            from_address=self.data["sig"]["message"]["recipient"],
            to_address=self.data["signer"],
            ipfs_hash=self.ipfsHash,
            txid=self.txid
        )
    
    
class AttentationMetadata(BaseModel):
    uid: str
    created_at: datetime
    expiration: int = 0
    revoked: bool = False
    from_address: str
    to_address: str
    
    ipfs_hash: str
    txid: str
    
    
class SingleWorkoutReceipt(BaseModel):
    """Single Workout Receipt
    https://base.easscan.org/schema/view/0x48d9973eb6863978c104f85dc6864e827fc0f72c4083dd853171e0bf034f8774
    """
    title: str
    sport_type: str # maybe enum?
    receipt_type: str
    moving_time: int
    distance: int
    average_speed: str
    elevation_gain: int
    timezone: str
    local_time: str
    utc_time: int
    receipt_map: Optional[str] = None
    strava_single_activity: bool
    data_source: str
    
    metadata: AttentationMetadata
    
    @staticmethod
    def get_schema_id() -> str:
        return "0x48d9973eb6863978c104f85dc6864e827fc0f72c4083dd853171e0bf034f8774"
    
    @staticmethod
    def is_single_workout(attestation: Attestation) -> bool:
        return attestation.data["sig"]["message"]["schema"] == SingleWorkoutReceipt.get_schema_id()
    
    @classmethod
    def from_attestation(cls, attestation: Attestation) -> "SingleWorkoutReceipt":
        if not cls.is_single_workout(attestation):
            raise ValueError("Not a single workout attestation")
        
        decoded_str = attestation.decodedDataJson
        decoded_data = parse_decoded_data_json(decoded_str)
        
        return cls(
            title=decoded_data["title"],
            sport_type=decoded_data["sport_type"],
            receipt_type=decoded_data["type"],
            moving_time=decoded_data["moving_time"],
            distance=decoded_data["distance"],
            average_speed=decoded_data["average_speed"],
            elevation_gain=decoded_data["elevation_gain"],
            timezone=decoded_data["timezone"],
            local_time=decoded_data["local_time"],
            utc_time=decoded_data["utc_time"],
            receipt_map=decoded_data["map"],
            strava_single_activity=decoded_data["strava_single_activity"],
            data_source=decoded_data["data_source"],
            metadata=attestation.to_metadata()
        )
        
    @classmethod
    def from_uid(cls, uid: str) -> "SingleWorkoutReceipt":
        attestation = Attestation.from_uid(uid)
        return cls.from_attestation(attestation)
        

class WeekToDateReceipt(BaseModel):
    
    activities: int
    sport_types: Dict[str, int]
    running_distance: int
    cycling_distance: int
    moving_time: int
    range_start: int # in timestamp
    range_end: int
    strava_week_range: bool
    data_source: str
    
    metadata: AttentationMetadata
    
    @staticmethod
    def get_schema_id() -> str:
        return "0xcd6475d55ff914b51faf41f8f85a6bfe27875fc87eaa7d50762cf6c89050adac"
    
    @staticmethod
    def is_week_to_date(attestation: Attestation) -> bool:
        return attestation.data["sig"]["message"]["schema"] == WeekToDateReceipt.get_schema_id()
        
    @classmethod
    def from_attestation(cls, attestation: Attestation) -> "WeekToDateReceipt":
        if not cls.is_week_to_date(attestation):
            raise ValueError("Not a single workout attestation")
        
        decoded_str = attestation.decodedDataJson
        decoded_data = parse_decoded_data_json(decoded_str)
        
        return cls(
            activities=decoded_data["activities"],
            sport_types=json.loads(decoded_data["sport_types"]),
            running_distance=decoded_data["running_distance"],
            cycling_distance=decoded_data["cycling_distance"],
            moving_time=decoded_data["moving_time"],
            range_start=decoded_data["range_start"],
            range_end=decoded_data["range_end"],
            strava_week_range=decoded_data["strava_week_range"],
            data_source=decoded_data["data_source"],
            metadata=attestation.to_metadata()
        )
        
    @classmethod
    def from_uid(cls, uid: str) -> "WeekToDateReceipt":
        attestation = Attestation.from_uid(uid)
        return cls.from_attestation(attestation)

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
    