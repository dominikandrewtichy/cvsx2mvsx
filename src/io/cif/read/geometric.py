from src.models.read.geometric import ShapePrimitiveData


def parse_geometric_json(json_string: str) -> ShapePrimitiveData:
    return ShapePrimitiveData.model_validate_json(json_string)
