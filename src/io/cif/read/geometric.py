from src.models.read.geometric import ShapePrimitiveData


def parse_geometric_json(json_string: str) -> ShapePrimitiveData:
    geometric_data = ShapePrimitiveData.model_validate_json(json_string)
    return geometric_data
