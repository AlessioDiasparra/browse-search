import requests
import json
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Union
from urllib.parse import quote_plus
import asyncio
import aiohttp # type: ignore
import charset_normalizer

async def scrape_website_async(session, url):
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            # Detect the encoding of the response
            raw_content = await response.read()
            detected_encoding = charset_normalizer.detect(raw_content)['encoding']
            html = raw_content.decode(detected_encoding)
            soup = BeautifulSoup(html, 'html.parser')

            article_title = soup.title.get_text(separator='\n', strip=True) if soup.title else "No title found."

            main_content_tags = ['div', 'article', 'section', 'main']
            main_content_classes = ['entry-content', 'content', 'main-content', 'post-content', 'article-content']

            main_content = None
            for tag in main_content_tags:
                for cls in main_content_classes:
                    content = soup.find(tag, class_=cls)
                    if content:
                        main_content = content.get_text(separator='\n', strip=True)
                        break
                if main_content:
                    break

            if not main_content:
                paragraphs = soup.find_all('p')
                main_content = "\n".join([p.get_text(separator='\n', strip=True) for p in paragraphs])

            return {
                'article_title': article_title,
                'main_content': main_content
            }

    except aiohttp.ClientResponseError as e:
        return {
            'article_title': f"An error occurred: {e}",
            'main_content': f"An error occurred: {e}"
        }

class MiniGroqqle:
    def __init__(self, num_results: int = 10, proxies: List[Dict[str, str]] = None):
        self.num_results = num_results
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }
        self.proxies = proxies

    async def search_async(self, query: str, json_output: bool = False) -> Union[List[Dict[str, Any]], str]:
        encoded_query = quote_plus(query)
        search_url = f"https://www.google.com/search?q={encoded_query}&num={self.num_results * 2}"
        
        async with aiohttp.ClientSession(headers=self.headers) as session:
            try:
                async with session.get(search_url, timeout=20) as response:
                    response.raise_for_status()
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    search_results = []
                    tasks = []
                    for position, g in enumerate(soup.find_all('div', class_='g'), start=1):
                        anchor = g.find('a')
                        title = g.find('h3').text if g.find('h3') else 'No title'
                        url = anchor.get('href', '') if anchor else ''
                        
                        description = ''
                        description_div = g.find('div', class_=['VwiC3b', 'yXK7lf'])
                        if description_div:
                            description = description_div.get_text(strip=True)
                        else:
                            description = g.get_text(strip=True)
                        
                        if url.startswith('http'):
                            domain = url.split('/')[2]
                            source = domain.split('.')[-2] + '.' + domain.split('.')[-1]
                            link_displayed = url
                            snippet_highlighted_words = [word for word in query.split() if word in description]
                            tasks.append(scrape_website_async(session, url))
                            search_results.append({
                                'position': position,
                                'title': title,
                                'link': url,
                                'source': source,
                                'domain': domain,
                                'link_displayed': link_displayed,
                                'snippet': description,
                                'snippet_highlighted_words': snippet_highlighted_words,
                                'article_title': None,
                                'main_content': None
                            })
                    
                    contents = await asyncio.gather(*tasks)
                    for result, content in zip(search_results, contents):
                        result['article_title'] = content['article_title']
                        result['main_content'] = content['main_content']
                    
                    results = search_results[:self.num_results]
                    
                    if json_output:
                        return json.dumps(results, indent=2)
                    else:
                        return results
            except aiohttp.ClientResponseError as e:
                error_message = f"Error performing search: {str(e)}"
                if json_output:
                    return json.dumps({"error": error_message})
                else:
                    return [{"error": error_message}]

    def search(self, query: str, json_output: bool = False) -> Union[List[Dict[str, Any]], str]:
        return asyncio.run(self.search_async(query, json_output))

# Example usage
if __name__ == "__main__":
    searcher = MiniGroqqle(num_results=5)
    results = searcher.search("Python programming")
    for result in results:
        print(f"Position: {result['position']}")
        print(f"Title: {result['title']}")
        print(f"Link: {result['link']}")
        print(f"Source: {result['source']}")
        print(f"Domain: {result['domain']}")
        print(f"Link Displayed: {result['link_displayed']}")
        print(f"Snippet: {result['snippet']}")
        print(f"Snippet Highlighted Words: {result['snippet_highlighted_words']}")
        print("---")
