from pydantic import BaseModel
from openai import OpenAI

class People(BaseModel):
    name: str
    age: int

client = OpenAI(base_url="http://localhost:8000/v1", api_key="")

completion = client.chat.completions.create(
    model='deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B',
    messages=[
        {
            "role": "user",
            "content": "Generate a JSON with name and age of a random person."
        }
    ],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "people",
            "schema": People.model_json_schema()
        }
    }
)

print(completion)
