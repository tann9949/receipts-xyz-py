import logging
from typing import List

from .api import ReceiptsXYZGraphQLAPI
from .exception import ParsingFailException
from .schema import Attestation, SingleWorkoutReceipt, WeekInterval
from .utils import deduplicate_receipts


def get_weekly_attested_workouts(deduplicate: bool = True) -> List[SingleWorkoutReceipt]:
    weekly_interval = WeekInterval.get_current_interval()

    logging.info(f"Fetching attestations between {weekly_interval.formatted_interval}")
    output = ReceiptsXYZGraphQLAPI().query_workouts_with_interval(
        start_timestamp=weekly_interval.start_timestamp, 
        end_timestamp=weekly_interval.end_timestamp
    )
    
    workouts = list()
    for _a in output:
        try:
            attestation = Attestation.from_dict(_a)
            if SingleWorkoutReceipt.is_single_workout(attestation):
                workouts.append(SingleWorkoutReceipt.from_attestation(attestation))
        except ParsingFailException:
            logging.warning(f"Failed to parse attestation: {_a['id']}")
            
    if deduplicate:
        workouts = deduplicate_receipts(workouts)
    
    return workouts
