"""
RAG System for Trauma Knot Analysis
Retrieves relevant context and generates LLM responses
"""

import os
import json
from typing import List, Dict, Optional
from datetime import datetime
from openai import OpenAI
from trauma_knot_kb import TraumaKnotKB
from dotenv import load_dotenv

# Load environment variables from .env (if present). This allows running
# the app locally by placing OPENAI_API_KEY in a .env file.
load_dotenv()


class TraumaKnotRAG:
    """RAG System combining trauma knowledge base with LLM"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize RAG system with OpenAI client"""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable not set. "
                "Set it in your shell (PowerShell: $env:OPENAI_API_KEY=\"sk-...\") "
                "or create a .env file with OPENAI_API_KEY and the library will load it."
            )
        
        self.client = OpenAI(api_key=self.api_key)
        self.kb = TraumaKnotKB()
        self.conversation_history: List[Dict] = []
        self.session_id = datetime.now().isoformat()
    
    def extract_keywords(self, user_input: str) -> List[str]:
        """Extract keywords from user input using simple heuristics"""
        # Split and filter common words
        common_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'is', 'are', 'was', 'were',
            'been', 'be', 'have', 'has', 'had', 'do', 'does', 'did', 'i', 'you',
            'he', 'she', 'it', 'we', 'they', 'my', 'your', 'his', 'her', 'its',
            'in', 'on', 'at', 'to', 'from', 'of', 'with', 'by', 'for', 'about',
            'what', 'which', 'who', 'when', 'where', 'why', 'how', 'can', 'could',
            'would', 'should', 'may', 'might', 'must', 'will', 'shall'
        }
        
        words = user_input.lower().split()
        keywords = [w.strip('.,!?;:') for w in words if w.lower() not in common_words and len(w) > 2]
        return keywords
    
    def retrieve_context(self, user_input: str) -> Dict:
        """Retrieve relevant context from knowledge base"""
        keywords = self.extract_keywords(user_input)
        
        # Find relevant nodes
        relevant_nodes = self.kb.find_relevant_nodes(keywords)
        
        # Get current trauma cycles
        trauma_cycles = self.kb.get_trauma_cycles()
        
        # Build context
        context = {
            "relevant_nodes": relevant_nodes[:5],  # Top 5 relevant nodes
            "trauma_cycles": trauma_cycles[:3],  # Top 3 cycles
            "intervention_points": [],
            "healing_pathways": []
        }
        
        # Get interventions for relevant cycles
        for cycle in trauma_cycles[:2]:
            interventions = self.kb.get_intervention_points(cycle)
            context["intervention_points"].extend(interventions)
        
        # Get healing pathways
        if relevant_nodes:
            for node in relevant_nodes[:2]:
                healing = self.kb.get_healing_pathways(node["name"])
                context["healing_pathways"].extend(healing)
        
        return context
    
    def format_context_for_llm(self, context: Dict) -> str:
        """Format retrieved context as LLM prompt"""
        prompt = "# TRAUMA KNOT FRAMEWORK CONTEXT\n\n"
        
        if context["relevant_nodes"]:
            prompt += "## Relevant Emotional/Psychological Nodes\n"
            for node in context["relevant_nodes"]:
                prompt += f"- **{node['name']}** ({node['category']}): {node['description']}\n"
            prompt += "\n"
        
        if context["trauma_cycles"]:
            prompt += "## Identified Trauma Cycles\n"
            for i, cycle in enumerate(context["trauma_cycles"], 1):
                prompt += f"{i}. {' → '.join(cycle)} → {cycle[0]}\n"
            prompt += "\n"
        
        if context["intervention_points"]:
            prompt += "## High-Priority Intervention Points\n"
            for point in context["intervention_points"][:5]:
                prompt += f"- {point['edge']}: {point['intervention']}\n"
            prompt += "\n"
        
        if context["healing_pathways"]:
            prompt += "## Healing Pathways Available\n"
            for pathway in context["healing_pathways"][:5]:
                prompt += f"- **{pathway['healing_factor']}**: {pathway['description']}\n"
            prompt += "\n"
        
        return prompt
    
    def build_system_prompt(self) -> str:
        """Build the system prompt for the LLM"""
        return """You are a compassionate and trauma-informed AI therapist assistant.

Your role is to:
1. Listen carefully to the user's experiences and struggles
2. Validate their feelings and experiences
3. Use the Trauma Knot Framework to identify patterns in their trauma responses
4. Suggest evidence-based therapeutic interventions
5. Provide psychoeducation about how trauma cycles work
6. Empower the user toward healing

Guidelines:
- Always be empathetic and non-judgmental
- Acknowledge the complexity of trauma
- Never attempt to replace professional therapy - encourage professional support
- Provide concrete, actionable suggestions
- Reference the framework concepts when helpful
- Be culturally sensitive and trauma-informed

When suggesting interventions, prioritize:
1. Safety and stabilization first
2. Psychoeducation about trauma patterns
3. Skill-building for managing symptoms
4. Addressing core negative beliefs
5. Behavioral activation and exposure when appropriate

Remember: Healing is non-linear and everyone's journey is unique."""
    
    def generate_response(self, user_input: str) -> Dict:
        """Generate LLM response with retrieved context"""
        # Retrieve context from KB
        context = self.retrieve_context(user_input)
        context_str = self.format_context_for_llm(context)
        
        # Add to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": user_input
        })
        
        # Build messages for LLM
        messages = [
            {
                "role": "system",
                "content": self.build_system_prompt() + "\n\n" + context_str
            }
        ] + self.conversation_history
        
        try:
            model_name = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
            # tokens and temperature may be configured via env, otherwise use safe defaults
            max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "1000"))
            temp_env = os.getenv("OPENAI_TEMPERATURE")
            temperature = float(temp_env) if temp_env is not None else None

            # Build base params
            base_params = {
                "model": model_name,
                "messages": messages,
            }

            # Try preferred call with max_completion_tokens (newer API) and optional temperature
            call_params = base_params.copy()
            call_params["max_completion_tokens"] = max_tokens
            if temperature is not None:
                call_params["temperature"] = temperature

            def attempt_call(params):
                return self.client.chat.completions.create(**params)

            response = None
            try:
                response = attempt_call(call_params)
            except Exception as err1:
                err_text = str(err1)
                # If temperature unsupported, retry without it
                if "temperature" in err_text and "unsupported" in err_text:
                    call_params2 = {k: v for k, v in call_params.items() if k != "temperature"}
                    try:
                        response = attempt_call(call_params2)
                    except Exception as err2:
                        err_text = str(err2)
                # If max_completion_tokens unsupported, try max_tokens
                if response is None and ("max_completion_tokens" in err_text or "unsupported_parameter" in err_text or "Unsupported parameter" in err_text):
                    call_params3 = base_params.copy()
                    call_params3["max_tokens"] = max_tokens
                    if temperature is not None and "temperature" not in call_params3:
                        call_params3["temperature"] = temperature
                    try:
                        response = attempt_call(call_params3)
                    except Exception as err3:
                        # Final fallback: try without tokens or temperature
                        try:
                            response = attempt_call(base_params)
                        except Exception as err4:
                            # Re-raise the last exception for handling in outer except
                            raise err4

            # If still None raise
            if response is None:
                raise RuntimeError("Failed to get response from LLM")

            # Extract assistant content robustly
            assistant_message = None
            try:
                assistant_message = response.choices[0].message.content
            except Exception:
                try:
                    assistant_message = response.choices[0].text
                except Exception:
                    assistant_message = str(response)

            # Add to conversation history
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })

            return {
                "response": assistant_message,
                "context": context,
                "session_id": self.session_id,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            return {
                "error": str(e),
                "response": "I encountered an error processing your request. Please try again.",
                "context": context
            }
    
    def _llm_call(self, messages: List[Dict]) -> str:
        """Internal helper to call the LLM with robust parameter handling.

        Returns assistant message string or raises an exception.
        """
        model_name = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "1000"))
        temp_env = os.getenv("OPENAI_TEMPERATURE")
        temperature = float(temp_env) if temp_env is not None else None

        base_params = {"model": model_name, "messages": messages}
        call_params = base_params.copy()
        call_params["max_completion_tokens"] = max_tokens
        if temperature is not None:
            call_params["temperature"] = temperature

        def attempt_call(params):
            return self.client.chat.completions.create(**params)

        response = None
        last_err = None
        try:
            response = attempt_call(call_params)
        except Exception as err1:
            last_err = err1
            err_text = str(err1)
            if "temperature" in err_text and "unsupported" in err_text:
                call_params2 = {k: v for k, v in call_params.items() if k != "temperature"}
                try:
                    response = attempt_call(call_params2)
                except Exception as err2:
                    last_err = err2
                    err_text = str(err2)
            if response is None and ("max_completion_tokens" in err_text or "unsupported_parameter" in err_text or "Unsupported parameter" in err_text):
                call_params3 = base_params.copy()
                call_params3["max_tokens"] = max_tokens
                if temperature is not None and "temperature" not in call_params3:
                    call_params3["temperature"] = temperature
                try:
                    response = attempt_call(call_params3)
                except Exception as err3:
                    last_err = err3
                    try:
                        response = attempt_call(base_params)
                    except Exception as err4:
                        last_err = err4

        if response is None:
            raise last_err or RuntimeError("LLM call failed without an error message")

        # Extract assistant text robustly
        try:
            return response.choices[0].message.content
        except Exception:
            try:
                return response.choices[0].text
            except Exception:
                return str(response)

    def clinical_assess_and_plan(self, user_input: str, followup_questions: int = 3) -> Dict:
        """Perform clinical-style assessment: analyze knots and ask the LLM to create
        a stepwise plan plus a set of clinician-style follow-up questions.

        Returns a dict containing analysis, suggested plan, and questions.
        """
        # Retrieve structured context from KB
        context = self.retrieve_context(user_input)

        # Enhance context with detected knots and breakpoints
        knots = self.kb.detect_trauma_knots(top_k=5) if hasattr(self.kb, 'detect_trauma_knots') else self.kb.get_trauma_cycles()
        knot_summaries = []
        for entry in knots:
            # knots may be (cycle, score, edges) or cycle list
            if isinstance(entry, tuple) and len(entry) >= 1 and isinstance(entry[0], list):
                cycle = entry[0]
                score = entry[1] if len(entry) > 1 else None
            else:
                cycle = entry
                score = None
            weakest = None
            try:
                weakest, _ = self.kb.find_break_point_for_knot(cycle)
            except Exception:
                weakest = None
            knot_summaries.append({
                "cycle": cycle,
                "score": score,
                "weakest": weakest
            })

        # Build prompt for LLM clinician
        prompt = "You are a trauma-informed clinician. Given the user description and the retrieved trauma framework context, do the following:\n"
        prompt += "1) Provide a concise analysis of the user's main trauma knots.\n"
        prompt += "2) Suggest a prioritized, step-by-step intervention plan (3-6 steps), including safety/stabilization, short-term coping, and longer-term therapeutic approaches.\n"
        prompt += f"3) Produce {followup_questions} clinician-style follow-up questions to ask the user to clarify important details (open, non-leading, compassionate).\n"
        prompt += "4) Provide crisis guidance and when to seek professional help.\n\n"

        # Append structured context
        prompt += "CONTEXT:\n"
        prompt += f"User message: {user_input}\n\n"
        prompt += "Relevant nodes:\n"
        for n in context.get('relevant_nodes', []):
            prompt += f"- {n['name']}: {n.get('description','')}\n"
        prompt += "\nIdentified cycles:\n"
        for k in knot_summaries:
            try:
                cycle_str = ' → '.join(k['cycle'])
            except Exception:
                cycle_str = str(k['cycle'])
            prompt += f"- {cycle_str} | score={k.get('score')} | weakest={k.get('weakest')}\n"
        prompt += "\nIntervention points:\n"
        for ip in context.get('intervention_points', [])[:6]:
            prompt += f"- {ip.get('edge')}: {ip.get('intervention')}\n"
        prompt += "\nHealing pathways:\n"
        for hp in context.get('healing_pathways', [])[:6]:
            prompt += f"- {hp.get('healing_factor')}: {hp.get('description')}\n"

        # Instruct the model to return structured JSON for easier parsing
        prompt += "\nIMPORTANT: Return a single valid JSON object ONLY (no additional explanatory text) with the following keys:\n"
        prompt += "- analysis: a concise clinician analysis (string)\n"
        prompt += "- plan: an array of steps; each step should be an object with keys: step (int), title (string), description (string), priority (string e.g. HIGH/MEDIUM/LOW)\n"
        prompt += "- followup_questions: an array of clinician-style follow-up question strings\n"
        prompt += "- crisis_advice: a short crisis guidance string (if applicable)\n\n"

        # Build messages
        messages = [
            {"role": "system", "content": self.build_system_prompt() + "\n\nYou are acting as a trauma-informed clinician."},
            {"role": "user", "content": prompt}
        ]

        # Call LLM
        clinician_text = self._llm_call(messages)

        # Try to parse JSON output from the model
        parsed = None
        try:
            parsed = json.loads(clinician_text)
        except Exception:
            # Attempt to extract JSON substring if model wrapped text
            import re
            match = re.search(r"\{.*\}", clinician_text, flags=re.DOTALL)
            if match:
                try:
                    parsed = json.loads(match.group(0))
                except Exception:
                    parsed = None

        if parsed and isinstance(parsed, dict):
            result = {
                "analysis": parsed.get("analysis") or parsed.get("summary") or clinician_text,
                "plan": parsed.get("plan", []),
                "followup_questions": parsed.get("followup_questions", []),
                "crisis_advice": parsed.get("crisis_advice", ""),
                "context": context,
                "knot_summaries": knot_summaries,
                "session_id": self.session_id,
                "timestamp": datetime.now().isoformat()
            }
        else:
            # Fallback: return raw clinician text
            result = {
                "analysis": clinician_text,
                "plan": [],
                "followup_questions": [],
                "crisis_advice": "",
                "context": context,
                "knot_summaries": knot_summaries,
                "session_id": self.session_id,
                "timestamp": datetime.now().isoformat()
            }

        # Add clinician message to history (raw text)
        self.conversation_history.append({"role": "assistant", "content": clinician_text})
        return result

    def generate_followup_question(self) -> str:
        """Generate the next clinician-style follow-up question based on conversation history and KB state."""
        # Summarize recent user messages
        recent_user = [m['content'] for m in self.conversation_history if m['role'] == 'user'][-3:]
        user_summary = "\n".join(recent_user)

        prompt = "You are a trauma-informed clinician. Based on the recent user messages, suggest one clear, compassionate, open-ended follow-up question that helps clarify trauma timing, triggers, safety, or coping.\n"
        prompt += f"Recent user messages:\n{user_summary}\n\n"
        prompt += "Return only the single question sentence."

        messages = [
            {"role": "system", "content": self.build_system_prompt() + "\n\nAct as a clinician asking one follow-up question."},
            {"role": "user", "content": prompt}
        ]

        return self._llm_call(messages)
    
    def save_conversation(self, filepath: str):
        """Save conversation history to file"""
        data = {
            "session_id": self.session_id,
            "created_at": datetime.now().isoformat(),
            "messages": self.conversation_history
        }
        # Sanitize filename for the current OS (Windows forbids ':' in filenames)
        dirpath = os.path.dirname(filepath) or '.'
        basename = os.path.basename(filepath)

        # Replace characters that are invalid in Windows filenames
        import re
        safe_basename = re.sub(r'[<>:"/\\|?*]', '-', basename)

        safe_path = os.path.join(dirpath, safe_basename)

        os.makedirs(dirpath, exist_ok=True)
        # Write file
        with open(safe_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

        # Return the path written for caller convenience
        return safe_path
    
    def load_conversation(self, filepath: str):
        """Load conversation history from file"""
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                data = json.load(f)
                self.conversation_history = data.get("messages", [])
                self.session_id = data.get("session_id", self.session_id)
    
    def get_conversation_summary(self) -> Dict:
        """Generate summary of conversation"""
        if len(self.conversation_history) < 2:
            return {"summary": "Conversation just started"}
        
        # Count user messages
        user_msgs = [m for m in self.conversation_history if m["role"] == "user"]
        
        return {
            "session_id": self.session_id,
            "total_exchanges": len(user_msgs),
            "message_count": len(self.conversation_history),
            "created_at": datetime.now().isoformat()
        }
    
    def reset_conversation(self):
        """Reset conversation history"""
        self.conversation_history = []
        self.session_id = datetime.now().isoformat()

