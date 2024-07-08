from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from transformers import BertTokenizer, BertModel
import pandas as pd
import pickle
import faiss
import os
import argparse
import torch
from torch.multiprocessing import Pool, set_start_method

def get_openai_embeddings(texts, api_key):
    """
    Generate OpenAI embeddings for a list of texts.
    """
    embeddings = OpenAIEmbeddings(api_key=api_key)
    return embeddings.embed_texts(texts)

def initialize_bert_model():
    """
    Initialize BERT tokenizer and model.
    """
    tokenizer = BertTokenizer.from_pretrained('bert-base-multilingual-cased')
    model = BertModel.from_pretrained('bert-base-multilingual-cased')
    return tokenizer, model

def compute_bert_embeddings(batch_texts, tokenizer, model):
    """
    Compute BERT embeddings for a batch of texts.
    """
    inputs = tokenizer(batch_texts, return_tensors='pt', max_length=512, truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    batch_embeddings = outputs.last_hidden_state.mean(dim=1).detach().numpy()
    return batch_embeddings

def get_bert_multilingual_embeddings(texts):
    """
    Generate BERT multilingual embeddings for a list of texts using parallel processing.
    """
    tokenizer, model = initialize_bert_model()
    batch_size = 32

    with Pool() as pool:
        batches = [texts[i:i + batch_size] for i in range(0, len(texts), batch_size)]
        results = pool.starmap(compute_bert_embeddings, [(batch, tokenizer, model) for batch in batches])

    embeddings = [embedding for batch_embeddings in results for embedding in batch_embeddings]
    return embeddings

def main(path_to_data: str, output_dir: str, embedding_type: str):
    """
    Main function to generate a vector database from the newly scraped data.
    """
    # Load the dataset
    df = pd.read_csv(path_to_data)

    # Get the list of descriptions & replace missing values
    descriptions = df['description'].fillna('No Description').astype(str).tolist()

    # Initialize the embeddings object based on the selected embedding type
    if embedding_type == 'openai':
        api_key = os.getenv('OPEN_API_KEY')
        vectors = get_openai_embeddings(descriptions, api_key)
    elif embedding_type == 'bert_multilingual':
        vectors = get_bert_multilingual_embeddings(descriptions)
    else:
        raise ValueError(f"Unsupported embedding type: {embedding_type}")

    # Create the FAISS database from descriptions
    dimension = vectors[0].shape[0]
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(vectors))

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Save the index
    index_path = os.path.join(output_dir, 'house_descriptions_faiss_index')
    faiss.write_index(index, index_path)

    # Create metadata
    metadata = [{'id': idx, 'description': desc} for idx, desc in enumerate(descriptions)]

    # Save the metadata
    metadata_path = os.path.join(output_dir, 'metadata.pkl')
    with open(metadata_path, 'wb') as f:
        pickle.dump(metadata, f)

    print("Index and metadata created and saved.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate a vector database from scraped data.')
    parser.add_argument('--path_to_data', type=str, required=True, help='Path to the CSV file containing the data.')
    parser.add_argument('--output_dir', type=str, required=True, help='Directory where the output files will be saved.')
    parser.add_argument('--embedding_type', type=str, required=True, choices=['openai', 'bert_multilingual'], help='Type of embeddings to use (openai or bert_multilingual).')
    args = parser.parse_args()
    set_start_method('spawn')
    main(args.path_to_data, args.output_dir, args.embedding_type)