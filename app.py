import os
import io
import json
import sqlite3
from flask import Flask, render_template, request, send_file, jsonify
from flask_sock import Sock
import markdown
from xhtml2pdf import pisa
from tempfile import NamedTemporaryFile

# Import agents
from src.agents.assistant_agent import AssistantAgent
from src.agents.researcher_agent import ResearcherAgent
from src.agents.reporter_agent import ReporterAgent

app = Flask(__name__)
sock = Sock(app)

def init_db():
    conn = sqlite3.connect('reports.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT NOT NULL,
            report_markdown TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def landing_page():
    return render_template('index.html')

@app.route('/product')
def product_page():
    return render_template('product.html')

@sock.route('/ws/research')
def websocket_research(ws):
    query = ws.receive()
    if not query:
        return
        
    try:
        ws.send(json.dumps({
            "type": "status", 
            "message": "Assistant Agent is analyzing your query and gathering context..."
        }))
        
        # Step 1: Assistant Agent
        assistant_agent = AssistantAgent()
        context = assistant_agent.run(query)
        
        ws.send(json.dumps({
            "type": "status", 
            "message": "Assistant Agent finished. Researcher Agent is fetching real-time competitor data..."
        }))
        
        # Step 2: Researcher Agent
        researcher_agent = ResearcherAgent()
        research_data = researcher_agent.run(context)
        
        ws.send(json.dumps({
            "type": "status", 
            "message": "Researcher Agent finished. Reporter Agent is generating the final comprehensive report..."
        }))
        
        # Step 3: Reporter Agent
        reporter_agent = ReporterAgent()
        reports = reporter_agent.run(research_data)
        
        # ReporterAgent returns a list of strings (reports for each competitor)
        # We join them into a single markdown string
        final_report = "\n\n".join(reports)
        
        # Save to database
        conn = sqlite3.connect('reports.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO reports (query, report_markdown) VALUES (?, ?)', (query, final_report))
        report_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Send completion with final markdown report
        ws.send(json.dumps({
            "type": "complete",
            "report": final_report,
            "id": report_id
        }))
        
    except Exception as e:
        print(f"Error during research pipeline: {e}")
        ws.send(json.dumps({
            "type": "error",
            "message": str(e)
        }))

@app.route('/api/reports')
def get_reports():
    conn = sqlite3.connect('reports.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT id, query, created_at FROM reports ORDER BY created_at DESC')
    reports = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(reports)

@app.route('/api/reports/<int:report_id>')
def get_report(report_id):
    conn = sqlite3.connect('reports.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT id, query, report_markdown, created_at FROM reports WHERE id = ?', (report_id,))
    report = cursor.fetchone()
    conn.close()
    if report:
        return jsonify(dict(report))
    return jsonify({"error": "Report not found"}), 404

@app.route('/download-pdf', methods=['POST'])
def download_pdf():
    try:
        data = request.json
        if not data or 'markdown_text' not in data:
            return jsonify({"error": "No markdown_text provided"}), 400
            
        markdown_text = data['markdown_text']
        
        # Convert markdown to HTML
        # Enabling 'tables' and 'fenced_code' extensions for better formatting
        html_content = markdown.markdown(
            markdown_text, 
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
        return send_file(
            temp_pdf.name,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='competitor_research_report.pdf'
        )
        
    except Exception as e:
        print(f"PDF generation error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=8000)
