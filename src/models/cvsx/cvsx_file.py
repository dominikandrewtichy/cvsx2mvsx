from pydantic import BaseModel

from src.models.cvsx.cvsx_annotations import CVSXAnnotations
from src.models.cvsx.cvsx_index import CVSXIndex
from src.models.cvsx.cvsx_metadata import CVSXMetadata
from src.models.cvsx.cvsx_query import CVSXQuery


class CVSXFile(BaseModel):
    filepath: str
    index: CVSXIndex
    annotations: CVSXAnnotations
    metadata: CVSXMetadata
    query: CVSXQuery
