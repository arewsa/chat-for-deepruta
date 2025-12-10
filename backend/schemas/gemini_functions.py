from google.genai.types import FunctionDeclaration

def get_geocoding_functions():
    """Возвращает схемы функций для Gemini Function Calling."""
    return [
        FunctionDeclaration(
            name="forward_geocode",
            description="Forward geocoding: convert address to coordinates",
            parameters_json_schema={
                "type": "object",
                "properties": {
                    "address": {
                        "type": "string",
                        "description": "Address to geocode without city(e.g. 'проспект Металлургов ')"
                    },
                    "address_type": {
                        "type": "string",
                        "description": "Type of address (STREET, LOCATION)",
                        "enum": ["STREET", "LOCATION"]
                    },
                    "language": {
                        "type": "string",
                        "description": "Language for results (e.g. 'ru', 'en')"
                    },
                    "normalize": {
                        "type": "boolean",
                        "description": "Whether to normalize the address",
                        "default": True
                    }
                },
                "required": ["address"]
            }
        ),
        FunctionDeclaration(
            name="reverse_geocode",
            description="Reverse geocoding: convert coordinates to address",
            parameters_json_schema={
                "type": "object",
                "properties": {
                    "longitude": {
                        "type": "number",
                        "description": "Longitude coordinate"
                    },
                    "latitude": {
                        "type": "number",
                        "description": "Latitude coordinate"
                    },
                    "language": {
                        "type": "string",
                        "description": "Language for results"
                    }
                },
                "required": ["longitude", "latitude"]
            }
        ),
        FunctionDeclaration(
            name="suggest_addresses",
            description="Suggest addresses based on query",
            parameters_json_schema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (e.g. 'Олимп')"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of suggestions to return",
                        "default": 10
                    }
                },
                "required": ["query"]
            }
        ),
        FunctionDeclaration(
            name="lookup_address",
            description="Lookup address information",
            parameters_json_schema={
                "type": "object",
                "properties": {
                    "address": {
                        "type": "string",
                        "description": "Address to lookup"
                    },
                    "normalize": {
                        "type": "boolean",
                        "description": "Whether to normalize the address",
                        "default": True
                    },
                    "language": {
                        "type": "string",
                        "description": "Language for results"
                    }
                },
                "required": ["address"]
            }
        )
    ]
