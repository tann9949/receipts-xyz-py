from .v1 import ReceiptsXYZV1GraphQLAPI


class ReceiptsXYZV2GraphQLAPI(ReceiptsXYZV1GraphQLAPI):
    
    def __init__(self) -> None:
        super().__init__()
        self.receiptsxyz_address = "0x2261A703139c6230f2a9Fb173cc245B83348C6Ba"
        self.schema_id = {
            "workout": "0x306c3768de1da8b0d36386d395ccafd05526741a6d38a3cee1bbbb7765d461d2"
        }
    
    def query_workouts(self) -> dict:
        base_query = """
        query Attestations {{
            attestations(
                orderBy: {{time: desc}},
                where: {{
                    schema: {{
                        is: {{
                            id: {{
                                equals: "{schema_id}"
                            }}
                        }}
                    }},
                    attester: {{
                        equals: "{receiptsxyz_address}"
                    }}
                }},
                take: {batch_size},
                skip: {skip}
            ) {{
                id
                time
                txid
                data
                decodedDataJson
                revoked
                ipfsHash
                schema {{
                    id
                }}
            }}
        }}
        """
        
        data_path = ['data', 'attestations']
        results = self.fetch_all_data(
            base_query, 
            data_path,
            receiptsxyz_address=self.receiptsxyz_address,
            schema_id=self.schema_id['workout'],
        )
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
                                equals: "{schema_id}"
                            }}
                        }}
                    }},
                    attester: {{
                        equals: "{receiptsxyz_address}"
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
                }}
            }}
        }}
        """
        
        data_path = ['data', 'attestations']
        results = self.fetch_all_data(
            base_query, 
            data_path, 
            receiptsxyz_address=self.receiptsxyz_address,
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
            schema_id=self.schema_id['workout'],
        )
        return results
    