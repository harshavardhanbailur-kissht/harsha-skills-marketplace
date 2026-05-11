# Agentic RAG & Self-Reflective Retrieval: Exhaustive Encyclopedia

**Last Updated:** March 2026
**Scope:** Comprehensive coverage of Agentic RAG architectures, self-reflective mechanisms, implementation patterns, and production deployment strategies.

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Part 1: Evolution - Naive RAG → Advanced RAG → Agentic RAG](#part-1-evolution)
3. [Part 2: Core Agentic RAG Frameworks](#part-2-core-frameworks)
4. [Part 3: Self-Reflective Mechanisms](#part-3-self-reflective)
5. [Part 4: Advanced Architectures](#part-4-advanced-architectures)
6. [Part 5: System 1 vs System 2 Reasoning](#part-5-reasoning-paradigms)
7. [Part 6: Implementation Patterns](#part-6-implementation)
8. [Part 7: Cost-Benefit Analysis](#part-7-cost-benefit)
9. [Part 8: Production Deployment](#part-8-production)
10. [Part 9: Decision Framework](#part-9-decision-framework)

---

## Executive Summary {#executive-summary}

Agentic Retrieval-Augmented Generation (Agentic RAG) represents the frontier of information retrieval and generation systems, transcending limitations of traditional RAG by embedding autonomous AI agents that leverage reflection, planning, tool use, and multiagent collaboration to dynamically manage retrieval strategies and iteratively refine contextual understanding.

**Key Innovation:** Moving from static, one-shot retrieval to dynamic, multi-step reasoning loops where agents actively decide *what to retrieve*, *when to retrieve*, *how to synthesize* information, and *when to reflect* on their own outputs.

**Survey Reference:** The comprehensive [Agentic Retrieval-Augmented Generation survey (arXiv 2501.09136)](https://arxiv.org/abs/2501.09136) published January 2025 establishes the taxonomy and landscape of this emerging domain, categorizing systems by architecture (single-agent, multi-agent, hierarchical), reasoning pattern (System 1 vs System 2), and key capabilities (reflection, planning, tool use).

---

## Part 1: Evolution - Naive RAG → Advanced RAG → Agentic RAG {#part-1-evolution}

### 1.1 Naive RAG: The Foundation

**Characteristics:**
- Single retrieval pass: Query → Vector Search → Top-K chunks
- One-shot generation: Concatenate retrieved docs → LLM generates answer
- Fixed workflow: No adaptation to query complexity
- Minimal error recovery

**Architecture:**
```
User Query
    ↓
Vector Embedder
    ↓
Vector DB Search
    ↓
Top-K Chunks
    ↓
Prompt Template
    ↓
LLM Generation
    ↓
Answer
```

**Limitations Revealed at Scale:**
- Cannot handle multi-hop reasoning (questions requiring information synthesis across multiple documents)
- Struggles with ambiguous queries lacking context refinement
- No evaluation of retrieval quality; proceeds with possibly irrelevant chunks
- High hallucination rates when retrieved context is insufficient
- Cannot adapt to knowledge gaps dynamically

**When Appropriate:**
- Small, homogeneous document collections (<10K documents)
- Simple, factual lookup queries
- Proof-of-concept applications
- Resource-constrained environments

### 1.2 Advanced RAG: Sophistication Layer

**Key Enhancements:**

1. **Hybrid Retrieval:**
   - Combines vector search (semantic) + keyword search (BM25)
   - Ensures both conceptual understanding and exact term matching
   - Hybrid ranking algorithms merge results intelligently

2. **Re-ranking:**
   - Initial retrieval returns 100-1000 candidates
   - Lightweight cross-encoder re-ranks top-50 by relevance
   - Cross-encoder typically smaller than generation LLM, keeping costs reasonable

3. **Knowledge Graphs:**
   - Explicit entity relationships: `(Person) --[founded]--> (Company)`
   - Graph traversal enables multi-hop reasoning
   - Hybrid approach: vector search + graph queries
   - [Knowledge graphs reduce error rates by ~20%](https://www.qed42.com/insights/how-knowledge-graphs-take-rag-beyond-retrieval), with LinkedIn achieving 28.6% resolution time improvement

4. **Rewriting & Query Transformation:**
   - Multi-query expansion: Single query → 3-5 semantically similar variants
   - Problem decomposition: Complex query → sub-queries
   - Step-back prompting: Abstraction to general concepts, then retrieval

5. **Feedback Loops:**
   - Answer quality evaluation
   - Retrieval quality assessment
   - Iterative refinement of retrieved context

**Architecture:**
```
User Query
    ↓
Query Analyzer (complexity classification)
    ├─ Multi-Query Expansion
    ├─ Problem Decomposition
    └─ Step-back Abstraction
    ↓
Hybrid Retrieval Engine
    ├─ Vector Search (semantic)
    ├─ Keyword Search (exact match)
    └─ Graph Traversal (relationship extraction)
    ↓
Fusion & Re-ranking
    ├─ Candidate merging
    └─ Cross-encoder re-ranking
    ↓
Context Assembly
    ├─ Chunk selection
    ├─ Ordering
    └─ Deduplication
    ↓
Feedback Evaluation
    └─ Quality check
    ↓
LLM Generation with Enhanced Context
    ↓
Answer with Citations
```

**Performance Gains:**
- 86.31% accuracy on RobustQA benchmark (knowledge graph variant)
- ~20-30% error rate reduction vs. naive RAG
- Handles 70-80% of multi-hop questions vs. 40-50% for naive RAG

**When Appropriate:**
- Enterprise deployments with 100K-10M documents
- Diverse content types and modalities
- Multi-hop reasoning requirements
- High accuracy demands with acceptable latency (100-500ms)

### 1.3 Agentic RAG: Dynamic Intelligence Layer

**Fundamental Shift:**
Advanced RAG executes predetermined, modular workflows. Agentic RAG positions the LLM as an autonomous decision-maker orchestrating retrieval, tool use, reflection, and planning in real-time.

**Key Capabilities:**

1. **Autonomous Retrieval Decisions:**
   - Agent decides whether to retrieve for each step
   - Decides which tool/database to query
   - Decides when to stop retrieving (sufficient information acquired)

2. **Iterative Reasoning:**
   - Multi-step thought processes
   - Reflection on intermediate results
   - Self-correction of errors
   - Progressive refinement of understanding

3. **Tool Orchestration:**
   - Semantic search, keyword search, graph queries, web search, API calls
   - Conditional tool selection based on query analysis
   - Sequential or parallel tool invocation

4. **Planning & Decomposition:**
   - Break complex goals into subtasks
   - Create execution plans
   - Monitor progress and adapt plans

5. **Reflection Mechanisms:**
   - Self-grading outputs
   - Identifying gaps in knowledge
   - Re-retrieving when confidence is low
   - Validating answers against evidence

**Example Flow: Multi-Hop Question**

Question: "Which Fortune 500 company founded by Peter Thiel also invested in Airbnb, and what was their initial investment amount?"

Agentic RAG Flow:
```
1. [Planning] Decompose into subtasks:
   - Find company founded by Peter Thiel
   - Find companies that invested in Airbnb
   - Find intersection
   - Extract investment amount

2. [Retrieval-1] Search for "Peter Thiel founded company"
   → Found: PayPal (1998)

3. [Reasoning] PayPal is not Fortune 500 currently, but Founders Fund is the VC
   → Decide to search for "Peter Thiel Founders Fund Airbnb investment"

4. [Retrieval-2] Search vector DB + web search
   → Found: Founders Fund invested Series B in Airbnb

5. [Tool Use] Call web search API for specific investment amount
   → Found: $12 million Series B round

6. [Reflection] Cross-check: Founders Fund is associated with Peter Thiel ✓
   Airbnb investment confirmed ✓, Amount verified ✓

7. [Generation] Output: "Founders Fund, co-founded by Peter Thiel, invested
   $12 million in Airbnb's Series B round..."

8. [Self-Grade] Confidence: 95% (primary sources cited)
```

**Contrast with Advanced RAG:**
- Advanced RAG would execute predetermined steps: query expansion → hybrid search → re-rank → generate
- Would likely miss the PayPal → Founders Fund connection
- No ability to decide mid-flow that web search is necessary

---

## Part 2: Core Agentic RAG Frameworks {#part-2-core-frameworks}

### 2.1 CRAG: Corrective Retrieval-Augmented Generation

**Paper:** [Corrective Retrieval Augmented Generation (arXiv 2401.15884)](https://arxiv.org/abs/2401.15884)

**Core Innovation:** Lightweight retrieval evaluator that assesses document quality and triggers adaptive corrective actions.

#### Architecture

```
Query
  ↓
Retrieve (Top-K documents)
  ↓
Retrieval Evaluator (Fine-tuned T5-large)
  ↓
┌─────────────────────────────────────┐
│ Confidence Score Assessment         │
├─────────────────────────────────────┤
│ High (>85%) → CORRECT Action        │
│ Medium (50-85%) → AMBIGUOUS Action  │
│ Low (<50%) → INCORRECT Action       │
└─────────────────────────────────────┘
  ↓
┌──────────────────────────────────────────────────┐
│ Adaptive Corrective Actions:                     │
├──────────────────────────────────────────────────┤
│ CORRECT:                                         │
│ • Decompose-then-recompose technique            │
│ • Remove irrelevant information                  │
│ • Refine retrieved chunks                       │
│                                                  │
│ AMBIGUOUS:                                       │
│ • Keep refined retrieval results                │
│ • Supplement with web search                    │
│ • Synthesize hybrid results                     │
│                                                  │
│ INCORRECT:                                       │
│ • Discard faulty retrievals                     │
│ • Trigger web search (external knowledge)      │
│ • Prioritize up-to-date information            │
└──────────────────────────────────────────────────┘
  ↓
Enhanced Context
  ↓
LLM Generation
  ↓
Answer with Confidence Indicator
```

**Key Components:**

1. **Retrieval Evaluator:**
   - Binary or multi-class classifier
   - Trained on retrieval quality labels
   - Lightweight (T5-large): <100ms inference
   - Evaluates relevance, redundancy, contradiction

2. **Decompose-Then-Recompose:**
   - Decompose: Break down document into key concepts
   - Remove: Eliminate contradictory/irrelevant sections
   - Recompose: Reconstruct coherent context

3. **Web Search Integration:**
   - Dynamic query reformulation for web search
   - Relevance-based result fusion
   - Up-to-date information for time-sensitive queries

**Performance:**
- 10-15% improvement over naive RAG
- Reduced hallucination rate by ~25%
- Successfully handles temporal queries (e.g., current stock prices, recent news)

**Code Snippet (Conceptual):**
```python
def crag_workflow(query, documents):
    """CRAG: Corrective RAG workflow"""

    # 1. Retrieve initial documents
    retrieved_docs = vector_db.search(query, top_k=5)

    # 2. Evaluate retrieval quality
    evaluator = T5RetrievalEvaluator.load()
    confidence = evaluator.score(query, retrieved_docs)

    # 3. Take adaptive action based on confidence
    if confidence > 0.85:
        # CORRECT: Refine and use
        refined_context = decompose_recompose(retrieved_docs)
        action = "use_refined_retrieval"

    elif 0.5 < confidence <= 0.85:
        # AMBIGUOUS: Combine retrieval + web search
        web_results = web_search_api(query)
        refined_context = merge_results(retrieved_docs, web_results)
        action = "use_hybrid_results"

    else:  # confidence <= 0.5
        # INCORRECT: Replace with web search
        web_results = web_search_api(query)
        refined_context = web_results
        action = "use_web_search_only"

    # 4. Generate with enhanced context
    answer = llm.generate(query, context=refined_context)

    return {
        "answer": answer,
        "confidence": confidence,
        "action_taken": action,
        "source_citations": extract_citations(refined_context)
    }
```

### 2.2 CRAG-MoW: Mixture-of-Workflows for Multi-Agent Retrieval

**Innovation:** Orchestrates multiple CRAG workflow agents, each potentially using different LLM models or retrieval strategies, then synthesizes their outputs.

**Architecture:**
```
Query
  ↓
Orchestrator Agent
  ├─→ CRAG Workflow Agent-1 (LLM-A, Strategy-A)
  ├─→ CRAG Workflow Agent-2 (LLM-B, Strategy-B)
  ├─→ CRAG Workflow Agent-3 (LLM-C, Strategy-C)
  └─→ CRAG Workflow Agent-N (LLM-N, Strategy-N)
  ↓
Result Synthesis Agent
  ├─ Evaluate individual answers
  ├─ Extract reasoning from each agent
  ├─ Identify consensus/divergence
  ├─ Synthesize best-of-breed answer
  └─ Provide confidence scores
  ↓
Final Answer with Multi-Agent Attribution
```

**Key Advantages:**
- **Resilience:** If one agent fails, others continue
- **Diversity:** Multiple retrieval strategies capture different information
- **Performance:** Comparable to GPT-4o using open-source models (Llama, Mistral)
- **Interpretability:** Clear attribution to which agent contributed which insight

**Application Domain:** Materials science, chemical search, multi-modal NMR spectral retrieval

**Performance Data:**
- Achieves GPT-4o-level performance with open-source models
- Frequently preferred in comparative evaluations despite using smaller models
- Reveals performance variations across data types, enabling optimization

### 2.3 Self-RAG: Self-Reflective Retrieval with Critique Tokens

**Paper:** [Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection (arXiv 2310.11511)](https://arxiv.org/abs/2310.11511)

**Core Innovation:** Train arbitrary LLM with special reflection tokens for adaptive retrieval decisions and multi-dimensional quality critique.

#### The Reflection Token System

Self-RAG introduces two token families interspersed during generation:

**1. Retrieval Tokens (ISRET):**
- `[Retrieve]`: Model decides retrieval is needed
- `[No Retrieve]`: Model decides current knowledge is sufficient
- **Decision Criteria:**
  - Knowledge-intensive queries (facts, recent events): Retrieve
  - Reasoning tasks (logic, synthesis): May not need retrieval
  - Creativity tasks (storytelling): Retrieve if grounding needed

**2. Critique Tokens (ISSUP, ISREL, ISUSE):**
- `[Relevant]` / `[Irrelevant]`: Is retrieved passage relevant to query?
- `[Supported]` / `[Unsupported]`: Is generated text factually supported by passage?
- `[Useful]` / `[Useless]`: Is the answer useful and complete?

#### Generation Process with Reflection

```
LLM Generation Loop:
┌──────────────────────────────────────────────┐
│ Token-by-token generation with reflection    │
├──────────────────────────────────────────────┤
│ 1. Generate token_1: "The capital"           │
│    ↓                                          │
│    If [Retrieve] token generated:            │
│      → Query retriever for passage           │
│      → Continue generation with passage ctx  │
│                                              │
│ 2. Generate token_2: "of France"             │
│    ↓                                          │
│    Generate [Supported] or [Unsupported]    │
│    If [Unsupported]:                        │
│      → Mark for re-generation or warning    │
│                                              │
│ 3. Generate token_3: "is Paris"              │
│    ↓                                          │
│    Generate [Useful] or [Useless]           │
│    If [Useless]:                            │
│      → Trigger retrieval or re-generation   │
│                                              │
│ 4. Continue until [EOS]                      │
└──────────────────────────────────────────────┘
```

**Training Procedure:**

1. **Data Preparation:**
   - Generate critique labels using GPT-4 on training data
   - Annotate which passages are relevant/irrelevant
   - Label which outputs are supported/unsupported

2. **Model Training:**
   - Expand vocabulary to include reflection tokens
   - Train on input-reflection-output sequences
   - Optimize next-token prediction with reflection tokens

3. **Three-Model Architecture:**
   - **Retriever:** Returns relevant passages
   - **Critic:** Scores generation quality
   - **Generator:** Main LLM trained with reflection tokens

**Performance:**
- 7B and 13B Self-RAG models outperform ChatGPT on:
  - Open-domain QA (+5-8% accuracy)
  - Reasoning tasks (+3-6%)
  - Fact verification (+10-15%)
  - Long-form generation (fewer hallucinations)

**Benefits:**
- **Adaptive Retrieval:** Only retrieves when beneficial
- **Multi-Dimensional Quality:** Evaluates relevance, factuality, usefulness
- **Interpretability:** Reflection tokens provide reasoning transparency
- **Single Model:** No separate evaluator needed (unlike CRAG)

**Code Concept:**
```python
class SelfRAG(transformers.PreTrainedModel):
    """Self-RAG model with reflection tokens"""

    REFLECTION_TOKENS = {
        'retrieve': '[Retrieve]',
        'no_retrieve': '[No Retrieve]',
        'relevant': '[Relevant]',
        'irrelevant': '[Irrelevant]',
        'supported': '[Supported]',
        'unsupported': '[Unsupported]',
        'useful': '[Useful]',
        'useless': '[Useless]'
    }

    def generate_with_reflection(self, query, max_length=200):
        """Generate with adaptive retrieval and critique"""

        input_ids = self.tokenizer(query, return_tensors='pt')
        generated = []

        for _ in range(max_length):
            # Predict next token
            next_token_logits = self(input_ids).logits[:, -1, :]
            next_token = next_token_logits.argmax(-1)

            # Check if reflection token
            token_text = self.tokenizer.decode(next_token)

            if token_text == '[Retrieve]':
                # Trigger retrieval
                query_text = self.tokenizer.decode(input_ids[0])
                passages = self.retriever.search(query_text)

                # Augment context with retrieved passages
                input_ids = augment_with_passages(input_ids, passages)

            elif token_text in ['[Supported]', '[Useful]']:
                # Good signal, continue
                pass

            elif token_text in ['[Unsupported]', '[Useless]']:
                # Poor signal, may trigger re-generation or retrieval
                if confidence_low():
                    input_ids = self.retriever.augment(input_ids)

            generated.append(token_text)
            input_ids = torch.cat([input_ids, next_token.unsqueeze(1)], dim=1)

        return ''.join(generated)
```

---

## Part 3: Self-Reflective Mechanisms {#part-3-self-reflective}

### 3.1 The Reflection Pattern in Agentic Systems

**Three-Phase Loop:**

```
Phase 1: Generation
  ↓
Agent generates initial response, plan, or intermediate output
  ↓
↓─────────────────────────────────────────────────────┐
│ What was output?                                    │
│ - Answer to user query                              │
│ - Intermediate reasoning step                       │
│ - Retrieved context assessment                      │
│ - Tool invocation decision                          │
└─────────────────────────────────────────────────────┘
  ↓
Phase 2: Self-Reflection (Critical Evaluation)
  ↓
Agent evaluates own output against quality criteria:
  ├─ Relevance: Does it address the query?
  ├─ Factuality: Is it grounded in evidence?
  ├─ Completeness: Are all parts answered?
  ├─ Consistency: Does it contradict prior statements?
  ├─ Clarity: Is it understandable?
  └─ Confidence: How certain is the agent?
  ↓
┌─────────────────────────────────────────────────────┐
│ Reflection Decision Tree:                           │
├─────────────────────────────────────────────────────┤
│ Quality Score ≥ 90%?                                │
│ ├─ YES: Proceed to output                          │
│ └─ NO: Branch to Phase 3                           │
│                                                     │
│ Gaps Identified?                                    │
│ ├─ YES: Determine gap type                         │
│ └─ NO: Proceed                                      │
│                                                     │
│ Confidence < Threshold?                             │
│ ├─ YES: Trigger re-retrieval                       │
│ └─ NO: Proceed                                      │
└─────────────────────────────────────────────────────┘
  ↓
Phase 3: Iterative Refinement (if needed)
  ↓
Based on reflection, agent takes corrective action:
  ├─ Re-retrieve: Query knowledge base differently
  ├─ Decompose: Break problem into smaller parts
  ├─ Rewrite: Reformulate question for clarity
  ├─ Validate: Check output against sources
  ├─ Synthesize: Combine multiple sources
  └─ Regenerate: Create improved response
  ↓
Loop back to Phase 1 (up to N iterations)
```

### 3.2 Reflection Token Deep Dive

**Relevance Assessment:**
```
Query: "What was the impact of COVID-19 on airline industry employment?"

Generated: "Airline employment dropped sharply in 2020..."

[Relevant] → Directly addresses query impact aspect ✓
Confidence: 95%

OR

[Irrelevant] → Discusses general economic impact, not airline-specific ✗
Confidence: 45%
→ Trigger re-retrieval with refined query
```

**Support Assessment:**
```
Generated Text: "Major airlines laid off 20% of workforce in 2020."

Retrieved Context: "United Airlines reduced workforce by 24,000 employees
(about 16%) from 45,000 to 21,000 in 2020."

[Supported] → Number is within context range ✓
Confidence: 85%

vs.

Generated: "Airlines lost 50% of workforce..."
[Unsupported] → Context shows ~16%, not 50% ✗
→ Flag hallucination, regenerate with correct data
```

**Usefulness Assessment:**
```
Query: "How should I prepare for a job interview at Google?"

Generated: "Job interviews are important in hiring decisions."

[Useless] → Too generic, doesn't provide actionable guidance ✗
Confidence: 20%
→ Re-retrieve specific Google interview content
→ Regenerate with concrete tips

vs.

Generated: "Prepare by reviewing Google's core competencies (Problem-
Solving, Communication, Leadership), practicing system design problems
on LeetCode, and researching Google's recent products."

[Useful] → Specific, actionable, directly addresses query ✓
Confidence: 90%
```

### 3.3 Implementing Reflection Loops in LangGraph

**Reference:** [LangChain Blog: Self-Reflective RAG with LangGraph](https://blog.langchain.com/agentic-rag-with-langgraph/)

**Graph Structure:**
```
State Machine with Nodes:
┌──────────────────────────────────────────┐
│ Node: retrieve                           │
│ Action: Execute vector DB query          │
│ Output State: documents, question        │
└──────────────────────────────────────────┘
              ↓
┌──────────────────────────────────────────┐
│ Node: generate                           │
│ Action: LLM generates answer from docs   │
│ Output State: answer                     │
└──────────────────────────────────────────┘
              ↓
┌──────────────────────────────────────────┐
│ Node: grade_documents                    │
│ Action: Check relevance of retrieved docs│
│ Output State: filtered_documents, grade  │
└──────────────────────────────────────────┘
              ↓
        ┌─────────────┐
        │ All relevant?
        ├─────────────┤
        │ YES   │ NO  │
        ↓       ↓
      grade   web_search
      answer    (fallback)
        ↓       ↓
        └──→ merge & retry
              ↓
        ┌──────────────┐
        │ Node: grade
        │ _answer      │
        │ Action: Check│
        │ faithfulness │
        └──────────────┘
              ↓
        ┌─────────────┐
        │ Faithful?   │
        ├─────────────┤
        │ YES │ NO    │
        ↓      ↓
     output  rewrite
```

**Code Example (LangGraph):**
```python
from langgraph.graph import StateGraph, END
from langgraph.types import Send
from typing import TypedDict

class AgentState(TypedDict):
    question: str
    documents: list
    answer: str
    feedback: str
    iterations: int

def retrieve_node(state: AgentState):
    """Retrieve documents from vector DB"""
    retriever = get_retriever()
    docs = retriever.invoke(state["question"])
    return {**state, "documents": docs}

def generate_node(state: AgentState):
    """Generate answer from documents"""
    llm = get_llm()
    prompt = create_rag_prompt(state["question"], state["documents"])
    answer = llm.invoke(prompt)
    return {**state, "answer": answer}

def grade_documents_node(state: AgentState):
    """Check if documents are relevant to question"""
    llm = get_llm()

    grades = []
    for doc in state["documents"]:
        grade_prompt = f"""
        Question: {state['question']}
        Document: {doc}

        Is this document relevant? (yes/no)
        """
        grade = llm.invoke(grade_prompt)
        grades.append(grade.lower() == "yes")

    filtered_docs = [d for d, g in zip(state["documents"], grades) if g]

    return {
        **state,
        "documents": filtered_docs,
        "feedback": f"Filtered {len(grades) - len(filtered_docs)} irrelevant docs"
    }

def grade_answer_node(state: AgentState):
    """Check if answer is grounded in documents"""
    llm = get_llm()

    grade_prompt = f"""
    Question: {state['question']}
    Answer: {state['answer']}
    Documents: {state['documents']}

    Is the answer grounded in the documents? (yes/no)
    Explanation?
    """

    grade = llm.invoke(grade_prompt)

    if "yes" in grade.lower():
        return {**state, "feedback": "Answer is grounded"}
    else:
        return {**state, "feedback": "Answer not grounded, needs re-retrieval"}

def should_retry(state: AgentState):
    """Decide whether to retry or output"""
    if state["iterations"] > 3:
        return "output"  # Give up after 3 retries

    if "not grounded" in state["feedback"].lower():
        return "retrieve"  # Try different retrieval
    elif "filtered" in state["feedback"]:
        return "web_search"  # Fallback to web
    else:
        return "output"

def web_search_node(state: AgentState):
    """Fallback to web search"""
    web_results = web_search_api(state["question"])
    return {**state, "documents": web_results}

# Build graph
graph = StateGraph(AgentState)
graph.add_node("retrieve", retrieve_node)
graph.add_node("generate", generate_node)
graph.add_node("grade_documents", grade_documents_node)
graph.add_node("grade_answer", grade_answer_node)
graph.add_node("web_search", web_search_node)

graph.add_edge("retrieve", "generate")
graph.add_edge("generate", "grade_documents")
graph.add_conditional_edges(
    "grade_documents",
    should_retry,
    {
        "retrieve": "retrieve",  # Loop for poor retrieval
        "web_search": "web_search",  # Fallback
        "output": END
    }
)
graph.add_edge("grade_answer", END)
graph.add_edge("web_search", "generate")

runnable = graph.compile()
```

---

## Part 4: Advanced Architectures {#part-4-advanced-architectures}

### 4.1 Adaptive RAG: Complexity-Based Query Routing

**Key Insight:** Not all queries need the same retrieval strategy. Simple queries (direct lookup) should skip retrieval; complex queries need multi-hop reasoning.

**Query Complexity Classifier:**
```
Architecture:
Query Input
    ↓
    ┌─────────────────────────────────────┐
    │ Complexity Classifier               │
    │ (Lightweight LLM: Phi-2, Llama-7B) │
    │ Classification latency: <1ms        │
    └─────────────────────────────────────┘
    ↓
    Three-Way Decision:
    ├─ Simple (0-33% complexity)
    │  └─ Direct LLM Generation (skip retrieval)
    │     • Latency: 80-120ms
    │     • Cost: 1x token overhead
    │
    ├─ Moderate (34-67% complexity)
    │  └─ Single-Hop Retrieval
    │     • 1 retrieve + 1 generate call
    │     • Latency: 200-300ms
    │     • Cost: 2x token overhead
    │
    └─ Complex (68-100% complexity)
       └─ Multi-Hop Retrieval
          • Multiple retrieve calls, decomposition
          • Latency: 400-800ms
          • Cost: 5-10x token overhead
```

**Performance Metrics:**
- Classifier accuracy: 85-92% with small LLMs
- Latency reduction: 35% P50, 20% P99 vs. always-retrieve baseline
- Cost reduction: 28% via skipped unnecessary retrievals
- Accuracy improvement: +8% (targeted retrieval is more precise)

**Implementation:**
```python
class AdaptiveRAG:
    def __init__(self):
        self.complexity_classifier = load_model("phi-2")  # Small, fast
        self.retriever = load_retriever()
        self.llm = load_llm("gpt-4")

    def classify_complexity(self, query: str) -> str:
        """Classify query complexity"""
        prompt = f"""
        Rate query complexity (simple/moderate/complex):
        Query: {query}

        Reasoning:
        - Simple: Direct fact lookup, single concept
        - Moderate: Requires 1-2 retrieval steps, straightforward synthesis
        - Complex: Multi-hop reasoning, contradictory sources, time-sensitive
        """

        classification = self.complexity_classifier(prompt)
        return classification.split('\n')[0].lower()

    def answer_query(self, query: str) -> str:
        """Route based on complexity"""

        complexity = self.classify_complexity(query)

        if complexity == "simple":
            # Direct generation
            answer = self.llm(query)
            return answer

        elif complexity == "moderate":
            # Single-hop retrieval
            docs = self.retriever.search(query, k=5)
            context = "\n".join(docs)
            answer = self.llm(f"Context: {context}\n\nQuestion: {query}")
            return answer

        else:  # complex
            # Multi-hop with decomposition
            subtasks = self.decompose(query)
            results = []

            for subtask in subtasks:
                docs = self.retriever.search(subtask, k=10)
                context = "\n".join(docs)
                result = self.llm(f"Subtask: {subtask}\nContext: {context}")
                results.append(result)

            # Synthesize
            final_answer = self.llm(f"Synthesize: {results}\n\nOriginal query: {query}")
            return final_answer
```

### 4.2 Active RAG: Proactive Retrieval Timing Decisions

**Challenge:** When to retrieve is non-obvious. Retrieving too early wastes resources; too late misses information.

**Unified Active Retrieval (UAR) Framework:**

Four orthogonal criteria for retrieval timing:

1. **Time-Sensitive (T):** Query requires current information
   - Examples: Stock prices, weather, breaking news
   - Heuristic: Keywords like "current", "today", "latest"

2. **LLM-Unknown (U):** Query about facts outside training data
   - Examples: Recent events, proprietary data, specific products
   - Heuristic: Questions about dates post-training cutoff

3. **Knowledge-Intensive (K):** Query inherently needs grounding
   - Examples: Medical diagnosis, legal analysis
   - Heuristic: Domain classification (medical, legal, financial)

4. **Ambiguous Query (A):** Query lacks sufficient context
   - Examples: Pronouns, underspecified references
   - Heuristic: Query length, entity mention count

**Decision Logic:**
```
Input Query
    ↓
┌────────────────────────────────────┐
│ Check each criterion (T, U, K, A)  │
├────────────────────────────────────┤
│ T (Time-Sensitive)?                │
│  - Check for temporal keywords     │
│  - Compare date mentions to cutoff │
│                                    │
│ U (LLM-Unknown)?                   │
│  - Check for entity novelty        │
│  - Check for out-of-training data  │
│                                    │
│ K (Knowledge-Intensive)?           │
│  - Classify domain (med/legal/etc) │
│  - Check query complexity          │
│                                    │
│ A (Ambiguous)?                     │
│  - Count entity mentions           │
│  - Detect pronouns                 │
│  - Check question clarity          │
└────────────────────────────────────┘
    ↓
┌────────────────────────────────────┐
│ Score aggregation:                 │
│ retrieval_score = sum(T,U,K,A)    │
│ If score ≥ threshold (e.g., 2):   │
│   → RETRIEVE                       │
│ Else:                              │
│   → SKIP RETRIEVAL                 │
└────────────────────────────────────┘
```

**Benefits:**
- Prevents unnecessary retrievals for general knowledge
- Captures time-sensitive needs automatically
- Reduces latency for simple queries
- Maintains accuracy for knowledge-intensive tasks

### 4.3 Multi-Agent Orchestration Patterns

**Pattern 1: Supervisor Pattern (Hierarchical)**
```
User Query
    ↓
┌─────────────────────────────────────┐
│ Supervisor Agent                    │
│ - Route to specialized agents       │
│ - Monitor progress                  │
│ - Validate outputs                  │
│ - Synthesize final answer           │
└─────────────────────────────────────┘
    ↓
    ├─→ [Domain Expert Agent: Medical]
    │   • Specialized tools: medical DB, FDA database
    │   • Expert LLM fine-tuned on medical text
    │   └─→ [Sub-agent: Drug Info]
    │   └─→ [Sub-agent: Symptom Analysis]
    │
    ├─→ [Domain Expert Agent: Financial]
    │   • Specialized tools: stock API, financial DB
    │   • Expert LLM fine-tuned on financial data
    │   └─→ [Sub-agent: Market Analysis]
    │   └─→ [Sub-agent: Risk Assessment]
    │
    └─→ [General Knowledge Agent]
        • Fallback for unclassified queries
        • Broad retrieval from general corpus
        └─→ [Sub-agent: Web Search]
    ↓
┌─────────────────────────────────────┐
│ Synthesis & Validation              │
│ - Merge domain-specific insights    │
│ - Check for conflicts               │
│ - Provide unified answer            │
│ - Cite sources from each agent      │
└─────────────────────────────────────┘
    ↓
Final Answer
```

**Pattern 2: Sequential Workflow**
```
Query
  ↓ [Retriever Agent]
  Retrieves candidate documents
  ↓ [Evaluator Agent]
  Assesses relevance of documents
  ↓ [Refiner Agent]
  Deduplicates and prioritizes
  ↓ [Generator Agent]
  Creates initial answer
  ↓ [Critic Agent]
  Evaluates answer quality
  ↓ [Route Decision]
  If quality > threshold: Output
  Else: Loop back to [Retriever Agent] with refined query
```

**Pattern 3: Parallel Tool Invocation**
```
Query
  ↓
Agent decides needed tools:
  ├─→ [Vector Search Tool] (in parallel)
  ├─→ [Graph Query Tool] (in parallel)
  ├─→ [Web Search Tool] (in parallel)
  └─→ [API Call Tool] (in parallel)
  ↓
All results returned simultaneously
  ↓
Agent orchestrates synthesis:
  - Deduplicates identical information
  - Resolves contradictions
  - Ranks by relevance
  ↓
Generate comprehensive answer
```

**Pattern 4: Hierarchical Task Planning**
```
Meta-Agent (Main Orchestrator)
  ├─ Parses user request
  ├─ Decomposes into subtasks
  └─ Creates task graph
      ↓
  Task-1: [Gather market data]
    ├─ Sub-Agent-1a: Price retrieval
    └─ Sub-Agent-1b: Competitor analysis
      ↓
  Task-2: [Calculate metrics]
    ├─ Sub-Agent-2a: Financial ratio computation
    └─ Sub-Agent-2b: Trend analysis
      ↓
  Task-3: [Synthesize report]
    └─ Sub-Agent-3: Summary generation
      ↓
  Meta-Agent validates each output and adjusts plan as needed
      ↓
Final consolidated answer
```

---

## Part 5: System 1 vs System 2 Reasoning {#part-5-reasoning-paradigms}

### 5.1 Cognitive Framework Applied to RAG

**System 1 (Fast, Intuitive):**
- Automatic, low-effort processing
- Pattern matching from training data
- Heuristic-based decisions
- Low latency, lower accuracy potential

**System 2 (Slow, Deliberate):**
- Effortful, controlled processing
- Step-by-step reasoning
- Tool use and external verification
- High latency, higher accuracy potential

### 5.2 System 1 RAG Approach (Predefined Reasoning)

**Characteristics:**
- Fixed, modular workflows
- Predetermined retrieval strategies
- No runtime adaptation
- Fast execution (100-200ms)

**Example Pipeline:**
```
Query → Expand (multi-query) → Search → Rerank → Generate → Answer
```

**Strengths:**
- Predictable latency
- Easy to optimize and debug
- Familiar pattern for practitioners
- Cost-effective

**Limitations:**
- Cannot adapt to query nuances
- Fails on queries outside design assumptions
- No mid-execution correction
- Limited to predefined workflows

### 5.3 System 2 RAG Approach (Agentic Reasoning)

**Characteristics:**
- Dynamic decision-making at runtime
- Autonomous tool orchestration
- Reflection and self-correction
- Slower execution (1-10 seconds) but higher accuracy

**Example Flow:**
```
Query
  ↓
[Agent Thinks: What type of question is this?]
  → Domain classification
  → Complexity assessment
  → Information need analysis
  ↓
[Agent Plans: How should I approach this?]
  → Decompose into subtasks (if complex)
  → Select appropriate tools
  → Design retrieval strategy
  ↓
[Agent Retrieves]
  → Execute planned retrieval
  → Evaluate quality of results
  → Decide if sufficient or need more
  ↓
[Agent Reasons]
  → Synthesize information
  → Connect across sources
  → Identify gaps
  ↓
[Agent Reflects]
  → Self-grade the answer
  → Check factuality
  → Verify completeness
  ↓
[Agent Decides]
  → Output if confident (>90%)
  → Loop back if confidence low (<70%)
  → Use alternative tool/strategy if stuck
  ↓
Final Answer
```

**Strengths:**
- Handles novel, complex queries
- Corrects errors mid-execution
- Learns from reasoning process
- Adapts to edge cases

**Limitations:**
- Higher latency (user wait time)
- More costly (multiple LLM calls)
- Harder to predict behavior
- Requires more sophisticated infrastructure

### 5.4 Hybrid Approach: System 1 → System 2 Escalation

**Recommended Production Pattern:**

```
Query arrives
  ↓
[System 1 Fast Path]
Complexity classifier: <2ms
  ├─ Simple query (probability > 85%)?
  │  └─ Use fast, predetermined pipeline
  │     └─ Latency: 100-200ms
  │
  └─ Complex query (probability > 85%)?
     └─ Escalate to System 2 Agentic path
        └─ Latency: 2-5 seconds

Threshold Query (50-85% probability)?
  └─ Use hybrid: Fast System 1 + System 2 fallback
     └─ Return System 1 result with offer to "analyze further"
     └─ Enable user-triggered escalation to System 2
```

**Example Decision Boundary:**
```
System 1 Only: "What is the capital of France?"
  → Classification: Simple geography (99% confidence)
  → Path: Direct LLM generation
  → Time: 80ms

System 1 with System 2 Fallback: "What were the top 3 reasons for the 2008
financial crisis and how did they differ from the 2020 COVID recession?"
  → Classification: Complex, multi-factor comparison (72% confidence)
  → Path: Try fast pipeline first
  → If quality score <75%: Escalate to full agentic reasoning
  → Time: 150ms or 3s + fallback trigger

System 2 Only: "Given recent supply chain disruptions in semiconductor
manufacturing, what scenarios should our company prepare for, and what
do industry experts recommend?"
  → Classification: Complex, requires current info (98% confidence)
  → Path: Full agentic reasoning with web search capability
  → Time: 4-6 seconds

System 2 Preferred (Cost-Aware): "Help me prepare for a senior engineer
interview at a top tech company"
  → Classification: Complex, domain-specific, subjective (89% confidence)
  → Path: System 2 with human feedback loop
  → Time: 5-8 seconds (with optional human input)
```

---

## Part 6: Implementation Patterns {#part-6-implementation}

### 6.1 LangChain Implementation

**Self-Reflective RAG with CRAG:**

```python
from langchain.chat_models import ChatOpenAI
from langchain.vectorstores import Pinecone
from langchain.text_splitters import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader
from langchain.retrievers import BM25Retriever
from langchain.schema import Document

# 1. Setup retriever
vector_store = Pinecone.from_documents(
    documents=docs,
    embedding=OpenAIEmbeddings(),
    index_name="rag-index"
)
keyword_retriever = BM25Retriever.from_documents(docs)

# 2. Hybrid retrieval
def hybrid_retrieve(query: str, k: int = 5):
    """Combine vector + keyword retrieval"""
    vector_results = vector_store.similarity_search(query, k=k)
    keyword_results = keyword_retriever.get_relevant_documents(query)

    # Deduplicate and rank
    all_results = vector_results + keyword_results
    unique_docs = {doc.metadata['source']: doc for doc in all_results}
    return list(unique_docs.values())[:k]

# 3. Retrieval evaluator (CRAG)
def evaluate_retrieval(query: str, documents: list[Document]) -> float:
    """Score retrieval quality 0-1"""
    llm = ChatOpenAI(model="gpt-3.5-turbo")

    prompt = f"""
    Query: {query}
    Documents: {[doc.page_content for doc in documents]}

    Rate how relevant these documents are to the query (0-1):
    - Are they on-topic? (50% weight)
    - Do they contain specific facts? (30% weight)
    - Are they current/reliable? (20% weight)

    Return only a number between 0 and 1.
    """

    score = float(llm.predict(prompt))
    return score

# 4. Adaptive actions (CRAG)
def crag_workflow(query: str):
    """CRAG: Corrective RAG"""

    # Retrieve
    docs = hybrid_retrieve(query)
    confidence = evaluate_retrieval(query, docs)

    if confidence > 0.85:
        # CORRECT: Use and refine
        refined_context = decompose_recompose(docs)
        action = "use_refined"

    elif 0.5 < confidence <= 0.85:
        # AMBIGUOUS: Combine with web search
        from langchain.utilities import GoogleSearchAPIWrapper
        search = GoogleSearchAPIWrapper()
        web_results = search.results(query, num_results=3)
        refined_context = merge_sources(docs, web_results)
        action = "hybrid_search"

    else:
        # INCORRECT: Fall back to web
        from langchain.utilities import GoogleSearchAPIWrapper
        search = GoogleSearchAPIWrapper()
        refined_context = search.results(query, num_results=5)
        action = "web_only"

    # Generate
    llm = ChatOpenAI(model="gpt-4")
    prompt = f"""
    Context: {refined_context}

    Question: {query}

    Provide a detailed answer, citing sources.
    """

    answer = llm.predict(prompt)

    return {
        "answer": answer,
        "confidence": confidence,
        "action": action,
        "source_docs": docs
    }

# 5. Self-reflection loop
def self_reflective_rag(query: str, max_iterations: int = 3):
    """Iterative RAG with reflection"""

    answer = None
    iteration = 0

    while iteration < max_iterations:
        iteration += 1

        # Generate
        if answer is None:
            answer = crag_workflow(query)

        # Reflect
        llm = ChatOpenAI(model="gpt-4")
        reflection_prompt = f"""
        Question: {query}
        Answer: {answer['answer']}

        Evaluate this answer:
        1. Is it directly relevant? (yes/no)
        2. Is it supported by provided sources? (yes/no/partial)
        3. Is it complete? (yes/no/partial)
        4. Confidence score (0-100)?

        If not confident, suggest improvements.
        """

        reflection = llm.predict(reflection_prompt)

        # Check confidence
        if "confidence" in reflection and "100" in reflection:
            return answer  # Good enough

        # Refine if needed
        if iteration < max_iterations:
            refined_query = llm.predict(f"""
            Original query: {query}
            Last attempt feedback: {reflection}

            Suggest an improved/clarified version of the query.
            Return only the improved query.
            """)

            query = refined_query
            answer = None  # Reset for next iteration

    return answer
```

### 6.2 LlamaIndex AgentWorkflow

**Reference:** [LlamaIndex Agentic RAG Guide](https://www.llamaindex.ai/blog/agentic-rag-with-llamaindex-2721b8a49ff6)

```python
from llama_index.workflow import Workflow, StartEvent, StopEvent
from llama_index.workflow import Event
from llama_index.agents import ReActAgent

class RAGEvent(Event):
    """Event for RAG operations"""
    query: str
    documents: list

class RetrievalEvent(Event):
    """Event for retrieval operations"""
    query: str

class ReflectionEvent(Event):
    """Event for reflection operations"""
    answer: str
    documents: list

class RAGAgentWorkflow(Workflow):
    """Complete agentic RAG workflow"""

    @staticmethod
    def retrieve(ctx, ev: RetrievalEvent):
        """Retrieve relevant documents"""
        retriever = ctx.get_tool("retriever")
        documents = retriever.retrieve(ev.query)
        return RAGEvent(query=ev.query, documents=documents)

    @staticmethod
    def generate(ctx, ev: RAGEvent):
        """Generate answer with reflection"""
        llm = ctx.get_tool("llm")

        prompt = f"""
        Query: {ev.query}
        Context: {'\n'.join(d.get_content() for d in ev.documents)}

        Generate a comprehensive answer with citations.
        Also indicate your confidence (0-100).
        """

        response = llm.complete(prompt)
        return ReflectionEvent(
            answer=response.message.content,
            documents=ev.documents
        )

    @staticmethod
    def reflect(ctx, ev: ReflectionEvent):
        """Reflect on answer quality"""
        llm = ctx.get_tool("llm")

        reflection_prompt = f"""
        Query: {ev.query}
        Answer: {ev.answer}

        Is this answer:
        1. Relevant? (yes/no)
        2. Supported by docs? (yes/no)
        3. Complete? (yes/no)

        Confidence (0-100)?
        """

        reflection = llm.complete(reflection_prompt)

        # Parse confidence score
        confidence = extract_confidence_score(reflection.message.content)

        if confidence > 85:
            return StopEvent(value={"answer": ev.answer, "confidence": confidence})
        else:
            # Re-retrieve with refined query
            refined_query = llm.complete(f"""
            Original query: {ev.query}
            Feedback: {reflection.message.content}

            Suggest refined query for better results.
            """).message.content

            return RetrievalEvent(query=refined_query)

# Build workflow
workflow = RAGAgentWorkflow()

# Wire up edges
workflow.add_event_handlers(
    RetrievalEvent,
    RAGAgentWorkflow.retrieve
)
workflow.add_event_handlers(
    RAGEvent,
    RAGAgentWorkflow.generate
)
workflow.add_event_handlers(
    ReflectionEvent,
    RAGAgentWorkflow.reflect
)

# Run
result = workflow.run(
    StartEvent(query="Your question here")
)
```

### 6.3 CrewAI Multi-Agent Orchestration

```python
from crewai import Agent, Task, Crew, Process

# Define specialized agents
research_agent = Agent(
    role="Research Specialist",
    goal="Find and synthesize relevant information",
    backstory="Expert at gathering and analyzing information from multiple sources",
    tools=[retriever_tool, web_search_tool, web_scraper_tool]
)

analysis_agent = Agent(
    role="Data Analyst",
    goal="Analyze retrieved information for insights",
    backstory="Expert at finding patterns and connections in data",
    tools=[analysis_tool, visualization_tool]
)

critic_agent = Agent(
    role="Quality Critic",
    goal="Evaluate answer quality and completeness",
    backstory="Expert at identifying gaps and ensuring high standards",
    tools=[evaluation_tool, fact_checker_tool]
)

writer_agent = Agent(
    role="Content Writer",
    goal="Synthesize insights into clear, comprehensive answer",
    backstory="Expert at communicating complex information clearly",
    tools=[writing_assistant_tool]
)

# Define tasks
research_task = Task(
    description="Research the user query and gather relevant information",
    agent=research_agent,
    expected_output="Comprehensive list of relevant sources and information"
)

analysis_task = Task(
    description="Analyze the researched information for key insights",
    agent=analysis_agent,
    expected_output="Key findings, patterns, and connections"
)

critique_task = Task(
    description="Evaluate the analysis for accuracy and completeness",
    agent=critic_agent,
    expected_output="Assessment of answer quality with suggestions for improvement"
)

writing_task = Task(
    description="Synthesize all insights into a final, well-structured answer",
    agent=writer_agent,
    expected_output="Clear, comprehensive, well-cited answer"
)

# Create crew with sequential process
crew = Crew(
    agents=[research_agent, analysis_agent, critic_agent, writer_agent],
    tasks=[research_task, analysis_task, critique_task, writing_task],
    process=Process.SEQUENTIAL
)

# Execute
result = crew.kickoff(inputs={"query": "User question here"})
```

---

## Part 7: Cost-Benefit Analysis {#part-7-cost-benefit}

### 7.1 Token Cost Breakdown

**Naive RAG Pipeline:**
```
Single Pass Example: "What is the capital of France?"
Input tokens: 150 (query + context + prompt)
Output tokens: 50 (answer)
Total: 200 tokens × $0.002/1K tokens = $0.0004 per query

Cost efficiency: Very high
Latency: 200ms
Accuracy: 70-80%
```

**Agentic RAG Pipeline:**
```
Multi-Pass Example: Complex multi-hop question

Pass 1 - Decomposition:
Input: 500, Output: 100 tokens = 600 tokens

Pass 2 - Retrieval (3 subtasks):
Input: 800 × 3, Output: 200 × 3 = 3,600 tokens

Pass 3 - Synthesis:
Input: 2,000, Output: 500 tokens = 2,500 tokens

Pass 4 - Reflection/Validation:
Input: 1,500, Output: 200 tokens = 1,700 tokens

Total: 8,400 tokens × $0.002/1K = $0.0168 per query

Cost multiplier: 42× vs. naive RAG
Latency: 5-10 seconds
Accuracy: 90-95%
```

**Trade-off Visualization:**
```
Accuracy (%)
100 │                                    ●
    │                              ●  (Agentic)
 90 │                          ●
    │                      ●
 80 │                  ●
    │              ●
 70 │          ●  (Naive)
    │      ●
 60 │
    └─────────────────────────────────
      0.0004  0.002   0.01   0.05   0.2
      Cost per query ($) [log scale]
```

### 7.2 Optimization Strategies

**1. Prompt Caching (90% input cost reduction)**
```
Without caching:
Pass 1: 500 input tokens × $0.002/1K = $0.001
Pass 2: 500 input tokens × $0.002/1K = $0.001
Pass 3: 500 input tokens × $0.002/1K = $0.001
Total: $0.003

With caching:
Pass 1: 500 input tokens × $0.002/1K = $0.001 (cache miss)
Pass 2: 500 cached tokens × $0.0002/1K = $0.0001 (cache hit, 10× cheaper)
Pass 3: 500 cached tokens × $0.0002/1K = $0.0001 (cache hit)
Total: $0.0012 (60% savings)

For Orchestrator-Worker pattern (50 workers sharing context):
Without caching: 50 × $0.002 = $0.1
With caching: 1 × $0.002 + 49 × $0.0002 = $0.012 (88% savings!)
```

**2. Query Routing (40% cost reduction)**
```
Baseline (always retrieve):
Simple query: Retrieve (2,000 tokens) + Generate (400) = 2,400 tokens
Complex query: Retrieve (5,000) + Generate (800) = 5,800 tokens
Average: 4,100 tokens

With adaptive routing:
Simple query: Skip retrieval, Generate directly (400 tokens)
Complex query: Retrieve (5,000) + Generate (800) = 5,800 tokens
Average (70% simple, 30% complex): 0.7×400 + 0.3×5,800 = 2,120 tokens

Savings: (4,100 - 2,120) / 4,100 = 48% cost reduction
```

**3. Smaller Models for Specific Tasks (70% cost reduction)**
```
GPT-4 call: 2,000 tokens × $0.03/1K = $0.06
GPT-3.5 call: 2,000 tokens × $0.001/1K = $0.002 (20× cheaper)
Llama-7B (self-hosted): 2,000 tokens × $0.00002/1K = $0.00004 (1500× cheaper)

Task-specific optimization:
- Retrieval quality grading: Use GPT-3.5 instead of GPT-4 (95% same quality)
- Decomposition: Use Llama-7B locally (85% same quality)
- Final generation: Use GPT-4 (critical, needs best quality)

Cost: $0.002 + $0.00004 + $0.06 = $0.06204 vs. $0.06 for all-GPT-4
Savings: Minimal for single query, but 50%+ for batches with better latency
```

### 7.3 Production Performance Metrics

**Composite Quality-Cost Score:**
```
Score = (w_quality × Quality) - (w_cost × Cost) - (w_latency × Latency)

Example weights: w_quality = 100, w_cost = 5, w_latency = 0.1
(Prioritize quality, then cost, then latency)

Naive RAG:
Quality: 75%, Cost: $0.0004, Latency: 200ms
Score = 100×0.75 - 5×0.0004 - 0.1×0.2 = 74.97

Adaptive RAG (routing):
Quality: 82%, Cost: $0.0006, Latency: 250ms
Score = 100×0.82 - 5×0.0006 - 0.1×0.25 = 81.95

Agentic RAG (full):
Quality: 92%, Cost: $0.015, Latency: 4000ms
Score = 100×0.92 - 5×0.015 - 0.1×4 = 90.925
```

**When Agentic ROI Becomes Positive:**
```
Break-even analysis:

Cost of poor answer:
- Incorrect medical diagnosis: $10,000+ (liability + harm)
- Wrong legal advice: $50,000+ (malpractice)
- Poor business decision: $100,000+ (opportunity cost)

Agentic RAG cost per query: $0.015
Naive RAG cost per query: $0.0004
Delta: $0.0146

Agentic RAG accuracy improvement: 20% (from 70% to 90%)

For 1,000 queries:
- Expected damage from 300 wrong answers: 300 × $10,000 = $3M
- Expected damage from 100 wrong answers (agentic): 100 × $10,000 = $1M
- Damage reduction: $2M
- Agentic cost increase: 1,000 × $0.0146 = $14.60

ROI: $2M / $14.60 = 137,000× cost reduction!
```

---

## Part 8: Production Deployment {#part-8-production}

### 8.1 Deployment Architectures

**Option 1: Serverless (e.g., AWS Lambda)**

Pros:
- No infrastructure management
- Pay-per-invocation
- Auto-scaling

Cons:
- 15-minute timeout limit (kills long agentic flows)
- Cold starts (1-5s delay)
- State management difficult

Use case: Simple RAG queries only

**Option 2: Container Orchestration (Kubernetes)**

Pros:
- Full control over execution environment
- Support for long-running agents
- Horizontal scaling
- Service mesh for reliability

Cons:
- Operational complexity
- Persistent state management challenging
- Higher baseline costs

Use case: Production agentic RAG with SLA requirements

**Option 3: Managed Agent Platforms (Render, Fly.io)**

Pros:
- Designed for agents specifically
- Long-running task support (hours)
- Built-in monitoring
- Simpler than K8s

Cons:
- Less flexibility than self-hosted
- Vendor lock-in
- Cost can be higher

Use case: Startups and teams without DevOps expertise

### 8.2 Monitoring & Observability

**Key Metrics:**
```
Latency Metrics:
- P50 (median): Should be <500ms for simple, <5s for complex
- P99 (tail): <2s for simple, <30s for complex
- Timeout rate: <0.1%

Accuracy Metrics:
- Faithfulness: % answers grounded in sources (target: >95%)
- Completeness: % questions fully answered (target: >90%)
- Hallucination rate: % made-up facts (target: <5%)

Cost Metrics:
- Cost per query: Monitor token usage trends
- Cost per successful query: Only count correct answers
- Cost anomalies: Alert if 2× baseline

System Metrics:
- Error rate: <1% (agentic loops may fail)
- Tool invocation rate: Track which tools used most
- Reflection loop iterations: Average 1-2 for good questions
```

**Observability Tools:**
- **LangSmith:** LLM-specific observability, evaluation, debugging
- **AgentOps:** Agent execution tracing, cost tracking
- **Langfuse:** LLM observability with prompt management
- **Custom dashboards:** Grafana + Prometheus for infrastructure

**Example Monitoring Code:**
```python
import time
from prometheus_client import Counter, Histogram, Gauge

# Define metrics
query_count = Counter('rag_queries_total', 'Total queries processed')
query_duration = Histogram('rag_query_duration_seconds', 'Query latency')
tokens_used = Counter('rag_tokens_total', 'Total tokens used')
answer_quality = Gauge('rag_answer_quality', 'Last answer quality score')

def instrumented_rag_query(query):
    """RAG query with monitoring"""
    start = time.time()
    query_count.inc()

    try:
        # Execute query
        answer = agentic_rag(query)
        duration = time.time() - start

        # Record metrics
        query_duration.observe(duration)
        tokens_used.inc(answer['tokens_used'])
        answer_quality.set(answer['quality_score'])

        return answer

    except Exception as e:
        # Log error
        logger.error(f"Query failed: {e}")
        raise
```

### 8.3 Caching Strategies

**Query Result Caching:**
```
Exact match cache:
Query: "What is the capital of France?"
Cached for: 30 days
Hit rate: ~5-10% for typical workloads

Semantic similarity cache:
"What is France's capital?" matches "What is the capital of France?"
Uses embedding similarity (threshold: 0.95)
Hit rate: ~15-25%

Example implementation:
def cached_rag_query(query):
    # Check exact match
    if query in exact_match_cache:
        return exact_match_cache[query]

    # Check semantic similarity
    query_embedding = embedder.embed(query)
    for cached_query, cached_answer in semantic_cache.items():
        cached_embedding = embedder.embed(cached_query)
        similarity = cosine_similarity(query_embedding, cached_embedding)
        if similarity > 0.95:
            return cached_answer

    # Not cached, compute
    answer = agentic_rag(query)
    exact_match_cache[query] = answer
    return answer
```

**Document Embedding Caching:**
```
Problem: Re-embedding same documents wastes computation
Solution: Cache embeddings for documents that don't change

Implementation:
doc_embeddings = load_from_redis("embeddings")
if doc_id not in doc_embeddings:
    embedding = embedder.embed(doc_content)
    redis.hset("embeddings", doc_id, embedding)
else:
    embedding = redis.hget("embeddings", doc_id)
```

### 8.4 Error Handling & Graceful Degradation

**Fallback Strategies:**
```
Tier 1 (Primary): Full agentic RAG
  Success rate: 85-90%
  Latency: 3-10 seconds
  Accuracy: 90-95%

Tier 2 (Fallback): Simplified retrieval (skip agentic loops)
  Success rate: 95%+
  Latency: 500-1500ms
  Accuracy: 75-85%
  Triggered when: Tier 1 fails or times out

Tier 3 (Emergency): Basic keyword search
  Success rate: 99%+
  Latency: 100-300ms
  Accuracy: 50-70%
  Triggered when: Tiers 1-2 fail

```

**Example Implementation:**
```python
async def robust_rag_query(query, user_id=None, timeout=10):
    """RAG with automatic fallback"""

    try:
        # Tier 1: Full agentic RAG
        result = await asyncio.wait_for(
            agentic_rag(query),
            timeout=timeout
        )
        log_metric("tier", "agentic", "success")
        return result

    except asyncio.TimeoutError:
        logger.warning(f"Agentic RAG timeout for query: {query}")

        try:
            # Tier 2: Simplified retrieval
            result = await asyncio.wait_for(
                simple_rag(query),
                timeout=timeout/2
            )
            log_metric("tier", "simple", "success")
            # Return with confidence indicator
            return {**result, "confidence": 0.7}

        except asyncio.TimeoutError:
            logger.error(f"Simple RAG timeout for query: {query}")

            # Tier 3: Keyword search fallback
            try:
                result = keyword_search(query)
                log_metric("tier", "keyword", "success")
                return {**result, "confidence": 0.5}

            except Exception as e:
                logger.error(f"All RAG tiers failed: {e}")
                # Return error to user gracefully
                return {
                    "answer": "I'm having trouble answering this right now. Could you try rewording the question?",
                    "confidence": 0.0,
                    "error": "system_overloaded"
                }
```

---

## Part 9: Decision Framework {#part-9-decision-framework}

### 9.1 Decision Matrix: Which Approach to Use

**Factors:**
1. Query complexity (simple, moderate, complex)
2. Accuracy requirement (70%, 85%, 95%+)
3. Latency budget (100ms, 500ms, 5s, >5s)
4. Cost tolerance (per-query cost)
5. Knowledge domain (general, specialized, proprietary)

**Decision Tree:**
```
START: New RAG Project?
  ↓
├─ "We're just starting, need quick MVP"
│  └─ → Use Naive RAG
│     Why: Fastest to deploy, lowest cost, sufficient for proof-of-concept
│     Tools: LangChain + Pinecone/Weaviate
│     Timeline: 1-2 weeks
│
├─ "Production system, high accuracy needed, moderate complexity"
│  └─ → Use Advanced RAG
│     Why: Handles 80-90% of real-world queries with good latency
│     Tools: LlamaIndex + hybrid retrieval + re-ranking
│     Timeline: 4-8 weeks
│     Features:
│       • Hybrid search (vector + keyword + graph)
│       • Re-ranking
│       • Query decomposition
│       • Feedback loops
│
└─ "Complex reasoning required, cost is secondary to accuracy"
   └─ → Use Agentic RAG
      Why: Handles multi-hop reasoning, can self-correct, adapts to unknowns
      Tools: LangGraph + LlamaIndex agents + CrewAI
      Timeline: 12-16 weeks (including evaluation framework)
      Features:
        • Multi-step planning
        • Adaptive tool selection
        • Self-reflection loops
        • Human-in-the-loop capability
        • Cost optimization (query routing, prompt caching)
```

### 9.2 Use Case Selection Guide

| Use Case | Recommended Approach | Reason | Examples |
|----------|----------------------|--------|----------|
| Simple Q&A | Naive RAG | High throughput, low cost | FAQ, basic facts |
| Multi-document search | Advanced RAG | Handles 2-3 hop reasoning | Research synthesis |
| Complex analysis | Agentic RAG | Multi-step reasoning required | Business intelligence |
| Real-time systems | Adaptive RAG | Cost/latency optimization | Customer support |
| Medical/Legal | Agentic RAG | High accuracy, liability | Clinical decision support |
| Internal knowledge base | Advanced RAG | Sufficient for most needs | Enterprise search |
| Research/Academic | Agentic RAG | Complex reasoning, citations | Literature review |
| Customer-facing chatbot | Adaptive RAG | Balance of speed & quality | E-commerce support |
| Financial analysis | Agentic RAG | Multi-source synthesis, current data | Market analysis |
| Coding assistance | Agentic RAG (System 2) | Complex reasoning, multi-file context | GitHub Copilot style |

### 9.3 Implementation Checklist

**Phase 1: Planning (Week 1)**
- [ ] Define user personas and query types
- [ ] Set accuracy targets (baseline + improvement goal)
- [ ] Establish latency SLA
- [ ] Calculate acceptable cost per query
- [ ] Identify data sources (proprietary, public, real-time)
- [ ] Plan evaluation dataset (200+ representative queries)

**Phase 2: Infrastructure (Week 2-3)**
- [ ] Choose vector database (Pinecone, Weaviate, Milvus)
- [ ] Setup document ingestion pipeline
- [ ] Implement retrieval evaluation
- [ ] Create basic hybrid retrieval (vector + keyword)
- [ ] Build monitoring infrastructure
- [ ] Implement caching layer

**Phase 3: Core RAG (Week 4-6)**
- [ ] Implement baseline naive RAG
- [ ] Evaluate on test set
- [ ] Add reranking
- [ ] Add query transformation (multi-query, decomposition)
- [ ] Implement feedback loops
- [ ] Re-evaluate and establish Advanced RAG baseline

**Phase 4: Agentic Enhancements (Week 7-12)**
- [ ] Choose orchestration framework (LangGraph, LlamaIndex)
- [ ] Implement reflection loops
- [ ] Add adaptive routing (query complexity classifier)
- [ ] Implement CRAG or Self-RAG
- [ ] Add multi-agent orchestration (if needed)
- [ ] Implement human-in-the-loop for edge cases

**Phase 5: Optimization (Week 13-14)**
- [ ] Implement prompt caching
- [ ] Optimize token usage
- [ ] Identify and cache frequent queries
- [ ] Fine-tune model selection (GPT-4 vs 3.5 vs local)
- [ ] Implement cost analytics

**Phase 6: Production Hardening (Week 15-16)**
- [ ] Implement comprehensive monitoring
- [ ] Set up alerting
- [ ] Define SLAs and error budgets
- [ ] Implement fallback strategies
- [ ] Load testing
- [ ] Security review (injection protection, PII handling)
- [ ] Documentation and runbooks

### 9.4 When NOT to Use Agentic RAG

**Avoid agentic approaches if:**

1. **Query complexity is inherently simple**
   - Example: "What are the top 3 features of product X?"
   - Use: Naive or Advanced RAG
   - Reason: Agentic overhead not justified

2. **Sub-second latency is required**
   - Example: Real-time autocomplete
   - Use: Naive RAG with caching
   - Reason: Agentic loops add 3-5s minimum latency

3. **Cost per query is critical**
   - Example: High-volume consumer application with thin margins
   - Use: Advanced RAG with careful cost optimization
   - Reason: Agentic can be 10-50× more expensive

4. **System is highly specialized and static**
   - Example: Internal knowledge base that never changes
   - Use: Advanced RAG with embedding caching
   - Reason: Predetermined workflows are efficient here

5. **Data is primarily unstructured text only**
   - Example: Article corpus without tabular/graph data
   - Use: Advanced RAG with good re-ranking
   - Reason: Hybrid approaches less beneficial

6. **Human validation is already in the pipeline**
   - Example: HR knowledge base for employee review
   - Use: Naive RAG (human will catch errors)
   - Reason: Human-in-the-loop already exists

---

## Summary: Agentic RAG Maturity Model

| Maturity Level | Approach | Timeline | Accuracy | Latency | Cost | Complexity |
|---|---|---|---|---|---|---|
| **Level 1** | Naive RAG | 1-2 weeks | 70-75% | 100-200ms | $0.0004 | Low |
| **Level 2** | Advanced RAG | 4-8 weeks | 80-88% | 300-800ms | $0.002 | Medium |
| **Level 3** | Adaptive RAG | 8-12 weeks | 82-90% | 150-2000ms (adaptive) | $0.001-0.01 | Medium-High |
| **Level 4** | Agentic RAG (Basic) | 12-16 weeks | 88-93% | 2-5s | $0.01-0.05 | High |
| **Level 5** | Agentic RAG (Advanced) | 16-24 weeks | 92-97% | 3-10s | $0.02-0.1 | Very High |

**Recommendation:** Start at Level 1-2, progress to higher levels only as:
1. Current level reaches 90%+ accuracy ceiling
2. User feedback indicates need for improvement
3. Business ROI justifies increased complexity/cost
4. Team has gained experience with lower levels

---

## Additional Resources & References

### Academic Papers
- [Agentic RAG Survey (arxiv 2501.09136)](https://arxiv.org/abs/2501.09136)
- [Corrective RAG (arxiv 2401.15884)](https://arxiv.org/abs/2401.15884)
- [Self-RAG (arxiv 2310.11511)](https://arxiv.org/abs/2310.11511)
- [Adaptive RAG (arxiv 2403.14403)](https://arxiv.org/html/2403.14403v2)
- [Unified Active Retrieval (arxiv 2406.12534)](https://arxiv.org/abs/2406.12534)
- [Reasoning RAG via System 1/2 (arxiv 2506.10408)](https://arxiv.org/abs/2506.10408)
- [From System 1 to System 2 (arxiv 2502.17419)](https://arxiv.org/abs/2502.17419)

### Frameworks & Tools
- [LangChain Agentic RAG Docs](https://docs.langchain.com/oss/python/langgraph/agentic-rag)
- [LlamaIndex Agentic RAG Guide](https://www.llamaindex.ai/blog/agentic-rag-with-llamaindex-2721b8a49ff6)
- [LangGraph Self-Reflective RAG Tutorial](https://blog.langchain.com/agentic-rag-with-langgraph/)
- [CrewAI Framework](https://github.com/joaomdmoura/crewai)
- [Mem0 Persistent Memory](https://mem0.ai/)

### Practical Guides
- [DataCamp: CRAG Implementation](https://www.datacamp.com/tutorial/corrective-rag-crag)
- [DataCamp: Self-RAG with LangGraph](https://www.datacamp.com/tutorial/self-rag)
- [Analytics Vidhya: Agentic RAG Systems](https://www.analyticsvidhya.com/blog/2024/09/how-agentic-rag-systems-transform-tech/)
- [DigitalOcean: RAG vs Agentic RAG Comparison](https://www.digitalocean.com/community/conceptual-articles/rag-ai-agents-agentic-rag-comparative-analysis)

### Production & Deployment
- [Building Production-Ready Agentic RAG Systems](https://labs.adaline.ai/p/building-production-ready-agentic)
- [IBM: Human-in-the-Loop Agents with LangGraph](https://www.ibm.com/think/tutorials/human-in-the-loop-ai-agent-langraph-watsonx-ai)
- [Microsoft: Multi-Agent Intelligence Design](https://developer.microsoft.com/blog/designing-multi-agent-intelligence)
- [Render: Deploying AI Agents to Production](https://render.com/articles/deploy-ai-agents-langchain-llamaindex-crewai)

---

**Document Status:** Complete and comprehensive as of March 2026.
**Last Review:** March 1, 2026
**Next Review:** September 1, 2026 (or when major new frameworks/papers emerge)

---

## See Also (Cross-References)

→ **references/00-search-recipes/** — Recipe #4: Agentic RAG implementation provides detailed walkthrough
→ **references/00-migration-playbooks/** — Playbook #7: Naive RAG → Agentic RAG shows step-by-step progression
→ **references/00-benchmark-matrix/** — RAG accuracy tiers comparing naive, advanced, and agentic approaches
→ **references/12-rag-patterns/** — Standard RAG patterns as baseline for agentic improvements
→ **references/38-multi-hop-reasoning/** — Multi-hop retrieval for complex multi-step questions
→ **references/45-neural-reranking-distillation/** — Reranking in agentic pipelines for improved precision
