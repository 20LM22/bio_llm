import re

regex = r'\*\*.*\*\*' # for matching the STL statement in the response returned by the LLM
response = "**test test**"
extracted_response = re.search(regex, response)
print(extracted_response.group(0))
print(type(extracted_response))


