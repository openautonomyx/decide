"""
Framework Demo UI
Simple demo interface for LangGraph import flow.
"""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/demo", tags=["demo"])

DEMO_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Decide Framework Demo</title>
    <style>
        * { box-sizing: border-box; }
        body { font-family: -apple-system,system-ui,sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; background: #f5f5f5; }
        h1 { color: #333; }
        h2 { color: #555; border-bottom: 2px solid #ddd; padding-bottom: 8px; }
        .card { background: white; padding: 20px; margin: 16px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        input, textarea { width: 100%; padding: 10px; margin: 8px 0; border: 1px solid #ddd; border-radius: 4px; font-family: monospace; }
        textarea { min-height: 200px; }
        button { background: #2563eb; color: white; padding: 12px 24px; border: none; border-radius: 4px; cursor: pointer; margin: 8px 8px 8px 0; }
        button:hover { background: #1d4ed8; }
        button.secondary { background: #64748b; }
        button.secondary:hover { background: #475569; }
        .result { background: #f8fafc; padding: 16px; border-radius: 4px; margin: 12px 0; white-space: pre-wrap; font-family: monospace; font-size: 13px; max-height: 400px; overflow: auto; }
        .error { background: #fef2f2; border: 1px solid #fecaca; color: #991b1b; }
        .success { background: #f0fdf4; border: 1px solid #bbf7d0; color: #166534; }
        .warning { background: #fffbeb; border: 1px solid #fed7aa; color: #9a3412; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .full { grid-column: 1 / -1; }
        label { font-weight: 600; color: #374151; }
        .badge { display: inline-block; background: #e0e7ff; color: #3730a3; padding: 2px 8px; border-radius: 4px; font-size: 12px; margin-right: 4px; }
    </style>
</head>
<body>
    <h1>🔧 Decide Framework Demo</h1>
    <p>Demo the LangGraph → LangFlow → Decide workflow import flow.</p>
    
    <div class="grid">
        <!-- LangGraph Input -->
        <div class="card">
            <h2>1. Paste LangGraph Definition</h2>
            <label>Tenant ID:</label>
            <input type="text" id="tenant_id" value="demo-tenant" placeholder="tenant-123">
            
            <label>LangGraph JSON:</label>
            <textarea id="langgraph_json" placeholder='{
  "name": "My Workflow",
  "description": "A test workflow",
  "nodes": [
    {"id": "start", "type": "start", "data": {}},
    {"id": "llm", "type": "llm", "data": {"model": "gpt-4"}},
    {"id": "end", "type": "end", "data": {}}
  ],
  "edges": [
    {"source": "start", "target": "llm"},
    {"source": "llm", "target": "end"}
  ]
}'></textarea>
            <button onclick="compileOnly()">🔄 Compile Only</button>
            <button onclick="importWorkflow()">📥 Compile + Import</button>
        </div>
        
        <!-- Results -->
        <div class="card">
            <h2>2. Compiler Results</h2>
            <div id="compile_result" class="result">Results will appear here...</div>
        </div>
        
        <!-- Workflow Actions -->
        <div class="card full">
            <h2>3. Workflow Actions</h2>
            <div id="workflow_actions">
                <p style="color: #666;">Import a workflow first to enable actions.</p>
            </div>
        </div>
        
        <!-- Roundtrip Export -->
        <div class="card full">
            <h2>4. Roundtrip Export</h2>
            <div id="roundtrip_result" class="result">Run roundtrip export after importing...</div>
        </div>
    </div>
    
    <script>
        let currentWorkflowId = null;
        
        async function compileOnly() {
            const tenantId = document.getElementById('tenant_id').value;
            const json = document.getElementById('langgraph_json').value;
            
            try {
                const graph = JSON.parse(json);
                const result = document.getElementById('compile_result');
                result.innerHTML = 'Compiling...';
                result.className = 'result';
                
                const resp = await fetch('/api/v1/frameworks/langgraph/compile-to-langflow', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(graph)
                });
                
                const data = await resp.json();
                result.innerHTML = JSON.stringify(data, null, 2);
                
                if (data.warnings && data.warnings.length > 0) {
                    result.className = 'result warning';
                } else {
                    result.className = 'result success';
                }
            } catch (e) {
                document.getElementById('compile_result').innerHTML = 'Error: ' + e.message;
                document.getElementById('compile_result').className = 'result error';
            }
        }
        
        async function importWorkflow() {
            const tenantId = document.getElementById('tenant_id').value;
            const json = document.getElementById('langgraph_json').value;
            
            try {
                const graph = JSON.parse(json);
                const result = document.getElementById('compile_result');
                result.innerHTML = 'Importing...';
                result.className = 'result';
                
                const resp = await fetch('/api/v1/frameworks/langgraph/import?tenant_id=' + encodeURIComponent(tenantId), {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(graph)
                });
                
                const data = await resp.json();
                result.innerHTML = JSON.stringify(data, null, 2);
                
                if (data.success) {
                    currentWorkflowId = data.workflow_id;
                    result.className = 'result success';
                    updateWorkflowActions(data.workflow_id);
                } else {
                    result.className = 'result error';
                }
            } catch (e) {
                document.getElementById('compile_result').innerHTML = 'Error: ' + e.message;
                document.getElementById('compile_result').className = 'result error';
            }
        }
        
        function updateWorkflowActions(wfId) {
            const div = document.getElementById('workflow_actions');
            div.innerHTML = `
                <p><strong>Workflow ID:</strong> ${wfId}</p>
                <button class="secondary" onclick="validateWorkflow()">✓ Validate</button>
                <button class="secondary" onclick="publishWorkflow()">📤 Publish</button>
                <button class="secondary" onclick="runWorkflow()">▶ Run</button>
                <button class="secondary" onclick="viewRoundtrip()">🔄 Roundtrip</button>
                <div id="workflow_result" class="result" style="margin-top:12px">Action results appear here...</div>
            `;
        }
        
        async function validateWorkflow() {
            if (!currentWorkflowId) return;
            try {
                const resp = await fetch('/api/v1/workflows/' + currentWorkflowId + '/validate');
                const data = await resp.json();
                document.getElementById('workflow_result').innerHTML = JSON.stringify(data, null, 2);
            } catch (e) {
                document.getElementById('workflow_result').innerHTML = 'Error: ' + e.message;
            }
        }
        
        async function publishWorkflow() {
            if (!currentWorkflowId) return;
            try {
                const resp = await fetch('/api/v1/workflows/' + currentWorkflowId + '/publish', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({})
                });
                const data = await resp.json();
                document.getElementById('workflow_result').innerHTML = JSON.stringify(data, null, 2);
            } catch (e) {
                document.getElementById('workflow_result').innerHTML = 'Error: ' + e.message;
            }
        }
        
        async function runWorkflow() {
            if (!currentWorkflowId) return;
            try {
                const resp = await fetch('/api/v1/workflows/' + currentWorkflowId + '/run', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({inputs: {}})
                });
                const data = await resp.json();
                document.getElementById('workflow_result').innerHTML = JSON.stringify(data, null, 2);
            } catch (e) {
                document.getElementById('workflow_result').innerHTML = 'Error: ' + e.message;
            }
        }
        
        async function viewRoundtrip() {
            if (!currentWorkflowId) return;
            try {
                const resp = await fetch('/api/v1/frameworks/roundtrip/' + currentWorkflowId);
                const data = await resp.json();
                document.getElementById('roundtrip_result').innerHTML = JSON.stringify(data, null, 2);
            } catch (e) {
                document.getElementById('roundtrip_result').innerHTML = 'Error: ' + e.message;
            }
        }
    </script>
</body>
</html>
"""


@router.get("/framework", response_class=HTMLResponse)
async def framework_demo():
    """Framework demo page."""
    return DEMO_HTML


@router.get("", response_class=HTMLResponse)
async def demo_index():
    """Redirect to framework demo."""
    return DEMO_HTML