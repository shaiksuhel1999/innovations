# Trauma Knot RAG System - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies (1 minute)

```bash
cd D:\suhel-learning\python-test-workspace\trauma-knot-proof
pip install -r requirements_rag.txt
```

### Step 2: Configure API Key (2 minutes)

Copy the example and add your OpenAI API key:

```bash
copy .env.example .env
# Edit .env and add: OPENAI_API_KEY=sk-your-key-here
```

Get free API credits at: https://platform.openai.com/api-keys

### Step 3: Choose Your Interface (2 minutes)

#### Option A: CLI (Simplest - Command Line)
```bash
python cli.py
```

Then type:
```
chat I'm struggling with anxiety and avoidance behaviors after a traumatic event
```

#### Option B: FastAPI Server (Most Flexible)
```bash
uvicorn main:app --reload
```

Visit: http://localhost:8000/docs

#### Option C: Python Script (Most Customizable)
```python
from rag_system import TraumaKnotRAG

rag = TraumaKnotRAG()
response = rag.generate_response("Describe your trauma/problem here")
print(response["response"])
```

---

## 📋 Quick Examples

### CLI Examples

```bash
# Chat about your problem
chat I feel paralyzed by fear after my accident

# Continue conversation
continue

# View trauma cycles
cycles

# Get intervention strategies
interventions

# Visualize a cycle
visualize Fear Avoidance NegativeBelief

# Save session
save my_session.json

# Load session
load my_session.json

# Show all commands
help
```

### API Examples

**Basic Chat:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "I am avoiding my work after a conflict"}'
```

**Get All Cycles:**
```bash
curl http://localhost:8000/cycles
```

**View Conversation:**
```bash
curl http://localhost:8000/sessions/YOUR_SESSION_ID
```

### Python Examples

**Multi-turn conversation:**
```python
from rag_system import TraumaKnotRAG

rag = TraumaKnotRAG()

# First message
rag.generate_response("I'm anxious and can't sleep")

# Follow-up (maintains context)
rag.generate_response("What can help me relax?")

# Save for later
rag.save_conversation("my_conversation.json")
```

**Knowledge base exploration:**
```python
from trauma_knot_kb import TraumaKnotKB

kb = TraumaKnotKB()

# Get all cycles
cycles = kb.get_trauma_cycles()

# Get details about a node
node_info = kb.get_node_description("Fear")
print(node_info)

# Get interventions
interventions = kb.get_intervention_points(cycles[0])
```

---

## 🎯 What to Expect

### When You Submit Your Problem

The system will:

1. **Extract Keywords** - Identify key psychological terms
2. **Retrieve Context** - Find relevant trauma framework nodes
3. **Identify Cycles** - Show self-reinforcing patterns
4. **Suggest Interventions** - Provide therapeutic strategies
5. **Generate Response** - AI analysis with personalized suggestions

### Example Output

```
🤖 AI Response:
I hear you. Anxiety after trauma is a natural protective response. 
What you're describing sounds like a trauma cycle:
- Fear → Avoidance (avoiding situations to reduce fear)
- Avoidance → Fear (avoiding prevents learning that situations are safe)
- This creates a self-reinforcing loop

The good news: This cycle CAN be broken through evidence-based approaches...

📍 Relevant Nodes:
• Fear: Primary alarm response to threat
• Avoidance: Behavioral attempt to manage anxiety
• Anxiety: Anticipatory alarm state

🔥 Identified Cycles:
• Fear → Avoidance → Fear

🔧 Intervention Points:
• Exposure Therapy: Gradually face feared situations
• Safety Planning: Develop concrete safety strategies
• Grounding Techniques: Bring awareness to present moment

