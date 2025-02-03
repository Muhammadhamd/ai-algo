# import pandas as pd
# import numpy as np
# from sentence_transformers import SentenceTransformer
# import spacy
# import openai
# import string
# import os
# import re
# from fastapi import FastAPI
# from datetime import datetime
# from nltk.corpus import stopwords
# import nltk

# app = FastAPI()

# # Initialize the necessary models and API keys
# nlp = spacy.load("en_core_web_lg")
# model = SentenceTransformer('all-MiniLM-L6-v2')


# def openAiReq(data):

#     client = openai.Client(api_key='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')
    
#     stream = client.chat.completions.create(
#         model="gpt-4o-mini",
#         response_format={"type": "json_object"},
#         messages=[
#             {
#                 "role": "user", 
#                "content": f"""
#                 Extract only the **most important and domain-specific nouns and verbs** from the following texts.
                
#                 1. **Ignore generic words** like 'area', 'guide', 'details', 'location', 'activities', 'types' , 'things', 'information', 'place', and 'visit', even if they appear relevant.
#                 2. **Prioritize specific entities** like company names, services, locations, and key actions related to the topic. For example, if the text mentions a company, product, or important service (e.g., 'Al Nahda', 'sewing', 'golf', 'laundry'), include those.
#                 3. Focus on **contextually important** words, i.e., those which are relevant to the specific domain discussed in the source or top 10 items. The extraction should focus on **relevant industry terms**, proper nouns, specific actions, and keywords central to the topic.
#                 4. **Do not include common or generic words** like 'area', 'place', 'things', or city names unless they are the main subject of the discussion.
#                 5. Ensure **specific and industry-relevant words** (e.g., 'fighting', 'laundry', 'cricket', 'sewing', etc.) have higher relevance scores.
#                 6. **Ignore Common words** like 'Dubai', 'UAE', 'Emirates'.
#                 Additionally, calculate a **similarity score** between the **source** and each of the top 10 based on **contextual relevance** rather than simple word overlap. For example, if the source talks about 'sewing', related activities like 'laundry' should get higher scores, but generic words like 'guide' or 'area' should get lower scores.

#                 Source: {data['source']}
#                 Top10: {data['top10']}

#                 Example of desired format:
#                 Input:
#                 Source: Sew far, sew good – Where to get sewing lessons in Dubai. Always wanted to learn how to sew? With our guide to the best sewing classes in Dubai, you'll be stitching up masterpieces in no time!
#                 Top10:
#                 [
#                     "Best Golf Courses in Dubai. If you’re searching for the best golf courses in Dubai, we’ve got you. This article is your perfect guide for the best ones in the emirate.",
#                     "Where to Do Cheap Shopping in Dubai – Full Guide! Wondering where to do cheap shopping in Dubai - well you are in luck. Find here the best places to shop in Dubai for cheap prices!",
#                     "Explore the Nahwa Enclave. Let's unfold the mystery pervading the Nahwa Enclave Sharjah. We bring you complete details of location, history, and things to do in Nahwa.",
#                     ...
#                 ]

#                 Output:
#                 {{
#                     "source": ['sew', 'sewing', 'stitch'],
#                     "top10": [
#                         {{"keywords": ["golf"], "similarity_score": 0.1}},
#                         {{"keywords": ["shopping", "cheap shopping"], "similarity_score": 0.05}},
#                         {{"keywords": ["Nahwa Enclave", "Nahwa", "Sharjah"], "similarity_score": 0.04}},
#                         ...
#                     ]
#                 }}

#                 Please return the output as a JSON object, including both **important domain-specific keywords** and their **contextual similarity score**.
#              """




#             }
#         ],
#         max_tokens=300
#     )

#     return stream.choices[0].message.content



# @app.get("/{file1}/{file2}")
# async def reat_root(file1: str, file2: str):
#     # Load the CSV files
#     df1 = pd.read_csv(f"BlogsData/{file1}")
#     df2 = pd.read_csv(f"BlogsData/{file2}")

#     # Preprocess text in 'Title' and 'Meta Description'
#     df1['combined_content'] = df1[['Title', 'Meta Description']].apply(lambda x: ' '.join(x.dropna()), axis=1).str.strip()
#     df2['combined_content'] = df2[['Title', 'Meta Description']].apply(lambda x: ' '.join(x.dropna()), axis=1).str.strip()

#     # Encode using SentenceTransformer for semantic similarity
#     embeddings_df1 = model.encode(df1['combined_content'].tolist(), convert_to_numpy=True)
#     embeddings_df2 = model.encode(df2['combined_content'].tolist(), convert_to_numpy=True)

#     # Calculate semantic similarities using context-based embeddings
#     semantic_similarities = np.dot(embeddings_df2,embeddings_df1) / (
#         np.linalg.norm(embeddings_df2, axis=1, keepdims=True) * np.linalg.norm(embeddings_df1, axis=1)
#     )

#     # Convert the results into a DataFrame
#     df2['semantic_similarity'] = semantic_similarities.max(axis=1)

#     # Select top 10 matches for each row from df1 to compare with df2
#     top_10_blogs = []
#     for i, row in df1.iterrows():
#         top10_indices = np.argsort(-semantic_similarities[i])[:10]  # Indices of top 10 similar blogs
#         top_10_contents = df2.iloc[top10_indices]['Processed_Text'].tolist()
        
