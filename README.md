# Receipts-xyz-py

<div align="center">
</div>

A fun project for playing with [receipts.xyz](receipts.xyz) data.

## Installation
Clone this repository and import this from source. Also, run `pip install -r requirements.txt` for downloading necessary libraries. Using an isolated virtual environment is recommended.

## Usage
This SDK calls a GraphQL for [Ethereum Attestation Service (EAS)](https://docs.attest.org/docs/welcome), and use publicly available [receipts.xyz leaderboard endpoint](https://leaderboard.receipts.xyz/) for fetching leaderboard.

## Examples

Get workouts from a user
```python
from receipts_xyz.user import get_workouts

address = "chompk.eth" # or 0x...
workouts = get_workouts(address)
```

Get single workout receipt from UID
```python
from receipts_xyz.schema import SingleWorkoutReceipt

uid = "0x..."
receipt = SingleWorkoutReceipt.from_uid(uid)
```

Get top 10 leaderboard
```python
from receipts_xyz.api import ReceiptsXYZLeaderboardAPI
from receipts_xyz.const import LeaderboardFilter

top10 = ReceiptsXYZLeaderboardAPI().get_weekly_leaderboard(
    leaderboard_filter=LeaderBoardFilter.RUNNING_DISTANCE, 
    limit=10
)
```

## Author
`chompk.eth`