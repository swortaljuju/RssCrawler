from urllib.parse import urlparse


def get_extractor(url, root_elem):
    return DefaultHtmlExtractor(url, root_elem)


class DefaultHtmlExtractor(object):
    ''' A class to extract content from html.

    Attributes
    ----------
    _url : str
        URL of the html doc.
    _root_elem : Element
        HTML doc root.
    _root_body_elem : Element
        HTML body element
    '''

    def __init__(self, url, root_elem):
        self._url = urlparse(url)
        self._root_elem = root_elem
        self._root_body_elem = root_elem.find('.//body')

    def extract_text(self):
        '''Extract meaningful text from HTML body.

        Right now we only extract text in <p> element because most meaningful texts are in
        this element.
        '''
        paragraphs = self._root_body_elem.findall(".//p")
        extracted_text = ''
        for p in paragraphs:
            extracted_text += p.text_content()
        return extracted_text

    def extract_same_origin_links(self):
        ''' Extract all links which have same origin as the current HTML's.'''
        return [{'url': link.get('href'), 'title': link.text_content()} for link in self._root_body_elem.findall(
            './/a') if urlparse(link.get('href')).hostname == self._url.hostname]

    def extract_title(self):
        ''' Extract HTML's title. '''
        return self._root_elem.find(".//head/title").text_content()
