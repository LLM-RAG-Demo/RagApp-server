import time

import dashscope
from http import HTTPStatus

from src.conf import config


def text_rerank():
    start_time = time.time()
    resp = dashscope.TextReRank.call(
        model="gte-rerank-v2",
        query="什么是文本排序模型",
        documents=[
            "文本排序模型广泛用于搜索引擎和推荐系统中，它们根据文本相关性对候选文本进行排序",
            "量子计算是计算科学的一个前沿领域",
            "预训练语言模型的发展给文本排序模型带来了新的进展"
        ],
        top_n=10,
        return_documents=True,
        api_key=config.data['tongyi']['api_key']
    )
    if resp.status_code == HTTPStatus.OK:
        print(resp)
    else:
        print(resp)
    end_time = time.time()
    print(f"Execution time: {end_time - start_time} seconds")


if __name__ == '__main__':
    text_rerank()