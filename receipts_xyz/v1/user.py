import logging
from typing import List, Optional

from ..api.v1 import ReceiptsXYZV1GraphQLAPI
from ..schema.base import AttestationV1
from ..schema.v1 import SingleWorkoutReceipt
from ..utils import resolve_ens_name, to_checksum_address


def get_user_workouts(
    address: str, 
    start_timestamp: Optional[int] = None, 
    end_timestamp: Optional[int] = None,
) -> List[SingleWorkoutReceipt]:
    if not address.startswith("0x"):
        ens_name = address
        address = resolve_ens_name(address)
        logging.info(f"Resolved ENS name from {ens_name} to address: {address}")
        
    address = to_checksum_address(address)
    if start_timestamp is None and end_timestamp is None:
        logging.info("Fetching all attestations for address: {address}")
        output = ReceiptsXYZV1GraphQLAPI().query_user_workouts(address=address)
    else:
        logging.info(f"Fetching attestations for address: {address} between {start_timestamp} and {end_timestamp}")
        output = ReceiptsXYZV1GraphQLAPI().query_user_workouts_with_inteval(
            address=address, 
            start_timestamp=start_timestamp, 
            end_timestamp=end_timestamp
        )
    
    logging.info(f"Found {len(output)} attestations for address: {address}")
    
    return [
        SingleWorkoutReceipt.from_attestation(
            AttestationV1.from_dict(_a)
        ) for _a in output]
    