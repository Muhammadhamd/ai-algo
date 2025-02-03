from fastapi import APIRouter
from python.services.dataLoader import load_data
from python.services.embaddings import get_embeddings
from python.models.load_sentence_transformer import model
import numpy as np
import pandas as pd

router = APIRouter()

@router.get("/{file_name}/{single_blog}")
async def find_similar(file_name: str, single_blog: str):
    df = load_data(file_name)
    embeddings_csv = get_embeddings(file_name, df)
    embedding_single_blog = model.encode(single_blog, convert_to_numpy=True)

    semantic_similarities = np.dot(
        embeddings_csv, embedding_single_blog
    ) / (np.linalg.norm(embeddings_csv, axis=1) * np.linalg.norm(embedding_single_blog))
    df['Similarity'] = semantic_similarities

    # Get the top 20 similar blogs sorted by similarity
    top_similar = df.sort_values(by='Similarity', ascending=False).head(20)

    response_data = []
    for _, row in top_similar.iterrows():
        response_data.append({
            'Topic': single_blog,
            'Similarity': None if pd.isna(row['Similarity']) else row['Similarity'],
            'Similar Title': row['Title'],
            'Title': row['Title'],
            'Meta Description': row['Meta Description'],
            'Canonical Link': row['Canonical Link']
        })

    return response_data
