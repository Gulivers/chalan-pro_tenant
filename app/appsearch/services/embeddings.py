import logging

from django.conf import settings

logger = logging.getLogger(__name__)


class EmbeddingServiceError(Exception):
    pass


def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Generate embeddings via OpenAI text-embedding-3-small (1536 dims by default).
    """
    if not texts:
        return []

    api_key = getattr(settings, 'OPENAI_API_KEY', '')
    if not api_key:
        raise EmbeddingServiceError(
            'OPENAI_API_KEY is not configured. Add it to envs/backend.dev.env'
        )

    model = getattr(settings, 'SEARCH_EMBEDDING_MODEL', 'text-embedding-3-small')
    dimensions = getattr(settings, 'SEARCH_EMBEDDING_DIMENSIONS', 1536)

    try:
        from openai import OpenAI
    except ImportError as exc:
        raise EmbeddingServiceError('openai package is not installed') from exc

    client = OpenAI(api_key=api_key)
    try:
        response = client.embeddings.create(
            model=model,
            input=texts,
            dimensions=dimensions,
        )
    except Exception as exc:
        logger.exception('OpenAI embedding request failed')
        raise EmbeddingServiceError(str(exc)) from exc

    return [item.embedding for item in response.data]
