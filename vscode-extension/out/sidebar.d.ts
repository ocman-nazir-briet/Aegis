import * as vscode from 'vscode';
import { SimulationResult } from './aegisClient';
export declare class AegisSidebarProvider implements vscode.WebviewViewProvider {
    private context;
    static readonly viewType = "aegis.sidebar";
    private webviewView?;
    constructor(context: vscode.ExtensionContext);
    resolveWebviewView(webviewView: vscode.WebviewView, _context: vscode.WebviewViewResolveContext, _token: vscode.CancellationToken): void | Thenable<void>;
    updateResult(result: SimulationResult): void;
    private getHtml;
}
//# sourceMappingURL=sidebar.d.ts.map