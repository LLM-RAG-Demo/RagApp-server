from typing import List

from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever

class SeriveRetriever(BaseRetriever):
    def _get_relevant_documents(self, query, *, run_manager) -> List[Document]:

        # return super()._get_relevant_documents(query, run_manager=run_manager)