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
exports.StatusBarManager = void 0;
const vscode = __importStar(require("vscode"));
class StatusBarManager {
    constructor(context) {
        this.state = 'idle';
        this.lastRisk = '';
        this.statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 100);
        this.statusBarItem.command = 'aegis.runSimulation';
        this.statusBarItem.tooltip = 'Click to run Aegis risk analysis';
        context.subscriptions.push(this.statusBarItem);
        this.setIdle();
    }
    setLoading() {
        this.state = 'loading';
        this.statusBarItem.text = '$(sync~spin) Aegis: Analyzing...';
        this.statusBarItem.show();
    }
    setIdle() {
        this.state = 'idle';
        this.statusBarItem.text = '$(shield) Aegis: Idle';
        this.statusBarItem.show();
    }
    setResult(riskScore) {
        this.state = 'result';
        this.lastRisk = riskScore;
        const icon = riskScore === 'Critical'
            ? '$(error)'
            : riskScore === 'High'
                ? '$(warning)'
                : '$(shield)';
        const color = riskScore === 'Critical'
            ? '#ef4444'
            : riskScore === 'High'
                ? '#f59e0b'
                : '#22c55e';
        this.statusBarItem.text = `${icon} Aegis: ${riskScore}`;
        this.statusBarItem.color = color;
        this.statusBarItem.show();
    }
    setError() {
        this.state = 'error';
        this.statusBarItem.text = '$(error) Aegis: Error';
        this.statusBarItem.color = '#ef4444';
        this.statusBarItem.show();
    }
    dispose() {
        this.statusBarItem.dispose();
    }
}
exports.StatusBarManager = StatusBarManager;
//# sourceMappingURL=statusBar.js.map