import pandas as pd

def load_blogs_data(file_name):
    csv_path = f"./python/database/BlogsData/{file_name}"
    df = pd.read_csv(csv_path, quotechar='"', skipinitialspace=True)
    df['combined_content'] = df[['Title']].apply(lambda x: ' '.join(x.dropna()), axis=1).str.strip()
    return df