import * as vscode from 'vscode';
import { SimulationResult } from './aegisClient';

export class DecorationManager {
  private readonly riskDecoration: vscode.TextEditorDecorationType;
  private readonly criticalDecoration: vscode.TextEditorDecorationType;
  private readonly diagnostics: vscode.DiagnosticCollection;

  constructor() {
    this.riskDecoration = vscode.window.createTextEditorDecorationType({
      backgroundColor: 'rgba(245, 158, 11, 0.15)',
      overviewRulerColor: 'rgba(245, 158, 11, 0.8)',
      overviewRulerLane: vscode.OverviewRulerLane.Full,
    } as any);

    this.criticalDecoration = vscode.window.createTextEditorDecorationType({
      backgroundColor: 'rgba(239, 68, 68, 0.3)',
      overviewRulerColor: 'rgba(239, 68, 68, 0.8)',
      overviewRulerLane: vscode.OverviewRulerLane.Full,
    } as any);

    this.diagnostics = vscode.languages.createDiagnosticCollection('aegis-risk');
  }

  applyRisk(
    editor: vscode.TextEditor,
    diff: string,
    result: SimulationResult
  ): void {
    const changedLines = this.parseChangedLines(diff, editor.document.fileName);
    const riskLevel = result.risk_score.toLowerCase();
    const isCritical = riskLevel === 'critical' || riskLevel === 'high';

    const decorations: vscode.Range[] = [];
    const diags: vscode.Diagnostic[] = [];

    for (const lineNum of changedLines) {
      if (lineNum < editor.document.lineCount) {
        const line = editor.document.lineAt(lineNum);
        const range = line.range;
        decorations.push(range);

        if (isCritical) {
          const diag = new vscode.Diagnostic(
            range,
            result.mitigations[0] || `${result.risk_score} risk detected`,
            vscode.DiagnosticSeverity.Error
          );
          diags.push(diag);
        }
      }
    }

    const decoration = isCritical ? this.criticalDecoration : this.riskDecoration;
    editor.setDecorations(decoration, decorations);
    this.diagnostics.set(editor.document.uri, diags);
  }

  clear(): void {
    const editor = vscode.window.activeTextEditor;
    if (editor) {
      editor.setDecorations(this.riskDecoration, []);
      editor.setDecorations(this.criticalDecoration, []);
    }
    this.diagnostics.clear();
  }

  dispose(): void {
    this.riskDecoration.dispose();
    this.criticalDecoration.dispose();
    this.diagnostics.dispose();
  }

  private parseChangedLines(diff: string, fileName: string): number[] {
    const lines: number[] = [];
    const lines_arr = diff.split('\n');

    let currentFile = '';
    let lineNum = 0;

    for (const line of lines_arr) {
      if (line.startsWith('+++') || line.startsWith('---')) {
        currentFile = line.slice(4).trim();
      } else if (line.startsWith('@@')) {
        const match = line.match(/@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@/);
        if (match) {
          lineNum = parseInt(match[1]) - 1;
        }
      } else if (currentFile.includes(fileName.split('/').pop() || '')) {
        if (line.startsWith('+') && !line.startsWith('+++')) {
          lines.push(lineNum);
        }
        if (!line.startsWith('-') || line.startsWith('---')) {
          lineNum++;
        }
      }
    }

    return lines;
  }
}
