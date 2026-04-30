import * as https from 'https';
import * as http from 'http';

export interface SimulationResult {
  risk_score: string;
  confidence: number;
  blast_radius: { services: number; endpoints: number; databases: number };
  explanation: string;
  mitigations: string[];
  predicted_impact?: any;
}

export class AegisClient {
  constructor(private baseUrl: string, private token?: string) {}

  async simulateChange(
    diff: string,
    repoUrl: string,
    context?: string
  ): Promise<SimulationResult | null> {
    const body = JSON.stringify({
      diff,
      repo_url: repoUrl,
      context: context || '',
    });

    return this.post<SimulationResult>('/api/v1/simulate/change', body);
  }

  async getHotspots(): Promise<any[]> {
    const result = await this.get<any>('/api/v1/insights/hotspots');
    return result?.data?.hotspots || [];
  }

  async getPrAnalysis(prId: string): Promise<SimulationResult | null> {
    const result = await this.get<any>(`/api/v1/pr/${prId}/analysis`);
    return result?.data || null;
  }

  private async post<T>(path: string, body: string): Promise<T | null> {
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
          } catch {
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

  private async get<T>(path: string): Promise<T | null> {
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
          } catch {
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
