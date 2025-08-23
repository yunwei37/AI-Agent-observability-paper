# AgentSight: System-Level Observability for AI Agents Using eBPF

Modern software infrastructure increasingly relies on LLM agents for development and maintenance, such as Claude Code and Gemini-cli. However, these AI agents differ fundamentally from traditional deterministic software, posing a significant challenge to conventional monitoring and debugging. This creates a critical semantic gap: existing tools observe either an agent's high-level intent (via LLM prompts) or its low-level actions (e.g., system calls), but cannot correlate these two views. This blindness makes it difficult to distinguish between benign operations, malicious attacks, and costly failures. We introduce AgentSight, an observability framework that bridges this semantic gap using a hybrid approach. Our approach, *boundary tracing*, monitors agents from outside their application code at stable system interfaces using eBPF. AgentSight intercepts TLS-encrypted LLM traffic to extract semantic intent, monitors kernel events to observe system-wide effects, and causally correlates these two streams across process boundaries using a real-time engine and secondary LLM analysis. This instrumentation-free technique is framework-agnostic, resilient to rapid API changes, and incurs less than 3% performance overhead. Our evaluation shows AgentSight detects prompt injection attacks, identifies resource-wasting reasoning loops, and reveals hidden coordination bottlenecks in multi-agent systems. AgentSight is released as an open-source project at https://github.com/agent-sight/agentsight.

## Introduction

The role of machine learning in systems is undergoing a fundamental shift from optimizing well-defined tasks, such as database query planning, to a new paradigm of *agentic computing*. From a systems perspective, an AI agent couples a Large Language Model's (LLM) reasoning with direct access to system tools, granting it agency to perform operations like spawning processes, modifying the filesystem, and executing commands. This technology is being rapidly integrated into production environments, powering autonomous developer tools like [claude code](https://www.anthropic.com/news/claude-code), [cursor agent](https://cursor.com/) and [gemini-cli](https://blog.google/technology/developers/introducing-gemini-cli-open-source-ai-agent/), which can independently handle complex software engineering and system maintenance tasks. In essence, we are deploying non-deterministic ML systems, creating an unprecedented class of challenges for system reliability, security, and verification.

This paradigm shift creates a critical semantic gap: the chasm between an agent's high-level *intent* and its low-level *system actions*. Unlike traditional programs with predictable execution paths, agents use LLMs and autonomous tools to dynamically generate code and spawn arbitrary subprocesses. This makes it hard for existing observability tools to distinguish benign operations from catastrophic failures. Consider an agent tasked with code refactoring that, due to a malicious prompt it reads from external url in the search result when search for API documents, instead injects a backdoor ([indirect prompt injection](https://arxiv.org/abs/2403.02691)). An application-level monitor might see a successful "execute script" tool call, while a system monitor sees a `bash` process writing to a file. Neither can bridge the gap to understand that a benign intention has been twisted into a malicious action, rendering them effectively blind.

