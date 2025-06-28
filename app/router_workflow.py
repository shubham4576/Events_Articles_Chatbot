from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from app.nodes_defination import (
    STATE,
    article_writer,
    classify_user_query,
    full_text_search,
    get_answer,
    get_keywords,
)

graph_builder = StateGraph(STATE)

graph_builder.add_node("get_keywords", get_keywords)
graph_builder.add_node("full_text_search", full_text_search)
graph_builder.add_node("get_answer", get_answer)
graph_builder.add_node("classify_user_query", classify_user_query)
graph_builder.add_node("article_writer", article_writer)


def category_check(state: STATE):
    if state.category == "ARTICLE_WRITER":
        return "article_writer"
    else:
        return "get_answer"


graph_builder.set_entry_point("get_keywords")
graph_builder.add_edge("get_keywords", "full_text_search")
graph_builder.add_edge("full_text_search", "classify_user_query")

graph_builder.add_conditional_edges(
    "classify_user_query",
    category_check,
    {
        "article_writer": "article_writer",
        "get_answer": "get_answer",
    },
)

graph_builder.add_edge("article_writer", END)
graph_builder.add_edge("get_answer", END)

workflow = graph_builder.compile(checkpointer=MemorySaver())


try:
    img_data = workflow.get_graph().draw_mermaid_png()
    with open("workflow_graph.png", "wb") as f:
        f.write(img_data)
    print("✅ Mermaid graph saved as 'workflow_graph.png'")
except Exception as e:
    # Optional: drawing the Mermaid graph may require extra dependencies
    print(f"⚠️ Could not generate Mermaid graph: {e}")
