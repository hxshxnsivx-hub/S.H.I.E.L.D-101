export interface Decision {
  cls: string;
  action: "allow" | "mask" | "tokenize" | "block" | "escalate";
  reason: string;
  confidence: number;
  method: string;
}

export interface GuardResult {
  sanitized: string;
  status: "clean" | "sanitized" | "needs_review" | "blocked_parts";
  trust: string;
  latency_ms: number;
  decisions: Decision[];
  evidence_id: string;
}

export interface ArgumentsResult {
  tool: string;
  status: string;
  blocked: boolean;
  sanitized: Record<string, unknown>;
}

export class KavachClient {
  constructor(baseUrl?: string);
  guard(text: string, destination: string): Promise<GuardResult>;
  guardArguments(tool: string, args: Record<string, unknown>): Promise<ArgumentsResult>;
  audit(): Promise<unknown>;
}

export default KavachClient;
