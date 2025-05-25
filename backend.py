import logging
import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain_core.output_parsers import StrOutputParser
from vector import search_knowledge

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Smart City Assistant API",
    description="API for the Smart City Information Assistant powered by Llama2.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    text: str

class Source(BaseModel):
    title: str
    category: str

class QueryResponse(BaseModel):
    answer: str
    sources: list[Source]

llm = None
chain = None

try:
    logger.info("Initializing LLM for RAG...")
    ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    llm = OllamaLLM(model="llama2", base_url=ollama_base_url)
    logger.info(f"LLM initialized successfully with base_url: {ollama_base_url}")

    template = (
        "You are a helpful and informative Smart City Assistant.\n"
        "Your primary role is to provide comprehensive and detailed answers based on the information available in the provided context.\n\n"
        "Please thoroughly review the context below to answer the user's question.\n"
        "Explain the key aspects, provide relevant details, and aim for a clear and elaborate response.\n"
        "If the context contains specific steps, lists, or multiple pieces of information related to the question, try to include them in your answer.\n\n"
        "If the information is not available in the context to fully answer the question, or if the context is limited, \n"
        "clearly state what information you could find and what remains unanswered based on the provided context. \n"
        "Do not invent information or answer outside of the provided context.\n\n"
        "Context:\n"
        "{context}\n\n"
        "Question: {question}\n\n"
        "Detailed Answer:"
    )
    prompt_template = ChatPromptTemplate.from_template(template)

    chain = LLMChain(
        llm=llm,
        prompt=prompt_template,
        output_parser=StrOutputParser()
    )
    logger.info("LLM RAG chain created successfully with updated prompt for detailed answers.")

except Exception as e:
    logger.error(f"Error during LLM or RAG Chain initialization: {e}", exc_info=True)

def format_rag_context(documents: dict) -> str:
    if not documents:
        return "No relevant information found in the knowledge base."

    context_parts = []
    if isinstance(documents, dict) and 'documents' in documents and 'metadatas' in documents:
        docs_content_lists = documents['documents']
        meta_lists = documents['metadatas']

        for i in range(len(docs_content_lists)):
            for j in range(len(docs_content_lists[i])):
                content = docs_content_lists[i][j]
                metadata = meta_lists[i][j] if meta_lists and i < len(meta_lists) and j < len(meta_lists[i]) else {}
                title = metadata.get('title', 'N/A')
                category = metadata.get('category', 'N/A')
                context_parts.append(f"Source Title: {title}\nCategory: {category}\nContent: {content}\n---")
    else:
        try:
            for doc in documents: 
                title = doc.metadata.get('title', 'N/A')
                category = doc.metadata.get('category', 'N/A')
                context_parts.append(f"Source Title: {title}\nCategory: {category}\nContent: {doc.page_content}\n---")
        except TypeError:
             return "Error formatting context. Document structure is unexpected."

    return "\n".join(context_parts) if context_parts else "No relevant information found after formatting."

@app.get("/health", summary="Health Check", tags=["General"])
async def health_check():
    logger.info("Health check endpoint called.")
    return {"status": "healthy", "llm_initialized": llm is not None, "chain_initialized": chain is not None}

@app.post("/query", response_model=QueryResponse, summary="Process a user query using RAG", tags=["Smart City Assistant"])
async def handle_query(query_request: QueryRequest):
    logger.info(f"Received query for RAG: {query_request.text}")
    if not chain:
        logger.error("RAG Chain not initialized. Cannot process query.")
        raise HTTPException(status_code=500, detail="RAG chain is not initialized. Please check server logs.")

    try:
        logger.info(f"Searching knowledge base for: {query_request.text}")
        retrieved_docs_dict = search_knowledge(query_request.text, top_k=3)

        if not retrieved_docs_dict or not retrieved_docs_dict.get('documents') or not retrieved_docs_dict['documents'][0]:
            logger.info("No relevant documents found in knowledge base.")
            return QueryResponse(answer="I couldn't find specific information for your query in the knowledge base.", sources=[])

        formatted_context = format_rag_context(retrieved_docs_dict)
        logger.info(f"Context for RAG: {formatted_context[:500]}...")

        response_payload = {"context": formatted_context, "question": query_request.text}
        logger.info("Invoking RAG chain...")
        answer = chain.invoke(response_payload)
        logger.info(f"RAG chain answer: {answer}")

        response_sources = []
        if retrieved_docs_dict and retrieved_docs_dict.get('metadatas'):
            meta_lists = retrieved_docs_dict['metadatas']
            for i in range(len(meta_lists)):
                 for j in range(len(meta_lists[i])):
                    metadata = meta_lists[i][j]
                    response_sources.append(Source(
                        title=metadata.get('title', 'N/A'),
                        category=metadata.get('category', 'N/A')
                    ))
                    if len(response_sources) >= 3:
                        break
                 if len(response_sources) >= 3:
                     break

        return QueryResponse(answer=str(answer), sources=response_sources)

    except Exception as e:
        logger.error(f"Error processing RAG query: {e}", exc_info=True)
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting FastAPI server (RAG implementation)...")
    uvicorn.run(app, host="0.0.0.0", port=8000) 