import json
from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel

from ..api.v1 import ReceiptsXYZV1GraphQLAPI
from ..exception import ParsingFailException
from .base import (
    AttentationMetadata,
    parse_decoded_data_json
)


class AttestationV1(BaseModel):
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
    
    @property
    def eas_url(self) -> str:
        return f"https://base.easscan.org/attestation/{self.id}"
    
    @property
    def ipfs_url(self) -> str:
        return f"ipfs://{self.ipfsHash}"

    @classmethod
    def from_dict(cls, attestation_data: dict) -> "AttestationV1":
        # Extract the attestation data from the response
        
        # Parse the "data" field from JSON string to dictionary
        if isinstance(attestation_data["data"], str):
            if attestation_data["data"].startswith("0x"):
                raise ParsingFailException(f"Failed to parse attestation data: {attestation_data['data']}")
            attestation_data["data"] = json.loads(attestation_data["data"])
        
        # Create an instance of Attestation
        attestation = cls(
            **attestation_data,
        )
        
        return attestation
    
    @classmethod
    def from_uid(cls, uid: str) -> "AttestationV1":
        api = ReceiptsXYZV1GraphQLAPI()
        
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
        )


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
    
    def to_json(self) -> dict:
        return {
            "title": self.title,
            "sport_type": self.sport_type,
            "receipt_type": self.receipt_type,
            "moving_time": self.moving_time,
            "distance": self.distance,
            "average_speed": self.average_speed,
            "elevation_gain": self.elevation_gain,
            "timezone": self.timezone,
            "local_time": self.local_time,
            "utc_time": self.utc_time,
            "receipt_map": self.receipt_map,
            "strava_single_activity": self.strava_single_activity,
            "data_source": self.data_source,
            "user_address": self.metadata.from_address
        }
        
    @staticmethod
    def get_schema_id() -> str:
        return "0x48d9973eb6863978c104f85dc6864e827fc0f72c4083dd853171e0bf034f8774"
    
    @staticmethod
    def is_single_workout(attestation: AttestationV1) -> bool:
        return attestation.data["sig"]["message"]["schema"] == SingleWorkoutReceipt.get_schema_id()
    
    @classmethod
    def from_attestation(cls, attestation: AttestationV1) -> "SingleWorkoutReceipt":
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
        attestation = AttestationV1.from_uid(uid)
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
    def is_week_to_date(attestation: AttestationV1) -> bool:
        return attestation.data["sig"]["message"]["schema"] == WeekToDateReceipt.get_schema_id()
        
    @classmethod
    def from_attestation(cls, attestation: AttestationV1) -> "WeekToDateReceipt":
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
        attestation = AttestationV1.from_uid(uid)
        return cls.from_attestation(attestation)
