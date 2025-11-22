import os
os.environ['GRPC_DNS_RESOLVER'] = 'native'
from dotenv import load_dotenv

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document


load_dotenv()

def load_tech_docs(root_dir: str):
    """
    지정된 루트 디렉토리에서 특정 폴더를 제외하고 원하는 확장자 파일만 로드
    """
    docs = []
    # 무시할 폴더 목록
    excluded_dirs = {'.venv', '.git', '__pycache__', 'faiss_index', 'scripts'}

    for dirpath, dirnames, filenames in os.walk(root_dir):
        dirnames[:] = [d for d in dirnames if d not in excluded_dirs]

        for filename in filenames:
            if filename.endswith(('.py', '.md', '.mdx')):
                file_path = os.path.join(dirpath, filename)
                try:
                    with open(file_path, 'r', encoding='UTF-8') as f:
                        content = f.read()
                    doc = Document(page_content=content, metadata={"source": file_path})
                    docs.append(doc)
                except Exception:
                    continue
    print(f"총 {len(docs)}개의 문서를 로드했습니다.")
    return docs
            
def split_docs_into_chunks(docs):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", r"(?<=\. )", " ", ""], # 문단 -> 줄바꿈 -> 문장 순으로 분리
    )
    splitted_docs = text_splitter.split_documents(docs)
    print(f"문서를 총 {len(splitted_docs)}개의 청크로 분할했습니다.")
    return splitted_docs

def build_and_save_vector_store(splitted_docs, db_path="faiss_index"):
    print("Google Gemini 임베딩을 시작합니다...")

    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        task_type="RETRIEVAL_DOCUMENT"
    )
    
    db = FAISS.from_documents(splitted_docs, embeddings)
    db.save_local(db_path)
    print(f"벡터 저장소가 '{db_path}' 경로에 성공적으로 구축 및 저장되었습니다.")
    return db


if __name__ == '__main__':
    documents = load_tech_docs(".")

    splitted_documenets = split_docs_into_chunks(documents)

    build_and_save_vector_store(splitted_documenets)