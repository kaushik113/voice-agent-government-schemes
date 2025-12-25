import time

from stt.whisper_stt import speech_to_text
from agent.llm_normalizer import normalize
from agent.state_machine import AgentState
from agent.memory import ConversationMemory
from tools.eligibility import check_eligibility
from tts.gtts_tts import speak


# ===============================
# AUDIO HELPER
# ===============================
def speak_and_wait(text):
    speak(text)
    time.sleep(0.8)


# ===============================
# MAIN AGENT
# ===============================
def main():
    state = AgentState.START
    memory = ConversationMemory()
    eligible_schemes = []

    FIELDS = [
        "age",
        "income",
        "category",
        "state",
        "gender",
        "student",
        "bpl",
    ]

    print("Agent started (voice-only mode)")

    while state != AgentState.END:
        print(f"\nSTATE → {state.value}")

        # -------------------------------------------------
        # START
        # -------------------------------------------------
        if state == AgentState.START:
            speak_and_wait("नमस्कार, मी तुमचा सरकारी योजना सहाय्यक आहे.")
            state = AgentState.COLLECT_INFO
            continue

        # -------------------------------------------------
        # COLLECT INFO
        # -------------------------------------------------
        if state == AgentState.COLLECT_INFO:
            MAX_RETRIES = 3

            for key in FIELDS:
                if memory.get(key) is not None:
                    continue

                retries = 0
                value = None

                while retries < MAX_RETRIES:
                    print(f"Asking for {key}...")

                    # ---------- PROMPT + NORMALIZE ----------
                    if key == "age":
                        speak_and_wait("कृपया तुमचं वय सांगा.")
                        value = normalize(speech_to_text(), "age")

                    elif key == "income":
                        speak_and_wait("कृपया तुमचं वार्षिक उत्पन्न सांगा.")
                        value = normalize(speech_to_text(), "income")

                    elif key == "category":
                        speak_and_wait(
                            "तुमची जात श्रेणी निवडा. "
                            "एस सी साठी एक. "
                            "एस टी साठी दोन. "
                            "ओ बी सी साठी तीन. "
                            "जनरल साठी चार."
                        )
                        value = normalize(speech_to_text(), "category")

                    elif key == "state":
                        speak_and_wait(
                            "महाराष्ट्र मध्ये राहत असाल तर एक. "
                            "नसल्यास दोन."
                        )
                        value = normalize(speech_to_text(), "state")

                    elif key == "gender":
                        speak_and_wait(
                            "लिंग निवडा. "
                            "पुरुष साठी एक. "
                            "महिला साठी दोन."
                        )
                        value = normalize(speech_to_text(), "gender")

                    elif key == "student":
                        speak_and_wait(
                            "तुम्ही विद्यार्थी असाल तर एक. "
                            "नसाल तर दोन."
                        )
                        value = normalize(speech_to_text(), "yesno")

                    elif key == "bpl":
                        speak_and_wait(
                            "तुमचं कुटुंब बी पी एल श्रेणीत असेल तर एक. "
                            "नसल्यास दोन."
                        )
                        value = normalize(speech_to_text(), "yesno")

                    # ---------- SUCCESS / CONTRADICTION ----------
                    if value is not None:
                        ok = memory.update(key, value)

                        if not ok:
                            speak_and_wait(
                                "तुम्ही आधी दिलेल्या माहितीत बदल केला आहे. कृपया स्पष्ट करा."
                            )
                            retries += 1
                            value = None
                            continue

                        print(f"[CAPTURED] {key} = {value}")
                        break

                    # ---------- RETRY ----------
                    retries += 1
                    speak_and_wait("समजलं नाही. पुन्हा सांगा.")
                    print(f"[WARN] Retry {retries}/{MAX_RETRIES}")

                # ---------- HARD FAIL ----------
                if value is None:
                    speak_and_wait("क्षमस्व. माहिती समजली नाही. सत्र समाप्त.")
                    state = AgentState.END
                    break

            if memory.is_complete():
                state = AgentState.VALIDATE_INFO

            continue

        # -------------------------------------------------
        # VALIDATE INFO
        # -------------------------------------------------
        if state == AgentState.VALIDATE_INFO:
            speak_and_wait(
                f"मी तुमची माहिती वाचतो. "
                f"वय {memory.get('age')} वर्षे. "
                f"उत्पन्न {memory.get('income')} रुपये. "
                f"जात {memory.get('category')}. "
                f"राज्य {memory.get('state')}. "
                f"लिंग {memory.get('gender')}. "
                f"विद्यार्थी {'होय' if memory.get('student') else 'नाही'}. "
                f"बी पी एल {'होय' if memory.get('bpl') else 'नाही'}. "
                "माहिती बरोबर असल्यास एक. चूक असल्यास दोन."
            )

            confirmed = None
            retries = 0

            while retries < 2 and confirmed is None:
                confirmed = normalize(speech_to_text(), "yesno")
                if confirmed is None:
                    retries += 1
                    speak_and_wait("कृपया एक किंवा दोन म्हणा.")

            if confirmed is False:
                speak_and_wait("ठीक आहे. पुन्हा सुरुवात करूया.")
                memory.reset()
                state = AgentState.COLLECT_INFO
                continue

            if confirmed is None:
                speak_and_wait("क्षमस्व. पुष्टी करता आली नाही.")
                state = AgentState.END
                continue

            speak_and_wait("धन्यवाद. पात्रता तपासतो.")
            state = AgentState.CHECK_ELIGIBILITY
            continue

        # -------------------------------------------------
        # CHECK ELIGIBILITY
        # -------------------------------------------------
        if state == AgentState.CHECK_ELIGIBILITY:
            eligible_schemes = check_eligibility(memory)
            state = AgentState.RECOMMEND_SCHEME
            continue

        # -------------------------------------------------
        # RECOMMEND SCHEME
        # -------------------------------------------------
        if state == AgentState.RECOMMEND_SCHEME:
            if eligible_schemes:
                speak_and_wait("तुम्ही खालील योजनांसाठी पात्र आहात.")
                for s in eligible_schemes:
                    speak_and_wait(s["name"])
            else:
                speak_and_wait("क्षमस्व, तुमच्यासाठी कोणतीही योजना सापडली नाही.")

            state = AgentState.END
            continue

    print("\nAgent finished.")


# ===============================
# ENTRY
# ===============================
if __name__ == "__main__":
    main()
