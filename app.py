import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

app = FastAPI(title="AI Multi-Agent Scraper")

# --- The Agents ---
def scrape_website(url: str):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        for script in soup(["script", "style"]):
            script.extract()
        text = soup.get_text(separator=' ', strip=True)
        return text[:4000]
    except Exception as e:
        return f"Failed to scrape: {e}"

def agent_a_summarizer(text: str):
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are a fast summarizer. Read the text and provide a concise 3-sentence summary."},
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message.content

def agent_b_extractor(text: str):
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are a data extractor. Read the text and extract all key people, companies, and locations. Return them as a comma-separated list."},
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message.content

def agent_c_writer(summary: str, entities: str):
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are a technical writer. Take the summary and the extracted entities, and write a beautifully formatted Markdown report. You MUST use '## ' for main section headings and '### ' for subheadings. Put exactly two line breaks between every section and paragraph so there is clear visual separation. Use bullet points for lists."},
            {"role": "user", "content": f"Summary: {summary}\n\nEntities: {entities}"}
        ]
    )
    return response.choices[0].message.content

# --- API Endpoint ---
class ScrapeRequest(BaseModel):
    url: str

@app.post("/api/scrape")
async def run_agents(request: ScrapeRequest):
    try:
        raw_text = scrape_website(request.url)
        if "Failed" in raw_text:
            return {"error": raw_text}
        
        summary = agent_a_summarizer(raw_text)
        entities = agent_b_extractor(raw_text)
        final_report = agent_c_writer(summary, entities)
        
        return {"report": final_report}
    except Exception as e:
        return {"error": str(e)}

# --- Modern HTML Frontend ---
@app.get("/", response_class=HTMLResponse)
async def get_ui():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Multi-Agent Scraper</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
        <style>
            body { font-family: 'Inter', sans-serif; }
            #resultDiv::-webkit-scrollbar { width: 8px; }
            #resultDiv::-webkit-scrollbar-track { background: #374151; border-radius: 10px; }
            #resultDiv::-webkit-scrollbar-thumb { background: #6366f1; border-radius: 10px; }
            
            /* Bulletproof CSS for the Markdown Render */
            #resultDiv h2 { 
                color: #a5b4fc; 
                font-size: 1.5rem; 
                font-weight: 700; 
                margin-top: 2.5rem; 
                margin-bottom: 1rem; 
                padding-bottom: 0.5rem; 
                border-bottom: 1px solid #4b5563; 
            }
            #resultDiv h3 { 
                color: #c7d2fe; 
                font-size: 1.25rem; 
                font-weight: 700; 
                margin-top: 1.5rem; 
                margin-bottom: 1rem; 
            }
            #resultDiv p { 
                color: #d1d5db; 
                line-height: 1.7; 
                margin-bottom: 1.5rem; 
            }
            #resultDiv ul { 
                list-style-type: disc; 
                padding-left: 2rem; 
                margin-bottom: 1.5rem; 
            }
            #resultDiv li { 
                color: #d1d5db; 
                margin-bottom: 0.75rem; 
                line-height: 1.5; 
            }
            #resultDiv strong { 
                color: #ffffff; 
                font-weight: 600; 
            }
        </style>
    </head>
    <body class="bg-gray-900 text-white flex items-center justify-center min-h-screen p-4">
        <!-- Widened the container to max-w-4xl -->
        <div class="w-full max-w-4xl">
            <div class="bg-gray-800 p-8 rounded-2xl shadow-xl border border-gray-700">
                <h1 class="text-3xl font-bold text-center mb-2 text-indigo-400">AI Multi-Agent Scraper</h1>
                <p class="text-center text-gray-400 mb-6">Enter a URL to let the AI agents scrape, extract, and summarize.</p>
                
                <div class="flex gap-2 mb-6">
                    <input id="urlInput" type="text" placeholder="https://example.com/article" class="flex-1 bg-gray-700 text-white px-4 py-3 rounded-xl outline-none focus:ring-2 focus:ring-indigo-500">
                    <button id="scrapeBtn" class="bg-indigo-600 hover:bg-indigo-700 px-6 py-3 rounded-xl font-semibold transition">Analyze</button>
                </div>

                <div id="loading" class="hidden text-center py-10">
                    <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-indigo-400 mx-auto mb-3"></div>
                    <p class="text-gray-400">Agents are working...</p>
                </div>

                <!-- Removed prose classes, added custom padding -->
                <div id="resultDiv" class="hidden bg-gray-700 p-8 rounded-xl max-h-[600px] overflow-y-auto"></div>
            </div>
        </div>

        <script>
            const btn = document.getElementById('scrapeBtn');
            const input = document.getElementById('urlInput');
            const loading = document.getElementById('loading');
            const resultDiv = document.getElementById('resultDiv');

            btn.addEventListener('click', async () => {
                const url = input.value;
                if(!url) return alert('Please enter a URL');

                btn.disabled = true;
                btn.innerText = 'Working...';
                loading.classList.remove('hidden');
                resultDiv.classList.add('hidden');

                try {
                    const response = await fetch('/api/scrape', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({url: url})
                    });
                    const data = await response.json();

                    loading.classList.add('hidden');
                    btn.disabled = false;
                    btn.innerText = 'Analyze';

                    if(data.error) {
                        resultDiv.innerHTML = `<p class="text-red-400">${data.error}</p>`;
                    } else {
                        resultDiv.innerHTML = marked.parse(data.report);
                    }
                    resultDiv.classList.remove('hidden');
                } catch (err) {
                    loading.classList.add('hidden');
                    btn.disabled = false;
                    btn.innerText = 'Analyze';
                    alert('An error occurred. Check the console.');
                }
            });
        </script>
    </body>
    </html>
    """