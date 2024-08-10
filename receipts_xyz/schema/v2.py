from pydantic import BaseModel

from .base import (
    AttentationMetadata,
    parse_decoded_data_json
)
from ..api.v2 import ReceiptsXYZV2GraphQLAPI
from ..exception import ParsingFailException


class AttestationV2(BaseModel):
    
    id: str
    time: int
    txid: str
    data: str
    decodedDataJson: str
    revoked: bool
    ipfsHash: str
    
    @classmethod
    def from_uid(cls, uid: str) -> "AttestationV2":
        api = ReceiptsXYZV2GraphQLAPI()
        
        attestations = api.query_attestation(uid)["data"]["attestations"]
        if len(attestations) == 0:
            raise ValueError(f"UID {uid} not found in GraphQL API")
        elif len(attestations) > 1:
            raise ValueError(f"UID {uid} found more than once in GraphQL API")
        
        attestation = attestations[0]
        return cls.from_dict(attestation)
    
    @classmethod
    def from_dict(cls, attestation_data: dict) -> "AttestationV2":
        
        # Create an instance of Attestation
        attestation = cls(
            **attestation_data,
        )
        
        return attestation


class WorkoutReceipt(BaseModel):
    """v2 attestation receipt
    https://base.easscan.org/schema/view/0x306c3768de1da8b0d36386d395ccafd05526741a6d38a3cee1bbbb7765d461d2
    """
    id: str
    txid: str
    aid: str
    name: str
    time: int
    total_participants: int
    total_moving_time: int
    total_intensity_time: int
    total_run_distance: int
    total_bike_distance: int
    total_strength_time: int
    has_ended: bool
    
    def to_json(self) -> dict:
        return {
            "id": self.id,
            "txid": self.txid,
            "aid": self.aid,
            "time": self.time,
            "name": self.name,
            "total_participants": self.total_participants,
            "total_moving_time": self.total_moving_time,
            "total_intensity_time": self.total_intensity_time,
            "total_run_distance": self.total_run_distance,
            "total_bike_distance": self.total_bike_distance,
            "total_strength_time": self.total_strength_time,
            "has_ended": self.has_ended,
        }
        
    @staticmethod
    def get_schema_id() -> str:
        return "0x306c3768de1da8b0d36386d395ccafd05526741a6d38a3cee1bbbb7765d461d2"
    
    @classmethod
    def from_attestation(cls, attestation: AttestationV2) -> "WorkoutReceipt":
        decoded_str = attestation.decodedDataJson
        decoded_data = parse_decoded_data_json(decoded_str)
        
        return cls(
            id=decoded_data["id"],
            txid=attestation.txid,
            aid=attestation.id,
            time=attestation.time,
            name=decoded_data["name"],
            total_participants=decoded_data["total_participants"],
            total_moving_time=decoded_data["total_moving_time"],
            total_intensity_time=decoded_data["total_intensity_time"],
            total_run_distance=decoded_data["total_run_distance"],
            total_bike_distance=decoded_data["total_bike_distance"],
            total_strength_time=decoded_data["total_strength_time"],
            has_ended=decoded_data["has_ended"],
        )
        
    @classmethod
    def from_uid(cls, uid: str) -> "WorkoutReceipt":
        return cls.from_attestation(AttestationV2.from_uid(uid))
