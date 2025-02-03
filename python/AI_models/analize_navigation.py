import openai
import json
def openAiReqFindnavigation(prompt_additions=None):
  client = openai.Client(api_key='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')
  messages=[
         {
                "role":"system",
                "content": "I'm an expert web analyst. Analyze the provided HTML structure and identify the most reliable selectors for navigation to Next page."
            },
            
          
         {
                "role": "user",
               "content": """
Required Output Format:
You must return a JSON object with exactly three fields:
1. 'selector': The CSS or id that targets the navigation element for the next page.
2. 'clickable':\n
   - **0** if the navigation element uses a valid URL (e.g., <a href='https://example.com/page/2'>).\n
   - **1** if the navigation element does NOT use a valid URL (e.g., <a href='{javascript-content}:...'> or <button>).\n
   - **2** if the navigation does NOT availbale insted of providing useless selector return "2" and stop the process just return.\n
3. 'type': Either 'css' or 'id'.

Guidelines for selector identification:
1. Focus only on elements that are clearly for pagination or navigation, such as:
   - <a> tags with valid URLs for the next page (here, the 'clickable' field should be false).
   - <a> tags or <button> elements that use JavaScript or no valid URL (here, the 'clickable' field should be true).
2. Navigation elements are typically located at the bottom of an article listing container.

Important:
- The selector must strictly target only the next-page navigation element.\n
- the selector should be as simple as can\n
- Do not include explanations or extra fields in your response.\n
""",


            },
       
          {
                "role":"assistant",
                "content": "I Understood provide me html and i will return you the fields that will target only next-page navigation (url,button,or atag) and check if the url is valid url otherwise it will be clickable  and i will Ignore any additional content and return in expected json format"
            },
            
           
        ],
 
  if prompt_additions:
        messages.extend(prompt_additions)
        stream = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=messages,
        temperature=1.0,
    )

  return json.loads(stream.choices[0].message.content)

