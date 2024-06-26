import os

from flask import Flask
from openai import AzureOpenAI
from opentelemetry import trace

from monitor import count_completion_requests_and_tokens


# Initialize Flask app
app = Flask(__name__)

# Set OpenAI API key
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

# Monkey-patch the openai.Completion.create function
client.chat.completions.create = count_completion_requests_and_tokens(client.chat.completions.create)

tracer = trace.get_tracer("counter")


@app.route("/completion")
@tracer.start_as_current_span("completion")
def completion():
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": "How do I send my APM data to Elastic Observability?"}
        ],
        max_tokens=20,
        temperature=0
    )
    return(response.choices[0].message.content.strip())
