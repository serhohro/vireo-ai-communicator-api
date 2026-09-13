// ============================================================
// VIREO TYPESCRIPT SDK — AGENT
// ============================================================

import { AgentProxy, Message, Intent, Contract, DEFAULT_CONTRACT } from './client';

/**
 * Vireo agent with built-in negotiation capabilities.
 */

export interface AgentOptions {
  id: string;
  model?: string;
  capabilities?: string[];
  role?: string;
  contract?: Contract;
}

export class VireoAgent extends AgentProxy {
  public capabilities: string[];
  public role?: string;
  public contract: Contract;
  private messageHistory: Message[] = [];

  constructor(
    client: any,
    options: AgentOptions
  ) {
    super(client, options.id);
    this.capabilities = options.capabilities || [];
    this.role = options.role;
    this.contract = options.contract || { ...DEFAULT_CONTRACT };
  }

  async negotiateTask(
    recipient: string,
    task: string,
    maxRounds: number = 3
  ): Promise<{ success: boolean; result?: any; error?: string }> {
    let rounds = 0;
    let currentOffer: any = null;

    // Send initial proposal
    const proposal = await this.propose(recipient, task, this.contract);
    this.messageHistory.push(proposal);

    // Wait for response (simplified)
    // In a real implementation, this would use the message bus
    for (let i = 0; i < maxRounds; i++) {
      rounds++;
      
      // Simulate negotiation
      const decision = await this.decide(proposal);
      
      if (decision === "commit") {
        const commitMsg = await this.commit(recipient, proposal.messageId);
        this.messageHistory.push(commitMsg);
        
        // Execute task
        const result = await this.executeTask(proposal);
        
        // Verify result
        if (this.contract.verify) {
          const verified = await this.verifyTask(result, this.contract.verify);
          if (!verified) {
            await this.escalate(recipient, proposal.messageId, "Verification failed");
            return { success: false, error: "Verification failed" };
          }
        }
        
        await this.inform(recipient, proposal.messageId, result);
        return { success: true, result };
      } else if (decision === "reject") {
        await this.reject(recipient, proposal.messageId, "Negotiation failed");
        return { success: false, error: "Rejected" };
      }
    }

    await this.escalate(recipient, proposal.messageId, "Max rounds exceeded");
    return { success: false, error: "Max rounds exceeded" };
  }

  private async decide(message: Message): Promise<string> {
    // In a real implementation, this would use an LLM
    // For now, simulate decision
    return "commit";
  }

  private async executeTask(message: Message): Promise<any> {
    // Execute the task from the message
    const code = message.payload?.code || "";
    // In a real implementation, this would execute Vireo code
    return { status: "success", result: "Task completed" };
  }

  private async verifyTask(result: any, condition: string): Promise<boolean> {
    // Verify the result against the condition
    // In a real implementation, this would evaluate the condition
    return true;
  }

  getHistory(): Message[] {
    return [...this.messageHistory];
  }

  clearHistory(): void {
    this.messageHistory = [];
  }

  addCapability(capability: string): void {
    this.capabilities.push(capability);
  }

  removeCapability(capability: string): void {
    this.capabilities = this.capabilities.filter(c => c !== capability);
  }

  setContract(contract: Contract): void {
    this.contract = { ...this.contract, ...contract };
  }
}

// ============================================================
// AGENT FACTORY
// ============================================================

export function createAgent(
  client: any,
  options: AgentOptions
): VireoAgent {
  return new VireoAgent(client, options);
}

export function createAgentFromConfig(
  client: any,
  config: {
    id: string;
    model?: string;
    capabilities?: string[];
    role?: string;
  }
): VireoAgent {
  return new VireoAgent(client, {
    id: config.id,
    model: config.model,
    capabilities: config.capabilities,
    role: config.role
  });
}