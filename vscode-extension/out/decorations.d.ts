import * as vscode from 'vscode';
import { SimulationResult } from './aegisClient';
export declare class DecorationManager {
    private readonly riskDecoration;
    private readonly criticalDecoration;
    private readonly diagnostics;
    constructor();
    applyRisk(editor: vscode.TextEditor, diff: string, result: SimulationResult): void;
    clear(): void;
    dispose(): void;
    private parseChangedLines;
}
//# sourceMappingURL=decorations.d.ts.map