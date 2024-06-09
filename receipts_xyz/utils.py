from typing import Dict, List, Optional, Tuple

from web3 import Web3

from .schema import SingleWorkoutReceipt


def get_default_mainnet_provider() -> str:
    """Change this via https://chainlist.org/"""
    return "https://eth.llamarpc.com"


def to_checksum_address(address: str) -> str:
    # Validate if the address is a valid Ethereum address
    if not Web3.is_address(address):
        raise ValueError(f"Invalid Ethereum address: {address}")
    
    # Convert to checksum address
    checksum_address = Web3.to_checksum_address(address)
    return checksum_address
        

def resolve_ens_name(ens_name: str, rpc_url: Optional[str] = None) -> str:
    # Connect to an Ethereum node using Infura
    rpc_url = rpc_url or get_default_mainnet_provider()
    web3 = Web3(Web3.HTTPProvider(rpc_url))
    
    # Check if the connection is successful
    if not web3.is_connected():
        raise Exception("Unable to connect to the Ethereum network")
    
    # Resolve the ENS name
    try:
        address = web3.ens.address(ens_name)
        if address:
            return address
        else:
            raise Exception(f"ENS name '{ens_name}' not found")
    except Exception as e:
        raise Exception(f"Error resolving ENS name: {str(e)}")
    

def deduplicate_receipts(receipts: List[SingleWorkoutReceipt]) -> List[SingleWorkoutReceipt]:
    # Define the key attributes for deduplication
    def generate_unique_identifier(receipt: SingleWorkoutReceipt) -> Tuple:
        return (
            receipt.title,
            receipt.sport_type,
            receipt.receipt_type,
            receipt.moving_time,
            receipt.distance,
            receipt.average_speed,
            receipt.elevation_gain,
            receipt.timezone,
            receipt.local_time,
            receipt.utc_time,
            receipt.strava_single_activity,
            receipt.data_source
        )
    
    # Dictionary to store the latest receipt for each unique identifier
    latest_receipts: Dict[Tuple, SingleWorkoutReceipt] = {}
    
    for receipt in receipts:
        identifier = generate_unique_identifier(receipt)
        if identifier in latest_receipts:
            existing_receipt = latest_receipts[identifier]
            # Compare created_at timestamp and keep the latest receipt
            if receipt.metadata.created_at > existing_receipt.metadata.created_at:
                latest_receipts[identifier] = receipt
        else:
            latest_receipts[identifier] = receipt
    
    # Extract the deduplicated receipts
    deduplicated_receipts = list(latest_receipts.values())
    return deduplicated_receipts

