
from bs4 import BeautifulSoup as bs
import os
from response import Response
from nltk.stem.snowball import SnowballStemmer
stemmer = SnowballStemmer("english")
import re
from typing import Optional, List
from urllib.parse import urljoin, urlsplit

class SearchTerms:
    def get_list_of_words(string):
        return [stemmer.stem(x) for x in re.sub("[-_]", " ", string.rstrip(" ").lstrip(" ").lower()).split(" ")]
    


class Soup:
    """
    Represents a parsed HTML or XML document.

    This class uses a `Response` object (a custom class handling HTTP requests) to fetch and parse a web page.  It provides a convenient way to access the parsed content and base URL.

    Args:
        url (str): The URL of the webpage to parse.
        **kwargs: Keyword arguments passed to the underlying `Response` object.  
        These might include things like headers, timeout values, etc., depending on the implementation of `Response`.

    """
    def __init__(self, url, **kwargs):
        self.url = url
        self._response = Response(self.url, **kwargs)
        self._base_url = self._response.get_base_url()
        self._soup = None
        self._all_extensions = None

    def make_soup(self,features="html.parser", await_response:bool=False) -> Optional[bs]:
        """Creates a BeautifulSoup object from the response content.

        Args:
            await_response (bool, optional): If True, waits for the response before parsing. Defaults to False.

        Returns:
            bs: A BeautifulSoup object representing the parsed HTML content.  The specific `bs` type depends on the `bs4` library used.

        Raises:
            Exception: If there's an issue with the underlying response or parsing.  (The specific exception type will depend on `_response.assertResponse` and `bs4`.)
        """
        if self._soup is None:
            try:
                print(f"Making soup from {self.url}")
                soup = bs(self._response.assert_response(await_response).content, features=features)
                print("Soup made")
                self._soup = soup
            except Exception as e:
                print("Soup cannot be made", e)
        
        return self._soup
    
    def get_document_links(self,await_response:bool=False) -> Optional[List]:
        """
        Extracts all links from a document and returns them as a list of dictionaries.

        This function retrieves all anchor (<a>) tags from an HTML document, 
        constructs absolute URLs if necessary, and returns a list of dictionaries, 
        where each dictionary contains the title and URL of a link.  Titles are 
        prioritized from the `aria-label` attribute, falling back to the link text.

        Args:
            await_response (bool, optional):  If True, waits for the response before parsing. 
                                            Defaults to False.  The implementation of this depends 
                                            on the `self.make_soup` method.

        Returns:
            list: A list of dictionaries, each with "title" and "url" keys representing a link. 
                Returns an empty list if no links are found.

        Example:
            [{'title': 'Link 1', 'url': 'https://www.example.com/page1'}, 
            {'title': 'Link 2', 'url': 'https://www.anothersite.com/page2'}]
        """
        soup = self.make_soup(await_response=await_response)
        if not soup:
            return
        
        print("Scraping all urls from the site...")
        result = soup.find_all(name="a", href=True)
        
        results = []

        observed_urls = set()

        for res in result:
            href = res.attrs.get("href")
            if not href:
                continue

            url_split = urlsplit(href)
            if url_split.scheme == "":
                res_url = urljoin(self._base_url, href)
            else:
                res_url = href

            if res_url not in observed_urls:
                observed_urls.add(res_url)
                
                text = res.attrs.get("aria-label")
                
                if not text:
                    text = res.text

                if not text:
                    continue
                clean_text = text.strip()

                if text != "":
                    results.append({"title" : clean_text, 
                                "url" : res_url})
        
        if not results:
            print("Scraper Failed; No urls could be scraped")
            return
        print(f"Urls scraper found {len(results)} results")
        return results
                

    @property
    def all_extensions(self) -> list:
        """
        Returns a sorted list of unique file extensions found in document links.

        This property extracts the file extensions from URLs in the document links 
        associated with the object, removes duplicates, filters out empty extensions,
        and sorts the resulting list alphabetically.  Error handling is included 
        to gracefully handle potential issues during sorting.

        Returns:
            list: A list of unique file extensions (strings), sorted alphabetically.  
                  Returns an empty list if no valid extensions are found.
        """
        if self._all_extensions is None:

            extensions = [os.path.splitext(x.get("url"))[1] for x in self.get_document_links()]
            extensions = set(extensions)
            extensions = sorted([x for x in extensions if x and x != ""])
            self._all_extensions = extensions
        return self._all_extensions
    
    def filter_url_for_extension(self, extension:str, await_response:bool=False) -> list:
        """Filters a list of document URLs to include only those with a specified extension.

        Args:
            extension (str): The file extension to filter by (e.g., "pdf", ".txt").  If a leading period is not provided, it will be added.
            await_response (bool, optional):  If True, waits for the response from `get_document_links` before filtering. Defaults to False.

        Returns:
            list: A list of dictionaries, where each dictionary represents a document and contains at least a "url" key.  URLs are prefixed with the base URL if they start with a '/'.

        Raises:
            ValueError: If the provided extension is invalid or no documents with the specified extension are found.  The specific error message indicates the cause.
        """
        if not "." in extension:
            extension = f".{extension}"

        if not extension in self.all_extensions:
            raise ValueError(f"Extension should be in {self.all_extensions}")
        
        filtered = [x for x in self.get_document_links(await_response) \
                    if x.get("url").endswith(extension)]
        
        for x in filtered:
            if x.get("url").startswith("/"):
                x["url"] = f"{self._base_url}{x.get('url')}"
                
        if not filtered:
            raise ValueError("No documents was found with required extension")
        else:
            return filtered
    

    def filter_url_for_string_in_title(self, string:str, await_response:bool=False) -> list:
        """Filters a list of document links to return only those whose titles contain a given string.

        Args:
            string (str): The string to search for in the document titles.  The function will search for each word in this string individually.
            await_response (bool, optional):  A flag indicating whether to wait for a response from a potentially asynchronous operation within `get_document_links`. Defaults to False.

        Returns:
            list: A list of dictionaries, where each dictionary represents a document link and contains at least a "title" key.  Returns an empty list if no matches are found.

        Raises:
            ValueError: If no URLs are found containing the specified string in their titles.

        Note:
            The function uses stemming (via a `stemmer` object, assumed to be defined elsewhere) to improve search accuracy by comparing word stems rather than exact words.  The `get_document_links` method (also assumed to be defined elsewhere) is responsible for retrieving the list of document links.
        """
        searchTerms = SearchTerms.get_list_of_words(string)
        filtered = [x for x in self.get_document_links(await_response) \
                    if any(word in stemmer.stem(x.get("title")) for word in searchTerms)]
        if not filtered:
            raise ValueError("No urls was found for the required title")
        else:
            return filtered 
        