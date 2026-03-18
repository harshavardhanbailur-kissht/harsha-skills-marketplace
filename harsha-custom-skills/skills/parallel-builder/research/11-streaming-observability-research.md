# Research 11: Streaming, Observability & Real-Time Monitoring

## Source Validation
- **Primary**: Anthropic Claude API Docs (Streaming Messages)
- **Secondary**: OneUptime integration guide (Jan 2026), claudeapi.net reference
- **Framework**: SSE (Server-Sent Events) specification
- **Scrutiny Level**: Enhanced (official API docs + production integration guides)

## Key Findings

### 1. Claude API Streaming Architecture
- Uses Server-Sent Events (SSE) via `stream: true` parameter
- Event types: content_block_start → content_block_delta → content_block_stop
- Each content block has an index corresponding to final Message content array
- SDK provides `.stream()` for real-time and `.get_final_message()` for accumulation

### 2. Stream Recovery Pattern
- SDK supports stream-with-recovery: partial content from broken stream can be
  included as assistant prefix in retry request
- Enables resume-from-failure at the streaming level
- **Application**: If a worker agent's stream breaks mid-response, recover partial
  output and retry with prefix rather than re-executing from scratch

### 3. Token Usage Tracking for Cost Monitoring
Production integration pattern (from OneUptime):
```python
class TokenUsageTracker:
    def __init__(self):
        self.total_input = 0
        self.total_output = 0
        self.model_prices = {
            "claude-opus-4-6": {"input": 5.0, "output": 25.0},
            "claude-sonnet-4-5": {"input": 3.0, "output": 15.0},
            "claude-haiku-4-5": {"input": 0.80, "output": 4.0},
        }

    def track(self, response):
        usage = response.usage
        self.total_input += usage.input_tokens
        self.total_output += usage.output_tokens

    def cost(self, model: str) -> float:
        prices = self.model_prices[model]
        return (self.total_input * prices["input"] +
                self.total_output * prices["output"]) / 1_000_000
```

### 4. Observability for Multi-Agent Pipelines
Key observability dimensions for our skill:
- **Per-task metrics**: tokens, latency, retry count, success/fail
- **Per-layer metrics**: parallelism utilization, bottleneck identification
- **Pipeline metrics**: total cost, total time, speedup vs sequential
- **Quality metrics**: verification pass rate, fix iteration count

### 5. Stateless Design Advantage
"Messages are stateless. Send the full history each turn to keep multi-step
workflows deterministic and easy to debug."

**Application**: Each worker agent call is independently reproducible —
log the full request (system prompt + messages) for debugging failed tasks.

### 6. Model Alias vs Pin
- `claude-sonnet-4-5` always points to latest snapshot (currently 20250929)
- **Production recommendation**: Pin exact snapshot for reproducibility
- **Our skill**: Should use pinned versions in scripts, document alias option

### 7. Real-Time Progress Reporting Architecture
For our executor, implement streaming progress:
```
Pipeline Progress:
[Layer 0] ████████████ 3/3 tasks complete (12.4s)
[Layer 1] ██████░░░░░░ 2/4 tasks complete (running...)
  - task_crud_endpoints: streaming (1,204 tokens)
  - task_middleware: streaming (892 tokens)
  - task_auth_integration: complete ✓
  - task_validation: complete ✓
[Layer 2] ░░░░░░░░░░░░ waiting for Layer 1
Cost so far: $0.047 | Tokens: 34,201
```

## Applied Improvements
1. Add streaming support to executor.py (SSE-based progress)
2. Add token/cost tracking per task and per layer
3. Add pipeline progress reporting (real-time terminal output)
4. Add request logging for reproducibility/debugging
5. Pin model versions in scripts, document alias option
6. Add stream recovery for partial agent failures
