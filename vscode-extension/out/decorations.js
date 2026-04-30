"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.DecorationManager = void 0;
const vscode = __importStar(require("vscode"));
class DecorationManager {
    constructor() {
        this.riskDecoration = vscode.window.createTextEditorDecorationType({
            backgroundColor: 'rgba(245, 158, 11, 0.15)',
            overviewRulerColor: 'rgba(245, 158, 11, 0.8)',
            overviewRulerLane: vscode.OverviewRulerLane.Full,
        });
        this.criticalDecoration = vscode.window.createTextEditorDecorationType({
            backgroundColor: 'rgba(239, 68, 68, 0.3)',
            overviewRulerColor: 'rgba(239, 68, 68, 0.8)',
            overviewRulerLane: vscode.OverviewRulerLane.Full,
        });
        this.diagnostics = vscode.languages.createDiagnosticCollection('aegis-risk');
    }
    applyRisk(editor, diff, result) {
        const changedLines = this.parseChangedLines(diff, editor.document.fileName);
        const riskLevel = result.risk_score.toLowerCase();
        const isCritical = riskLevel === 'critical' || riskLevel === 'high';
        const decorations = [];
        const diags = [];
        for (const lineNum of changedLines) {
            if (lineNum < editor.document.lineCount) {
                const line = editor.document.lineAt(lineNum);
                const range = line.range;
                decorations.push(range);
                if (isCritical) {
                    const diag = new vscode.Diagnostic(range, result.mitigations[0] || `${result.risk_score} risk detected`, vscode.DiagnosticSeverity.Error);
                    diags.push(diag);
                }
            }
        }
        const decoration = isCritical ? this.criticalDecoration : this.riskDecoration;
        editor.setDecorations(decoration, decorations);
        this.diagnostics.set(editor.document.uri, diags);
    }
    clear() {
        const editor = vscode.window.activeTextEditor;
        if (editor) {
            editor.setDecorations(this.riskDecoration, []);
            editor.setDecorations(this.criticalDecoration, []);
        }
        this.diagnostics.clear();
    }
    dispose() {
        this.riskDecoration.dispose();
        this.criticalDecoration.dispose();
        this.diagnostics.dispose();
    }
    parseChangedLines(diff, fileName) {
        const lines = [];
        const lines_arr = diff.split('\n');
        let currentFile = '';
        let lineNum = 0;
        for (const line of lines_arr) {
            if (line.startsWith('+++') || line.startsWith('---')) {
                currentFile = line.slice(4).trim();
            }
            else if (line.startsWith('@@')) {
                const match = line.match(/@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@/);
                if (match) {
                    lineNum = parseInt(match[1]) - 1;
                }
            }
            else if (currentFile.includes(fileName.split('/').pop() || '')) {
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
exports.DecorationManager = DecorationManager;
//# sourceMappingURL=decorations.js.map