🌱 Healing Pathways:
• Safety: Developing sense of security
• Resilience: Building capacity to handle challenges
```

---

## 💡 Tips for Best Results

1. **Be Specific** - More details = better analysis
   - ✅ "I was in a car accident 3 months ago. Now I panic when driving"
   - ❌ "I'm scared"

2. **Multi-turn Dialogue** - Use follow-up messages
   - Ask clarifying questions
   - Explore specific cycles
   - Request concrete techniques

3. **Save Sessions** - Keep conversations for reference
   - Track patterns over time
   - Review suggestions
   - Share with therapist (with your consent)

4. **Explore the Framework**
   - Run `cycles` to understand common trauma patterns
   - Run `nodes` to learn about psychological concepts
   - Run `interventions` to see evidence-based strategies

---

## 🛠️ File Structure

```
trauma-knot-proof/
├── cli.py              ← ⭐ Start here for CLI
├── main.py             ← FastAPI server
├── demo.py             ← Example usage
├── rag_system.py       ← RAG implementation
├── trauma_knot_kb.py   ← Knowledge base
├── requirements_rag.txt
├── .env                ← Your API key (create from .env.example)
├── SETUP_GUIDE.md      ← Detailed documentation
├── QUICKSTART.md       ← This file
└── conversations/      ← Saved sessions
```

---

## ❓ Troubleshooting

**"OPENAI_API_KEY not found"**
- Create `.env` file with your API key
- Or set environment variable: `$env:OPENAI_API_KEY="sk-xxx"`

**"Connection refused on port 8000"**
- Port already in use
- Try: `uvicorn main:app --port 8001`

**"Module not found"**
- Install dependencies: `pip install -r requirements_rag.txt`

**"Poor AI responses"**
- Describe your situation in more detail
- Ensure you have GPT-4 access (fallback to GPT-3.5 if needed)

---

## 🎓 Learn More

- **Framework Details**: Read `README.md`
- **Full Documentation**: Read `SETUP_GUIDE.md`
- **API Docs**: http://localhost:8000/docs (when server running)
- **Examples**: Read `demo.py`

---

## ⚠️ Important Notes

- **NOT a replacement for therapy** - Always seek professional mental health support
- **Confidential** - Save conversations locally (not sent to Anthropic/others)
- **Educational** - Learn about trauma frameworks and healing approaches
- **Evidence-Based** - Suggestions align with established therapeutic practices

---

## 🚦 Next Steps

1. Choose your interface (CLI / API / Python)
2. Run it and submit a problem
3. Explore the trauma framework
4. Discuss patterns and interventions
5. Save your session
6. Consider professional therapy

Happy healing! 🌱

---

## Quick Command Reference

| Task | Command |
|------|---------|
| Chat | `chat Your problem here` |
| View cycles | `cycles` |
| View nodes | `nodes` |
| Get interventions | `interventions` |
| Visualize | `visualize Node1 Node2 Node3` |
| Save | `save filename.json` |
| Load | `load filename.json` |
| History | `history` |
| Help | `help` |
| Exit | `quit` |

## How it works (architecture and flow)

This section explains the internal architecture and the runtime flow so you understand what happens after you submit a problem.

- Knowledge Base (KB): `trauma_knot_kb.py` builds a directed graph representing trauma triggers, emotions, cognitions, behaviors and healing factors. It supports cycle detection, intervention point ranking, activation simulation, and graph (de)serialization.

- Retrieval component: `rag_system.py` uses lightweight heuristics to extract keywords from user input, queries the KB for relevant nodes, trauma cycles, intervention points and healing pathways, and formats that context for the LLM.

- LLM orchestration (RAG): The system combines a clinical system prompt, the retrieved context, and the user's message to create an LLM prompt. Responses are fetched through a robust helper that adapts to model parameter differences (e.g., `max_tokens` vs `max_completion_tokens`) and extracts the assistant text.

- Clinical workflow: New endpoints `/clinical/assess` and `/clinical/followup` drive a clinician-style interaction:
  - `/clinical/assess` runs `clinical_assess_and_plan()` which: (1) retrieves KB context and detected knots, (2) asks the LLM to generate a JSON structured analysis, prioritized plan (3–6 steps), follow-up questions, and crisis guidance, (3) parses the JSON and returns structured data. If the model doesn't return valid JSON, the raw clinician text is returned as fallback.
  - `/clinical/followup` uses recent user messages and session history to ask the LLM for a single compassionate follow-up question (clinician-style).

- Safety: The server performs a quick crisis-keyword scan at the endpoint level (for common emergency terms) and provides immediate crisis guidance without calling the LLM. You can extend this with a more sophisticated classifier later.

- Session & persistence: Conversations are stored in `conversations/` as JSON. Filenames are sanitized for Windows compatibility. Use `save` and `load` in the CLI or visit `/sessions/{session_id}` to retrieve history.

- Model configuration: Use `.env` or environment variables to control the model and parameters:
  - `OPENAI_API_KEY` (required)
  - `OPENAI_MODEL` (e.g., `gpt-3.5-turbo`, `gpt-4`)
  - `OPENAI_MAX_TOKENS` (default 1000)
  - `OPENAI_TEMPERATURE` (optional; only applied when supported by the model)

Flow summary when you POST to `/clinical/assess`:
1. Receive user message + session id
2. Quick crisis keyword check (if matched, return crisis advice)
3. Extract keywords and retrieve KB context (nodes, cycles, interventions, pathways)
4. Detect trauma knots and identify break-points
5. Build a clinician prompt and ask the LLM to return a single JSON object describing analysis, plan, questions, crisis guidance
6. Parse JSON (or fallback to raw text) and return structured response
7. Save conversation and return session id

This architecture keeps the knowledge base deterministic and auditable while letting the LLM provide empathic analysis and dynamic clinical questioning.

---

If you'd like, I can add a short diagram image and a small example of the JSON schema the LLM is asked to return — tell me if you want that included in the Quickstart.

## Clinical endpoints: examples and JSON schema

We added two clinician-focused endpoints to support an interactive assessment workflow:

- POST `/clinical/assess` — Run a clinician-style assessment that analyzes trauma knots, returns a prioritized plan and clinician follow-up questions (attempts to return structured JSON).
- GET `/clinical/followup` — Return a single clinician-style follow-up question based on session history.

Example: Clinical assessment (curl)

```bash
curl -X POST http://127.0.0.1:8000/clinical/assess \
  -H "Content-Type: application/json" \
  -d '{"message":"I was in a car accident and now I panic when driving; I avoid roads and have flashbacks at night."}'
