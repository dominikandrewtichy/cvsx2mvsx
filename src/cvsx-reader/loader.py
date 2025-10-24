import json
from pathlib import Path

from models.cvsx.cvsx_annotations import CVSXAnnotations
from models.cvsx.cvsx_entry import CVSXEntry
from models.cvsx.cvsx_index import CVSXIndex
from models.cvsx.cvsx_metadata import CVSXMetadata
from models.cvsx.cvsx_query import CVSXQuery


def load_cvsx_index(filepath: str) -> CVSXIndex:
    with open(filepath) as f:
        json_string = f.read()
        json_data = json.loads(json_string)
        return CVSXIndex.model_validate(json_data)


def load_cvsx_annotations(filepath: str) -> CVSXAnnotations:
    with open(filepath) as f:
        json_string = f.read()
        json_data = json.loads(json_string)
        return CVSXAnnotations.model_validate(json_data)


def load_cvsx_metadata(filepath: str) -> CVSXMetadata:
    with open(filepath) as f:
        json_string = f.read()
        json_data = json.loads(json_string)
        return CVSXMetadata.model_validate(json_data)


def load_cvsx_query(filepath: str) -> CVSXQuery:
    with open(filepath) as f:
        json_string = f.read()
        json_data = json.loads(json_string)
        return CVSXQuery.model_validate(json_data)


def load_cvsx_entry(filepath: str) -> CVSXEntry:
    filepath = Path(filepath)
    cvsx_filepath = filepath / "index.json"

    cvsx_index = load_cvsx_index(cvsx_filepath)

    annotations_filepath = filepath / cvsx_index.annotations
    metadata_filepath = filepath / cvsx_index.metadata
    query_filepath = filepath / cvsx_index.query

    cvsx_annotations = load_cvsx_annotations(annotations_filepath)
    cvsx_metadata = load_cvsx_metadata(metadata_filepath)
    cvsx_query = load_cvsx_metadata(query_filepath)

    return CVSXEntry(
        index=cvsx_index,
        annotations=cvsx_annotations,
        metadata=cvsx_metadata,
        query=cvsx_query,
    )
