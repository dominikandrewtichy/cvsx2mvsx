import json
from typing import Type, TypeVar
from zipfile import ZipFile

from src.models.cvsx.cvsx_annotations import CVSXAnnotations
from src.models.cvsx.cvsx_entry import CVSXEntry
from src.models.cvsx.cvsx_index import CVSXIndex
from src.models.cvsx.cvsx_metadata import CVSXMetadata
from src.models.cvsx.cvsx_query import CVSXQuery

T = TypeVar("T")


def check_index_exists_in_zip(zip_path: str, index_path: str = "index.json") -> None:
    with ZipFile(zip_path, "r") as z:
        zip_contents = set(z.namelist())

    if index_path not in zip_contents:
        raise FileNotFoundError(
            f"Index file '{index_path}' not found in ZIP archive '{zip_path}'"
        )


def check_all_files_exist_in_zip(zip_path: str, cvsx_index: CVSXIndex) -> None:
    with ZipFile(zip_path, "r") as z:
        zip_contents = set(z.namelist())

    expected_files = set()

    expected_files.update(
        [
            cvsx_index.annotations,
            cvsx_index.metadata,
            cvsx_index.query,
        ]
    )

    expected_files.update(cvsx_index.volumes.keys())
    if cvsx_index.latticeSegmentations:
        expected_files.update(cvsx_index.latticeSegmentations.keys())
    if cvsx_index.geometricSegmentations:
        expected_files.update(cvsx_index.geometricSegmentations.keys())
    if cvsx_index.meshSegmentations:
        for mesh_info in cvsx_index.meshSegmentations:
            expected_files.update(mesh_info.segmentsFilenames)

    missing_files = sorted(f for f in expected_files if f not in zip_contents)
    if missing_files:
        raise FileNotFoundError(
            "The following files are missing from the ZIP archive:\n"
            + "\n".join(f"  - {f}" for f in missing_files)
        )


def load_model_from_zip(zip_path: str, inner_path: str, model_class: Type[T]) -> T:
    with ZipFile(zip_path, "r") as z:
        with z.open(inner_path) as f:
            json_data = json.load(f)
    return model_class.model_validate(json_data)


def load_cvsx_entry(zip_filepath: str) -> CVSXEntry:
    check_index_exists_in_zip(zip_filepath, "index.json")
    cvsx_index = load_model_from_zip(zip_filepath, "index.json", CVSXIndex)
    check_all_files_exist_in_zip(zip_filepath, cvsx_index)
    cvsx_annotations = load_model_from_zip(
        zip_filepath, cvsx_index.annotations, CVSXAnnotations
    )
    cvsx_metadata = load_model_from_zip(zip_filepath, cvsx_index.metadata, CVSXMetadata)
    cvsx_query = load_model_from_zip(zip_filepath, cvsx_index.query, CVSXQuery)

    return CVSXEntry(
        filepath=zip_filepath,
        index=cvsx_index,
        annotations=cvsx_annotations,
        metadata=cvsx_metadata,
        query=cvsx_query,
    )
