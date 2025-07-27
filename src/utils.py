from jsonschema import validate

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
    # Ensure outline is always a list of proper objects
    if not isinstance(data.get("outline"), list):
        data["outline"] = []
    
    # Validate each outline item
    valid_outline = []
    for item in data["outline"]:
        if isinstance(item, dict) and all(k in item for k in ["level", "text", "page"]):
            valid_outline.append(item)
    
    data["outline"] = valid_outline or [{
        "level": "H1",
        "text": data.get("title", "Document Headings"),
        "page": 1
    }]
    
    validate(instance=data, schema=OUTLINE_SCHEMA)