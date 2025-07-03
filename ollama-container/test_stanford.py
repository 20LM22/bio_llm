import requests, json
import os

print(os.environ['CUDA_VISIBLE_DEVICES'])
# print(os.environ['NVIDIA_VISIBLE_DEVICES'])
# print(os.environ['NVIDIA_REQUIRE_CUDA'])

ollama_url = "http://127.0.0.1:39404"

try:
    r = requests.get(ollama_url)
    r.raise_for_status()
    print("✅ Success:", r.text)
except requests.exceptions.RequestException as e:
    print("❌ Failed to connect:", e)

LLM_API_URL = f"{ollama_url}/api/chat"  # Could also be /api/generate
payload = {
    "model": "deepseek-r1:1.5b",
    "prompt": (
        "What color is the sky?"
    ),
    "keep_alive": -1  # Keeps model loaded after request
}
headers = {"Content-Type": "application/json"}

# Send POST request
response = requests.post(LLM_API_URL, headers=headers, data=json.dumps(payload))
# Assuming the API returns a JSON response, print the result.
data = response.json()
print(data['message']['content'])

# Ollama is running successfully

# import argparse
# import requests

# def main():
#     # Set up argument parsing.
#     parser = argparse.ArgumentParser(
#         description="Send a request to an Ollama API endpoint on a given node hostname and port."
#     )
#     parser.add_argument("--host", type=str, help="The hostname of the server's GPU node)")
#     parser.add_argument("--port", type=str, default="11434", help="The port number for the API (default: 11434)")
    
#     args = parser.parse_args()
    
#     # Construct the URL using the provided hostname and port.
#     hostname = "n0229.savio2"
#     portname = "49376"

#     url = f"http://{hostname}:{portname}/api/generate" # f"http://{args.host}:{args.port}/api/generate"
#     print(f"Sending request to URL: {url}")
    
#     payload = {
#         "model": "deepseek-r1:7b",
#         "prompt": (
#             "With the upcoming 100-year celebration this fall, how do you envision Stanford GSB using "
#             "this milestone to inspire the next generation of business leaders? Identify two specific "
#             "initiatives or themes that should be highlighted during the celebration, and discuss how "
#             "these can both honor the school’s century-long legacy and shape innovative approaches to business "
#             "education going forward. Provide examples to support your recommendations."
#         ),
#         "stream": False  # Disable streaming to get one complete response
#     }
#     headers = {"Content-Type": "application/json"}
    
#     try:
#         # Make the POST request.
#         response = requests.post(url, json=payload, headers=headers)
#         response.raise_for_status()
#         # Assuming the API returns a JSON response, print the result.
#         data = response.json()
#         print(data['response'])
#     except requests.exceptions.RequestException as e:
#         print(f"An error occurred: {e}")

# if __name__ == '__main__':
#     main()