import chromadb
import json
import os
import logging
from langchain_community.embeddings import OllamaEmbeddings
from langchain_core.documents import Document
from langchain_chroma import Chroma

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

embeddings = OllamaEmbeddings(model="mxbai-embed-large")

db_location = "./chroma_city_knowledge_db"
add_documents = not os.path.exists(db_location)


KNOWLEDGE_BASE_PATH = r"C:\Users\jithe\OneDrive\Desktop\codes\smart city agent -3\knowledge.json"

def load_knowledge_base():
    """Load and process the knowledge base from JSON file"""
    try:
        with open(KNOWLEDGE_BASE_PATH, "r", encoding='utf-8') as f:
            data = json.load(f)
        return data["knowledge_base"]
    except FileNotFoundError:
        logger.error(f"Knowledge base file not found at: {KNOWLEDGE_BASE_PATH}")
        raise FileNotFoundError(f"Knowledge base file not found at: {KNOWLEDGE_BASE_PATH}")
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON format in knowledge base file: {KNOWLEDGE_BASE_PATH}")
        raise ValueError(f"Invalid JSON format in knowledge base file: {KNOWLEDGE_BASE_PATH}")
    except KeyError:
        logger.error(f"'knowledge_base' key not found in JSON file: {KNOWLEDGE_BASE_PATH}")
        raise KeyError(f"'knowledge_base' key not found in JSON file: {KNOWLEDGE_BASE_PATH}")
    except Exception as e:
        logger.error(f"Error loading knowledge base: {str(e)}")
        raise Exception(f"Error loading knowledge base: {str(e)}")

def create_documents(knowledge_base):
    """Create Document objects from knowledge base entries"""
    documents = []
    ids = []
    
    for category_key, items_list in knowledge_base.items():
        if category_key == "test_queries":  
            continue
            
        for item in items_list:
            
            title = item.get('title', 'N/A')
            content_text = item.get('content', '')
            content = f"Title: {title}\nCategory: {category_key}\n{content_text}"
            
            
            doc_id = str(item.get("id", f"{category_key}_{items_list.index(item)}"))

            metadata = {
                "id": doc_id,
                "title": title,
                "category": category_key,
                "subcategory": item.get("category", ""),
            }
            
            
            optional_fields = ["contact", "location", "hours", "address", "phone", 
                               "emergency", "website", "parking", "reservations"]
            for field in optional_fields:
                if field in item:
                    metadata[field] = item[field]
            
            document = Document(
                page_content=content,
                metadata=metadata
            )
            
            documents.append(document)
            ids.append(doc_id)
    
    return documents, ids

def initialize_vector_store():
    """Initialize or load the vector store"""
    vector_store = Chroma(
        collection_name="city_knowledge",
        persist_directory=db_location,
        embedding_function=embeddings
    )
    return vector_store

def setup_vector_store():
    """Set up the vector store with knowledge base data"""
    knowledge_base_data = load_knowledge_base()
    documents, ids = create_documents(knowledge_base_data)
    vector_store = initialize_vector_store()
    
    if add_documents and documents:
        logger.info(f"Adding {len(documents)} documents to the vector store.")
        vector_store.add_documents(documents=documents, ids=ids)
        vector_store.persist()
        logger.info("Documents added and vector store persisted.")
    elif not documents:
        logger.warning("No documents were created from the knowledge base. Vector store not populated with new data.")
    else:
        logger.info("Vector store already exists and is populated (or no new documents to add).")
    
    return vector_store

vector_store = setup_vector_store()
retriever = vector_store.as_retriever(
    search_kwargs={"k": 3}
)

def search_knowledge(query: str, k: int = 3):
    """Search the knowledge base for relevant information"""
    try:
        if k != retriever.search_kwargs.get("k"):
            pass

        results = retriever.invoke(query)
        logger.info(f"Search for '{query}' returned {len(results)} documents by retriever.")
        
        output_docs = []
        output_metadatas = []
        output_ids = []

        for doc in results[:k]:
            output_docs.append(doc.page_content)
            output_metadatas.append(doc.metadata)
            output_ids.append(doc.metadata.get('id', ''))

        return {
            "documents": [output_docs] if output_docs else [[]],
            "ids": [output_ids] if output_ids else [[]],
            "metadatas": [output_metadatas] if output_metadatas else [[]]
        }

    except Exception as e:
        logger.error(f"Error during search: {str(e)}", exc_info=True)
        return {"documents": [[]], "ids": [[]], "metadatas": [[]]}

if __name__ == "__main__":
    logger.info("Testing vector.py module...")
    test_query = "How do I apply for a building permit?"
    search_results_dict = search_knowledge(test_query)
    
    logger.info(f"\nResults for query: '{test_query}'")
    if search_results_dict and search_results_dict.get('documents') and search_results_dict['documents'][0]:
        docs_list = search_results_dict['documents'][0]
        metas_list = search_results_dict['metadatas'][0]
        for i in range(len(docs_list)):
            doc_content = docs_list[i]
            metadata = metas_list[i]
            print("\n---")
            print(f"Title: {metadata.get('title')}")
            print(f"Category: {metadata.get('category')}")
            print(f"Content: {doc_content[:200]}...")
    else:
        print("No results found or unexpected result structure.")
    logger.info("vector.py module test finished.")