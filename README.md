AI Collaboration Hub
AI Collaboration HubThis project is an advanced tool for collaboration with artificial intelligence, utilizing various language models (OpenAI, Anthropic, xAI) to handle tasks such as strategy design, code generation, quality control, and detailed analysis. The system is built on a FastAPI backend, Streamlit GUI, and Notion integration for storing results.
What We’ve Created

Multi-agent system: Four agents (Architect, Coder, Critic, GrokCoder) and one analytical agent (GrokAnalyst) collaborate on various tasks.
Supported models:
OpenAI GPT-4o for strategy development.
Anthropic Claude-3-5-Sonnet-20240620 for review and improvement.
xAI Grok-2 for humorous code generation.
xAI Grok-3-beta for advanced analysis.



Features:

Task processing (strategy, critique, grok_kód, grok_3_analysis).
Storage of results in a Notion database.
Robust processing with retries and extended timeouts for slow responses.

Technologies: Python, FastAPI, Streamlit, httpx, Notion API.

New Features in Version 2

Automated Agent Workflow: Enables task processing across multiple agents (Architect → GrokCoder → Critic) with results passed between them.
File Upload Support: The system automatically handles TXT, PDF, and image files.
Notion Storage with Conversation ID: Each task is now saved to the Notion database with a unique Conversation ID, simplifying conversation history tracking.
Improved Error Handling and Debugging: Added detailed logging of Notion API responses and robust error handling for better system reliability.
Timeout: The system handles slow responses (e.g., Grok-3-beta) with a 300-second timeout in the GUI and 300 seconds on the server.

How It Works
The system runs on a local server with FastAPI, which communicates with APIs of various models. Streamlit provides a simple graphical interface where you can input a task and select its type (strategy, critique, etc.). Results are stored in a Notion database for later review.
Installation

Clone the repository:
git clone https://github.com/VikitorFree/ai-collaboration-hub.git
cd ai-collaboration-hub


Create virtual environments:
python -m venv venv-agent
python -m venv venv-gui


Install dependencies:
.\venv-agent\Scripts\activate
pip install fastapi uvicorn httpx tenacity python-dotenv
.\venv-gui\Scripts\activate
pip install streamlit requests


Set up environment variables:Create a .env file in the root directory and add:
OPENAI_API_KEY=your_API_key
XAI_API_KEY=your_API_key
ANTHROPIC_API_KEY=your_API_key
NOTION_API_KEY=your_API_key
NOTION_DATABASE_ID=your_database_id


Run the server and GUI:FastAPI:
.\venv-agent\Scripts\activate
uvicorn main:app --reload

Streamlit:
.\venv-gui\Scripts\activate
streamlit run frontend/app.py



Usage

Open the Streamlit GUI in your browser (usually http://localhost:8501).
Select the task type (strategy, critique, grok_kód, grok_3_analysis).
Enter the task content (e.g., “Create 5 quiz questions”).
Click “Submit” and wait for the result.
Results are saved to the Notion database (check under the ID specified in .env).

Technical Details

Timeout: The system handles slow responses (e.g., Grok-3-beta) with a 120-second timeout in the GUI and 60 seconds on the server.
Retry: Automatic retries for network errors (3 attempts with a 2-second delay).
Logging: Errors and successes are recorded in router.log.

Contributions
The project is open to contributions! If you want to add new agents, models, or features, submit a pull request.Report issues on GitHub Issues.
License
MIT License – Ensure the license is included in the repository.
Happy coding, and best of luck with your AI hub!
