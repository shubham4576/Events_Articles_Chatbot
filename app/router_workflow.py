from langgraph.graph import END, StateGraph
from langgraph.checkpoint.memory import InMemorySaver

from app.nodes_defination import (
    STATE,
    get_keywords,
    get_answer,
    full_text_search,
)

graph_builder = StateGraph(STATE)

graph_builder.add_node("get_keywords", get_keywords)
graph_builder.add_node("full_text_search", full_text_search)
graph_builder.add_node("get_answer", get_answer)

graph_builder.set_entry_point("get_keywords")
graph_builder.add_edge("get_keywords", "full_text_search")
graph_builder.add_edge("full_text_search", "get_answer")
graph_builder.add_edge("get_answer", END)

workflow = graph_builder.compile(checkpointer=InMemorySaver())

try:
    img_data = workflow.get_graph().draw_mermaid_png()
    with open("workflow_graph.png", "wb") as f:
        f.write(img_data)
    print("✅ Mermaid graph saved as 'workflow_graph.png'")
except Exception as e:
    # Optional: drawing the Mermaid graph may require extra dependencies
    print(f"⚠️ Could not generate Mermaid graph: {e}")
