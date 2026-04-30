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
exports.AegisClient = void 0;
const https = __importStar(require("https"));
const http = __importStar(require("http"));
class AegisClient {
    constructor(baseUrl, token) {
        this.baseUrl = baseUrl;
        this.token = token;
    }
    async simulateChange(diff, repoUrl, context) {
        const body = JSON.stringify({
            diff,
            repo_url: repoUrl,
            context: context || '',
        });
        return this.post('/api/v1/simulate/change', body);
    }
    async getHotspots() {
        const result = await this.get('/api/v1/insights/hotspots');
        return result?.data?.hotspots || [];
    }
    async getPrAnalysis(prId) {
        const result = await this.get(`/api/v1/pr/${prId}/analysis`);
        return result?.data || null;
    }
    async post(path, body) {
        return new Promise((resolve) => {
            const handler = this.baseUrl.startsWith('https') ? https : http;
            const url = new URL(this.baseUrl + path);
            const options = {
                hostname: url.hostname,
                port: url.port || (url.protocol === 'https:' ? 443 : 80),
                path: url.pathname + url.search,
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Content-Length': Buffer.byteLength(body),
                    ...(this.token && { Authorization: `Bearer ${this.token}` }),
                },
                timeout: 30000,
            };
            const req = handler.request(options, (res) => {
                let data = '';
                res.on('data', (chunk) => (data += chunk));
                res.on('end', () => {
                    try {
                        const parsed = JSON.parse(data);
                        resolve(parsed.data || null);
                    }
                    catch {
                        resolve(null);
                    }
                });
            });
            req.on('error', () => resolve(null));
            req.on('timeout', () => {
                req.destroy();
                resolve(null);
            });
            req.write(body);
            req.end();
        });
    }
    async get(path) {
        return new Promise((resolve) => {
            const handler = this.baseUrl.startsWith('https') ? https : http;
            const url = new URL(this.baseUrl + path);
            const options = {
                hostname: url.hostname,
                port: url.port || (url.protocol === 'https:' ? 443 : 80),
                path: url.pathname + url.search,
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    ...(this.token && { Authorization: `Bearer ${this.token}` }),
                },
                timeout: 30000,
            };
            const req = handler.request(options, (res) => {
                let data = '';
                res.on('data', (chunk) => (data += chunk));
                res.on('end', () => {
                    try {
                        const parsed = JSON.parse(data);
                        resolve(parsed);
                    }
                    catch {
                        resolve(null);
                    }
                });
            });
            req.on('error', () => resolve(null));
            req.on('timeout', () => {
                req.destroy();
                resolve(null);
            });
            req.end();
        });
    }
}
exports.AegisClient = AegisClient;
//# sourceMappingURL=aegisClient.js.map