import os
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import BedrockEmbeddings
from langchain_community.document_loaders import PyPDFLoader

def process_document(file_path):
    """Process a single document: read, split, and return chunks"""
    # Try different encodings
    encodings = ['utf-8', 'latin-1', 'cp1252', 'ascii']
    
    for encoding in encodings:
        try:
            with open(file_path, "r", encoding=encoding) as file:
                text = file.read()
                break
        except UnicodeDecodeError:
            if encoding == encodings[-1]:  # If this was the last encoding to try
                print(f"Could not read file {file_path} with any encoding")
                return []
            continue
    
    splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=5000,
        chunk_overlap=100,
        length_function=len
    )
    
    return splitter.create_documents([text])

def main():
    # Setup directories
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    doc_repo = os.path.join(current_dir, "index_doc_repo")
    
    # Create doc_repo if it doesn't exist
    os.makedirs(doc_repo, exist_ok=True)
    
    # Initialize Bedrock embeddings
    embeddings = BedrockEmbeddings(
        credentials_profile_name="default",
        region_name="us-west-2",
        model_id="amazon.titan-embed-text-v1"
    )
    
    all_chunks = []  # Store all document chunks
    
    # Process documents
    for filename in os.listdir(doc_repo):
        file_path = os.path.join(doc_repo, filename)
        if os.path.isfile(file_path):
            file_type = filename.split(".")[-1]

            print(f"Processing {file_path}")

            print(f"File Type: {file_type}")
            print(f"File Name: {filename}")

            if file_type.lower() == "pdf":
                loader = PyPDFLoader(file_path)
                pages = loader.load_and_split()
                for page in pages:
                    all_chunks.append(page)


            if file_type.lower() == "txt":

            
                # Split document into chunks
                chunks = process_document(file_path)
                if not chunks:  # Skip if no chunks were created
                    continue
                
                all_chunks.extend(chunks)
                
        print(f"Completed {filename}")
    
    
    # Create FAISS index from all chunks
    vectorstore = FAISS.from_documents(
        documents=all_chunks,
        embedding=embeddings
    )
    
    # Save the vectorstore
    index_path = os.path.join(parent_dir, "document_faiss_index")
    vectorstore.save_local(index_path)
    
    print(f"Index saved at: {index_path}")
    print(f"Processed {len(all_chunks)} text chunks")

if __name__ == "__main__":
    main()
