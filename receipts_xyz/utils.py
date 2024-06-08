import json
from typing import Optional

from web3 import Web3


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
        parsed_dict[key] = value
    return parsed_dict
