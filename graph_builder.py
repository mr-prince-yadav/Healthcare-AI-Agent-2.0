from langgraph.graph import StateGraph, END
from functions import (
    get_symptom,
    classify_symptom,
    symptom_router,
    general_node,
    emergency_node,
    mental_health_node
)

def build_graph():
    builder = StateGraph(dict)

    builder.set_entry_point("get_symptom")

    builder.add_node("get_symptom", get_symptom)
    builder.add_node("classify", classify_symptom)
    builder.add_node("general", general_node)
    builder.add_node("emergency", emergency_node)
    builder.add_node("mental_health", mental_health_node)

    builder.add_edge("get_symptom", "classify")

    builder.add_conditional_edges(
        "classify",
        symptom_router,
        {
            "general": "general",
            "emergency": "emergency",
            "mental_health": "mental_health"
        }
    )

    builder.add_edge("general", END)
    builder.add_edge("emergency", END)
    builder.add_edge("mental_health", END)

    return builder.compile()
