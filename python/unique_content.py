import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.corpus import stopwords
import string
import gzip
import base64
import re
from fastapi import FastAPI, HTTPException, BackgroundTasks
from datetime import datetime
import os
import numpy as np
from sentence_transformers import SentenceTransformer
import json
import openai
from openai import OpenAIError, RateLimitError
  # Importing the correct exceptions
import time
import requests
import csv
app = FastAPI()

# Initialize the SentenceTransformer model
model = SentenceTransformer('all-MiniLM-L6-v2')
progress = {"status": "Not started", "current": 0, "total": 0}
webhook_url = "http://localhost:4000/api/webhook/comparison"  # Webhook URL




def openAiReq(data):
  client = openai.Client(api_key='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')

  stream = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
          messages=[
            {
                "role":"system",
                "content": "I am your contextual similarity calculator expert"
            },
             {
                "role":"user",
                "content": f"""
                thats great 
                here are some instructions:
                Extract only the **most important and domain-specific nouns and verbs** from the following texts.

                1. **Ignore generic words** like 'area', 'guide', 'details', 'location', 'activities', 'types' , 'things', 'information', 'place', and 'visit', even if they appear relevant.
                2. **Prioritize specific entities** like company names, services, locations, and key actions related to the topic. For example, if the text mentions a company, product, or important service (e.g., 'Al Nahda', 'sewing', 'golf', 'laundry'), include those.
                3. Focus on **contextually important** words, i.e., those which are relevant to the specific domain discussed in the source or top 10 items. The extraction should focus on **relevant industry terms**, proper nouns, specific actions, and keywords central to the topic.
                4. **Do not include common or generic words** like 'area', 'place', 'things', or city names unless they are the main subject of the discussion.
                5. Ensure **specific and industry-relevant words** (e.g., 'fighting', 'laundry', 'cricket', 'sewing', etc.) have higher relevance scores.
                6. **Ignore Common words** like 'Dubai', 'UAE', 'Emirates'.
                Additionally, calculate a **similarity score** between the **source** and each of the top 10 based on **contextual relevance** rather than simple word overlap. For example, if the source talks about 'sewing', related activities like 'laundry' should get higher scores, but generic words like 'guide' or 'area' should get lower scores.
    
                """
            },
            {
                "role":"system",
                "content": "Got it! Please provide the source text and the top 10 items you mentioned so I can analyze them and extract the relevant terms as per your instructions."
            },
            {
             "role":"user",
             "content":"""
             I will Provide you one source sentence top10 sentences you have to extract the most important and domain-specific nouns and verbs from sentences according to the instructons above and return me score
             """  
            },
            {
                "role": "system",
                "content": "Please go ahead and share the source sentence and the top 10 sentences you'd like me to analyze."
            },
            {
                "role": "user",
                "content": """
                  **source**:"Best buildings to buy apartments in Downtown Dubai From the Burj Khalifa to Burj Views, we've compiled a comprehensive guide on the best buildings to buy apartments in Downtown Dubai.",
                 **top10**:['Downtown Dubai Part of our Dubai Area Guide, we look at Downtown Dubai. Including community overview, property choices, pros & cons of living in the area.', "Best Hotels in Downtown Dubai If you're hesitant about staying in the heart of the city, you surely should not, because there are many lavish hotels in Downtown Dubai", "Best Things to Do in Downtown Dubai Downtown Dubai is packed full of one-of-a-kind experiences and brilliant sights. Here's our list of the best things to do in Downtown Dubai.", 'Best Restaurants in Downtown Dubai There are different restaurants in Downtown Dubai that offer amazing food, spectacular views, and high-end service.', 'Pros and Cons of Living in Downtown Dubai Downtown Dubai is the backbone of Dubai’s tourism. But is it a great place to settle down? Explore what living in Downtown Dubai looks like.', "Best Cafes in Downtown Dubai If you're searching for the best cafes in Downtown Dubai, here is your guide to the area's top with high quality and service.", 'Top Areas to Buy Townhouses in Dubai Looking to buy townhouse in Dubai and discover how to find the best townhouse in Dubai in different up-scale communities.', 'Burj Khalifa: Dubai’s Centrepiece Explore the Burj Khalifa: Marvel at its breathtaking views, luxurious amenities, and iconic architecture in the heart of Dubai.', 'Top 10 Tallest Buildings in Dubai Dubai’s skyline, dominated by the tallest buildings in Dubai, has always been one that had the entire world’s attention all the time. It constantly Discover the tallest buildings in Dubai, from the iconic Burj Khalifa to the stunning Princess Tower. Explore their unique features and designs here.', "15 Most Famous Buildings in Dubai Learn about Dubai's most iconic buildings, which range from hotels and tourist attractions to imposing residential buildings."]
                """
            },
            {
                "role": "system",
                "content": """{{"scores": [0.7,0.3,0.4,0.3,0.6,0.3,0.4,0.8,0.6,0.7]}}"""
            },
            {
                "role":"user",
                "content":f"""
                **source**:'Throw a spectacular baby shower at these venues in Dubai Discover the best venues to host a baby shower in Dubai, with afternoon teas, lunches and customised sweet treats to make the mum-to-be feel extra special!'
                **top10**: ['Mother’s Day Dubai Celebrations & Festivities Mother’s Day Dubai is just around the corner on March, 21. Explore the best restaurant deals in dubai for Mother’s Day and more here.', 'Best Indoor Play Areas in Dubai Do you want to take you kids for a day out? Check the best kids indoor play areas in Dubai for an unmissable family day.', 'Mother’s Day Abu Dhabi – Celebrations, Gifts & More Discover the participating restaurants for Mother’s Day Abu Dhabi in this detailed guide along with gift ideas and more.', 'Kids Activities in Dubai – Fun and Exciting Options for All Ages Check out the best kids activities in Dubai here! From outdoor fun to activities in Dubai Mall, explore the best activities for kids.', 'Best Nurseries in Dubai If you’re living in Dubai and searching for the perfect nursery for your little one, you’re in the right place now. We know the hassle so we prepared this', 'Family Activities in Dubai – Fun and Exciting Options for All Ages Find the best family activities in Dubai! As Dubai is full of fun spots for everyone, explore the best family activities in Dubai with us.', 'Best Places to Visit in Dubai with Family Here are the best places to visit in Dubai with family for unlimited entertainment and unforgettable moments.', 'Best Outdoor Activities in Dubai Dubai is mostly famous for all the malls, glamorous restaurants, and indoor places you can visit. There is so much more to do than these mainstream', "Finding the Perfect Gift for Mother’s Day Find the perfect gift for Mother’s Day in Dubai or Abu Dhabi here. These Mother's Day gifts will definitely make a mum very happy.", 'Best Waterparks in Dubai Are you in the mood for some splashing fun? Waterparks in Dubai are a trademark attraction and we’re here to spill secrets about the best ones in the city']
                """
            },
            
            {
                "role": "system",
                "content": """{{"scores": [0.01, 0.005, 0.09, 0.2, 0.09, 0.0, 0.0, 0.0, 0.04, 0.0]}}"""
            },
            {
                "role": "user",
                "content": """
                the result is perfect 0.01 for the first sentence and 0.005 for the second sentence of **top10** sentences according to there simialrty score
                
                """
            },
            {
                "role": "system",
                "content": "provide me more data so i wil analize it"
            },
            {
                "role": "user",
                "content": """
                  **source**:Sew far, sew good – Where to get sewing lessons in Dubai . Always wanted to learn how to sew? With our guide to the best sewing classes in Dubai you'll be stitching up masterpieces in no time!,
                 **top10**: ['Best Golf Courses in Dubai If you’re searching for the best golf courses in Dubai, we’ve got you. This article is your perfect guide for the best ones in the emirate.\xa0 Dubai is', 'Popular Thrift Shops in Dubai Looking to choose your next thrifting destination? Here are the top 6 thrift shops in Dubai.', 'Best Dry Cleaning & Laundry Dubai Shops Looking for a good laundry Dubai shop? If so, explore here the top 10 laundry in Dubai which provide cleaning services across the city.', 'Dubai Area Guide Our complete Dubai Area Guide of some of the most coveted areas of the city. Including community overview, property choices, pros & cons...', 'Know All About Souk Madinat Jumeirah Souk Madinat Jumeirah is your gate to an authentic shopping, dining, and fun experience in the heart of Dubai; find out all about it here.', 'Online Fashion Shopping UAE – Best Apps and Websites See top online fashion shopping UAE websites and apps. Find the best fashion shop online for you such as Max Fashion, Matalan and more.', 'Where to Do Cheap Shopping in Dubai – Full Guide! Wondering where to do cheap shopping in Dubai - well you are in luck. Find here the best places to shop in Dubai for cheap prices!', 'Where to Do Cheap Shopping in Dubai – Full Guide! Wondering where to do cheap shopping in Dubai - well you are in luck. Find here the best places to shop in Dubai for cheap prices!', 'Top 10 Dubai Abaya Shops Head to one of the Dubai abaya shops to get the most lavish traditional attires. Here are the top ten best abaya shops in Dubai for you.', 'Best Staycations in Dubai Whether you’re living in Dubai or coming for a visit and want to enjoy a lovely staycation, this article is for you. Dubai has a collection of world-class']}
                """
            },
            {
                "role": "system",
                "content": """
                Let's extract the most important and domain-specific nouns and verbs from each sentence in the provided set, while also calculating the contextual similarity scores relative to the source text about sewing lessons.

### Source Text:
- "Sew far, sew good – Where to get sewing lessons in Dubai. Always wanted to learn how to sew? With our guide to the best sewing classes in Dubai you'll be stitching up masterpieces in no time!"

### Keywords Extraction and Similarity Scoring:

#### 1. Best Golf Courses in Dubai
- **Keywords**: golf courses
- **Similarity Score**: 0.005 - Completely different focus (golf vs sewing).

#### 2. Popular Thrift Shops in Dubai
- **Keywords**: thrift shops
- **Similarity Score**: 0.06 - Slightly relevant due to the clothing aspect, but not directly related to sewing.

#### 3. Best Dry Cleaning & Laundry Dubai Shops
- **Keywords**: laundry, cleaning services
- **Similarity Score**: 0.08 - Relevant through the connection with fabric care, indirectly related to sewing.

#### 4. Dubai Area Guide
- **Keywords**: areas, property
- **Similarity Score**: 0.0 - Not relevant to sewing.

#### 5. Know All About Souk Madinat Jumeirah
- **Keywords**: shopping, dining, Souk Madinat Jumeirah
- **Similarity Score**: 0.01 - Minimal relevance, only connects through the broader category of shopping.

#### 6. Online Fashion Shopping UAE – Best Apps and Websites
- **Keywords**: online fashion shopping, apps, websites
- **Similarity Score**: 0.09 - Slightly relevant due to the connection with clothing and fashion.

#### 7. Where to Do Cheap Shopping in Dubai – Full Guide!
- **Keywords**: cheap shopping
- **Similarity Score**: 0.04 - Minimal relevance; shopping is a broad category.

#### 8. Where to Do Cheap Shopping in Dubai – Full Guide! (repeated)
- **Keywords**: cheap shopping
- **Similarity Score**: 0.04 - Same as above, minimal relevance.

#### 9. Top 10 Dubai Abaya Shops
- **Keywords**: abaya shops
- **Similarity Score**: 0.09 - Slightly relevant due to the specific focus on clothing.

#### 10. Best Staycations in Dubai
- **Keywords**: staycations
- **Similarity Score**: 0.0 - Not relevant to sewing.

### Summary:
The computed similarity scores reflect the contextual connection based on the focus of sewing lessons and related topics. Most texts are not directly relevant, with only a few having slight connections through broader categories related to clothing and fabric care. 

Let me know if this aligns with your expectations or if you need further refinements!
                """
            },
            {
                "role": "user",
                "content": """
                only return the simialrty score in array json formet
                """
            },
            {
                "role": "system",
                "content": """
                {{"scores": [0.005, 0.09, 0.06, 0.0, 0.01, 0.09, 0.04, 0.04, 0.09, 0.0]}}
                """
            },
             {
                "role":"user",
                "content":f"""
                **source**:'British curriculum GEMS schools in Dubai . Dubai-based and looking for a British schooling? MyBayut brings you a list of the primary and secondary GEMS British curriculum schools in Dubai.'
                **top10**:["Best British Schools in Dubai If you're looking for the best British schools in Dubai, check out this article for the top ones with all the details you need.", 'Top Cheap Schools in Dubai Discover the best cheap schools in Dubai in this guide. Including the top cheap British schools in Dubai along with American and Indian.', 'Best British Schools in Abu Dhabi Need a detailed list for the best British schools in Abu Dhabi? your demand is here; this guide includes all about the top ones in the city!', 'Best Universities in Dubai Want to complete or upgrade your education in Dubai? Find here a list of the best universities in Dubai to pursue a notable learning journey', 'Discovering the Best Schools in UAE – Top Institutions and Curricula Explore the best schools in UAE offering diverse curricula. From law schools in UAE to international and more, see locations, fees, and more!', 'British or American Curriculum in UAE: Which to Choose? Explore the key difference between the american and british curriculum, focusing on teaching styles, assessment methods, and subject variety.', 'The Best Arabic Language Schools in Dubai Bracing yourself to learn Arabic language? Check out these best Arabic language schools in Dubai and know more about them.', "Best Indian Schools in Dubai Discover the list of best Indian schools in Dubai for your child's education. Offering top-quality education and nurturing environment.", 'Best American Schools in Dubai If you chose the US educational system for your child and need to about the best American schools in Dubai yet, here is the optimum guide!', 'Dubai Schooling Guide: Expert Tips for Choosing the Perfect School Does choosing the best school in Dubai hard? Check this schooling guide with tips from experts that will help you find the perfect choice.']
                """
            },
            {
                "role": "system",
                "content": """
                {{
               "scores": [0.9, 0.7, 0.6, 0.1, 0.2, 0.4, 0.0, 0.1, 0.2, 0.3]
                }}
                
                """
            },
             {
                "role":"user",
                "content":f"""
                **source**:Hotel Guide – Royal Rose Hotel Abu Dhabi . Inspired by 17th Century French Castles, here's your guide to Royal Rose Abu Dhabi, a part of Hilton's Curio Collection. We share all the deets you need!'
                **top10**:['Explore the Best Abu Dhabi Hotels Looking for Abu Dhabi hotels to plan your next vacation? This guide will showcase some of the best hotels in Abu Dhabi with all their details.', 'Full Guide to Cheap Hotels in Abu Dhabi Looking for budget-friendly options? Discover the best cheap hotels in Abu Dhabi. Find the perfect place to stay in without breaking the bank.', 'Best Staycations in Abu Dhabi Experience luxury, relaxation, and unparalleled hospitality with our curated list of the best staycations in Abu Dhabi.', 'Cheap Hotel Apartments in Abu Dhabi Coming to the capital and searching for an affordable stay? Check here the best cheap hotel apartments in Abu Dhabi to enjoy on a budget.', 'Top 10 Summer Staycations in Abu Dhabi Enjoy summer staycations in Abu Dhabi in any of these amazing hotels that offer countless amenities and prioritise your comfort.', 'Places to Rent Luxury Apartments in Abu Dhabi Are you seeking luxury but not quite sure where to start in Abu Dhabi? Luxury doesn’t always mean a grand villa; you can go for a very elegant apartment', 'Emirates Palace Abu Dhabi – A Luxurious Stay & Experience Emirates Palace Abu Dhabi is a luxurious destination in the UAE’s capital. Learn all about Emirates Palace rooms and more amenities here.', 'Discover the Best Hotels in Reem Island Abu Dhabi Discover the hotels in Reem Island Abu Dhabi which offer great accommodation. Along with the best hotels near Reem Island in detail.', 'Dalma Island Abu Dhabi – A True Hidden Gem Discover the Dalma Island Abu Dhabi within this detailed guide, including both the amenities and attractions situated on the Island.', '20 Best Places to Visit in Abu Dhabi Explore the best places to visit in Abu Dhabi. Discover iconic landmarks, cultural treasures, and unforgettable experience']
                """
            },
            {
                "role": "system",
                "content": """
                {{
                 "scores": [0.9, 0.8, 0.7, 0.8, 0.7, 0.6, 1.0, 0.7, 0.5, 0.4]
}}
                
                """
            },
           
            {
                "role":"user",
                "content": "how you calculate the similarity of  **source**:Hotel Guide – Royal Rose Hotel Abu Dhabi . Inspired by 17th Century French Castles, here's your guide to Royal Rose Abu Dhabi, a part of Hilton's Curio Collection. We share all the deets you need!'"
            },
            {
                "role":"system",
                "content":"""
                Here’s a breakdown of the similarity scores between the source sentence about the Royal Rose Hotel Abu Dhabi and the top 10 sentences:

Explore the Best Abu Dhabi Hotels:
Relevance: High, focuses on hotels in Abu Dhabi but not focus on Royal Rose.
Score: 0.1
Full Guide to Cheap Hotels in Abu Dhabi:
Relevance: High, though focused on budget options but not focus on Royal Rose which is luxuary hotel in abu dhabi.
Score: 0.08
Best Staycations in Abu Dhabi:
Relevance: High, aligns well with hotel experiences and luxury but not focus on Royal Rose.
Score: 0.1
Cheap Hotel Apartments in Abu Dhabi:
Relevance: High, discusses affordable hotel options but not about Royal Rose specifically.
Score: 0.05
Top 10 Summer Staycations in Abu Dhabi:
Relevance: High, aligns with staycations and hotel experiences.
Score: 0.08
Places to Rent Luxury Apartments in Abu Dhabi:
Relevance: Moderate, talks about luxury accommodations but not hotels specifically.
Score: 0.06
Emirates Palace Abu Dhabi – A Luxurious Stay & Experience:
Relevance: not specifically about Royal rose but talking about hotels in abu dhabi.
Score: 0.12
Discover the Best Hotels in Reem Island Abu Dhabi:
Relevance: High, focuses on hotel accommodations in a specific area of Abu Dhabi which is different to Royal rose.
Score: 0.04
Dalma Island Abu Dhabi – A True Hidden Gem:
Relevance: Moderate, more focused on attractions than accommodations.
Score: 0.03
20 Best Places to Visit in Abu Dhabi:
Relevance: Low, more general tourist information.
Score: 0.1
These scores are based on how directly each of the top 10 texts relates to the specific focus of the source sentence on the Royal Rose Hotel in Abu Dhabi, factoring in both the context of luxury and hospitality services.
                """
            },
            {
                "role":"user",
                'content':"""
                Sure! Let me rephrase the prompt to be clearer:

You are comparing similarity scores between a source sentence and the top 10 comparison sentences. The source sentence provides detailed information about the Royal Rose Hotel in Abu Dhabi, highlighting its inspiration from 17th-century French castles and its affiliation with Hilton's Curio Collection. One of the top 10 comparison sentences is generally about the best hotels in Abu Dhabi but not specifically about the Royal Rose Hotel. 

The challenge is that the similarity score of 0.9 for these two sentences seems too high given that the comparison is general and the source is specific. You believe that for such cases, where the comparison lacks specific details found in the source, the similarity score should be less.

You want the similarity calculation to more accurately reflect the detail disparity between general and specific sentences, and adjust the scores accordingly. Could you help adjust the similarity score calculation to better differentiate between general and specific content matches?
                """
            },
             {
                 "role":"system",
                "content": """
                {{
                 "scores": [0.1, 0.08, 0.1, 0.05, 0.08, 0.06, 0.12, 0.04, 0.03, 0.1]
}}
                
                """
             },
             {
                "role":"user",
                "content":"that correct now and remember this each time you claculate similarity"  
            },
           
            {
                "role": "user",
               "content": f"""
    
    **source**: {data['source']}
    **Top10**: {data['top10']}    
     """




            }
        ],
        max_tokens=300,
        temperature=1.0,
    )

  return stream.choices[0].message.content

