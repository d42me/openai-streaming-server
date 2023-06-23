import uvicorn
from starlette.applications import Starlette
from starlette.routing import Route
from sse_starlette.sse import EventSourceResponse
import openai
import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

openai.api_key = os.environ.get("OPENAI_API_KEY")

system_prompt: str = "You are a helpful, creative, clever, and very friendly assistant and answer all questions of the visionOS user.",

async def requestOpenAICompletion(prompt):
    messages = [
        {"role": "system", "content": f"{system_prompt}"},
        {"role": "user", "content": prompt},
    ]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.5,
        max_tokens=1000,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0.1,
        stream=True
    )

    for chunk in response:
        print(chunk)
        chunk_message = chunk['choices'][0]['delta'] 

        if "content" in chunk_message:
            yield f"data: {chunk_message['content']}\n\n"

async def sse(request):
    query_param = request.query_params.get("q", "What can you do for me?")
    generator = requestOpenAICompletion(query_param)
    return EventSourceResponse(generator)

routes = [
    Route("/", endpoint=sse)
]

app = Starlette(debug=True, routes=routes)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level='info')
