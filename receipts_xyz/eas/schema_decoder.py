"""
Thanks Gemini-1.5-pro for the original code

Original code: 
https://github.com/ethereum-attestation-service/eas-sdk/blob/master/src/schema-encoder.ts

I told Gemini-1.5-pro to convert this into python and provide typescript usage example as shown in this URL:
https://base.easscan.org/schema/view/0x48d9973eb6863978c104f85dc6864e827fc0f72c4083dd853171e0bf034f8774

This is wild!

PS. I forgot to save the prompt so the prompt is now gone
"""
from typing import Any, Dict, List

from eth_abi import decode as decode_abi
from eth_utils import decode_hex
from hexbytes import HexBytes

ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"


class SchemaDecoder:
    
    def __init__(self, schema_string: str) -> None:
        self.schema = []
        fixed_schema = schema_string.replace("ipfsHash", "bytes32")
        components = [param.strip() for param in fixed_schema.split(",")]

        for component in components:
            parts = component.split(" ")
            if len(parts) == 2:
                type_name, name = parts
            else:
                type_name = component
                name = ""
            self.schema.append({"name": name, "type": type_name})

    def decode_data(self, hex_string: str) -> List[Dict[str, Any]]:
        """Decodes attestation bytes data into a schema.

        Args:
            data: The attestation bytes data.

        Returns:
            A list of dictionaries, where each dictionary represents a schema item.
        """
        decoded_values = decode_abi(
            [item["type"] for item in self.schema], decode_hex(hex_string) # Pass the hex string
        )
        result = []
        for i, item in enumerate(self.schema):
            value = decoded_values[i]
            if item["type"] == "bytes32":
                try:
                    # Attempt to decode as a string
                    value = value.decode("utf-8").strip("\x00")
                except UnicodeDecodeError:
                    # If decoding fails, leave it as bytes
                    pass
            result.append({"name": item["name"], "type": item["type"], "value": value})
        return SchemaDecoder.parse_data(result)
    
    @staticmethod
    def parse_data(decoded_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Parses the decoded data into a dictionary.

        Args:
            decoded_data: The decoded data.

        Returns:
            A dictionary with the parsed data.
        """
        return {item["name"]: item["value"] for item in decoded_data}
