# Build: We only run it once or whenever the pdf changes. Internally it performs all the following;
# pdf -> read_pdf -> split onto pages -> split pages into chunks -> generate embedding -> store in chroma
# We run it once -> build knowledge base -> store on disk
from ai.retriever import build_knowledge_base
build_knowledge_base()