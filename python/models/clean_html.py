from bs4 import BeautifulSoup

def clean_html(html_content, remove_empty_space=False , isSoup=False):
    if(isSoup):
        soup = html_content
    else:    
     soup = BeautifulSoup(html_content, 'html.parser')

    # List of common classes used in headers and footers
    common_classes = [
        'header', 'page-header', 'main-header', 'footer', 'page-footer', 'main-footer', 
        'navbar', 'footer-nav', 'navbar-nav', 'nav', 
        'site-header','site_header', 'site-footer', 
        'sh-header', 'sh-footer', 
        'tw-header', 'tw-footer', 
        'chakra-header', 'chakra-footer', 
        'mat-toolbar', 'mat-footer'
    ]

    # Remove script and style tags
    for script in soup(["script", "style"]):
        script.decompose()

    # Print initial state for debugging
    print("Initial body length:", len(str(soup.body)))

    # Remove elements with common header and footer classes
    for class_name in common_classes:
        for elem in soup.find_all(class_=lambda value: value and class_name in value.split()):
            elem.decompose()

    # Print state after cleaning for debugging
    print("Post-cleanup body length:", len(str(soup.body)))

    # Optionally remove empty spaces
    if remove_empty_space:
        cleaned_html = ''.join(str(soup).split())
        print("Final cleaned body length:", len(cleaned_html))
        return cleaned_html
    else:
        return str(soup)
