// ============================================================
// VIREO TYPESCRIPT SDK — CLIENT
// ============================================================

/**
 * Vireo TypeScript SDK client for agent communication.
 */

// ============================================================
// ENUMS
// ============================================================

export enum Intent {
  PROPOSE = "PROPOSE",
  NEGOTIATE = "NEGOTIATE",
  COMMIT = "COMMIT",
  REJECT = "REJECT",
  EXECUTE = "EXECUTE",
  VERIFY = "VERIFY",
  INFORM = "INFORM",
  CANCEL = "CANCEL",
  QUERY_CAPABILITIES = "QUERY_CAPABILITIES",
  INFORM_CAPABILITIES = "INFORM_CAPABILITIES",
  ESCALATE = "ESCALATE"
}

// ============================================================
// INTERFACES
// ============================================================

export interface Contract {
  maxTokens?: number;
  maxCostUsd?: number;
  timeoutSec?: number;
  verifyTimeoutSec?: number;
  maxRounds?: number;
  maxMemoryMb?: number;
  allowedActions?: string[];
  requiredApprovals?: number;
  verify?: string;
}

export interface AgentInfo {
  id: string;
  model?: string;
  capabilities?: string[];
  role?: string;
}

export interface Message {
  protocol: string;
  version: string;
  messageId: string;
  conversationId: string;
  sender: string;
  recipient: string;
  intent: Intent;
  payload: Record<string, any>;
  timestamp: number;
  signature?: string;
}

// ============================================================
// DEFAULT CONTRACT
// ============================================================

export const DEFAULT_CONTRACT: Contract = {
  maxTokens: 1000,
  maxCostUsd: 0.05,
  timeoutSec: 30,
  verifyTimeoutSec: 15,
  maxRounds: 3,
  maxMemoryMb: 1024,
  allowedActions: ["train_model", "predict", "evaluate", "generate_code"],
  requiredApprovals: 1
};

export function createContract(options: Partial<Contract> = {}): Contract {
  return { ...DEFAULT_CONTRACT, ...options };
}

// ============================================================
// MESSAGE HELPER
// ============================================================

function generateId(prefix: string): string {
  const hex = Math.floor(Math.random() * 0xFFFFFFFF).toString(16).padStart(8, '0');
  return `${prefix}-${hex}`;
}

export function createMessage(
  sender: string,
  recipient: string,
  intent: Intent,
  payload: Record<string, any> = {}
): Message {
  return {
    protocol: "VIREO-A2A",
    version: "2.0.2",
    messageId: generateId("msg"),
    conversationId: generateId("conv"),
    sender,
    recipient,
    intent,
    payload,
    timestamp: Date.now() / 1000
  };
}

// ============================================================
// VIREO CLIENT
// ============================================================

export class VireoClient {
  private baseUrl: string;
  private agents: Map<string, AgentInfo> = new Map();
  private messageHandlers: Map<Intent, (message: Message) => Promise<any>> = new Map();

  constructor(baseUrl: string = "http://localhost:5000") {
    this.baseUrl = baseUrl.replace(/\/$/, '');
  }

  async registerAgent(agentId: string, model?: string): Promise<AgentInfo> {
    const agentInfo: AgentInfo = { id: agentId, model };
    this.agents.set(agentId, agentInfo);
    console.log(`✅ Agent registered: ${agentId}`);
    return agentInfo;
  }

  getAgent(agentId: string): AgentInfo | undefined {
    return this.agents.get(agentId);
  }

  listAgents(): string[] {
    return Array.from(this.agents.keys());
  }

  async sendMessage(message: Message): Promise<Message> {
    console.log(`📤 Sending message: ${message.intent} from ${message.sender} to ${message.recipient}`);
    return message;
  }

  on(intent: Intent, handler: (message: Message) => Promise<any>): void {
    this.messageHandlers.set(intent, handler);
  }

  async handleMessage(message: Message): Promise<any> {
    const handler = this.messageHandlers.get(message.intent);
    if (handler) {
      return handler(message);
    }
    console.warn(`⚠️ No handler for intent: ${message.intent}`);
    return null;
  }
}

// ============================================================
// AGENT PROXY
// ============================================================

export class AgentProxy {
  constructor(
    private client: VireoClient,
    public agentId: string
  ) {}

  async propose(
    recipient: string,
    task: string,
    contract?: Contract
  ): Promise<Message> {
    const message = createMessage(
      this.agentId,
      recipient,
      Intent.PROPOSE,
      {
        task,
        contract: contract || undefined
      }
    );
    return this.client.sendMessage(message);
  }

  async commit(recipient: string, proposalId: string): Promise<Message> {
    const message = createMessage(
      this.agentId,
      recipient,
      Intent.COMMIT,
      { proposalId }
    );
    return this.client.sendMessage(message);
  }

  async reject(recipient: string, proposalId: string, reason: string = ""): Promise<Message> {
    const message = createMessage(
      this.agentId,
      recipient,
      Intent.REJECT,
      { proposalId, reason }
    );
    return this.client.sendMessage(message);
  }

  async inform(recipient: string, proposalId: string, result: any): Promise<Message> {
    const message = createMessage(
      this.agentId,
      recipient,
      Intent.INFORM,
      { proposalId, result }
    );
    return this.client.sendMessage(message);
  }

  async verify(
    recipient: string,
    proposalId: string,
    result: any,
    condition: string
  ): Promise<Message> {
    const message = createMessage(
      this.agentId,
      recipient,
      Intent.VERIFY,
      { proposalId, result, condition }
    );
    return this.client.sendMessage(message);
  }

  async escalate(recipient: string, proposalId: string, reason: string): Promise<Message> {
    const message = createMessage(
      this.agentId,
      recipient,
      Intent.ESCALATE,
      { proposalId, reason }
    );
    return this.client.sendMessage(message);
  }

  async negotiate(
    recipient: string,
    proposalId: string,
    counterOffer: Record<string, any>
  ): Promise<Message> {
    const message = createMessage(
      this.agentId,
      recipient,
      Intent.NEGOTIATE,
      { proposalId, counterOffer }
    );
    return this.client.sendMessage(message);
  }
}