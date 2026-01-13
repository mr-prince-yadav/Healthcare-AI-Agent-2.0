from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from config import GOOGLE_API_KEY

llm = ChatGoogleGenerativeAI(
    model="models/gemini-2.5-flash",
    temperature=0.2,
    google_api_key=GOOGLE_API_KEY,
)

)


def get_symptom(state: dict) -> dict:
    return state


def classify_symptom(state: dict) -> dict:
    prompt = (
        "You are a medical triage assistant. "
        "Classify the symptom into one category only: "
        "general, emergency, mental health.\n"
        f"Symptom: {state.get('symptom','')}\n"
        "Respond with only one word."
    )

    response = llm.invoke([HumanMessage(content=prompt)])
    state["category"] = response.content.strip().lower()
    return state


def symptom_router(state: dict) -> str:
    cat = state.get("category", "")
    if "emergency" in cat:
        return "emergency"
    if "mental" in cat:
        return "mental_health"
    return "general"


def general_node(state: dict) -> dict:
    state["answer"] = (
        f"'{state.get('symptom','')}' appears non-critical. "
        "You are directed to the general consultation ward."
    )
    return state


def emergency_node(state: dict) -> dict:
    state["answer"] = (
        f"'{state.get('symptom','')}' indicates a medical emergency. "
        "Immediate attention required."
    )
    return state


def mental_health_node(state: dict) -> dict:
    state["answer"] = (
        f"'{state.get('symptom','')}' suggests a mental health concern. "
        "You are directed to a counsellor."
    )
    return state


