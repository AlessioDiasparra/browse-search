Perfetto! Dato che utilizzi un file locale `minigroqqle.py` per gestire le ricerche web, quando creerai la funzione Lambda, dovrai includere questo file nel pacchetto di distribuzione della Lambda, insieme a tutte le dipendenze necessarie (come `requests` e `beautifulsoup4`). AWS Lambda non ha accesso diretto a file locali, quindi dovrai pacchettare tutto correttamente.

Ecco i passaggi dettagliati per integrare la tua funzione Python in AWS Lambda:

### 1. Crea il pacchetto ZIP per Lambda:
- Poiché Lambda ha bisogno di tutte le dipendenze in un singolo pacchetto, segui questi passaggi per impacchettare `minigroqqle.py` e le librerie necessarie:

```bash
# Crea una directory per il pacchetto
mkdir lambda-package
cd lambda-package

# Copia il file minigroqqle.py
cp /path/to/your/local/minigroqqle.py .

# Installa le dipendenze in quella cartella
pip install requests beautifulsoup4 -t .

# Crea un file `lambda_function.py` con il codice per Lambda (vedi sotto)

# Comprimi tutto in un file zip
zip -r lambda-function.zip .
```

### 2. Codice per `lambda_function.py`:
Il file `lambda_function.py` userà la tua classe `MiniGroqqle` e la renderà disponibile tramite API Gateway.

```python
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
    # Recupera i parametri dall'evento API Gateway
    search_query = event.get("search_query", "")
    num_results = event.get("num_results", 10)
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
            "body": json.dumps(results)
        }
    else:
        return {
            "statusCode": 200,
            "body": json.dumps(print_results(results))
        }
```

### 3. Carica su AWS Lambda:
- Vai nella console AWS Lambda.
- Crea una nuova funzione Lambda.
- Carica il file `lambda-function.zip` creato nel passaggio precedente.
- Assicurati che il runtime sia impostato su Python 3.x.

### 4. Configura API Gateway:
- Crea una nuova API REST in API Gateway.
- Configura un endpoint `POST` per inviare i parametri `search_query` e `num_results`.
- Collega l'endpoint alla tua funzione Lambda.

### 5. Test:
Puoi testare l'API utilizzando il comando `curl` o Postman per inviare una richiesta con parametri, come:

```bash
curl -X POST "https://<api-endpoint>/search" \
     -H "Content-Type: application/json" \
     -d '{"search_query": "AWS Lambda", "num_results": 5, "json_output": true}'
```

Questo ti permetterà di eseguire la ricerca Google tramite API Gateway e Lambda.