Current approaches are trapped on one side of this semantic gap. *Application-level instrumentation*, found in frameworks like [LangChain](https://github.com/langchain-ai/langchain) and [AutoGen](https://github.com/microsoft/autogen), captures an agent's reasoning and tool selection. While these tools see the *intent*, they are brittle, require constant API updates, and are easily bypassed: a single shell command escapes their view, breaking the chain of visibility under a flawed trust model. Conversely, *generic system-level monitoring* sees the *actions*, tracking every system call and file access. However, it lacks all semantic context. To such a tool, an agent writing a data analysis script is indistinguishable from a compromised agent writing a malicious payload. Without understanding the preceding LLM instructions, the *why* behind the *what*, its stream of low-level events is meaningless noise.

We propose boundary tracing as a novel observability method designed specifically to bridge this semantic gap. Our key insight is that while agent internals and frameworks are volatile, the interfaces through which they interact with the world (the kernel for system operations and the network for communication) are stable and unavoidable. By monitoring from outside the application at these boundaries, we can capture an agent's high-level intent and its low-level system effects. We present **AgentSight**, a system that realizes boundary tracing using eBPF to intercept TLS-encrypted LLM traffic for intent and monitor kernel events for effects. Its core is a novel, two-stage correlation process: a real-time engine links an LLM response to the system behavior it triggers, and a secondary "observer" LLM performs a deep semantic analysis on the resulting trace to infer risks and explain *why* a sequence of events is suspicious. This instrumentation-free, framework-agnostic technique incurs less than 3% overhead and effectively detects prompt injection attacks, resource-wasting reasoning loops, and multi-agent system bottlenecks.

## Background and Related Work

This section outlines LLM agent architecture, reviews existing observability work to highlight the semantic gap, and introduces eBPF as our foundational technology.

### LLM Agent Architecture

The agentic systems described in the introduction are typically implemented using a common architecture. These systems consist of three core components: (1) an LLM backend for reasoning, (2) a tool execution framework for system interactions, and (3) a control loop that orchestrates prompts, tool calls, and state management. Popular frameworks such as [LangChain](https://github.com/langchain-ai/langchain), [AutoGen](https://github.com/microsoft/autogen), [cursor agent](https://cursor.com/), [gemini-cli](https://blog.google/technology/developers/introducing-gemini-cli-open-source-ai-agent/) and [Claude Code](https://www.anthropic.com/news/claude-code) all implement variations of this model. This architecture is what enables agents to dynamically construct and execute complex plans (e.g., autonomously writing and running a script to analyze a dataset) based on high-level natural language objectives.

### Observability for LLM Agent

Existing approaches are siloed on one side of the semantic gap. Intent-side observability, supported by industry tools like Langfuse, LangSmith, and Datadog and is unifying by standards from the OpenTelemetry GenAI working group and academics conceptual taxonomies under the AgentOps concept, excels at tracing application-level events but is fundamentally blind to out-of-process system *actions*. Conversely, action-side observability with tools like Falco and Tracee offers comprehensive visibility into system calls but lacks the semantic context to understand an agent's *intent*, failing to distinguish a benign task from a malicious one. A parallel line of research into reasoning-level and interpretability aims to make the agent's internal thought processes more transparent by reconstructing cognitive traces or enabling explanatory dialogues, but these work mainly focus on the llm itself, does not bridge the gap between the agent's internal reasoning and its external, low-level effects on the system.

### extended Berkeley Packet Filter (eBPF)

To bridge the semantic gap, our approach requires a technology that can safely and efficiently observe both network communication and kernel activity. eBPF (extended Berkeley Packet Filter) is a fundamental advancement in kernel programmability that provides precisely this capability. Originally designed for packet filtering, eBPF has evolved into a general-purpose, in-kernel virtual machine that powers modern observability and security tools. For AI agent observability, eBPF is uniquely suited because it allows observation at the exact boundaries where agents interact with the world, enabling both TLS interception for semantic *intent* and syscall monitoring for system *actions* with minimal overhead. Critically, its kernel-enforced safety guarantees, including verified termination and memory safety, make it ideal for production environments and provide a stable foundation for our solution.

## Design

The design of AgentSight is guided by a single imperative: to bridge the semantic gap between an agent's intent and its actions. We achieve this through a novel observability method, boundary tracing, realized by a multi-signal correlation engine.

### Boundary Tracing: A Principled Approach

Our key insight is that all agent interactions must traverse well-defined and stable system boundaries: the kernel for system operations and the network for external communications with LLM serving backends (Figure 1). By monitoring at these boundaries rather than within volatile agent code, we achieve comprehensive monitoring independent of implementation details. This approach enables Semantic Correlation, the ability to causally link high-level intentions with low-level system events. This is supported by two principles. First is Comprehensiveness, as kernel-level monitoring ensures no system action from process creation to file I/O goes unobserved, even across spawned subprocesses. Second is Stability, since system call ABIs and network protocols evolve far more slowly than agent frameworks, providing a durable, future-proof solution. This paradigm shifts the trust model from assuming a cooperative agent to enforcing observation at tamper-proof boundaries.

![agent framework overview](figture/agent.png)
*Figure 1: agent framework overview*

### System Architecture: Observing the Boundaries

AgentSight's architecture simultaneously taps into the two critical boundaries. As shown in Figure 2, we use eBPF to place non-intrusive probes that capture a decrypted Intent Stream (LLM prompts/responses) from userspace SSL functions and an Action Stream (syscalls, process events) from the kernel. A userspace correlation engine then processes and joins these streams into a unified, causally-linked trace.

![AgentSight System Architecture](figture/arch.png)
*Figure 2: AgentSight System Architecture*

Several key components enable AgentSight to effectively bridge the semantic gap:

**eBPF for Safe, Unified Probing:** We chose eBPF for its production safety, high performance, and unified ability to access both userspace and kernel data streams. Our design intercepts decrypted data from the agent's interaction with LLM serving backend, which is more efficient and manageable than network-level packet capture or proxy-based solutions.

**Multi-Signal Causal Correlation Engine:** The core of our design is a correlation strategy that establishes causality between intent and action. We designed a multi-signal engine that relies on three key mechanisms: Process Lineage, which builds a complete process tree by tracking `fork` and `execve` events to link actions in child processes back to the parent agent; Temporal Proximity, which associates actions that occur within a narrow time window immediately following an LLM response; and Argument Matching, which directly matches content from LLM responses, such as filenames, URLs, or commands, with the arguments of subsequent system calls. Together, these signals enable AgentSight to definitively establish causal relationships between high-level intentions and low-level system operations across process boundaries.

**LLM-Powered Semantic Analysis:** To move beyond brittle, rule-based detection, we designed the system to use a secondary LLM as a reasoning engine. By prompting a powerful model with the correlated event trace, we leverage its ability to understand semantic nuance, infer causality in complex scenarios, and summarize findings in natural language. This "AI to watch AI" approach allows AgentSight to detect threats that do not match predefined patterns.

## Implementation

AgentSight is implemented as a userspace daemon (6000 lines of Rust/C) orchestrating eBPF programs, with a TypeScript frontend (3000 lines) for analysis. It is designed for high performance, processing raw kernel event streams into correlated, human-readable data.

### Data Collection at the Boundaries

Our eBPF probes capture the raw intent and action streams from the system. To capture semantic intent, an eBPF program with uprobes attaches to SSL_read/SSL_write in crypto libraries like OpenSSL to intercept decrypted LLM communications. Our userspace daemon implements a stateful reassembly mechanism to handle streaming protocols such as Server-Sent Events (SSE). To capture system actions, a second eBPF program uses stable tracepoints like sched_process_exec to build a process tree and kprobes to dynamically monitor relevant syscalls such as openat2, connect, and execve. To manage the high volume of kernel events without data loss, aggressive in-kernel filtering is applied to ensure only events from targeted agent processes are sent to userspace, minimizing overhead.

### The Hybrid Correlation Engine

The Rust-based userspace daemon houses our two-stage correlation engine. The first stage consumes events from eBPF ring buffers and performs real-time heuristic linking. This streaming pipeline enriches raw events with context like mapping a file descriptor to a full path, maintains a stateful process tree, and applies the causal linking logic described in our design, using a 100-500ms window for temporal correlation. Once a coherent trace is constructed, the second stage formats it into a structured log for semantic analysis. This log is used to construct a detailed prompt for a secondary LLM, instructing it to act as a security analyst. The LLM's natural language analysis and confidence score become the final output of our system. A key challenge at this stage is managing the latency and cost of LLM analysis, which our system mitigates through asynchronous processing and robust prompt engineering.

## Evaluation

Our evaluation is guided by two research questions: First, what is the performance overhead of AgentSight in realistic workflows? Second, how effectively does it bridge the semantic gap to detect critical security threats and performance pathologies, while also revealing complex dynamics in multi-agent systems?

### Performance Evaluation

We evaluated AgentSight on a server (Ubuntu 22.04, Linux 6.14.0) using Claude Code 1.0.62 as the test agent. The benchmarks focused on three real-world developer workflows using a [tutorial repo](https://github.com/eunomia-bpf/bpf-developer-tutorial): repository understanding with the `/init` command, code generation for bpftrace scripts, and full repository compilation with parallel builds. Each experiment was run 3 times with and without AgentSight to measure runtime overhead.

| Task | Baseline (s) | AgentSight (s) | Overhead |
|------|--------------|----------------|----------|
| Understand Repo | 127.98 | 132.33 | 3.4% |
| Code Writing | 22.54 | 23.64 | 4.9% |
| Repo Compilation | 92.40 | 92.72 | 0.4% |

*Table 1: Overhead Introduced by AgentSight*

Table 1 quantifies the runtime overhead of AgentSight across three developer workflows, with a average 2.9% overhead.

### Case Studies

We evaluated AgentSight's effectiveness through case studies that demonstrate its ability to detect security threats, identify performance issues, and provide insights into complex multi-agent systems.

#### Case Study 1: Detecting Prompt Injection Attacks

We tested AgentSight's ability to detect [indirect prompt injection attacks](https://arxiv.org/abs/2403.02691). In our test, a data analysis agent received a crafted prompt that embedded malicious commands within a legitimate request, ultimately causing it to exfiltrate `/etc/passwd`. AgentSight captured the complete attack chain: from the initial LLM interaction with the suspicious webpage to the final sensitive file read, including the intermediate subprocess spawn and outbound connection. The correlated event trace was passed to our observer LLM for analysis, which returned a high-confidence attack score (5/5). The LLM's analysis concluded that the agent's actions, executing a shell command to read `/etc/passwd` and connecting to a non-corporate domain, were logically inconsistent with its stated "analyze sales data" goal, identifying a classic data exfiltration pattern from a successful prompt injection. This demonstrates how combining intent and action provides actionable, context-aware detection.

#### Case Study 2: Reasoning Loop Detection

An agent attempting a complex task entered an infinite loop due to a common tool usage error. It repeatedly called a command-line tool with incorrect arguments, received an error, but then failed to correct its mistake, retrying the exact same failing command. AgentSight's real-time monitors detect this anomalous resource consumption from a trace of 12 API calls and passed it to the observer LLM. The LLM identified the root cause as a persistent tool error, noting the agent was caught in a "try-fail-re-reason" loop; it executed the same failing command, passed the identical error back to the reasoning LLM, and failed to learn from the tool's output. The system triggered an alert after three complete cycles, a configurable threshold, where the agent had already consumed 4,800 tokens. This intervention prevented further resource waste and service degradation, saving an estimated $2.40 in API cost, and highlighted the importance of semantic-aware monitoring.

#### Case Study 3: Multi-Agent Coordination Monitoring

AgentSight monitored a team of three collaborating software development agents, capturing 12,847 total events. For instance, Agent B was blocked for 34% of its total wall-clock time waiting on Agent A's multiple design revisions, which triggered cascading rework. File locking contention between Agent B's implementation and Agent C's testing caused 23 retry cycles. The analysis demonstrated that while the agents developed some emergent coordination, explicit mechanisms could reduce total runtime by up to 25% on this workload and message-based communication could eliminate most of the polling overhead. This reveals how boundary tracing uniquely captures multi-agent system dynamics that application-level monitoring cannot observe across process boundaries.

## Conclusion

This paper introduced AgentSight to bridge the critical semantic gap between an AI agent's intent and its system-level actions using novel *boundary tracing* approach. By leveraging eBPF, the system monitors network and kernel events without instrumentation, causally linking LLM communications to their system-wide effects via a hybrid correlation engine. Our evaluation shows AgentSight effectively detects prompt injection attacks, reasoning loops, and multi-agent bottlenecks with under 3% performance overhead. This "AI to watch AI" provides a foundational methodology for the secure and reliable deployment of increasingly autonomous AI systems.

---

## References

1. **claudecode**: Anthropic. "Introducing Claude Code." Anthropic Blog, Feb 2025. https://www.anthropic.com/news/claude-code

2. **cursor**: Anysphere Inc. "Cursor: The AI‑powered Code Editor." 2025. https://cursor.com/

3. **geminicli**: Mullen, T., Salva, R.J. "Gemini CLI: Your Open‑Source AI Agent." Google Developers Blog, Jun 2025. https://blog.google/technology/developers/introducing-gemini-cli-open-source-ai-agent/

4. **indirect-prompt-inject**: Zhan, Q., Liang, Z., Ying, Z., Kang, D. "InjecAgent: Benchmarking Indirect Prompt Injections in Tool-Integrated Large Language Model Agents." ACL Findings, 2024. https://arxiv.org/abs/2403.02691

5. **langchain**: Chase, H. "LangChain: Building applications with LLMs through composability." 2023. https://github.com/langchain-ai/langchain

6. **autogen**: Wu, Q., et al. "AutoGen: Enable Next-Gen Large Language Model Applications." Microsoft Research, 2023. https://github.com/microsoft/autogen

7. **Maierhofer2025Langfuse**: Maierhöfer, J. "AI Agent Observability with Langfuse." Langfuse Blog, March 16, 2025. https://langfuse.com/blog/2024-07-ai-agent-observability-with-langfuse

8. **langfuse**: "Langfuse - LLM Observability & Application Tracing." 2024. https://langfuse.com/

9. **langsmith**: LangChain. "Observability Quick Start - LangSmith." 2023. https://docs.smith.langchain.com/observability

10. **Datadog2023Agents**: Datadog Inc. "Monitor, troubleshoot, and improve AI agents with Datadog." Datadog Blog, 2023. https://www.datadoghq.com/blog/monitor-ai-agents/

11. **helicone**: "Helicone / LLM-Observability for Developers." 2023. https://www.helicone.ai/

12. **Liu2025OTel**: Liu, G., Solomon, S. "AI Agent Observability -- Evolving Standards and Best Practices." OpenTelemetry Blog, March 6, 2025. https://opentelemetry.io/blog/2025/ai-agent-observability/

13. **Bandurchin2025Uptrace**: Bandurchin, A. "AI Agent Observability Explained: Key Concepts and Standards." Uptrace Blog, April 16, 2025. https://uptrace.dev/blog/ai-agent-observability

14. **Dong2024AgentOps**: Dong, L., Lu, Q., Zhu, L. "AgentOps: Enabling Observability of LLM Agents." arXiv preprint arXiv:2411.05285, 2024.

15. **Moshkovich2025Pipeline**: Moshkovich, D., Zeltyn, S. "Taming Uncertainty via Automation: Observing, Analyzing, and Optimizing Agentic AI Systems." arXiv preprint arXiv:2507.11277, 2025.

16. **falco**: The Falco Authors. "Falco: Cloud Native Runtime Security." 2023. https://falco.org/

17. **tracee**: Aqua Security. "Tracee: Runtime Security and Forensics using eBPF." 2023. https://github.com/aquasecurity/tracee

18. **Rombaut2025Watson**: Rombaut, B., et al. "Watson: A Cognitive Observability Framework for the Reasoning of LLM-Powered Agents." arXiv preprint arXiv:2411.03455, 2025.

19. **Kim2025AgenticInterp**: Kim, B., et al. "Because we have LLMs, we Can and Should Pursue Agentic Interpretability." arXiv preprint arXiv:2506.12152, 2025.

20. **brendangregg**: Gregg, B. "BPF Performance Tools." Addison-Wesley Professional, 2019.

21. **ebpfio**: eBPF Community. "eBPF Documentation." 2023. https://ebpf.io/

22. **cilium**: Cilium Project. "eBPF-based Networking, Observability, and Security." 2023. https://cilium.io/

23. **kerneldoc**: Linux Kernel Community. "BPF Documentation - The Linux Kernel." 2023. https://www.kernel.org/doc/html/latest/bpf/

24. **ebpftutorial**: eunomia-bpf. "eBPF Developer Tutorial." GitHub, 2024. https://github.com/eunomia-bpf/bpf-developer-tutorial

---

**Repository**: https://github.com/eunomia-bpf/agentsight

