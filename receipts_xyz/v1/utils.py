from typing import Dict, List, Tuple

from ..schema.v1 import SingleWorkoutReceipt


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
