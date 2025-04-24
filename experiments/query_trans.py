import time

from langchain_deepseek import ChatDeepSeek
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

llm = ChatDeepSeek(
    model="deepseek-chat",
    temperature=0.5,
    api_key='sk-69c9811fc0784c9099acbf6d8b10bfe0'
)

parser = JsonOutputParser()

template = PromptTemplate.from_template(
    """
    下面是用户的Query，我希望你将用户的Query改写为三个可能的搜索语句，以用来在搜索引擎中搜索用户可能希望的内容：
    Query: {query}
    请用Json格式输出，格式如下：
    {{
        "statements": [
            "第一个搜索语句",
            "第二个搜索语句",
            "第三个搜索语句"
        ]
    }}
    """
)

# 组合提示词和解析器
prompt = template.partial(format_instructions=parser.get_format_instructions())

chain = prompt | llm | parser

start_time = time.time()

response = chain.invoke({"query": "你知道白鹿吗"})

end_time = time.time()
print(f"Execution time: {end_time - start_time} seconds")

print(response)