import os
import numpy as np
from python.models.load_sentence_transformer import model

def get_embeddings(file_name, df):
    embeddings_dir = "./app/Embeddings"
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
