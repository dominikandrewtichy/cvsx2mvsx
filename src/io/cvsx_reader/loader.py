import json
from pathlib import Path

from src.models.cvsx.cvsx_annotations import CVSXAnnotations
from src.models.cvsx.cvsx_entry import CVSXEntry
from src.models.cvsx.cvsx_index import CVSXIndex
from src.models.cvsx.cvsx_metadata import CVSXMetadata
from src.models.cvsx.cvsx_query import CVSXQuery


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


def load_cvsx_entry(unzipped_cvsx_entry_filepath: str) -> CVSXEntry:
    unzipped_cvsx_entry_path = Path(unzipped_cvsx_entry_filepath)
    cvsx_filepath = unzipped_cvsx_entry_path / "index.json"

    cvsx_index = load_cvsx_index(cvsx_filepath)

    annotations_filepath = unzipped_cvsx_entry_path / cvsx_index.annotations
    metadata_filepath = unzipped_cvsx_entry_path / cvsx_index.metadata
    query_filepath = unzipped_cvsx_entry_path / cvsx_index.query

    cvsx_annotations = load_cvsx_annotations(annotations_filepath)
    cvsx_metadata = load_cvsx_metadata(metadata_filepath)
    cvsx_query = load_cvsx_query(query_filepath)

    return CVSXEntry(
        index=cvsx_index,
        annotations=cvsx_annotations,
        metadata=cvsx_metadata,
        query=cvsx_query,
    )
