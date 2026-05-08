import requests

APP_URL = "https://app7py-4q95yycvpvnw7ij7hifjyu.streamlit.app/" # Change this to your URL

def ping_app():
    try:
        response = requests.get(APP_URL, timeout=15)
        print(f"Status Code: {response.status_code}")
    except Exception as e:
        print(f"Failed to ping: {e}")

if __name__ == "__main__":
    ping_app()
