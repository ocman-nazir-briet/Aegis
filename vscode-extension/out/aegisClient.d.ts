export interface SimulationResult {
    risk_score: string;
    confidence: number;
    blast_radius: {
        services: number;
        endpoints: number;
        databases: number;
    };
    explanation: string;
    mitigations: string[];
    predicted_impact?: any;
}
export declare class AegisClient {
    private baseUrl;
    private token?;
    constructor(baseUrl: string, token?: string | undefined);
    simulateChange(diff: string, repoUrl: string, context?: string): Promise<SimulationResult | null>;
    getHotspots(): Promise<any[]>;
    getPrAnalysis(prId: string): Promise<SimulationResult | null>;
    private post;
    private get;
}
//# sourceMappingURL=aegisClient.d.ts.map