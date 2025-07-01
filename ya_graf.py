import base64
from typing import List, TypedDict, Annotated, Optional
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage
from langgraph.graph.message import add_messages
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from IPython.display import Image, display
from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, START, END
import re
import json

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage

import os
from dotenv import load_dotenv, find_dotenv
from yandex_cloud_ml_sdk import YCloudML
from langchain_community.llms import YandexGPT

operationdirectory = """

    1-я междурядная культивация
    2-я междурядная культивация
    Боронование довсходовое
    Внесение минеральных удобрений
    Выравнивание зяби
    2-е Выравнивание зяби
    Гербицидная обработка
    1 Гербицидная обработка
    2 Гербицидная обработка
    3 Гербицидная обработка
    4 Гербицидная обработка
    Дискование
    Дискование 2-е
    Инсектицидная обработка
    Культивация
    Пахота
    Подкормка
    Предпосевная культивация
    Прикатывание посевов
    Сев
    Сплошная культивация
    Уборка
    Функицидная обработка
    Чизлевание
    """

crop_direc ="""
Вика+Тритикале
Горох на зерно
Горох товарный
Гуар
Конопля
Кориандр
Кукуруза кормовая
Кукуруза семенная
Кукуруза товарная
Люцерна
Многолетние злаковые травы
Многолетние травы прошлых лет
Многолетние травы текущего года
Овес
Подсолнечник кондитерский
Подсолнечник семенной
Подсолнечник товарный
Просо
Пшеница озимая на зеленый корм
Пшеница озимая семенная
Пшеница озимая товарная
Рапс озимый
Рапс яровой
Свекла сахарная
Сорго
Сорго кормовой
Сорго-суданковый гибрид
Соя семенная
Соя товарная
Чистый пар
Чумиза
Ячмень озимый
Ячмень озимый семенной
"""

class MessageState(TypedDict):
    # The email being processed
    input_message: Optional[str]  # Contains subject, sender, body, etc.

    operations: List[str]

    classifyedjson: Optional[str]

    # Category of the email (inquiry, complaint, etc.)
    extract_data: Optional[str]

    # Reason why the email was marked as spam
    uncorrect_reason: Optional[str]

    # Analysis and decisions
    is_correct: Optional[bool]

    # Response generation
    json_draft: Optional[str]

    # Processing metadata
    messages: List[Dict[str, Any]]  # Track conversation with LLM for analysis



model = YandexGPT(iam_token="--", folder_id="--")


def read_message(state: MessageState):
    """Read and log the incoming meassage"""
    input_message = state["input_message"]

    # Here we might do some initial preprocessing
    print(f"Proccesing meassage {input_message}")

    # No state changes needed here
    return {}

def devide_per_oper(state: MessageState):
    """As an agronomist divet input message per operations"""
    input_message = state["input_message"]

    # Prepare our prompt for the LLM
    prompt = f"""
    As an agronomist, analyze this message and devide it by operations.

    message: {input_message}

    Use the {operationdirectory} with operations to facilitate the separation.
    Use line breaks to split, so you need to remove unnecessary line breaks.
    """

    # Call the LLM
    # messages = [HumanMessage(content=prompt)]
    # response = model.invoke(messages)

    # Return state updates
    return {"operations": list([1,2])}


json_parser = JsonOutputParser()

