# ai_discussion/graph/nodes.py - RAG 검색 노드 및 찬성/반대/심판 에이전트 노드
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from core.config import llm
from core.state import DebateState, DebateStatus, SpeakerRole
from rag.vectorstore import retrieve_relevant_info


def retrieve_info_for_role(
    state: DebateState, search_type: str, perspective: str
) -> DebateState:
    """역할에 따른 정보 검색 공통 함수."""
    base_query = f"{state['topic']} {perspective}"

    if search_type == "pro" and state["current_round"] > 1:
        prev_con_arguments = [m for m in state["messages"] if m["role"] == "반대 측"]
        if prev_con_arguments:
            base_query += f" {prev_con_arguments[-1]['content']}에 대한 반박"

    elif search_type == "con" and state["messages"]:
        pro_arguments = [e for e in state["messages"] if e["role"] == "찬성 측"]
        if pro_arguments:
            base_query += f" {pro_arguments[-1]['content']}에 대한 반박"

    context, docs = "", []
    if state["vector_store"]:
        k = 2 if search_type == "judge" else 3
        context, docs = retrieve_relevant_info(
            base_query, state["vector_store"], k=k
        )

    new_state = state.copy()
    new_state["current_query"] = base_query
    new_state["current_context"] = context

    if "retrieved_docs" not in new_state:
        new_state["retrieved_docs"] = {"pro": [], "con": []}

    if search_type in ["pro", "con"]:
        new_state["retrieved_docs"][search_type] = new_state["retrieved_docs"].get(
            search_type, []
        ) + ([doc.page_content for doc in docs] if docs else [])

    return new_state


def retrieve_pro_info(state: DebateState) -> DebateState:
    """찬성 측 정보 검색 노드."""
    return retrieve_info_for_role(
        state, search_type="pro", perspective="찬성 장점 이유 근거"
    )


def retrieve_con_info(state: DebateState) -> DebateState:
    """반대 측 정보 검색 노드."""
    return retrieve_info_for_role(
        state, search_type="con", perspective="반대 단점 문제점 근거"
    )


def retrieve_judge_info(state: DebateState) -> DebateState:
    """심판 정보 검색 노드."""
    return retrieve_info_for_role(
        state, search_type="judge", perspective="평가 기준 객관적 사실"
    )


def pro_agent(state: DebateState) -> DebateState:
    """찬성 측 에이전트 노드."""
    system_prompt = "당신은 논리적이고 설득력 있는 찬성 측 토론자입니다."
    messages = [SystemMessage(content=system_prompt)]

    for msg in state["messages"]:
        if msg["role"] == "assistant":
            messages.append(AIMessage(content=msg["content"]))
        else:
            messages.append(HumanMessage(content=f"{msg['role']}: {msg['content']}"))

    context = state.get("current_context", "")

    if state["current_round"] == 1:
        prompt = f"""
        당신은 '{state['topic']}'에 대해 찬성 입장을 가진 토론자입니다.
        
        다음은 이 주제와 관련된 정보입니다:
        {context}
        
        논리적이고 설득력 있는 찬성 측 주장을 제시해주세요.
        가능한 경우 제공된 정보에서 구체적인 근거를 인용하세요.
        2 ~ 3문단, 각 문단은 100자내로 작성해주세요.
        """
    else:
        previous_messages = [m for m in state["messages"] if m["role"] == "반대 측"]
        if previous_messages:
            last_con_message = previous_messages[-1]["content"]
            prompt = f"""
            당신은 '{state['topic']}'에 대해 찬성 입장을 가진 토론자입니다.
            
            다음은 이 주제와 관련된 정보입니다:
            {context}
            
            반대 측의 다음 주장에 대해 반박하고, 찬성 입장을 더 강화해주세요:

            반대 측 주장: "{last_con_message}"

            가능한 경우 제공된 정보에서 구체적인 근거를 인용하세요.
            2 ~ 3문단, 각 문단은 100자내로 작성해주세요.
            """
        else:
            prompt = f"""
            당신은 '{state['topic']}'에 대해 찬성 입장을 가진 토론자입니다.
            
            다음은 이 주제와 관련된 정보입니다:
            {context}
            
            논리적이고 설득력 있는 찬성 측 주장을 제시해주세요.
            2 ~ 3문단, 각 문단은 100자내로 작성해주세요.
            """

    messages.append(HumanMessage(content=prompt))
    response = llm.invoke(messages)

    new_state = state.copy()
    new_state["messages"].append({"role": "찬성 측", "content": response.content})
    new_state["current_speaker"] = SpeakerRole.CON
    return new_state


