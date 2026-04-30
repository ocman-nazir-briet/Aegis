import * as vscode from 'vscode';
import { SimulationResult } from './aegisClient';

export class AegisSidebarProvider implements vscode.WebviewViewProvider {
  public static readonly viewType = 'aegis.sidebar';
  private webviewView?: vscode.WebviewView;

  constructor(private context: vscode.ExtensionContext) {}

  resolveWebviewView(
    webviewView: vscode.WebviewView,
    _context: vscode.WebviewViewResolveContext,
    _token: vscode.CancellationToken
  ): void | Thenable<void> {
    this.webviewView = webviewView;

    webviewView.webview.options = {
      enableScripts: true,
      localResourceRoots: [this.context.extensionUri],
    };

    webviewView.webview.html = this.getHtml();

    webviewView.webview.onDidReceiveMessage((data) => {
      console.log('Sidebar message:', data);
    });
  }

  updateResult(result: SimulationResult): void {
    if (this.webviewView) {
      this.webviewView.webview.postMessage({
        type: 'update',
        data: result,
      });
    }
  }

  private getHtml(): string {
    return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Aegis Risk Analysis</title>
  <style>
    body {
      margin: 0;
      padding: 12px;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: var(--vscode-editor-background);
      color: var(--vscode-editor-foreground);
      font-size: 12px;
    }
    .container { padding: 8px 0; }
    .section { margin-bottom: 16px; }
    .label {
      font-size: 11px;
      color: var(--vscode-descriptionForeground);
      text-transform: uppercase;
      margin-bottom: 4px;
      font-weight: 600;
    }
    .risk-badge {
      display: inline-block;
      padding: 4px 8px;
      border-radius: 4px;
      font-weight: 600;
      margin-bottom: 8px;
    }
    .risk-low { background: rgba(34, 197, 94, 0.2); color: #22c55e; }
    .risk-medium { background: rgba(245, 158, 11, 0.2); color: #f59e0b; }
    .risk-high { background: rgba(249, 115, 22, 0.2); color: #f97316; }
    .risk-critical { background: rgba(239, 68, 68, 0.2); color: #ef4444; }
    .metric-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
      margin-bottom: 12px;
    }
    .metric-card {
      background: var(--vscode-input-background);
      border: 1px solid var(--vscode-input-border);
      padding: 8px;
      border-radius: 4px;
      text-align: center;
    }
    .metric-value {
      font-size: 16px;
      font-weight: bold;
      color: var(--vscode-editor-foreground);
    }
    .metric-label {
      font-size: 10px;
      color: var(--vscode-descriptionForeground);
      margin-top: 2px;
    }
    .list { list-style: none; margin: 0; padding: 0; }
    .list-item {
      padding: 4px 0;
      font-size: 11px;
      color: var(--vscode-editor-foreground);
    }
    .list-item::before {
      content: "→ ";
      color: var(--vscode-descriptionForeground);
      margin-right: 4px;
    }
    .empty {
      padding: 24px 12px;
      text-align: center;
      color: var(--vscode-descriptionForeground);
    }
  </style>
</head>
<body>
  <div id="content" class="empty">
    <p>No analysis yet. Save a file or run a simulation.</p>
  </div>

  <script>
    const vscode = acquireVsCodeApi();
    
    window.addEventListener('message', (event) => {
      const { type, data } = event.data;
      if (type === 'update') {
        renderResult(data);
      }
    });

    function renderResult(result) {
      const riskClass = 'risk-' + result.risk_score.toLowerCase();
      const html = \`
        <div class="container">
          <div class="section">
            <div class="risk-badge \${riskClass}">\${result.risk_score}</div>
          </div>
          
          <div class="section">
            <div class="label">Confidence</div>
            <div class="metric-grid">
              <div class="metric-card">
                <div class="metric-value">\${Math.round(result.confidence * 100)}%</div>
                <div class="metric-label">Confidence</div>
              </div>
            </div>
          </div>

          <div class="section">
            <div class="label">Blast Radius</div>
            <div class="metric-grid">
              <div class="metric-card">
                <div class="metric-value">\${result.blast_radius.services}</div>
                <div class="metric-label">Services</div>
              </div>
              <div class="metric-card">
                <div class="metric-value">\${result.blast_radius.endpoints}</div>
                <div class="metric-label">Endpoints</div>
              </div>
            </div>
          </div>

          <div class="section">
            <div class="label">Mitigations</div>
            <ul class="list">
              \${result.mitigations.slice(0, 3).map((m, i) => \`
                <li class="list-item">\${m}</li>
              \`).join('')}
            </ul>
          </div>
        </div>
      \`;
      document.getElementById('content').innerHTML = html;
    }
  </script>
</body>
</html>`;
  }
}
