from pydantic import BaseModel

from .cvsx_annotations import CVSXAnnotations
from .cvsx_index import CVSXIndex
from .cvsx_metadata import CVSXMetadata
from .cvsx_query import CVSXQuery


class CVSXEntry(BaseModel):
    index: CVSXIndex
    annotations: CVSXAnnotations
    metadata: CVSXMetadata
    query: CVSXQuery
