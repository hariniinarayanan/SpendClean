import requests

def convert_currency(from_currency, to_currency, amount):
    # use for testing to avoid maxing api calls:
    # return amount 

    # free key
    api_key = "239d02e45417bf93b2f8fb06"
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/pair/{from_currency}/{to_currency}/{amount}"

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        if data.get("result") == "success":
            return data.get("conversion_result")  # Only return the converted value
        else:
            print("Conversion failed:", data.get("error-type"))
            return None
    except requests.exceptions.RequestException as e:
        print(f"API request error: {e}")
        return None
    except ValueError:
        print("Invalid response from API")
        return None


