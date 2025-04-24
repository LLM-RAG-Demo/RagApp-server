from asyncio import Queue, Lock
from functools import lru_cache
from typing import Optional, AsyncGenerator

from langchain_deepseek import ChatDeepSeek

from src.conf import config


class LLMConnector:
    _instance: Optional['LLMConnector'] = None
    _llm_queue: Queue
    _lock: Lock

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(LLMConnector, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.api_key = config.data['deepseek']['api_key']
        self.core_num = config.data['deepseek']['core_num']
        self.max_num = config.data['deepseek']['max_num']
        self._llm_queue = Queue()
        self._lock = Lock()
        for _ in range(self.core_num):
            # 初始化时就开启 streaming 并配置回调
            llm = ChatDeepSeek(
                api_key=self.api_key,
                model='deepseek-chat',
                streaming=True,
            )
            self._llm_queue.put_nowait(llm)

    async def get_llm(self) -> ChatDeepSeek:
        async with self._lock:  # 使用锁保护队列操作
            if self._llm_queue.empty():
                if self._active_llms < self.max_num:  # 追踪活跃LLM数量
                    self._active_llms += 1
                    llm = ChatDeepSeek(
                        api_key=self.api_key,
                        model='deepseek-chat',
                        streaming=True,
                    )
                    return llm
                else:
                    # 等待队列中有LLM可用
                    pass
            return await self._llm_queue.get()

    async def release_llm(self, llm: ChatDeepSeek):
        async with self._lock:
            await self._llm_queue.put(llm)
            

async def use_llm() -> AsyncGenerator[ChatDeepSeek, None]:
    connector = LLMConnector()
    llm = await connector.get_llm()
    try:
        yield llm
    finally:
        await connector.release_llm(llm)

