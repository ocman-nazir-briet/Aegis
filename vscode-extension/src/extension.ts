import * as vscode from 'vscode';
import { AegisClient } from './aegisClient';
import { DecorationManager } from './decorations';
import { StatusBarManager } from './statusBar';
import { AegisSidebarProvider } from './sidebar';

let client: AegisClient;
let decorMgr: DecorationManager;
let statusBar: StatusBarManager;
let sidebar: AegisSidebarProvider;

export function activate(context: vscode.ExtensionContext) {
  const config = vscode.workspace.getConfiguration('aegisTwin');
  const apiUrl = config.get<string>('apiUrl', 'http://localhost:8000');
  const token = config.get<string>('token', '');

  client = new AegisClient(apiUrl, token);
  decorMgr = new DecorationManager();
  statusBar = new StatusBarManager(context);
  sidebar = new AegisSidebarProvider(context);

  vscode.window.registerWebviewViewProvider(
    AegisSidebarProvider.viewType,
    sidebar
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('aegis.runSimulation', async () => {
      const editor = vscode.window.activeTextEditor;
      if (!editor) {
        vscode.window.showWarningMessage('No active editor');
        return;
      }
      await runAnalysis(editor, config);

    }
    )
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('aegis.openDashboard', () => {
      const url = config.get<string>('apiUrl', 'http://localhost:8000');
      const dashboardUrl = url.replace(':8000', ':3000');
      vscode.env.openExternal(vscode.Uri.parse(dashboardUrl));
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('aegis.clearDecorations', () => {
      decorMgr.clear();
      statusBar.setIdle();
    })
  );

  context.subscriptions.push(
    vscode.workspace.onDidSaveTextDocument(async (doc) => {
      if (!config.get<boolean>('autoAnalyzeOnSave', true)) {
        return;
      }
      const editor = vscode.window.visibleTextEditors.find(
        (e) => e.document === doc
      );
      if (editor) {
        await runAnalysis(editor, config);
      }
    })
  );

  context.subscriptions.push(decorMgr);
  context.subscriptions.push(statusBar);
}

async function runAnalysis(
  editor: vscode.TextEditor,
  config: vscode.WorkspaceConfiguration
): Promise<void> {
  statusBar.setLoading();

  const diff = await getGitDiff();
  if (!diff) {
    statusBar.setError();
    vscode.window.showErrorMessage('No git diff available');
    return;
  }

  const repoUrl =
    config.get<string>('repoUrl', '') || (await detectRepoUrl());
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

  vscode.window.showInformationMessage(
    `Risk: ${result.risk_score} (${Math.round(result.confidence * 100)}% confidence)`
  );
}

async function getGitDiff(): Promise<string | null> {
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
  } catch {
    return null;
  }
}

async function detectRepoUrl(): Promise<string> {
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

    interface Remote {
      name: string;
      url?: string;
    }
    const origin: Remote | undefined = (remotes as Remote[]).find((r: Remote) => r.name === 'origin');
    return origin?.url || '';
  } catch {
    return '';
  }
}

export function deactivate() {
  decorMgr?.dispose();
  statusBar?.dispose();
}

