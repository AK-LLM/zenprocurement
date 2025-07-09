import replicate
import os

def generate_image(prompt: str) -> str:
    """
    Generate an image based on the prompt using Replicate's Stable Diffusion model.
    Returns the URL of the generated image.
    """
    replicate_api_key = os.environ.get("REPLICATE_API_KEY")
    if not replicate_api_key:
        return "Replicate API key not set."

    client = replicate.Client(api_token=replicate_api_key)
    model = client.models.get("stability-ai/stable-diffusion")
    output = model.predict(prompt=prompt)
    return output[0]  # Returns the first generated image URL