def extract_important_keywords(source, top10):
    top10_content = top10.tolist()

    data = {
        "source": source,
        "top10": top10_content
    }
    openai_response = openAiReq(data)
    print(openai_response)
    return openai_response
       

def adjust_similarity(keywords_and_scores, top_10_blogs):
    # Load the JSON string into a Python dictionary
    keywords_and_scores_dict = json.loads(keywords_and_scores)
    top10 = keywords_and_scores_dict['scores']

    adjustment_factor = 0.9  # Give 70% weight to keyword similarity

    # Ensure the 'semantic_similarity' column is of type float32
    top_10_blogs['semantic_similarity'] = top_10_blogs['semantic_similarity'].astype(np.float32)
    print(f"uniqueness isss before: {1 - top_10_blogs['semantic_similarity'].max()}")

    for i in range(len(top10)):
        try:
            print(f"sim of keywords{top10[i]} and simi of real{top_10_blogs.at[i, 'semantic_similarity']}")
            # Adjust similarity score
            top_10_blogs.at[i, 'semantic_similarity'] = (
                top_10_blogs.at[i, 'semantic_similarity'] * (1 - adjustment_factor)
            ) + (top10[i] * adjustment_factor)
            print(f"simi of real after{top_10_blogs.at[i, 'semantic_similarity']}")

        except KeyError as e:
            print(f"KeyError: {e} - Index {i} might be missing in the DataFrame.")
        except Exception as e:
            print(f"Exception occurred while adjusting similarity: {e}")

    print(f"uniqueness isss: {1 -top_10_blogs['semantic_similarity'].max()}")
    highest_sim_index = top_10_blogs['semantic_similarity'].idxmax()

    # Extract the title, uniqueness score, and link of the most similar blog
    title = top_10_blogs.at[highest_sim_index, 'Title']
    uniqueness = 1 - top_10_blogs.at[highest_sim_index, 'semantic_similarity']
    link = top_10_blogs.at[highest_sim_index, 'links']

    # Return the title, uniqueness, and link
    return title, uniqueness, link

