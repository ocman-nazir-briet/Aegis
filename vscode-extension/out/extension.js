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
exports.activate = activate;
exports.deactivate = deactivate;
const vscode = __importStar(require("vscode"));
const aegisClient_1 = require("./aegisClient");
const decorations_1 = require("./decorations");
const statusBar_1 = require("./statusBar");
const sidebar_1 = require("./sidebar");
let client;
let decorMgr;
let statusBar;
let sidebar;
function activate(context) {
    const config = vscode.workspace.getConfiguration('aegisTwin');
    const apiUrl = config.get('apiUrl', 'http://localhost:8000');
    const token = config.get('token', '');
    client = new aegisClient_1.AegisClient(apiUrl, token);
    decorMgr = new decorations_1.DecorationManager();
    statusBar = new statusBar_1.StatusBarManager(context);
    sidebar = new sidebar_1.AegisSidebarProvider(context);
    vscode.window.registerWebviewViewProvider(sidebar_1.AegisSidebarProvider.viewType, sidebar);
    context.subscriptions.push(vscode.commands.registerCommand('aegis.runSimulation', async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showWarningMessage('No active editor');
            return;
        }
        await runAnalysis(editor, config);
    }));
    context.subscriptions.push(vscode.commands.registerCommand('aegis.openDashboard', () => {
        const url = config.get('apiUrl', 'http://localhost:8000');
        const dashboardUrl = url.replace(':8000', ':3000');
        vscode.env.openExternal(vscode.Uri.parse(dashboardUrl));
    }));
    context.subscriptions.push(vscode.commands.registerCommand('aegis.clearDecorations', () => {
        decorMgr.clear();
        statusBar.setIdle();
    }));
    context.subscriptions.push(vscode.workspace.onDidSaveTextDocument(async (doc) => {
        if (!config.get('autoAnalyzeOnSave', true)) {
            return;
        }
        const editor = vscode.window.visibleTextEditors.find((e) => e.document === doc);
        if (editor) {
            await runAnalysis(editor, config);
        }
    }));
    context.subscriptions.push(decorMgr);
    context.subscriptions.push(statusBar);
}
async function runAnalysis(editor, config) {
    statusBar.setLoading();
    const diff = await getGitDiff();
    if (!diff) {
        statusBar.setError();
        vscode.window.showErrorMessage('No git diff available');
        return;
    }
    const repoUrl = config.get('repoUrl', '') || (await detectRepoUrl());
    if (!repoUrl) {
        statusBar.setError();
        vscode.window.showErrorMessage('Could not determine repository URL');
        return;
    }
    const result = await client.simulateChange(diff, repoUrl);
    if (!result) {
        statusBar.setError();
        vscode.window.showErrorMessage('Simulation failed');
        return;
    }
    decorMgr.applyRisk(editor, diff, result);
    statusBar.setResult(result.risk_score);
    sidebar.updateResult(result);
    vscode.window.showInformationMessage(`Risk: ${result.risk_score} (${Math.round(result.confidence * 100)}% confidence)`);
}
async function getGitDiff() {
    try {
        const gitExt = vscode.extensions.getExtension('vscode.git');
        if (!gitExt) {
            return null;
        }
        const git = gitExt.exports.getAPI(1);
        if (!git.repositories[0]) {
            return null;
        }
        const repo = git.repositories[0];
        const diff = await repo.diff(false);
        return diff || null;
    }
    catch {
        return null;
    }
}
async function detectRepoUrl() {
    try {
        const gitExt = vscode.extensions.getExtension('vscode.git');
        if (!gitExt) {
            return '';
        }
        const git = gitExt.exports.getAPI(1);
        if (!git.repositories[0]) {
            return '';
        }
        const repo = git.repositories[0];
        const remotes = repo.state.remotes;
        const origin = remotes.find((r) => r.name === 'origin');
        return origin?.url || '';
    }
    catch {
        return '';
    }
}
function deactivate() {
    decorMgr?.dispose();
    statusBar?.dispose();
}
//# sourceMappingURL=extension.js.map