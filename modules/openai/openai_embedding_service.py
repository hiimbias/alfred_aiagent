import tiktoken
from openai import OpenAI
from core.interfaces.base_embedding_model import BaseEmbeddingModel
from core.models.io.embedding_unit import EmbeddingUnit
from core.models.responses import EmbeddingResponse
from typing import Union, Literal, Optional

class OpenAIEmbeddingModel(BaseEmbeddingModel):
    def __init__(
        self,
        client: OpenAI,
        embedding_model: Literal[Literal[
            "text-embedding-3-small",
            "text-embedding-3-large",
            "text-embedding-ada-002",
        ]] = "text-embedding-3-small",
        embedding_encoding: str = "cl100k_base",
        encoding_format: Literal["base64", "float"] = "base64",):
        
        self.client = client
        self.embedding_model = embedding_model
        self.embedding_encoding = embedding_encoding
        self.encoding_format = encoding_format


        # The dimensions of the embedding vector are determined by the model used.
        match self.embedding_model: 
            case "text-embedding-3-small":
                self.dimensions = 1536
            case "text-embedding-3-large":
                self.dimensions = 3072
            case "text-embedding-ada-002":
                self.dimensions = 1536
                
    def encode_query(self,
                     query: str,
                     include_metadata: bool = False) -> Union[EmbeddingUnit, EmbeddingResponse]:
        
        """Encodes a query into embedding using the OpenAI embedding model."""
        
        embedding_response : Optional[EmbeddingResponse] = self.encode_texts(
            texts=[query],
            include_metadata=True
        )
        
        if include_metadata:
            return embedding_response # return the full response
        else:
            return embedding_response.embeddings[0] # return the first embedding unit
        
        
    def encode_texts(self,
                     texts: list[str],
                     include_metadata: bool = False) -> Union[list[EmbeddingUnit], EmbeddingResponse]:
        
        """Encodes a list of texts into embeddings using the OpenAI embedding model."""
        
        formatted_texts: list[str] = []
        for text in texts: 
            text = text.replace("\n", " ")
            formatted_texts.append(text)
            
            
        response = self.client.embeddings.create(
            model = self.embedding_model,
            input = formatted_texts,
            encoding_format = self.embedding_encoding,
        )
        
        embeddings: list[EmbeddingUnit] = []
        
        for embedding in response.data:
            embedding_unit = EmbeddingUnit(
                index=embedding.index,
                object=embedding.object,
                content=formatted_texts[embedding.index],
                embedding=embedding.embedding,
                type=self.encoding_format
            )
            embeddings.append(embedding_unit)
            
            
        if include_metadata:
            return EmbeddingResponse(
                embeddings=embeddings,
                embedding_model=self.embedding_model,
                total_tokens=response.usage.total_tokens,
            )
        else:
            return embeddings
        
    def tokenize_texts(self, texts = list[str]) -> list[list[int]]:
        """
        Tokenizes a list of texts using the OpenAI embedding model.
        """
        encoder = tiktoken.get_encoding(self.embedding_encoding)
        
        tokens: list[int] = []
        
        for text in texts:
            tokens.append(encoder.encode(text))
        
        return tokens
        
        
        
        
        