from bs4 import BeautifulSoup, Tag, NavigableString, Comment

# ---------------------------------------------------------------------
# Tailwind & Bootstrap class prefixes/lists
# ---------------------------------------------------------------------
TAILWIND_PREFIXES = [
    "bg-", "text-", "p-", "pt-", "pr-", "pb-", "pl-", "px-", "py-",
    "m-", "mt-", "mr-", "mb-", "ml-", "mx-", "my-", "flex", "items-",
    "justify-", "h-", "w-", "max-", "min-", "opacity-",
    # Add more as needed...
]

BOOTSTRAP_CLASSES = [
    "container", "row", "col", "btn", "btn-primary", "card", "d-flex",
    "align-items-", "justify-content-", "mx-", "my-", "px-", "py-",
    # Add more as needed...
]

# These tags will always be removed
FORBIDDEN_TAGS = {
    "nav", "header", "footer",   # from the previous requirement
    "style", "script",           # user asked to remove style/script
    "iframe", "embed", "img",    # newly requested
    "hr", "br"                   # newly requested
}

# ---------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------
def is_tailwind_or_bootstrap_class(cls_name: str) -> bool:
    """
    Returns True if `cls_name` is recognized as a Tailwind or Bootstrap class.
    We check both exact matches and prefix-based matches.
    """
    # Check against known Bootstrap classes/prefixes
    for b_class in BOOTSTRAP_CLASSES:
        # If b_class ends with a dash, treat it like a prefix
        if b_class.endswith("-"):
            if cls_name.startswith(b_class):
                return True
        else:
            if cls_name == b_class:
                return True

    # Check Tailwind prefixes
    for t_prefix in TAILWIND_PREFIXES:
        if cls_name.startswith(t_prefix):
            return True

    return False


def remove_disallowed_classes(element):
    """
    Removes all Tailwind/Bootstrap classes from element's class list.
    """
    if not element or not hasattr(element, 'attrs'):
        return
    if 'class' not in element.attrs:
        return

    filtered = [
        cls for cls in element['class']
        if not is_tailwind_or_bootstrap_class(cls)
    ]
    if filtered:
        element['class'] = filtered
    else:
        del element['class']


def is_heading_or_anchor(el):
    """
    Returns True if the element is an <h1>...<h6> or <a>.
    """
    if not el or not getattr(el, 'name', None):
        return False
    return el.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'a']


def is_relevant(element):
    """
    Determines if the current element is relevant:
      - It is itself a heading (<h1>-<h6>) or an anchor (<a>), OR
      - It has a descendant that is a heading or an anchor.
    """
    if is_heading_or_anchor(element):
        return True

    # Check if any descendant is relevant
    for child in element.children:
        if isinstance(child, Tag):
            if is_relevant(child):
                return True
    return False


def prune_dom(element):
    """
    Recursively prune the DOM:
      - Always remove elements in FORBIDDEN_TAGS.
      - Remove children that are not relevant (i.e., do not contain heading/link).
      - If, after pruning children, the current element is not relevant,
        return False so the caller can remove this element.
    """

    # If it's not a Tag (e.g. NavigableString, Comment), see if it's directly relevant
    if not isinstance(element, Tag):
        # Only relevant if it's an actual anchor (which can't be a NavigableString) or heading
        return False

    # If it's a forbidden tag, remove it
    if element.name in FORBIDDEN_TAGS:
        return False

    # Because element.children is a generator, make a list first
    children = list(element.children)
    for child in children:
        # If child is a Tag, recursively prune
        if isinstance(child, Tag):
            keep_child = prune_dom(child)
            if not keep_child:
                child.decompose()
        else:
            # For NavigableString, Comment, etc. -> remove if not relevant
            child.extract()

    # After dealing with children, check if current element is relevant
    return is_relevant(element)


def remove_unwanted_attributes(element):
    """
    Remove all attributes from the element except for 'class' and 'id'.
    Also remove Tailwind/Bootstrap classes from the 'class' attribute.
    """
    if not isinstance(element, Tag):
        return

    # Step 1: remove all attributes that are not 'class' or 'id'
    allowed_attrs = {}
    if 'class' in element.attrs:
        allowed_attrs['class'] = element['class']
    if 'id' in element.attrs:
        allowed_attrs['id'] = element['id']
    element.attrs = allowed_attrs

    # Step 2: remove any Tailwind/Bootstrap classes from 'class'
    remove_disallowed_classes(element)


# ---------------------------------------------------------------------
# Main Filter Function
# ---------------------------------------------------------------------
def html_filter_keep_headings_links(html_input: str) -> str:
    """
    1) Parse the HTML.
    2) Remove any elements that do not contain (or are) a heading or link.
       Also remove forbidden tags: nav, header, footer, style, script,
       iframe, embed, img, hr, br.
    3) Remove all attributes except class/id; also remove disallowed
       classes from the class attribute.
    4) Return the filtered HTML as a string.
    """

    if isinstance(html_input, str):
        soup = BeautifulSoup(html_input, "html.parser")
    else:
        # If it's already a BeautifulSoup object
        soup = html_input

    # If the input is a fragment, handle each top-level element in the soup.
    top_level_elements = list(soup.contents)

    # Prune top-level elements
    for el in top_level_elements:
        # If it's a Tag, prune it
        if isinstance(el, Tag):
            keep = prune_dom(el)
            if not keep:
                el.decompose()
        else:
            # NavigableString, Comment, etc. -> remove
            el.extract()

    # Now remove unwanted attributes from all remaining elements
    for el in soup.find_all():
        remove_unwanted_attributes(el)

    # Return the final cleaned-up HTML
    return str(soup)




