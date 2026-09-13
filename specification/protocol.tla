--------------------- MODULE VireoProtocol ---------------------
(* Vireo Protocol Specification v3.0.0 *)
(* TLA+ Formal Specification *)

EXTENDS Integers, Sequences, FiniteSets, TLC, Naturals

CONSTANTS 
    PROPOSE, COMMIT, EXECUTE, VERIFY, DONE, 
    ESCALATE, REJECT, TIMEOUT,
    Agents, MaxRounds, TimeoutSec

(* ============================================================
   CONSTANTS
   ============================================================ *)

VARIABLES
    state,          (* Current state of the protocol *)
    agent_id,       (* Current agent ID *)
    counterparty,   (* Counterparty agent ID *)
    contract,       (* Current contract *)
    result,         (* Execution result *)
    round,          (* Negotiation round *)
    timestamp,      (* Current timestamp *)
    nonce,          (* Message nonce *)
    messages,       (* Message history *)
    trust_level     (* Trust level *)

(* ============================================================
   TYPE INVARIANTS
   ============================================================ *)

TypeOK ==
    /\ state \in {"DISCOVER", "PROPOSE", "NEGOTIATE", "COMMIT", 
                  "EXECUTE", "VERIFY", "DONE", "ESCALATE", "REJECT", "TIMEOUT"}
    /\ agent_id \in Agents
    /\ counterparty \in Agents \cup {NIL}
    /\ contract \in [task: STRING, max_tokens: Nat, timeout: Nat] \cup {NIL}
    /\ result \in [status: STRING, output: Nat] \cup {NIL}
    /\ round \in 0..MaxRounds
    /\ timestamp \in Nat
    /\ nonce \in STRING \cup {NIL}
    /\ messages \in SEQ(STRING)
    /\ trust_level \in 0..100

(* ============================================================
   INITIAL STATE
   ============================================================ *)

Init ==
    /\ state = "DISCOVER"
    /\ agent_id = "agent-1"
    /\ counterparty = NIL
    /\ contract = NIL
    /\ result = NIL
    /\ round = 0
    /\ timestamp = 0
    /\ nonce = NIL
    /\ messages = <<>>
    /\ trust_level = 50

(* ============================================================
   TRANSITIONS
   ============================================================ *)

(* Discover → Propose *)
Discover ==
    /\ state = "DISCOVER"
    /\ counterparty' = CHOOSE a \in Agents: a /= agent_id
    /\ state' = "PROPOSE"
    /\ timestamp' = timestamp + 1
    /\ nonce' = "nonce-" + STRING timestamp'
    /\ messages' = Append(messages, "PROPOSE")
    /\ UNCHANGED <<contract, result, round, trust_level>>

(* Propose → Negotiate *)
ProposeNegotiate ==
    /\ state = "PROPOSE"
    /\ contract' = [task |-> "compute", max_tokens |-> 1000, timeout |-> 30]
    /\ state' = "NEGOTIATE"
    /\ round' = round + 1
    /\ timestamp' = timestamp + 1
    /\ messages' = Append(messages, "NEGOTIATE")
    /\ UNCHANGED <<result, nonce, trust_level>>

(* Propose → Reject *)
ProposeReject ==
    /\ state = "PROPOSE"
    /\ state' = "REJECT"
    /\ timestamp' = timestamp + 1
    /\ messages' = Append(messages, "REJECT")
    /\ UNCHANGED <<contract, result, round, nonce, trust_level>>

(* Negotiate → Commit *)
NegotiateCommit ==
    /\ state = "NEGOTIATE"
    /\ state' = "COMMIT"
    /\ timestamp' = timestamp + 1
    /\ messages' = Append(messages, "COMMIT")
    /\ UNCHANGED <<contract, result, round, nonce, trust_level>>

(* Negotiate → Reject *)
NegotiateReject ==
    /\ state = "NEGOTIATE"
    /\ state' = "REJECT"
    /\ timestamp' = timestamp + 1
    /\ messages' = Append(messages, "REJECT")
    /\ UNCHANGED <<contract, result, round, nonce, trust_level>>

(* Commit → Execute *)
CommitExecute ==
    /\ state = "COMMIT"
    /\ state' = "EXECUTE"
    /\ timestamp' = timestamp + 1
    /\ messages' = Append(messages, "EXECUTE")
    /\ UNCHANGED <<contract, result, round, nonce, trust_level>>

(* Commit → Reject *)
CommitReject ==
    /\ state = "COMMIT"
    /\ state' = "REJECT"
    /\ timestamp' = timestamp + 1
    /\ messages' = Append(messages, "REJECT")
    /\ UNCHANGED <<contract, result, round, nonce, trust_level>>