def compare_files(file1, file2, json_path, csv_filename,compressed_gz_path):
    global progress
    progress = {"status": "In progress", "current": 0, "total": 0}

    try:
        # Read the CSV files
        df1 = pd.read_csv(file1, quotechar='"', skipinitialspace=True)
        df2 = pd.read_csv(file2, quotechar='"', skipinitialspace=True)

        # Combine Title and Meta Description into a single content column
        df1['combined_content'] = df1[['Title', 'Meta Description']].apply(lambda x: ' '.join(x.dropna()), axis=1).str.strip()
        df2['combined_content'] = df2[['Title', 'Meta Description']].apply(lambda x: ' '.join(x.dropna()), axis=1).str.strip()

        # Generate embeddings for each file's content
        embeddings_df1 = model.encode(df1['combined_content'].tolist(), convert_to_numpy=True)
        embeddings_df2 = model.encode(df2['combined_content'].tolist(), convert_to_numpy=True)
        print("Similarity calculation ongoing.........")
        similarities = cosine_similarity(embeddings_df1, embeddings_df2)
        print("Similarity calculation done.........")

        progress["total"] = len(df1)

        # Create the JSON and CSV files during processing
        with open(json_path, 'w', encoding='utf-8') as json_file, \
             open(f"uniqueFolder/{csv_filename}", 'w', newline='', encoding='utf-8') as csv_file:
            csv_writer = None

            for idx_i, sentence1 in enumerate(df1['combined_content']):
                similarity_scores = similarities[idx_i]
                top_n_indices = np.argsort(similarity_scores)[-10:][::-1]
                top10 = df2['combined_content'].iloc[top_n_indices]

                top_10_blogs = pd.DataFrame({
                    'content': top10,
                    'semantic_similarity': similarity_scores[top_n_indices],
                    'links': df2['Canonical Link'].iloc[top_n_indices],
                    'Title': df2['Title'].iloc[top_n_indices]
                }).reset_index(drop=True)

                keywords_and_scores = extract_important_keywords(sentence1, top10)
                title, uniqueness_score, link = adjust_similarity(keywords_and_scores, top_10_blogs)

                df1.loc[idx_i, 'uniqueness_score'] = uniqueness_score
                df1.loc[idx_i, 'heighest_Similar_links'] = link
                df1.loc[idx_i, 'heighest_Similar_title'] = title
                result_entry = df1.loc[idx_i].to_dict()

                json.dump(result_entry, json_file, ensure_ascii=False)
                json_file.write('\n')

                if csv_writer is None:
                    csv_writer = csv.DictWriter(csv_file, fieldnames=result_entry.keys())
                    csv_writer.writeheader()
                csv_writer.writerow(result_entry)

                progress["current"] = idx_i + 1

        progress["status"] = "Completed"
        requests.post(webhook_url, json={"complete": True, "json_filename": compressed_gz_path, "csv_filename": csv_filename})

    except Exception as e:
        print(e)
        progress["status"] = "Error"
        requests.post(webhook_url, json={"complete": False, "error": str(e), "json_filename": compressed_gz_path, "csv_filename": csv_filename})

 

@app.get("/{file1}/{file2}")
async def compare_endpoint(file1: str, file2: str, background_tasks: BackgroundTasks):
    file1_path = f"BlogsData/{file1}"
    file2_path = f"BlogsData/{file2}"

    if not os.path.exists(file1_path) or not os.path.exists(file2_path):
        raise HTTPException(status_code=404, detail="File not found")

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    json_filename = f"comparison_results_{timestamp}.json"
    csv_filename = f"comparison_results_{timestamp}.csv"
    json_path = f"uniqueFolder/{json_filename}"

    # Start the background task with all paths set up
    background_tasks.add_task(compare_files, file1_path, file2_path, json_path, csv_filename ,json_path)

    return {"json_filename": json_filename, "csv_filename": csv_filename}
@app.get("/progress")
async def get_progress():
    return progress