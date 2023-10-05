
import openai
import os

import tiktoken
from llama_index.llms import AzureOpenAI
import numpy as np
from openai.embeddings_utils import get_embedding, cosine_similarity


openai.api_type = os.getenv("OPENAI_API_TYPE") or "azure"
openai.api_base = os.getenv("OPENAI_API_BASE") or "https://trimblehackathon2023.openai.azure.com/"
openai.api_version = os.getenv("OPENAI_VERSION") or "2023-07-01-preview"
openai.api_key = os.getenv("OPENAI_API_KEY") or "ef3be09daa914800ab7210a5c01256eb"
default_engine_name = os.getenv("OPENAI_ENGINE_NAME") or "gpt-35-turbo"
embedding_engine_name = os.getenv("OPENAI_EMBEDDING_ENGINE_NAME") or "text-embedding-ada-002"
azure_model_name = 'gpt-35-turbo-16k'

cost_dict ={
        "gpt-3.5-turbo-0613": 0.002,
        "gpt-3.5-turbo-16k-0613":0.002,
        "gpt-4-0314":0.03,
        "gpt-4-32k-0314":0.06,
        "gpt-4-0613":0.06,
        "gpt-4-32k-0613":0.12,
        "text-embedding-ada-002": 0.0001
        }

def get_azure_openai_defaults():
    deployment = default_engine_name
    endpoint = openai.api_base
    api_key = openai.api_key
    return deployment, api_key, endpoint

def fill_overrides(api_base, api_type, api_version):
    openai.api_type = api_type if api_version else openai.api_type
    openai.api_base = api_base if api_base else openai.api_base
    openai.api_version = api_version if api_version else openai.api_version


def chat_completion(messages, api_type=None, api_base=None, api_version=None, engine_name=default_engine_name,
                    stream=False,
                    temperature=0,
                    max_tokens=100,
                    top_p=0.95,
                    frequency_penalty=0,
                    presence_penalty=0,
                    stop=None):
    fill_overrides(api_base, api_type, api_version)
    return openai.ChatCompletion.create(
        engine=engine_name,
        messages=messages,
        stream=stream,
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
        stop=stop
    )


def imagine_image(user_prompt, size='1024x1024', n=1):
    response = openai.Image.create(
        prompt=user_prompt,
        size=size,
        n=n
    )
    image_url = response["data"][0]["url"]
    return image_url


def create_image_variants(image, size='1024x1024', n=1):
    response = openai.Image.create_variation(
        image=image,  # generated_image is the image generated above
        size=size,
        n=n,
        response_format="url",
    )
    image_url = response["data"][0]["url"]
    return image_url


def stream_completion(completion, message_placeholder):
    full_response = ""
    for response in completion:
        if len(response.choices) > 0:
            full_response += response.choices[0].delta.get("content", "")
            message_placeholder.markdown(full_response + "▌")
    message_placeholder.markdown(full_response)

def num_tokens_from_string(string: str, encoding_for_model: str = 'gpt-3.5-turbo') -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.encoding_for_model(encoding_for_model)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def num_tokens_from_messages(messages, model="gpt-3.5-turbo-16k-0613"):
    """Return the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")
    if model in {
        "gpt-3.5-turbo-0613",
        "gpt-3.5-turbo-16k-0613",
        "gpt-4-0314",
        "gpt-4-32k-0314",
        "gpt-4-0613",
        "gpt-4-32k-0613",
        }:
        tokens_per_message = 3
        tokens_per_name = 1
    elif model == "gpt-3.5-turbo-0301":
        tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
        tokens_per_name = -1  # if there's a name, the role is omitted
    elif "gpt-3.5-turbo" in model:
        print("Warning: gpt-3.5-turbo may update over time. Returning num tokens assuming gpt-3.5-turbo-0613.")
        return num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613")
    elif "gpt-4" in model:
        print("Warning: gpt-4 may update over time. Returning num tokens assuming gpt-4-0613.")
        return num_tokens_from_messages(messages, model="gpt-4-0613")
    else:
        raise NotImplementedError(
            f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."""
        )
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens


def render_completion(completion, message_placeholder):
    if len(completion.choices) > 0:
        message_placeholder.markdown(completion.choices[0].message.content)


def calculate_chat_cost(messages, model='gpt-3.5-turbo-16k-0613'):
    number_of_tokens = num_tokens_from_messages(messages)
    cost = cost_dict[model]*(number_of_tokens/1000)
    return cost

def calcualte_cost_string(string, model='gpt-3.5-turbo-16k-0613'):
    number_of_tokens = num_tokens_from_string(string)
    cost = cost_dict[model]*(number_of_tokens/1000)
    return cost

def get_llama_azure_openai_llm(temperature: float = 0.0,
        max_tokens = 1000):
    return AzureOpenAI(engine=default_engine_name, model="gpt-35-turbo-16k", temperature=0.0, max_tokens=max_tokens)


def get_embeddings_openai(content):
    return openai.Embedding.create(engine=embedding_engine_name, input=content)["data"][0]["embedding"]


def cosine_similarity_openai(vector1, vector2):
    # Calculate the cosine similarity
    similarity = cosine_similarity(vector1, vector2)

    return similarity


def get_random_image_prompt():
    messages = [{"role": "system",
                   "content": """You are an AI artist, give random image prompts. 
                   Give only one prompt. Be creative each time.
                   """},
                 ]
    completion = chat_completion(messages, max_tokens=200, stream=False, temperature=0.9)
    return completion.choices[0].message.content