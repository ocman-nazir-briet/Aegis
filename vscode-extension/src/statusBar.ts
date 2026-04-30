import * as vscode from 'vscode';

export class StatusBarManager {
  private statusBarItem: vscode.StatusBarItem;
  private state: 'idle' | 'loading' | 'result' | 'error' = 'idle';
  private lastRisk: string = '';

  constructor(context: vscode.ExtensionContext) {
    this.statusBarItem = vscode.window.createStatusBarItem(
      vscode.StatusBarAlignment.Left,
      100
    );
    this.statusBarItem.command = 'aegis.runSimulation';
    this.statusBarItem.tooltip = 'Click to run Aegis risk analysis';
    context.subscriptions.push(this.statusBarItem);
    this.setIdle();
  }

  setLoading(): void {
    this.state = 'loading';
    this.statusBarItem.text = '$(sync~spin) Aegis: Analyzing...';
    this.statusBarItem.show();
  }

  setIdle(): void {
    this.state = 'idle';
    this.statusBarItem.text = '$(shield) Aegis: Idle';
    this.statusBarItem.show();
  }

  setResult(riskScore: string): void {
    this.state = 'result';
    this.lastRisk = riskScore;
    const icon =
      riskScore === 'Critical'
        ? '$(error)'
        : riskScore === 'High'
        ? '$(warning)'
        : '$(shield)';
    const color =
      riskScore === 'Critical'
        ? '#ef4444'
        : riskScore === 'High'
        ? '#f59e0b'
        : '#22c55e';

    this.statusBarItem.text = `${icon} Aegis: ${riskScore}`;
    this.statusBarItem.color = color;
    this.statusBarItem.show();
  }

  setError(): void {
    this.state = 'error';
    this.statusBarItem.text = '$(error) Aegis: Error';
    this.statusBarItem.color = '#ef4444';
    this.statusBarItem.show();
  }

  dispose(): void {
    this.statusBarItem.dispose();
  }
}
