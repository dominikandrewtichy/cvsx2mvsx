from pydantic import BaseModel

from lib.models.cvsx.cvsx_annotations import CVSXAnnotations
from lib.models.cvsx.cvsx_index import CVSXIndex
from lib.models.cvsx.cvsx_metadata import CVSXMetadata
from lib.models.cvsx.cvsx_query import CVSXQuery


class CVSXEntry(BaseModel):
    filepath: str
    index: CVSXIndex
    annotations: CVSXAnnotations
    metadata: CVSXMetadata
    query: CVSXQuery