(* Execute → Verify *)
ExecuteVerify ==
    /\ state = "EXECUTE"
    /\ result' = [status |-> "success", output |-> 42]
    /\ state' = "VERIFY"
    /\ timestamp' = timestamp + 1
    /\ messages' = Append(messages, "VERIFY")
    /\ UNCHANGED <<contract, round, nonce, trust_level>>

(* Execute → Timeout *)
ExecuteTimeout ==
    /\ state = "EXECUTE"
    /\ timestamp - timestamp_of_execute_state > TimeoutSec
    /\ state' = "TIMEOUT"
    /\ messages' = Append(messages, "TIMEOUT")
    /\ UNCHANGED <<contract, result, round, nonce, trust_level>>

(* Verify → Done *)
VerifyDone ==
    /\ state = "VERIFY"
    /\ result.output = 42
    /\ trust_level' = MIN(100, trust_level + 5)
    /\ state' = "DONE"
    /\ timestamp' = timestamp + 1
    /\ messages' = Append(messages, "DONE")
    /\ UNCHANGED <<contract, result, round, nonce>>

(* Verify → Escalate *)
VerifyEscalate ==
    /\ state = "VERIFY"
    /\ result.output /= 42
    /\ trust_level' = MAX(0, trust_level - 10)
    /\ state' = "ESCALATE"
    /\ timestamp' = timestamp + 1
    /\ messages' = Append(messages, "ESCALATE")
    /\ UNCHANGED <<contract, result, round, nonce>>

(* Escalate → Done *)
EscalateDone ==
    /\ state = "ESCALATE"
    /\ trust_level' = MAX(0, trust_level - 20)
    /\ state' = "DONE"
    /\ timestamp' = timestamp + 1
    /\ messages' = Append(messages, "DONE")
    /\ UNCHANGED <<contract, result, round, nonce>>

(* ============================================================
   NEXT STATE RELATION
   ============================================================ *)

Next ==
    \/ Discover
    \/ ProposeNegotiate
    \/ ProposeReject
    \/ NegotiateCommit
    \/ NegotiateReject
    \/ CommitExecute
    \/ CommitReject
    \/ ExecuteVerify
    \/ ExecuteTimeout
    \/ VerifyDone
    \/ VerifyEscalate
    \/ EscalateDone

(* ============================================================
   LIVENESS
   ============================================================ *)

Fairness ==
    WF_Next

Spec == Init /\ [][Next]_<<state, agent_id, counterparty, contract, result, round, timestamp, nonce, messages, trust_level>> /\ Fairness

(* ============================================================
   PROPERTIES
   ============================================================ *)

(* The protocol always terminates *)
Termination ==
    <>(state = "DONE" \/ state = "REJECT" \/ state = "TIMEOUT")

(* No invalid transitions *)
NoInvalidTransitions ==
    [](state = "PROPOSE" => ~(state' = "VERIFY") /\ ~(state' = "DONE"))

(* Max rounds limit *)
MaxRoundsLimit ==
    [](round <= MaxRounds)

(* Success implies result is valid *)
SuccessImpliesValid ==
    [](state = "DONE" => result.output > 0)

(* Timestamp monotonicity *)
TimestampMonotonic ==
    [](timestamp' > timestamp)

(* Nonce uniqueness *)
NonceUniqueness ==
    [](nonce /= NIL => nonce' /= nonce)

(* Trust level bounds *)
TrustBounds ==
    [](0 <= trust_level /\ trust_level <= 100)

(* Trust increases on success *)
TrustOnSuccess ==
    [](state = "DONE" /\ result.output = 42 => trust_level' > trust_level)

(* Trust decreases on failure *)
TrustOnFailure ==
    [](state = "ESCALATE" => trust_level' < trust_level)

(* Message history grows *)
MessageHistoryGrows ==
    [](Len(messages') > Len(messages))

(* ============================================================
   THEOREMS
   ============================================================ *)

THEOREM Spec => Termination
THEOREM Spec => NoInvalidTransitions
THEOREM Spec => MaxRoundsLimit
THEOREM Spec => TimestampMonotonic
THEOREM Spec => TrustBounds
THEOREM Spec => MessageHistoryGrows

(* ============================================================
   INVARIANTS
   ============================================================ *)

(* State and nonce are linked *)
StateNonceInvariant ==
    [](state /= "DISCOVER" => nonce /= NIL)

(* Contract only exists after PROPOSE *)
ContractInvariant ==
    [](contract /= NIL => state \in {"PROPOSE", "NEGOTIATE", "COMMIT", "EXECUTE", "VERIFY", "DONE", "ESCALATE"})

(* Result only exists after EXECUTE *)
ResultInvariant ==
    [](result /= NIL => state \in {"VERIFY", "DONE", "ESCALATE"})

=================================================================