```

Sample response (when model returns structured JSON):

```json
{
  "success": true,
  "session_id": "2026-06-21T14:06:40.950260",
  "analysis": "Concise clinician analysis text...",
  "knot_summaries": [
    {
      "cycle": ["Fear","Helplessness","NegativeBelief","Avoidance"],
      "score": 35.0,
      "weakest": ["Fear","Helplessness",8,16.0]
    }
  ],
  "context": { /* KB context object */ },
  "timestamp": "2026-06-21T14:06:40.950260"
}
```

JSON schema the LLM is instructed to return (recommended format)

```json
{
  "analysis": "string",
  "plan": [
    {"step": 1, "title": "Stabilization", "description": "Short-term grounding and breathing exercises", "priority": "HIGH"},
    {"step": 2, "title": "Psychoeducation", "description": "Explain trauma cycles", "priority": "MEDIUM"}
  ],
  "followup_questions": ["When did these symptoms start?", "Have you had thoughts of harming yourself?"],
  "crisis_advice": "string (if any)"
}
```

Example: Request a single follow-up question

```bash
curl "http://127.0.0.1:8000/clinical/followup?session_id=2026-06-21T14:06:40.950260"
```

Sample followup response:

```json
{
  "success": true,
  "question": "If you’re comfortable sharing, how safe do you feel right now, and what would help increase your sense of safety?",
  "session_id": "2026-06-21T14:06:40.950260"
}
```

Notes & best practices
- The system attempts to parse JSON output from the model. If parsing fails the raw clinician text is returned in `analysis` and `plan`/`followup_questions` will be empty arrays. To improve reliability, set `OPENAI_MODEL` to a model that handles structured outputs (and/or tune the prompt).
- The server performs a quick keyword-based crisis check and will return immediate crisis guidance without calling the LLM when emergency words are detected — this is a safety-first fallback and should be augmented by a fuller classifier in production.
- Keep `.env` and `OPENAI_API_KEY` secure and out of version control; use secret stores for production.

---

