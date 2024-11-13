import sys
import json
from minigroqqle import MiniGroqqle
import os

# Load environment variables
http_proxy_1 = os.environ.get('HTTP_PROXY_1')
http_proxy_2 = os.environ.get('HTTP_PROXY_2')

def print_results(results):
    """
    Prints the results of a search in a human-readable format.

    If the results are a string, it is assumed to be in JSON format.
    If the results are a list, it is assumed to contain dictionaries with keys
    'title', 'url', and 'description'.

    Args:
        results (str or list[dict]): The results to print.
    """
    if isinstance(results, str):
        # Results are in JSON format
        parsed_results = json.loads(results)
        if "error" in parsed_results:
            print(f"Error: {parsed_results['error']}")
        else:
            for i, result in enumerate(parsed_results, 1):
                print(f"Result {i}:")
                print(f"Title: {result['title']}")
                print(f"URL: {result['url']}")
                print(f"Description: {result['description']}")
                print("---")
    else:
        # Results are in list format
        if results and "error" in results[0]:
            print(f"Error: {results[0]['error']}")
        else:
            for i, result in enumerate(results, 1):
                print(f"Result {i}:")
                print(f"Title: {result['title']}")
                print(f"URL: {result['url']}")
                print(f"Description: {result['description']}")
                print("---")



def main():
    """
    Runs a search query on Google and prints the results to the console.

    The user can specify a search query as the first command-line argument.
    The user can also specify the "--json" flag to print the results in JSON
    format.

    If the user does not specify a search query, the program prints usage
    instructions and exits with a non-zero status code.

    Otherwise, the program prints the search results in the format specified
    by the user.
    """
    if len(sys.argv) < 2:
        print("Usage: python test.py <search query> [--json]")
        sys.exit(1)

    json_output = "--json" in sys.argv
    search_query = " ".join(arg for arg in sys.argv[1:] if arg != "--json")

    proxies = [
        {'http': http_proxy_1},
        {'http': http_proxy_2},
    ]

    searcher = MiniGroqqle(num_results=15, proxies=proxies)
    results = searcher.search(search_query, json_output=json_output)

    if json_output:
        print(results)  # Print raw JSON string
    else:
        print_results(results)

if __name__ == "__main__":
    main()
