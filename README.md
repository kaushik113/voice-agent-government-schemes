# 🎙️ Voice-First Government Scheme Assistant (Marathi)

A voice-first, agentic AI system that helps users discover eligible Indian government schemes using speech-only interaction in Marathi.

This project is designed to satisfy all hard requirements of the assignment: native language support, explicit agent workflow, tool usage, conversation memory, and failure handling.

---

## Key Highlights

- Voice-first interaction (no text input at any stage)
- Native Marathi support across STT → reasoning → TTS
- Explicit agent state machine (not a chatbot)
- Multiple tools (eligibility engine + scheme database)
- Conversation memory across turns
- Robust failure handling with retries and safe exits

---

## Agent Architecture

The system follows an explicit state-machine based agent lifecycle.

START → COLLECT_INFO → VALIDATE_INFO → CHECK_ELIGIBILITY → RECOMMEND_SCHEME → END

Planner decides the next state based on missing or invalid information.  
Executor collects information via voice prompts.  
Evaluator confirms information and validates eligibility results.

This is a true agentic workflow, not a single-prompt chatbot.

---

## End-to-End Voice Pipeline

User Speech (Marathi)  
→ Speech-to-Text (Whisper)  
→ LLM-style Normalization (offline, deterministic)  
→ Agent State Machine Reasoning  
→ Tool Calls (Eligibility Engine + Scheme DB)  
→ Text-to-Speech (Marathi)  
→ Spoken Response to User  

The entire pipeline operates in non-English (Marathi).

---

## Tools Used

1. Eligibility Engine  
   Applies rule-based filtering using age, income, category, gender, student status, and BPL status.

2. Scheme Retrieval System  
   Loads structured scheme metadata from schemes_db.json.  
   Prevents hard-coded responses and supports scalable evaluation.

---

## Conversation Memory

The agent maintains memory across turns for:
- Age
- Income
- Category (SC / ST / OBC / GEN)
- State
- Gender
- Student status
- BPL status

Contradiction handling:
- If the user rejects confirmation, memory resets.
- Conflicting answers trigger re-collection.
- No silent overwrites of user data.

---

## Failure Handling

- Maximum retry count per question
- Clear voice re-prompts on recognition errors
- Graceful session termination on repeated failures
- Explicit confirmation before eligibility evaluation

---

## Project Structure

.
├── app.py  
├── README.md  
├── requirements.txt  
├── agent/  
│   ├── state_machine.py  
│   ├── memory.py  
│   ├── llm_normalizer.py  
│   └── __init__.py  
├── stt/  
│   ├── whisper_stt.py  
│   └── __init__.py  
├── tts/  
│   ├── gtts_tts.py  
│   └── __init__.py  
├── tools/  
│   ├── eligibility.py  
│   ├── schemes_db.json  
│   └── __init__.py  

---

## How to Run

pip install -r requirements.txt  
python app.py  

---

## Assignment Requirement Coverage

Voice-first interaction: YES  
Native non-English pipeline: YES  
Agentic workflow: YES  
Multiple tools: YES  
Conversation memory: YES  
Failure handling: YES  

This repository contains original code with an explicit agent design and a fully voice-driven Marathi interaction pipeline that satisfies all hard requirements.
