from fastapi import FastAPI
import pandas as pd
import numpy as np
import os
from sentence_transformers import SentenceTransformer

app = FastAPI()

# Update model to paraphrase-mpnet-base-v2
model = SentenceTransformer('paraphrase-mpnet-base-v2')

def load_data(file_name):
    csv_path = f"./BlogsData/{file_name}"
    df = pd.read_csv(csv_path, quotechar='"', skipinitialspace=True)
    
    # Use Article Content for internal linking
    # df['combined_content'] = df[['Article Content']].apply(lambda x: ' '.join(x.dropna()), axis=1).str.strip()
    return df
def get_embeddings(file_name, df):
    embeddings_dir = "./Embeddings"
    embedding_path = f"{embeddings_dir}/{file_name}_article_embeddings.npy"
    if not os.path.exists(embeddings_dir):
        os.makedirs(embeddings_dir)

    try:
        # Clean the 'Article Content' column to replace NaN or non-string values with empty strings
        df['Article Content'] = df['Article Content'].fillna('').astype(str)

        if os.path.exists(embedding_path):
            embeddings_csv = np.load(embedding_path)
            if embeddings_csv.shape[0] == df.shape[0]:
                return embeddings_csv
            else:
                print("Mismatch in data rows and embeddings. Recomputing...")
                os.remove(embedding_path)

        print("Computing new embeddings...")
        embeddings_csv = model.encode(df['Article Content'].tolist(), convert_to_numpy=True)
        np.save(embedding_path, embeddings_csv)
        print("New embeddings saved.")
        return embeddings_csv
    except Exception as e:
        print("Failed to process embeddings:", e)
        raise

@app.get("/{file_name}/{single_title}")
async def find_internal_links(file_name: str, single_title: str):
    print(file_name,single_title)
    # return {}
    df = load_data(file_name)
    
    # Get embeddings for the article content
    embeddings_csv = get_embeddings(file_name, df)
    print("Article content embeddings loaded.")
    
    # Encode the single title for comparison
    embedding_single_title = model.encode(single_title, convert_to_numpy=True)
    print("Title embedding completed.")
    
    # Calculate similarity between the single title and article content
    semantic_similarities = np.dot(embeddings_csv, embedding_single_title) / (np.linalg.norm(embeddings_csv, axis=1) * np.linalg.norm(embedding_single_title))
    df['Similarity'] = semantic_similarities
    print("Similarity calculation completed.")
    
    # Get the top 20 similar articles sorted by similarity
    top_similar = df.sort_values(by='Similarity', ascending=False).head(50)
    
    response_data = []
    for index, row in top_similar.iterrows():
        response_data.append({
            # 'Topic': single_title,
            'Similarity': None if pd.isna(row['Similarity']) else row['Similarity'],
            'Title': row['Title'],
            # 'Meta Description': row.get('Meta Description', 'N/A'),
            'Canonical Link': row.get('Canonical Link', 'N/A'),
            'Article Content': row['Article Content']  # Include article content for internal linking
        })

    return response_data
