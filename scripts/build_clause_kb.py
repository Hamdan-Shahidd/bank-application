# Clause-aware build. Run once, or whenever HBL_Conditions.pdf changes.
# pdf -> join pages -> parse clause numbers -> split sub-clauses ->
#     attach metadata -> embed into a dedicated Chroma collection
from ai.retriever import build_clause_knowledge_base
build_clause_knowledge_base()