def clean_navigation(html_input: str) -> str:
    # Example: If you want to remove certain classes (Tailwind/Bootstrap)
    TAILWIND_PREFIXES = [
        "bg-", "text-", "p-", "pt-", "pr-", "pb-", "pl-", "px-", "py-",
        "m-", "mt-", "mr-", "mb-", "ml-", "mx-", "my-", "flex", "items-",
        "justify-", "h-", "w-", "max-", "min-", "opacity-",
        # Add more as needed...
    ]

    BOOTSTRAP_CLASSES = [
        "container", "row", "col", "btn", "btn-primary", "card", "d-flex",
        "align-items-", "justify-content-", "mx-", "my-", "px-", "py-",
        # Add more as needed...
    ]

    def is_tailwind_or_bootstrap_class(cls_name: str) -> bool:
        """
        Returns True if `cls_name` is recognized as a Tailwind or Bootstrap class.
        We check both exact matches and prefix-based matches.
        """
        # Check against known Bootstrap classes/prefixes
        for b_class in BOOTSTRAP_CLASSES:
            # If b_class ends with a dash, treat it like a prefix
            if b_class.endswith("-"):
                if cls_name.startswith(b_class):
                    return True
            else:
                if cls_name == b_class:
                    return True

        # Check Tailwind prefixes
        for t_prefix in TAILWIND_PREFIXES:
            if cls_name.startswith(t_prefix):
                return True

        return False

    def remove_disallowed_classes(element):
        """
        Removes all Tailwind/Bootstrap classes from element's class list.
        Leaves 'id' and 'href' (and any other attributes) untouched (other
        than the broader attribute-cleaning performed separately).
        """
        if not element or not hasattr(element, 'attrs'):
            return

        if 'class' in element.attrs:
            filtered = [
                cls for cls in element['class']
                if not is_tailwind_or_bootstrap_class(cls)
            ]
            if filtered:
                element['class'] = filtered
            else:
                del element['class']

    def is_pagination_element(el):
        """
        Check if a Tag is one of:
          <a>,
          <button>,
          <input type="submit">.
        """
        if not el or not getattr(el, 'name', None):
            return False

        if el.name == 'a':
            return True

        if el.name == 'button':
            return True

        # Check for <input type="submit">
        if el.name == 'input' and el.has_attr('type'):
            if el['type'].lower() == 'submit':
                return True

        return False

    def is_relevant_for_pagination(element):
        """
        Returns True if the current element is relevant for pagination:
          - It IS a pagination element (a/button/input[submit]),
          - OR any of its descendants is a pagination element.
        """
        if is_pagination_element(element):
            return True

        for child in element.children:
            if isinstance(child, Tag):
                if is_relevant_for_pagination(child):
                    return True
        return False

    def prune_dom_for_pagination(element):
        """
        Recursively prune the DOM so that we only keep elements which
        contain or ARE a pagination element.
        
        - If a child is not relevant, we remove it.
        - If, after pruning children, the current element is not relevant,
          return False so the parent can remove it.
        """
        # If it's a NavigableString or Comment (not a Tag), keep it if parent is relevant
        if not isinstance(element, Tag):
            return True

        # Prune children first
        children = list(element.children)
        for child in children:
            if isinstance(child, Tag):
                keep_child = prune_dom_for_pagination(child)
                if not keep_child:
                    child.decompose()

        # After dealing with children, check if this element is relevant
        return is_relevant_for_pagination(element)

    def remove_unwanted_attributes(element):
        """
        Remove all attributes from the element except for:
          - If it's <button> or <input type="submit">, keep ALL attributes
            (but still filter out disallowed classes).
          - Else, keep 'class' (with disallowed classes removed),
            'id', 'href' (if <a>).
        """
        if not isinstance(element, Tag):
            return

        # Decide if we keep all attributes
        is_button = (element.name == 'button')
        is_input_submit = (element.name == 'input' and element.get('type', '').lower() == 'submit')

        if is_button or is_input_submit:
            # Keep ALL attributes for <button> or <input type="submit">
            # but still remove any disallowed classes from the 'class' attribute
            if 'class' in element.attrs:
                filtered = [
                    cls for cls in element['class']
                    if not is_tailwind_or_bootstrap_class(cls)
                ]
                if filtered:
                    element['class'] = filtered
                else:
                    del element['class']
        else:
            # Keep only class (filtered), id, and href (if <a>)
            allowed_attrs = {}

            # Keep 'class' if present (then filter out disallowed)
            if 'class' in element.attrs:
                allowed_attrs['class'] = element['class']

            # Keep 'id' if present
            if 'id' in element.attrs:
                allowed_attrs['id'] = element['id']

            # If it's an <a>, keep href
            if element.name == 'a' and element.has_attr('href'):
                allowed_attrs['href'] = element['href']

            # Overwrite the old attributes with the filtered set
            element.attrs = allowed_attrs

            # Remove disallowed classes from 'class'
            remove_disallowed_classes(element)

    # -------------------------------------------------------------------------
    # Main Logic
    # -------------------------------------------------------------------------
    if isinstance(html_input, str):
        soup = BeautifulSoup(html_input, "html.parser")
    else:
        soup = html_input

    # Prune top-level elements
    top_level_elements = list(soup.contents)
    for el in top_level_elements:
        if isinstance(el, Tag):
            keep = prune_dom_for_pagination(el)
            if not keep:
                el.decompose()
        else:
            # If it's text/comment at top level, remove it
            el.extract()

    # Remove unwanted attributes for all remaining elements
    for el in soup.find_all():
        remove_unwanted_attributes(el)

    # Return the final cleaned-up HTML
    return str(soup)
