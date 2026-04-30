import * as vscode from 'vscode';
export declare class StatusBarManager {
    private statusBarItem;
    private state;
    private lastRisk;
    constructor(context: vscode.ExtensionContext);
    setLoading(): void;
    setIdle(): void;
    setResult(riskScore: string): void;
    setError(): void;
    dispose(): void;
}
//# sourceMappingURL=statusBar.d.ts.map