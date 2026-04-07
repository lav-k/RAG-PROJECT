import os
from dotenv import load_dotenv

from langchain_community.document_loaders import (
    PyPDFLoader,
    CSVLoader,
    TextLoader
)

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

# ----------------------------
# Load ENV variables
# ----------------------------
load_dotenv()

# ----------------------------
# Configuration
# ----------------------------
DATA_DIR = "rag_data"
VECTOR_DB_DIR = "chroma_db"

# ----------------------------
# Load documents from folders
# ----------------------------
def load_documents():

    documents = []

    pdf_dir = os.path.join(DATA_DIR, "pdfs")
    csv_dir = os.path.join(DATA_DIR, "csv")
    text_dir = os.path.join(DATA_DIR, "text")

    # Load PDFs
    if os.path.exists(pdf_dir):
        for file in os.listdir(pdf_dir):
            if file.endswith(".pdf"):
                path = os.path.join(pdf_dir, file)

                loader = PyPDFLoader(path)
                docs = loader.load()

                for d in docs:
                    d.metadata["source"] = file
                    d.metadata["type"] = "pdf"

                documents.extend(docs)

    # Load CSV files
    if os.path.exists(csv_dir):
        for file in os.listdir(csv_dir):
            if file.endswith(".csv"):
                path = os.path.join(csv_dir, file)

                loader = CSVLoader(file_path=path)
                docs = loader.load()

                for d in docs:
                    d.metadata["source"] = file
                    d.metadata["type"] = "csv"

                documents.extend(docs)

    # Load Text files
    if os.path.exists(text_dir):
        for file in os.listdir(text_dir):
            if file.endswith(".txt"):
                path = os.path.join(text_dir, file)

                loader = TextLoader(path)
                docs = loader.load()

                for d in docs:
                    d.metadata["source"] = file
                    d.metadata["type"] = "txt"

                documents.extend(docs)

    print("Total documents loaded:", len(documents))

    return documents


# ----------------------------
# Chunk documents
# ----------------------------
def chunk_documents(documents):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
        separators=["\n\n", "\n", " ", ""]
    )

    chunks = splitter.split_documents(documents)

    print("Total chunks created:", len(chunks))

    return chunks


# ----------------------------
# Create embeddings
# ----------------------------
def get_embedding_model():

    embedding = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    return embedding


# ----------------------------
# Build vector database
# ----------------------------
def build_vector_db(chunks, embedding):

    db = Chroma.from_documents(
        chunks,
        embedding,
        persist_directory=VECTOR_DB_DIR
    )

    db.persist()

    print("Vector DB created")


# ----------------------------
# Load vector database
# ----------------------------
def load_vector_db(embedding):

    db = Chroma(
        persist_directory=VECTOR_DB_DIR,
        embedding_function=embedding
    )

    return db


# ----------------------------
# Prompt template
# ----------------------------
def get_prompt():

    template = """
You are an AI assistant.

Use ONLY the context below to answer the question.

Context:
{context}

Question:
{question}

If the answer is not in the context say:
"I don't know based on the provided documents."

Answer:
"""

    return PromptTemplate(
        template=template,
        input_variables=["context", "question"]
    )


# ----------------------------
# RAG Query
# ----------------------------
def ask_question(question, retriever, llm, prompt):

    docs = retriever.get_relevant_documents(question)

    context = "\n\n".join([d.page_content for d in docs])

    formatted_prompt = prompt.format(
        context=context,
        question=question
    )

    response = llm.invoke(formatted_prompt)

    print("\nAnswer:\n")
    print(response.content)

    print("\nSources:\n")

    for doc in docs:
        print(doc.metadata.get("source"))


# ----------------------------
# Main
# ----------------------------
def main():

    embedding = get_embedding_model()

    # If vector DB does not exist → build it
    if not os.path.exists(VECTOR_DB_DIR):

        docs = load_documents()

        chunks = chunk_documents(docs)

        build_vector_db(chunks, embedding)

    # Load vector DB
    db = load_vector_db(embedding)

    retriever = db.as_retriever(search_kwargs={"k": 4})

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0
    )

    prompt = get_prompt()

    while True:

        question = input("\nAsk question (type exit to quit): ")

        if question.lower() == "exit":
            break

        ask_question(question, retriever, llm, prompt)


if __name__ == "__main__":
    main()