🕵️ AI Multi-Agent Scraper & Analyst
A full-stack web application that utilizes a squad of AI agents to scrape, analyze, and summarize web content. Instead of a basic summarizer, this app uses a multi-agent architecture where Agent A summarizes text, Agent B extracts key entities, and Agent C compiles everything into a beautifully formatted Markdown report.

🧠 How It Works
- Scrape Engine: Python's BeautifulSoup extracts raw text from the target URL.
- Agent A (Summarizer): Reads the text and generates a concise 3-sentence summary.
- Agent B (Extractor): Identifies and extracts key people, companies, and locations.
- Agent C (Writer): Takes the summary and entities and formats them into a clean, structured Markdown report.
- Frontend: A custom Tailwind CSS interface parses the Markdown in real-time for a seamless user experience.

🛠 Tech Stack
- Backend: Python, FastAPI, Uvicorn
- AI/LLM: Groq (Llama-3.1-8b-instant) via the OpenAI Python SDK
- Frontend: HTML, Tailwind CSS, Vanilla JS, Marked.js
- Architecture: Multi-Agent Orchestration, Asynchronous API
