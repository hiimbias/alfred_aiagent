from pydantic import BaseModel
from core.models.io.embedding_unit import EmbeddingUnit

class EmbeddingResponse(BaseModel):
    """
    An fully populated embedding response.

    Schema:
        ```python
        class EmbeddingResponse(BaseModel):
            embeddings: list[EmbeddingUnit]
            embedding_model: str
            total_tokens: int
        ```
    Where:
        - `embeddings`: A list of embedding units.
        - `embedding_model`: The embedding model used.
        - `total_tokens`: The total tokens used.
    """
    embeddings: list[EmbeddingUnit]
    embedding_model: str
    total_tokens: int