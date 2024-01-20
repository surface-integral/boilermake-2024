from openai import OpenAI
client = OpenAI(api_key="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")

# client.api_key = "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"

response = client.images.generate(
  model="dall-e-3",
  prompt="a white siamese cat",
  size="1024x1024",
  quality="standard",
  n=1,
)

image_url = response.data[0].url