#         # Prepare the data for OpenAI request
#         data = {
#             "source": row['Processed_Text'],
#             "top10": top_10_contents
#         }

#         # Call OpenAI to extract domain-specific similarity
#         openai_response = openAiReq(data)
#         top_10_blogs.append((row['Processed_Text'], openai_response))

#     # Find unique blogs in df1 that are not similar to df2
#     threshold = 0.5  # Adjust as necessary
#     unique_rows = []
#     uniqueness_scores = []
    
#     for i, row in enumerate(df1.itertuples()):
#         max_similarity = row.semantic_similarity
#         if max_similarity < threshold:
#             unique_rows.append(df1.iloc[i])
#             uniqueness_scores.append(1 - max_similarity)

#     # Convert unique rows to DataFrame
#     unique_df = pd.DataFrame(unique_rows)
#     unique_df['Uniqueness_Score'] = uniqueness_scores

#     # Save the unique rows to a new CSV file
#     output_folder = "uniqueFolder"
#     os.makedirs(output_folder, exist_ok=True)
#     timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
#     output_csv_path = os.path.join(output_folder, f'unique_content_{timestamp}.csv')
#     output_json_path = os.path.join(output_folder, f'unique_content_{timestamp}.json')

#     unique_df.to_csv(output_csv_path, index=False)
#     unique_df.to_json(output_json_path, orient='records', lines=True)

#     return {
#         "Message": "Files Saved", 
#         "CSV_FileName": os.path.basename(output_csv_path),
#         "JSON_FileName": os.path.basename(output_json_path)
#     }

# @app.get("/progress")
# async def get_progress():
#     return {"Message": "Processing"}




import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import nltk
from nltk.corpus import stopwords
import string
import re
from fastapi import FastAPI
from datetime import datetime
import os

app = FastAPI()

# Download NLTK stopwords
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

# Function for text preprocessing

# Initialize the SentenceTransformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

@app.get("/{file1}/{file2}")
async def compare_files(file1: str, file2: str):
    # Load the CSV files
    print("Loading CSV files...")
    df1 = pd.read_csv(f"BlogsData/{file1}")
    df2 = pd.read_csv(f"BlogsData/{file2}")
    print("CSV files loaded successfully.")

    # Preprocess the texts in 'Title' and 'Meta Description' columns
    print("Preprocessing text columns...")
    df1['combined_content'] = (df1['Title'].fillna('') + ' ' + df1['Meta Description'].fillna('')).apply(lambda x: ' '.join(x.dropna()), axis=1).str.strip()
    df2['combined_content'] = (df2['Title'].fillna('') + ' ' + df2['Meta Description'].fillna('')).apply(lambda x: ' '.join(x.dropna()), axis=1).str.strip()
    print("Text columns preprocessed.")

    # Encode the processed texts using the Sentence Transformer model
    print("Encoding texts using Sentence Transformer...")
    embeddings_df1 = model.encode(df1['Processed_Text'].tolist(), convert_to_numpy=True)
    embeddings_df2 = model.encode(df2['Processed_Text'].tolist(), convert_to_numpy=True)
    print("Texts encoded.")

    for i,content1  in range(len(embeddings_df1)):
        similarity_matrix = np.dot(embeddings_df2, content1) / (
        np.linalg.norm(embeddings_df2, axis=1, keepdims=True) * np.linalg.norm(content1, axis=1)
    )
        top_10_indices = np.argsort(-similarity_matrix)[:10]  # Sort in descending order and take top 10

    # Print the top 10 similarities with their indices
    print(f"Top 10 similar entries for df1 index {i}:")
    for rank, index in enumerate(top_10_indices, start=1):
        print(f"Rank {rank}: df2 index {index} with similarity score {similarity_matrix[index]:.4f}")

    print("\n")  # For better readabilit
        

    

    # Find unique blogs in df1 not similar to any blogs in df2 and calculate their uniqueness score
    threshold = 0.5  # Adjust the threshold as needed
    unique_rows = []
    uniqueness_scores = []

    # for i in range(similarity_matrix.shape[0]):
    #     max_similarity = max(similarity_matrix[i])
    #     if max_similarity < threshold:
    #         unique_rows.append(df1.iloc[i])
    #         uniqueness_scores.append(1 - max_similarity)  # Uniqueness score (1 - max similarity)

    # # Convert the list of unique rows to a DataFrame
    # unique_df = pd.DataFrame(unique_rows)
    # unique_df['Uniqueness_Score'] = uniqueness_scores

    # # Ensure the directory exists before saving the file
    # output_folder = "uniqueFolder"
    # os.makedirs(output_folder, exist_ok=True)
    
    # # Generate a unique file name with timestamp
    # timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    # output_csv_path = os.path.join(output_folder, f'unique_content_{timestamp}.csv')
    # output_json_path = os.path.join(output_folder, f'unique_content_{timestamp}.json')

    # # Save the unique rows to a new CSV file
    # unique_df.to_csv(output_csv_path, index=False)
    # print(f"Unique content saved to '{output_csv_path}'.")

    # # Save the unique rows to a new JSON file
    # unique_df.to_json(output_json_path, orient='records', lines=True)
    # print(f"Unique content saved to '{output_json_path}'.")

    return {
        # "Message": "Files Saved", 
        # "CSV_FileName": os.path.basename(output_csv_path),
        # "JSON_FileName": os.path.basename(output_json_path)
    }

@app.get("/progress")
async def get_progress():
    return {"status": "in_progress"}
