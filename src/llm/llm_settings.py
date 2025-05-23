from llama_index.core import Settings
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.nvidia import NVIDIAEmbedding
from llama_index.llms.nvidia import NVIDIA


class LlmRAG():
      def __init__(self, embed_model, llm_model, chunk_size):

        #Define settings for LLM
        self.settings = Settings
        self.embed_model = embed_model
        self.llm_model = llm_model
        self.chunk_size =  chunk_size

        self.settings.embed_model = NVIDIAEmbedding(model=embed_model, truncate="END")
        self.settings.llm = NVIDIA(model=llm_model)
        self.settings.text_splitter = SentenceSplitter(chunk_size=self.chunk_size)


      def __repr__(self):
        print("Configuration llM")
        print(f" Embed_model => {self.embed_model}, llm is {self.llm_model}")

      def get_settings(self):
        return self.settings

      
if __name__ == "__main__":
    EMBED_MODEL="nvidia/nv-embedqa-e5-v5"
    LLM_MODEL="mistralai/mistral-7b-instruct-v0.2"
    CHUNCK_SIZE=600

    llm = LlmRAG(EMBED_MODEL,LLM_MODEL,CHUNCK_SIZE)

    print(llm.get_settings())
    

