from pydantic import BaseModel
from typing import Optional, Union, Literal

class EmbeddingSplits(BaseModel):
    """
    A list of splits.

    Schema:
        ```python
        class EmbeddingSplits(BaseModel):
            content: str
            index: int
            combined_splits: Optional[str] = None
        ```
    Where:
        - `content`: The content of the split.
        - `index`: The index of the split.
        - `combined_splits`: The combined splits of the split.
    """
    content: str
    index: int
    combined_splits: Optional[str] = None

class EmbeddingUnit(BaseModel):
    """
    An embedding unit.

    Schema:
        ```python
        class EmbeddingUnit(BaseModel):
            index: int
            object: str
            content: str
            embedding: list[float]
        ```
    Where:
        - `index`: The index of the embedding.
        - `object`: The object of the embedding.
        - `content`: The content of the embedding.
        - `embedding`: The embedding vector.
        - `type`: The type of the embedding.
    """
    index: int
    object: str
    content: str
    embedding: Optional[Union[list[float], str]]
    type: Literal["base64", "float"]