def classifying_jsoning(state: MessageState):
    """As an agronomist you need to classify the entities in the operation"""
    input_message = state["input_message"]
    classifyedjson = []
    prompt_template = ChatPromptTemplate.from_template("""
    As an agronomist, analyze this message and classify the entities in the operation by next classes.
                                                       {{
                "date": "Дата", или null
                "department": "Подразделение",
                "operation": "Операция",
                "crop": "Культура",
                "areaPerDay": "За день, га", или null
                "totalArea": "С начала операции, га", или null
                "yieldPerDay": "Вал за день, ц", или null
                "totalYield": "Вал с начала, ц" или null
            }}
    **Examples**:
                        -   "
                Пахота зяби под мн тр
                По Пу 26/488
                Отд 12 26/221
                " →
            {{
                "date":  null,
                "department": "АОР",
                "operation": "Пахота",
                "crop": "Многолетние травы текущего года",
                "areaPerDay": 26,
                "totalArea": 488,
                "yieldPerDay": null,
                "totalYield": null
            }}

            - " Мир
                27.10.день
                Предп культ под оз пш
                По Пу 215/1015
                Отд 12 128/317
                Отд 16 123/529" →
            {{
                "date":  27.10.2024,
                "department": "Мир",
                "operation": "Предпосевная культивация",
                "crop": "Пшеница озимая товарная",
                "areaPerDay": 215,
                "totalArea": 1015,
                "yieldPerDay": null,
                "totalYield": null
            }}

    **Message**: {input_message}

    **Additional context**: Use the
    {operationdirectory} and


    {crop_direc} for reference.

    **Strict rules**:
    - Output MUST be a valid JSON.
    - Do not include any additional text, explanations, or markdown like ```json```.
    - If you can't generate valid JSON, return an empty JSON object {{}}.

    **Required JSON format**:
    {format_instructions}
    """)

    chain = prompt_template | model | json_parser

    result = chain.invoke({
                "input_message": input_message,
                "operationdirectory": operationdirectory,
                "crop_direc": crop_direc,
                "format_instructions": json_parser.get_format_instructions()
            })

    return {"classifyedjson": result}



    # for operation in operations:
    #     prompt = f"""
    # As an agronomist, analyze this message and classify the entities in the operation by next classes.

    # message: {operation}

    # Use the {operationdirectory} with operations to facilitate the separation.
    # Your output should be in JSON format.
    # You need to output only JSON and nothing else.
    # It is strictly forbidden to write anything other than JSON
    # """
    #     messages = [HumanMessage(content=prompt)]
    #     response = model.invoke(messages)

    #     #Парсим json чтобы наверняка
    #     json_match = re.search(r'\{.*\}', response, re.DOTALL)
    #     if not json_match:
    #         json_match = 'тут не сгенерировался жсон или труба парсеру'
    #     classifyedjson.append(json_match)


    #     json_str = json_match.group(0)

    # We're done processing this email



def output(state: MessageState):
    """Alfred notifies Mr. Hugg about the email and presents the draft response"""
    classifyedjson = state["classifyedjson"]


    print(classifyedjson)

    # We're done processing this email
    return {}


# Create the graph
ogr_graph = StateGraph(MessageState)

# Add nodes
ogr_graph.add_node("read_message", read_message)
ogr_graph.add_node("devide_per_oper", devide_per_oper)
ogr_graph.add_node("classifying_jsoning", classifying_jsoning)
ogr_graph.add_node("output", output)

# Start the edges
ogr_graph.add_edge(START, "read_message")
# Add edges - defining the flow
ogr_graph.add_edge("read_message", "devide_per_oper")

# Add conditional branching from classify_email
# ogr_graph.add_conditional_edges(
#     "classify_email",
#     route_email,
#     {
#         "spam": "handle_spam",
#         "legitimate": "draft_response"
#     }
# )

# Add the final edges
ogr_graph.add_edge("devide_per_oper", "classifying_jsoning")
ogr_graph.add_edge("classifying_jsoning", "output")
ogr_graph.add_edge("output", END)

# Compile the graph
compiled_graph = ogr_graph.compile()


message = """Пахота зяби под мн тр
По Пу 26/488
Отд 12 26/221

Предп культ под оз пш
По Пу 215/1015
Отд 12 128/317
Отд 16 123/529

2-е диск сах св под пш
По Пу 22/627
Отд 11 22/217

2-е диск сои под оз пш
По Пу 45/1907
Отд 12 45/299"""

compiled_graph.invoke({
    "input_message": message,
    "classifyedjson": None,
    "extract_data": None,
    "uncorrect_reason": None,
    "is_correct": None,
    "json_draft": None,
    "messages": []
})
