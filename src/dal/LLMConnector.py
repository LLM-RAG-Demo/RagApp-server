from asyncio import Queue, Lock
from typing import Optional

from langchain_deepseek import ChatDeepSeek

from src.conf.config import config


class LLMConnector:
    _instance : Optional['LLMConnector'] = None
    _llm_queue: Queue
    _lock: Lock

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(LLMConnector, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.api_key = config.data['deepseek']['apikey']
        self.core_num = config.data['deepseek']['coreNum']
        self.max_num = config.data['deepseek']['maxNum']
        self._llm_queue = Queue()
        self._lock = Lock()
        for _ in range(self.core_num):
            llm = ChatDeepSeek(api_key=self.api_key, model='deepseek-chat')
            self._llm_queue.put_nowait(llm)

    async def get_llm(self) -> ChatDeepSeek:
        async with self._lock:
            if self._llm_queue.empty() and self._llm_queue.qsize() < self.max_num:
                llm = ChatDeepSeek(api_key=self.api_key, model='deepseek-chat')
                self._llm_queue.put_nowait(llm)
            return await self._llm_queue.get()

    async def release_llm(self, llm: ChatDeepSeek):
        async with self._lock:
            await self._llm_queue.put(llm)