def con_agent(state: DebateState) -> DebateState:
    """반대 측 에이전트 노드."""
    system_prompt = "당신은 논리적이고 설득력 있는 반대 측 토론자입니다. 찬성 측 주장에 대해 적극적으로 반박하세요."
    messages = [SystemMessage(content=system_prompt)]

    for msg in state["messages"]:
        if msg["role"] == "assistant":
            messages.append(AIMessage(content=msg["content"]))
        else:
            messages.append(HumanMessage(content=f"{msg['role']}: {msg['content']}"))

    context = state.get("current_context", "")
    previous_messages = [m for m in state["messages"] if m["role"] == "찬성 측"]
    last_pro_message = previous_messages[-1]["content"] if previous_messages else ""

    prompt = f"""
    당신은 '{state['topic']}'에 대해 반대 입장을 가진 토론자입니다.
    
    다음은 이 주제와 관련된 정보입니다:
    {context}
    
    찬성 측의 다음 주장에 대해 반박하고, 반대 입장을 제시해주세요:

    찬성 측 주장: "{last_pro_message}"

    가능한 경우 제공된 정보에서 구체적인 근거를 인용하세요.
    2 ~ 3문단, 각 문단은 100자내로 작성해주세요.
    """

    messages.append(HumanMessage(content=prompt))
    response = llm.invoke(messages)

    new_state = state.copy()
    new_state["messages"].append({"role": "반대 측", "content": response.content})
    new_state["current_round"] += 1

    if new_state["current_round"] <= new_state["max_rounds"]:
        new_state["current_speaker"] = SpeakerRole.PRO
    else:
        new_state["current_speaker"] = SpeakerRole.JUDGE

    return new_state


def judge_agent(state: DebateState) -> DebateState:
    """심판 에이전트 노드."""
    system_prompt = "당신은 공정하고 논리적인 토론 심판입니다. 양측의 주장을 면밀히 검토하고 객관적으로 평가해주세요."
    messages = [SystemMessage(content=system_prompt)]
    context = state.get("current_context", "")

    prompt = f"""
    다음은 '{state['topic']}'에 대한 찬반 토론입니다. 각 측의 주장을 분석하고 평가해주세요.
    
    다음은 이 주제와 관련된 객관적인 정보입니다:
    {context}

    토론 내용:
    """
    for msg in state["messages"]:
        prompt += f"\n\n{msg['role']}: {msg['content']}"

    prompt += """
    
    위 토론을 분석하여 다음을 포함하는 심사 평가를 해주세요:
    1. 양측 주장의 핵심 요약
    2. 각 측이 사용한 주요 논리와 증거의 강점과 약점
    3. 전체 토론의 승자와 그 이유
    4. 양측 모두에게 개선점 제안
    
    가능한 경우 제공된 객관적 정보를 참고하여 평가해주세요.
    """

    messages.append(HumanMessage(content=prompt))
    response = llm.invoke(messages)

    new_state = state.copy()
    new_state["messages"].append({"role": "심판", "content": response.content})
    new_state["debate_status"] = DebateStatus.COMPLETED
    new_state["current_speaker"] = SpeakerRole.COMPLETED
    return new_state
