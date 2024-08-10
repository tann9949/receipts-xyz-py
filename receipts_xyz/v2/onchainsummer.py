from typing import List

from ..api.v2 import ReceiptsXYZV2GraphQLAPI
from ..schema.v2 import WorkoutReceipt, AttestationV2


def get_onchainsummer_workouts() -> List[WorkoutReceipt]:
    api = ReceiptsXYZV2GraphQLAPI()
    workouts = [
        WorkoutReceipt.from_attestation(
            AttestationV2.from_dict(_w)
        )
        for _w in api.query_workouts()
    ]
    return sorted([
        _w for _w in workouts
        if _w.name == "Onchain Summer Olympics"
    ], key=lambda x: x.time, reverse=True)
