from langgraph import StateGraph, START, END
from crewai import Agent, Task, Crew
from pydantic_ai import BaseModel, Field
from autogen import GroupChat, GroupChatManager, AssistantAgent, UserProxyAgent
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv

load_dotenv()

# PydanticAI for type-safe validation
class PostDraft(BaseModel):
    topic: str = Field(description="The topic of the LinkedIn post")
    content: str = Field(description="The generated post content")
    hooks: List[str] = Field(description="List of hook lines")
    hashtags: List[str] = Field(description="List of suggested hashtags")
    audience: str = Field(description="Target audience")
    tone: str = Field(description="Tone of the post")

class WorkflowState(BaseModel):
    topic: str
    audience: str = "professionals"
    goal: str = "educate"
    tone: str = "professional"
    length: str = "150-200"
    keywords: str = ""
    cta: str = ""
    draft: Optional[PostDraft] = None
    approved: bool = False
    corrections: List[str] = []

# Master Orchestrator: LangGraph for stateful graph management
def create_workflow():
    graph = StateGraph(WorkflowState)

    # Node 1: Input Collection (Human-in-the-loop checkpoint)
    def collect_input(state: WorkflowState) -> WorkflowState:
        # Human input for topic, etc.
        # For demo, assume inputs are set
        return state

    # Node 2: Execution Squad (CrewAI) - Parallelized sub-tasks
    def generate_draft(state: WorkflowState) -> WorkflowState:
        try:
            # CrewAI: Spawn a crew of agents for research, analysis, writing
            researcher = Agent(
                role="Researcher",
                goal="Gather insights on LinkedIn trends for the topic",
                backstory="Expert in LinkedIn analytics and trends."
            )
            writer = Agent(
                role="Writer",
                goal="Generate engaging LinkedIn post content",
                backstory="Skilled content creator for professional networks."
            )
            analyst = Agent(
                role="Analyst",
                goal="Analyze and suggest hooks and hashtags",
                backstory="Data-driven strategist for social media optimization."
            )

            task1 = Task(description=f"Research LinkedIn trends for topic: {state.topic}", agent=researcher)
            task2 = Task(description=f"Write post draft for topic: {state.topic}, audience: {state.audience}, tone: {state.tone}", agent=writer)
            task3 = Task(description=f"Generate hooks and hashtags for topic: {state.topic}", agent=analyst)

            crew = Crew(agents=[researcher, writer, analyst], tasks=[task1, task2, task3])
            result = crew.kickoff()

            # Parse result into PostDraft using PydanticAI validation
            draft = PostDraft(
                topic=state.topic,
                content=result.get('content', 'Generated content'),
                hooks=result.get('hooks', []),
                hashtags=result.get('hashtags', []),
                audience=state.audience,
                tone=state.tone
            )
            state.draft = draft
        except Exception as e:
            print(f"Error in generate_draft: {str(e)}")
            state.corrections.append(f"Draft generation failed: {str(e)}")
        return state

    # Node 3: Reasoning Loop (AutoGen) - Collaborative debate
    def debate_draft(state: WorkflowState) -> WorkflowState:
        # AutoGen Group Chat for debate on draft quality
        assistant = AssistantAgent("Assistant", llm_config={"config_list": [{"model": "gpt-4", "api_key": os.getenv("OPENAI_API_KEY")}]})
        user_proxy = UserProxyAgent("User", code_execution_config=False)

        groupchat = GroupChat(agents=[assistant, user_proxy], messages=[], max_round=3)
        manager = GroupChatManager(groupchat=groupchat, llm_config={"config_list": [{"model": "gpt-4", "api_key": os.getenv("OPENAI_API_KEY")}]})

        debate_prompt = f"Debate the quality of this LinkedIn post draft: {state.draft.content if state.draft else 'No draft'}. Suggest improvements."
        user_proxy.initiate_chat(manager, message=debate_prompt)

        # Assume consensus reached, update state if needed
        return state

    # Node 4: Human Approval Checkpoint
    def human_approval(state: WorkflowState) -> WorkflowState:
        # Human-in-the-loop: Approve or reject
        # For demo, assume approved
        state.approved = True
        return state

    # Node 5: Self-Correction (Audit output)
    def self_correction(state: WorkflowState) -> WorkflowState:
        try:
            # Audit: Check for errors, hallucinations, etc.
            if state.draft and len(state.draft.content.split()) < 50:
                state.corrections.append("Content too short, regenerate.")
                # Trigger correction (e.g., re-run generate_draft)
            if state.draft and not state.draft.hashtags:
                state.corrections.append("Missing hashtags, regenerate.")
            if state.corrections:
                print(f"Corrections needed: {state.corrections}")
        except Exception as e:
            print(f"Error in self_correction: {str(e)}")
            state.corrections.append(f"Audit failed: {str(e)}")
        return state

    # Node 6: Finalize and Output
    def finalize(state: WorkflowState) -> WorkflowState:
        # Save or output the final post
        if state.draft:
            with open(f"outputs/{state.topic.replace(' ', '_')}.txt", 'w') as f:
                f.write(state.draft.content)
        return state

    # Add nodes to graph
    graph.add_node("collect_input", collect_input)
    graph.add_node("generate_draft", generate_draft)
    graph.add_node("debate_draft", debate_draft)
    graph.add_node("human_approval", human_approval)
    graph.add_node("self_correction", self_correction)
    graph.add_node("finalize", finalize)

    # Define edges
    graph.add_edge(START, "collect_input")
    graph.add_edge("collect_input", "generate_draft")
    graph.add_edge("generate_draft", "debate_draft")
    graph.add_edge("debate_draft", "human_approval")
    graph.add_edge("human_approval", "self_correction")
    graph.add_edge("self_correction", "finalize")
    graph.add_edge("finalize", END)

    # Conditional edge for self-correction loop
    def check_corrections(state: WorkflowState):
        return "generate_draft" if state.corrections else "finalize"

    graph.add_conditional_edges("self_correction", check_corrections)

    return graph.compile()

# Example usage
if __name__ == "__main__":
    try:
        workflow = create_workflow()
        initial_state = WorkflowState(topic="AI in Product Management")
        result = workflow.invoke(initial_state)
        print("Workflow completed:", result)
    except Exception as e:
        print(f"Workflow execution failed: {str(e)}")
