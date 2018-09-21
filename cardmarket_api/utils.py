from lxml import etree


def dict_to_xml(tree, d):
    """Recursive function to transform dict into XML tree
       Need a pre-exising tree to be attached to it"""

    element = None

    for key, value in d.items():
        if isinstance(value, list):
            for v in value:
                element = etree.SubElement(tree, key)
                dict_to_xml(element, v)
        elif isinstance(value, dict):
            element = etree.SubElement(tree, key)
            dict_to_xml(element, value)
        else:
            element = etree.SubElement(tree, key)
            if value is not None:
                element.text = str(value)

    return element
