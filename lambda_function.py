import json
from minigroqqle import MiniGroqqle

def print_results(results):
    if isinstance(results, str):
        parsed_results = json.loads(results)
        if "error" in parsed_results:
            return {"error": parsed_results["error"]}
        else:
            return parsed_results
    else:
        if results and "error" in results[0]:
            return {"error": results[0]["error"]}
        else:
            return results

def lambda_handler(event, context):
    # Recupera i parametri dall'evento
    search_query = event.get("search_query", "")
    num_results = event.get("num_results", 50)
    json_output = event.get("json_output", False)

    if not search_query:
        return {
            "statusCode": 400,
            "body": json.dumps("Missing search query")
        }

    # Crea un'istanza di MiniGroqqle
    searcher = MiniGroqqle(num_results=num_results)
    results = searcher.search(search_query, json_output=json_output)

    if json_output:
        return {
            "statusCode": 200,
            "body": json.dumps(results)  # Output JSON
        }
    else:
        return {
            "statusCode": 200,
            "body": json.dumps(print_results(results))
        }
