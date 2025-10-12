# Agent Observability 2025: Safety • Cost • Control
## 15-Minute Conference Talk (Survey-First Approach)

---

## Slide 1: Title
**Agent Observability 2025: Safety • Cost • Control**

**Key Points:**
- Agent Observability 2025: Safety • Cost • Control

**Script (30-40s):**
Today I'll start with what teams are actually fighting in production: safety under uncertainty, cost control, and vendor fragmentation. Then I'll map the existing tools and show why they don't close the loop. I'll finish with a production-ready architecture, the Data Plane plus Cognitive Plane, and a pragmatic adoption path.

---

## Slide 2: What the Room Cares About
**Key Points:**
- Safety under uncertainty: prompt-injection/jailbreaks, tool misuse, silent "logic" failures
- Run-cost & ROI: token sprawl, 10×+ cost explosions in multi-agent setups
- Cross-vendor control & audit: OpenTelemetry GenAI semantics, MCP standardization

**Script (60-75s):**
Security benchmarks show tool-integrated agents are attackable. These aren't 5xx errors, they're semantic failures. Costs can jump an order of magnitude when coordination is inefficient.

And standards like OpenTelemetry GenAI and MCP are arriving, which increases capability and integration complexity. We need consistent, cross-vendor observability.

**References:**
- InjecAgent benchmark: [arXiv:2403.02691](https://arxiv.org/abs/2403.02691)
- Multi-agent cost analysis: [arXiv:2503.13657](https://arxiv.org/pdf/2503.13657)
- OpenTelemetry GenAI: [opentelemetry.io/blog/2025/ai-agent-observability](https://opentelemetry.io/blog/2025/ai-agent-observability/)

---

## Slide 3: The Real Problem
**Key Points:**
1. 不确定性/复杂度 → 安全性问题: "quiet failures" + supply-chain style prompt/tool attacks
2. 执行环境与推理堆栈 → 高成本: token loops, planner overhead, 10×+ cost drift
3. 堆栈复杂 & 供应商碎片化: LLM SaaS + agent frameworks + ops tools → SDK碎片化

**Script (45-60s):**
Three core challenges:

A) Failures are semantic, not exceptions. There are no stack traces for bad reasoning.

B) Costs and errors propagate across LLM to tools to runtime. It's a distributed system with invisible handoffs.

C) Instrumentation is SDK-heavy and fragile, so we can't build unified, tamper-resistant causal graphs.

---

## Slide 4: Why Agent Observability ≠ APM/LLM/Serving
**Key Points:**
- APM & Serving → infrastructure SLOs (latency, throughput, GPU/memory)
- LLM Monitoring → model I/O, prompt analytics
- Missing: "Was the reasoning correct?" "Why did the agent call that tool?"

**Script (60s):**
APM and serving tell us how fast and how full the GPUs are. LLM monitoring tells us about model I/O. None alone answers: Did the agent think correctly, act appropriately, and stay within policy and budget?

