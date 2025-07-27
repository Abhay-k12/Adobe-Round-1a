import jsonschema

OUTLINE_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "outline": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "level": {"enum": ["H1", "H2", "H3"]},
                    "text": {"type": "string"},
                    "page": {"type": "integer", "minimum": 1}
                },
                "required": ["level", "text", "page"]
            }
        }
    },
    "required": ["title", "outline"]
}

def validate_json_schema(data):
    jsonschema.validate(instance=data, schema=OUTLINE_SCHEMA)