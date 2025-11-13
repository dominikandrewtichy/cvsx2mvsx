from pydantic import BaseModel


class EntryId(BaseModel):
    source_db_id: str | None
    source_db_name: str | None