**References:**
- vLLM metrics: [docs.vllm.ai/en/latest/design/metrics.html](https://docs.vllm.ai/en/latest/design/metrics.html)

---

## Slide 5: Survey - APM & Serving Observability
**Key Points:**
- Tools: Datadog, Honeycomb, vLLM, Triton
- Strengths: Infra SLOs, GPU/memory monitoring, latency tracking
- Limitations: No reasoning quality visibility, no semantic correctness checks

**Script (60s):**
APM and serving observability tools like Datadog, Honeycomb, vLLM, and Triton excel at infrastructure monitoring. They give us excellent visibility into latency, throughput, GPU utilization, and memory usage.

But they don't answer "was the reasoning correct?" or "why did the agent call that tool?". These are necessary but not sufficient for agents.

**References:**
- vLLM: [docs.vllm.ai/en/latest/design/metrics.html](https://docs.vllm.ai/en/latest/design/metrics.html)
- Triton: [docs.nvidia.com/triton metrics](https://docs.nvidia.com/deeplearning/triton-inference-server/user-guide/docs/user_guide/metrics.html)

---

## Slide 6: Survey - LLM-Centric Monitoring & Specs
**Key Points:**
- Tools: LangSmith, Langfuse, OpenInference (Phoenix), OpenLLMetry
- Strengths: Easy traces/evals, prompt analytics, cost dashboards, model I/O visibility
- Limitations: App-level hooks are brittle and tamperable, cross-layer correlation limited

**Script (60s):**
LLM-centric monitoring tools like LangSmith, Langfuse, OpenInference, and OpenLLMetry make it easy to trace model interactions through SDKs or proxies. They're strong for model I/O, prompt analytics, and cost dashboards.

But app-level hooks are brittle and tamperable, and cross-layer correlation, connecting what the model said to what the system did, remains limited.

**References:**
- LangChain observability: [docs.langchain.com/langsmith/observability](https://docs.langchain.com/langsmith/observability)

---

## Slide 7: Survey - Agent-Level Frameworks
**Key Points:**
- AgentOps: Proposes taxonomy of agent artifacts (goals/plans/tools) for observability
- Watson: Argues for cognitive observability, reconstructing reasoning without modifying runtime
- Limitations: Assume instrumented runtimes, no tamper-resistant boundary capture, no unified cost governance

**Script (60s):**
Early agent-level work is emerging. AgentOps proposes a taxonomy of agent artifacts: goals, plans, tools, for observability. Watson argues for cognitive observability, reconstructing reasoning without modifying runtime logic.

Both are promising but mostly assume instrumented runtimes and stop short of tamper-resistant boundary capture or unified cost governance across vendors.

**References:**
- AgentOps: [arXiv:2411.05285](https://arxiv.org/abs/2411.05285)

---

## Slide 8: Gap Analysis
**Key Points:**
- Instrumentation gap: App SDKs are brittle and can be bypassed
- Semantic gap: Boundary telemetry is stable but lacks intent
- Multi-agent amplifies both: More tools, more handoffs, more token spend without visibility

**Script (60-75s):**
Two complementary gaps:

First, the instrumentation gap. App SDKs are brittle and can be bypassed.

Second, the semantic gap. Boundary telemetry is stable but lacks intent.

Multi-agent makes both worse: more tools, more handoffs, more token spend without visibility.

---

## Slide 9: Two-Plane Architecture - Overview
**Key Points:**
- Data Plane: Capture at stable boundaries (vendor-neutral, tamper-resistant)
- Cognitive Plane: LLM-powered observers for semantic analysis
- Together: Trusted capture + semantic understanding

**Script (60s):**
Our architecture has two complementary planes.

The Data Plane captures telemetry at stable system boundaries: model hooks, TLS/API via uprobes, syscalls and processes via eBPF, and human feedback. This gives us vendor-neutral, tamper-resistant telemetry.

The Cognitive Plane uses agents to observe agents. LLM-powered observers do semantic evals, reconstruct decision traces, and enforce policy at scale.

---

## Slide 10: Data Plane - Boundary Capture
**Key Points:**
- Model hooks: Direct inference capture
- TLS/API uprobes: Plaintext before encryption (Tetragon/eCapture patterns)
- Syscalls/processes (eBPF): execve, file I/O without code changes
- Human feedback: Ground truth for evals

**Script (60s):**
Data Plane details: we capture at stable boundaries.

Model hooks for inference. TLS and API via uprobes to see plaintext before encryption at user-space boundaries. Syscalls and processes via eBPF to observe execve and file I/O without code changes. And human feedback for ground truth.

This approach, based on patterns from Tetragon and eCapture, is proven feasible for vendor-neutral, tamper-resistant telemetry.

**References:**
- Tetragon: [isovalent.com/blog/post/2022-05-16-tetragon](https://isovalent.com/blog/post/2022-05-16-tetragon/)
- eBPF TLS tracing: [blog.px.dev/ebpf-openssl-tracing](https://blog.px.dev/ebpf-openssl-tracing/)

---

## Slide 11: Cognitive Plane - Semantic Analysis
**Key Points:**
- LLM-powered observers: Semantic evals at scale
- Decision trace reconstruction: Connect intent to actions
- Multi-layer correlation: Link model → tools → runtime
- Policy/cost enforcement: Real-time governance actions

**Script (60s):**
The Cognitive Plane is where we need agents to observe agents.

LLM-powered observers perform semantic evaluations at scale, reconstruct decision traces to connect intent with actions, correlate signals across multiple layers: model, tools, runtime, and enforce policy and cost actions in real-time.

That's the only way to address quiet failures and scale beyond human analysis.

---

## Slide 12: 90-Day Adoption Path
**Key Points:**
- P0 (Days 1-30): Boundary tracing + minimal model I/O governance
- P1 (Days 31-60): OpenTelemetry GenAI/OpenInference spans + cost budgets
- P2 (Days 61-75): Observability agents for evals/triage
- P3 (Days 76-90): Multi-agent causal graphs + audit trails

**Script (60-75s):**
Here's a pragmatic 90-day path:

P0: deploy boundary tracing around agent workloads with minimal model I/O under governance.

P1: layer in OpenTelemetry GenAI and OpenInference spans with cost budgets.

P2: introduce observability agents for automated evals and triage.

P3: build multi-agent causal graphs and audit trails.

**References:**
- OTel GenAI: [opentelemetry.io/blog/2025/ai-agent-observability](https://opentelemetry.io/blog/2025/ai-agent-observability/)

---

## Slide 13: What to Measure
**Key Points:**
- Safety: MTTA, attack capture rate
- Cost: $/successful task, tokens per solved ticket
- Reliability: Agent incident MTTR
- Coverage: Boundary capture %, span coverage

**Script (45s):**
Measure four dimensions:

Safety: mean time to attack detection, attack capture rate.

Cost: dollars per successful task, tokens per solved ticket.

Reliability: agent incident mean time to resolution.

Coverage: percentage of boundaries captured and spans instrumented.

---

## Slide 14: Takeaways
**Key Points:**
1. Survey shows three silos (APM/Serving, LLM, Agent) and two gaps (instrumentation, semantic)
2. Data Plane + Cognitive Plane = trusted capture + semantic understanding
3. Start at boundaries, layer agentic observers, standardize with OTel GenAI

**Script (30-45s):**
Three takeaways:

The survey shows three observability silos and two critical gaps.

Data Plane plus Cognitive Plane gives you trusted capture plus semantic understanding.

Start at boundaries, layer agentic observers on top, and standardize with OpenTelemetry GenAI.

---

## Post-Talk Resource List
What they'll Google after your talk:

1. OpenTelemetry GenAI semantic conventions: [opentelemetry.io/blog/2025/ai-agent-observability](https://opentelemetry.io/blog/2025/ai-agent-observability/)
2. MCP (Model Context Protocol): [docs.github.com/en/copilot/concepts/context/mcp](https://docs.github.com/en/copilot/concepts/context/mcp)
3. eBPF TLS plaintext capture via uprobes: [blog.px.dev/ebpf-openssl-tracing](https://blog.px.dev/ebpf-openssl-tracing/)
4. AgentOps taxonomy & Watson cognitive observability: [arXiv:2411.05285](https://arxiv.org/abs/2411.05285)
5. Multi-agent cost multiplier research: [arXiv:2503.13657](https://arxiv.org/pdf/2503.13657)

---

## Timing Breakdown
- Survey & gaps (Slides 2-8): 9-10 minutes (60%)
- Architecture & adoption (Slides 9-12): 5-6 minutes (40%)
- Metrics & takeaways (Slides 13-14): 1-2 minutes

Total: approximately 15 minutes

---

## Key Differences from Paper
1. Problem-first framing: Lead with safety/cost/control concerns before solution
2. Heavier survey emphasis: 60% of talk on ecosystem landscape and gaps
3. Operational adoption path: Concrete 90-day plan with KPIs
4. Standards integration: Explicit connection to OTel GenAI, OpenInference, MCP
5. Market signals: Quantitative benchmarks (InjecAgent, cost multipliers) and qualitative practitioner pain points

---

## Optional Enhancements
1. Tooling landscape slide: 3-column comparison (APM/Serving, LLM Monitoring, Agent-level) with 2-3 tools each and key limitations
2. Backup slide on TLS/syscall capture: Feasibility details, privacy controls (masking, sampling)
3. Cost claim calibration: "Order-of-magnitude increases common; industry reports cite approximately 15× for certain workloads; peer-reviewed shows 10×+ effects"
