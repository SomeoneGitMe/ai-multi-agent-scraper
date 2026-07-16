import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Point the OpenAI library to Groq
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

# --- Tool: Web Scraper ---
def scrape_website(url: str):
    print(f"🛠️  Scraping {url}...")
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.extract()
        text = soup.get_text(separator=' ', strip=True)
        # Truncate to 4000 chars to fit LLM context window
        return text[:4000]
    except Exception as e:
        return f"Failed to scrape: {e}"

# --- Agent A: Summarizer ---
def agent_a_summarizer(text: str):
    print("🤖 Agent A (Summarizer) is working...")
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are a fast summarizer. Read the text and provide a concise 3-sentence summary."},
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message.content

# --- Agent B: Entity Extractor ---
def agent_b_extractor(text: str):
    print("🤖 Agent B (Extractor) is working...")
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are a data extractor. Read the text and extract all key people, companies, and locations. Return them as a comma-separated list."},
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message.content

# --- Agent C: Report Writer ---
def agent_c_writer(summary: str, entities: str):
    print("🤖 Agent C (Writer) is compiling the final report...")
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are a technical writer. Take the summary and the extracted entities, and write a beautifully formatted Markdown report."},
            {"role": "user", "content": f"Summary: {summary}\n\nEntities: {entities}"}
        ]
    )
    return response.choices[0].message.content

# --- Main Orchestrator ---
def main():
    url = input("Enter a URL to analyze: ")
    
    # 1. Scrape
    raw_text = scrape_website(url)
    if "Failed" in raw_text:
        print(raw_text)
        return

    # 2. Run Agents in parallel conceptually (sequentially in code)
    summary = agent_a_summarizer(raw_text)
    entities = agent_b_extractor(raw_text)
    
    # 3. Compile Report
    final_report = agent_c_writer(summary, entities)
    
    print("\n" + "="*50)
    print("📊 FINAL MULTI-AGENT REPORT")
    print("="*50)
    print(final_report)

if __name__ == "__main__":
    main()