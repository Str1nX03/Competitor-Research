import os
import io
import json
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import markdown
from xhtml2pdf import pisa
from tempfile import NamedTemporaryFile

# Import agents
from src.agents.assistant_agent import AssistantAgent
from src.agents.researcher_agent import ResearcherAgent
from src.agents.reporter_agent import ReporterAgent

app = FastAPI(title="Competitor Insights AI")

# Create necessary directories if they don't exist
os.makedirs("static/css", exist_ok=True)
os.makedirs("static/js", exist_ok=True)
os.makedirs("templates", exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")

class MarkdownRequest(BaseModel):
    markdown_text: str

@app.get("/", response_class=HTMLResponse)
async def landing_page(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/product", response_class=HTMLResponse)
async def product_page(request: Request):
    return templates.TemplateResponse(request=request, name="product.html")

@app.websocket("/ws/research")
async def websocket_research(websocket: WebSocket):
    await websocket.accept()
    try:
        # Receive the query from the client
        query = await websocket.receive_text()
        
        await websocket.send_json({
            "type": "status", 
            "message": "Assistant Agent is analyzing your query and gathering context..."
        })
        
        # We need to run synchronous LangGraph agents in a threadpool to not block the event loop
        # But for simplicity, if they aren't fully async, we can run them with asyncio.to_thread
        
        # Step 1: Assistant Agent
        assistant_agent = AssistantAgent()
        context = await asyncio.to_thread(assistant_agent.run, query)
        
        await websocket.send_json({
            "type": "status", 
            "message": "Assistant Agent finished. Researcher Agent is fetching real-time competitor data..."
        })
        
        # Step 2: Researcher Agent
        researcher_agent = ResearcherAgent()
        research_data = await asyncio.to_thread(researcher_agent.run, context)
        
        await websocket.send_json({
            "type": "status", 
            "message": "Researcher Agent finished. Reporter Agent is generating the final comprehensive report..."
        })
        
        # Step 3: Reporter Agent
        reporter_agent = ReporterAgent()
        reports = await asyncio.to_thread(reporter_agent.run, research_data)
        
        # ReporterAgent returns a list of strings (reports for each competitor)
        # We join them into a single markdown string
        final_report = "\n\n".join(reports)
        
        # Send completion with final markdown report
        await websocket.send_json({
            "type": "complete",
            "report": final_report
        })
        
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"Error during research pipeline: {e}")
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })

@app.post("/download-pdf")
async def download_pdf(request: MarkdownRequest):
    try:
        # Convert markdown to HTML
        # Enabling 'tables' and 'fenced_code' extensions for better formatting
        html_content = markdown.markdown(
            request.markdown_text, 
            extensions=['tables', 'fenced_code']
        )
        
        # Basic CSS for the PDF rendering to make tables and text look good
        pdf_css = """
        <style>
            @page {
                margin: 2cm;
                size: a4 portrait;
            }
            body {
                font-family: Helvetica, Arial, sans-serif;
                font-size: 12px;
                color: #333333;
                line-height: 1.5;
            }
            h1, h2, h3 {
                color: #111827;
                margin-top: 20px;
                margin-bottom: 10px;
            }
            h1 { font-size: 24px; border-bottom: 2px solid #e5e7eb; padding-bottom: 5px; }
            h2 { font-size: 20px; border-bottom: 1px solid #e5e7eb; padding-bottom: 3px; }
            h3 { font-size: 16px; }
            table {
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
            }
            th, td {
                border: 1px solid #d1d5db;
                padding: 8px;
                text-align: left;
                vertical-align: top;
            }
            th {
                background-color: #f3f4f6;
                font-weight: bold;
            }
            tr:nth-child(even) {
                background-color: #f9fafb;
            }
            p, ul, ol { margin-bottom: 15px; }
            code {
                background-color: #f3f4f6;
                padding: 2px 4px;
                border-radius: 3px;
                font-family: monospace;
            }
        </style>
        """
        
        full_html = f"<html><head>{pdf_css}</head><body>{html_content}</body></html>"
        
        # Use a temporary file to store the PDF
        temp_pdf = NamedTemporaryFile(delete=False, suffix=".pdf")
        
        # Create PDF using xhtml2pdf
        pisa_status = pisa.CreatePDF(
            io.StringIO(full_html),
            dest=temp_pdf
        )
        temp_pdf.close()
        
        if pisa_status.err:
            raise Exception("Failed to generate PDF")
            
        # Return as file response
        return FileResponse(
            path=temp_pdf.name,
            media_type='application/pdf',
            filename='competitor_research_report.pdf',
            background=None
        )
        
    except Exception as e:
        print(f"PDF generation error: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
