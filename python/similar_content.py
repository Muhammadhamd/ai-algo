from fastapi import FastAPI
import pandas as pd
import numpy as np
import os
from sentence_transformers import SentenceTransformer

app = FastAPI()

model = SentenceTransformer('all-MiniLM-L6-v2')

def load_data(file_name):
    csv_path = f"./database/BlogsData/{file_name}"
    df = pd.read_csv(csv_path, quotechar='"', skipinitialspace=True)
    df['combined_content'] = df[['Title']].apply(lambda x: ' '.join(x.dropna()), axis=1).str.strip()
    return df
def get_embeddings(file_name, df):
    embeddings_dir = "./Embeddings"
    embedding_path = f"{embeddings_dir}/{file_name}_embeddings.npy"
    if not os.path.exists(embeddings_dir):
        os.makedirs(embeddings_dir)

    try:
        if os.path.exists(embedding_path):
            embeddings_csv = np.load(embedding_path)
            if embeddings_csv.shape[0] == df.shape[0]:
                return embeddings_csv
            else:
                print("Mismatch in data rows and embeddings. Recomputing...")
                os.remove(embedding_path)

        print("Computing new embeddings...")
        embeddings_csv = model.encode(df['combined_content'].tolist(), convert_to_numpy=True)
        np.save(embedding_path, embeddings_csv)
        print("New embeddings saved.")
        return embeddings_csv
    except Exception as e:
        print("Failed to process embeddings:", e)
        raise

@app.get("/{file_name}/{single_blog}")
async def find_similar(file_name: str, single_blog: str):
    df = load_data(file_name)
    embeddings_csv = get_embeddings(file_name, df)
    print("embaddinge getit")
    embedding_single_blog = model.encode(single_blog, convert_to_numpy=True)
    print("embaddinge single blog complete...")

    semantic_similarities = np.dot(embeddings_csv, embedding_single_blog) / (np.linalg.norm(embeddings_csv, axis=1) * np.linalg.norm(embedding_single_blog))
    df['Similarity'] = semantic_similarities
    print("simalirity calcualtion blog complete...")

    # Get the top 40 similar blogs sorted by similarity
    top_similar = df.sort_values(by='Similarity', ascending=False).head(20)

    response_data = []
    for index, row in top_similar.iterrows():
        response_data.append({
            'Topic': single_blog,
        'Similarity': None if pd.isna(row['Similarity']) else row['Similarity'],
        'Similar Title': row['Title'],
        'Title': row['Title'],
        # 'Publish Date': row.get('Publish Date', 'N/A'),
        'Meta Description': row['Meta Description'],
        'Canonical Link': row['Canonical Link']
        })

    return response_data
