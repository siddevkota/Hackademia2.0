import mysite.utils as utils
from django.conf import settings

def generate_openai_response(prompt):
    utils.api_key = settings.OPENAI_API_KEY

    try:
        response = utils.Completion.create(
            engine="text-davinci-003",  # You can use different models such as GPT-4 if available.
            prompt=prompt,
            max_tokens=150,
            n=1,
            stop=None,
            temperature=0.7
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return f"Error generating response: {str(e)}"
