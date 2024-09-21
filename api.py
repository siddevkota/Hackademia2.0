from fastapi import FastAPI, Request
import openai
import PyPDF2 as pdf
import uvicorn
from mysite.views import percentage_score

app = FastAPI()

# Set up OpenAI API key
open.ai_api = "YOUR_API_KEY"

# Path to the static PDF file
PDF_FILE_PATH = "sample_removed.pdf"  # Set the path to your static PDF file

def get_openai_response(input_text, detailed=False):
    # Adjust the prompt based on whether the user requests detailed content or not
    messages = [
        {"role": "system", "content": "You are a study material generator. You are given a study material and asked to generate an easy to understand course content based on a specific topic. Just jump right into the topic and without any mention about the textbook. cover all of the points on the topic. MOST IMPORTANTLY do not forget to include '\n' at the end of every line break."},
        {"role": "user", "content": input_text}
    ]
    if detailed:
        messages.append({"role": "user", "content": "Please provide a detailed explanation."})
    else:
        messages.append({"role": "user", "content": "Please provide a concise summary."})
    
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",  # or use "gpt-4" if available
        messages=messages,
        max_tokens=1000 if detailed else 500,
        temperature=0.7
    )
    return response['choices'][0]['message']['content']

def input_pdf_text(file_path):
    with open(file_path, "rb") as f:
        reader = pdf.PdfReader(f)
        text = ""
        for page in range(len(reader.pages)):
            text += reader.pages[page].extract_text()
    return text

@app.post("/summarize_study_material")
async def summarize_study_material(request: Request):
    # Get the topic from the request body
    data = await request.json()
    topic = data.get('topic', 'general')

    # Read the static PDF file content
    pdf_content = input_pdf_text(PDF_FILE_PATH)
    
    # Define the prompt for summarizing the study material based on the selected topic
    input_prompt = f"The following text is from a study material which is as follows: {pdf_content}. The topic of interest is '{topic}'."
    
    # Get the summarized response from OpenAI
    summary = get_openai_response(input_prompt)
    
    # Return the summarized study material
    return {"summary": summary, "detailed_option": "If you want more details, click the 'Get Details' button."}

@app.post("/get_detailed_content")
async def get_detailed_content(request: Request):
    # Get the topic from the request body
    data = await request.json()
    topic = data.get('topic', 'general')

    # Read the static PDF file content
    pdf_content = input_pdf_text(PDF_FILE_PATH)
    
    # Define the prompt for detailed study material based on the selected topic
    input_prompt = f"explain {pdf_content} in more simple way. The topic of interest is '{topic}'."
    
    # Get the detailed response from OpenAI
    detailed_content = get_openai_response(input_prompt, detailed=True)
    
    # Return the detailed study material
    return {"detailed_content": detailed_content}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)
