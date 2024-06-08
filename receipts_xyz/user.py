import logging
from typing import List

from .api import ReceiptsXYZGraphQLAPI
from .schema import Attestation, SingleWorkoutReceipt
from .utils import resolve_ens_name, to_checksum_address


def get_workouts(address: str) -> List[SingleWorkoutReceipt]:
    if not address.startswith("0x"):
        ens_name = address
        address = resolve_ens_name(address)
        logging.info(f"Resolved ENS name from {ens_name} to address: {address}")
        
    address = to_checksum_address(address)
    
    output = ReceiptsXYZGraphQLAPI().query_user_workouts(address)
    
    return [
        SingleWorkoutReceipt.from_attestation(
            Attestation.from_dict(_a)
        ) for _a in output["attestations"]]
