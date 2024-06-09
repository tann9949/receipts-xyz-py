import requests
import logging

from typing import List, Optional

from .const import LeaderBoardFilter


class ReceiptsXYZGraphQLAPI:
    
    def __init__(self) -> None:
        self.graphql_url = "https://base.easscan.org/graphql"
        self.receiptsxyz_address = "0x77a3b79a2De700AfcfC761fED837a67D7d8fAe1B"
        
    def request_graphql(self, query: str):
        r = requests.post(self.graphql_url, json={"query": query})
        
        if r.status_code != 200:
            logging.error(f"GraphQL request failed with status code {r.status_code}")
            raise Exception(f"GraphQL request failed with status code {r.status_code}\n\n{r.text}")
        
        return r.json()
    
    def query_attestation(self, uid: str) -> dict:
        query = f"""
        query Attestations {{
            attestations(
                orderBy: {{time: desc}},
                where: {{
                    attester: {{
                        equals: "{self.receiptsxyz_address}"
                    }},
                    id: {{
                        equals: "{uid}"
                    }}
                }}
            ) {{
                id
                data
                decodedDataJson
                revoked
                ipfsHash
                schema {{
                    id
                    txid
                }}
            }}
        }}
        """
        
        result = self.request_graphql(query)
        return result

    def fetch_all_data(self, base_query: str, data_path: list, batch_size: int = 8000, **kwargs) -> list:
        all_results = []
        skip = 0
        has_more_data = True
        
        while has_more_data:
            query = base_query.format(batch_size=batch_size, skip=skip, **kwargs)
            logging.info(f"Fetching batch with skip value: {skip}")
            result = self.request_graphql(query)
            
            # Navigate through the nested dictionary to get to the data
            data = result
            for key in data_path:
                data = data.get(key, {})
            
            if data:
                all_results.extend(data)
                skip += batch_size
                has_more_data = len(data) == batch_size
                logging.info(f"Fetched {len(data)} records in this batch.")
            else:
                has_more_data = False
                logging.warning("No more data available or unexpected response format.")
        
        logging.info(f"Total records fetched: {len(all_results)}")
        return all_results
    
    def query_user_workouts(self, address: str) -> dict:
        base_query = """
        query Attestations {{
            attestations(
                orderBy: {{time: desc}},
                where: {{
                    recipient: {{
                        equals: "{address}"
                    }},
                    schema: {{
                        is: {{
                            id: {{
                                equals: "0x48d9973eb6863978c104f85dc6864e827fc0f72c4083dd853171e0bf034f8774"
                            }}
                        }}
                    }}
                }},
                take: {batch_size},
                skip: {skip}
            ) {{
                id
                data
                decodedDataJson
                revoked
                ipfsHash
                schema {{
                    id
                    txid
                }}
            }}
        }}
        """
        
        data_path = ['data', 'attestations']
        results = self.fetch_all_data(base_query, data_path, address=address)
        return results
    
    def query_workouts_with_interval(
        self,
        start_timestamp: int,
        end_timestamp: int
    ) -> dict:
        assert start_timestamp < end_timestamp
        base_query = """
        query Attestations {{
            attestations(
                orderBy: {{time: desc}},
                where: {{
                    time: {{
                        lte: {end_timestamp},
                        gte: {start_timestamp}
                    }},
                    schema: {{
                        is: {{
                            id: {{
                                equals: "0x48d9973eb6863978c104f85dc6864e827fc0f72c4083dd853171e0bf034f8774"
                            }}
                        }}
                    }}
                }},
                take: {batch_size},
                skip: {skip}
            ) {{
                id
                data
                decodedDataJson
                revoked
                ipfsHash
                schema {{
                    id
                    txid
                }}
            }}
        }}
        """
        
        data_path = ['data', 'attestations']
        results = self.fetch_all_data(
            base_query, 
            data_path, 
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp
        )
        return results
    
    def query_user_workouts_with_inteval(
        self, 
        address: str,
        start_timestamp: int,
        end_timestamp: int
    ) -> dict:
        assert start_timestamp < end_timestamp
        base_query = """
        query Attestations {{
            attestations(
                orderBy: {{time: desc}},
                where: {{
                    recipient: {{
                        equals: "{address}"
                    }},
                    time: {{
                        lte: {end_timestamp},
                        gte: {start_timestamp}
                    }},
                    schema: {{
                        is: {{
                            id: {{
                                equals: "0x48d9973eb6863978c104f85dc6864e827fc0f72c4083dd853171e0bf034f8774"
                            }}
                        }}
                    }}
                }},
                take: {batch_size},
                skip: {skip}
            ) {{
                id
                data
                decodedDataJson
                revoked
                ipfsHash
                schema {{
                    id
                    txid
                }}
            }}
        }}
        """
        
        data_path = ['data', 'attestations']
        results = self.fetch_all_data(
            base_query, 
            data_path, 
            address=address,
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp
        )
        return results
    
    def query_receipts_users(self) -> List[str]:
        base_query = """
        query Users {{
            attestations(
                orderBy: {{time: desc}},
                where: {{
                    schema: {{
                        is: {{
                            id: {{
                                equals: "0x0f575d6100ca5a0d82b037f97673b97ebb8bb55848aa8b861ee4a843e247c1d2"
                            }}
                        }}
                    }}
                }},
                take: {batch_size},
                skip: {skip}
            ) {{
                recipient
                time
            }}
        }}
        """
        
        data_path = ['data', 'attestations']
        results = self.fetch_all_data(base_query, data_path)
        return results
    
    
class ReceiptsXYZLeaderboardAPI:
    
    def __init__(self) -> None:
        self.endpoint = "https://leaderboard.receipts.xyz/api/receipts"
        
    def get_weekly_leaderboard(
        self, 
        limit: Optional[int] = None,
        leaderboard_filter: LeaderBoardFilter = LeaderBoardFilter.RUNNING_DISTANCE,
        sort_outputs: bool = True
    ) -> dict:
        # params
        params = {
            "social": "strava",
            "time_range": "week",
            "filter": leaderboard_filter,
            "activity": "",
            "time_class": "undefined",
            "limit": "undefined" if limit is None else limit
        }
        
        response = requests.get(self.endpoint, params=params)
        
        if response.status_code != 200:
            logging.error(f"Leaderboard request failed with status code {response.status_code}")
            raise Exception(f"Leaderboard request failed with status code {response.status_code}\n\n{response.text}")
        
        results = response.json()["data"]
        
        if sort_outputs:
            key = leaderboard_filter if leaderboard_filter != LeaderBoardFilter.TOTAL_ACTIVITIES else "activities"
            results = sorted(results, key=lambda x: x[key], reverse=True)
        return results
