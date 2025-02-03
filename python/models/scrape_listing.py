from bs4 import BeautifulSoup

def scrapecontent(body,parent, target):
    """
    Extracts content based on given CSS selectors.

    Returns:
    - On success: {'status': 'ok', 'code': 200, 'data': [{'url': ..., 'title': ...}, ...]}
    - On failure: {'status': 'error', 'code': <error_code>, 'message': <AI-friendly message>}
    """

    try:
        print(body," before")
   
        # Validate input types
        body = BeautifulSoup(body,'html.parser')
        print(body)
        if not isinstance(target, dict) or 'link_selector' not in target or 'title_selector' not in target:
            return {
                'status': 'error',
                'code': 401,
                'message': "The 'target' dictionary is missing required keys ('link_selector' or 'title_selector'). Ensure these fields exist and contain valid CSS selectors."
            }
        
        linkSelector = target.get('link_selector', '').strip()
        titleSelector = target.get('title_selector', '').strip()

        if not linkSelector or not titleSelector:
            return {
                'status': 'error',
                'code': 422,
                'message': "The provided selectors ('link_selector' or 'title_selector') are empty or invalid. Ensure they are correct and target valid elements in the HTML."
            }

        # Escape problematic class names
        # linkSelector = linkSelector.replace("space-y-1.5", "space-y-1\\.5")
        # titleSelector = titleSelector.replace("space-y-1.5", "space-y-1\\.5")

        # Find parent elements
        parents = body.select(parent)
        print(parents,"all parents")
        if not parents:
            return {
                'status': 'error',
                'code': 404,
                'message': f"No elements found for the article card selector '{parent}'. Ensure the selector is correct and target the article selector"
            }

        articles = []
        for idx, parent in enumerate(parents):
            try:
                link_element = parent.select_one(linkSelector)
                title_element = parent.select_one(titleSelector)

                url = link_element.get('href', 'No link found') if link_element else "No link found"
                title = title_element.get_text(strip=True) if title_element else "No title found"

                articles.append({'url': url, 'title': title})

            except AttributeError as e:
                return {
                    'status': 'error',
                    'code': 500,
                    'message': f"An error occurred while processing the parent element at index {idx}. This could be due to incorrect selectors or missing elements. Error details: {e}"
                }

        return {'status': 'ok', 'code': 200, 'data': articles}

    except Exception as e:
        return {
            'status': 'error',
            'code': 500,
            'message': f"An unexpected error occurred: {str(e)}. Ensure the HTML structure is correct, and selectors are valid."
        }
