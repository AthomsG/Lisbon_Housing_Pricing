from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from transformers import BertTokenizer, BertModel
import pandas as pd
import pickle
import faiss
import os
import argparse
import torch

def get_openai_embeddings(texts, api_key):
    """
    Generate OpenAI embeddings for a list of texts.
    """
    embeddings = OpenAIEmbeddings(api_key=api_key)
    return embeddings.embed_texts(texts)

def get_bert_multilingual_embeddings(texts):
    """
    Generate BERT multilingual embeddings for a list of texts.
    """
    tokenizer = BertTokenizer.from_pretrained('bert-base-multilingual-cased')
    model = BertModel.from_pretrained('bert-base-multilingual-cased')

    embeddings = []
    for text in texts:
        inputs = tokenizer(text, return_tensors='pt', max_length=512, truncation=True, padding='max_length')
        outputs = model(**inputs)
        embeddings.append(outputs.last_hidden_state.mean(dim=1).detach().numpy()[0])
    return embeddings

def main(path_to_data: str, output_dir: str, embedding_type: str):
    """
    This code automatically generates a vector database from the newly scraped data from the listings websites. 
    It reads the data from a CSV file, extracts the descriptions, and uses the specified embedding model to convert 
    these descriptions into vectors. These vectors are then stored in a FAISS database for efficient similarity search. 
    Additionally, it creates metadata for each description (containing its index and the description itself) and saves it to a pickle file.
    """

    # Load the dataset
    df = pd.read_csv(path_to_data)

    # Get the list of descriptions
    descriptions = df['description'].tolist()

    # Initialize the embeddings object based on the selected embedding type
    if embedding_type == 'openai':
        api_key = os.getenv('OPEN_API_KEY')
        vectors = get_openai_embeddings(descriptions, api_key)
    elif embedding_type == 'bert_multilingual':
        vectors = get_bert_multilingual_embeddings(descriptions)
    else:
        raise ValueError(f"Unsupported embedding type: {embedding_type}")

    # Create the FAISS database from descriptions
    db = FAISS.from_embeddings(vectors)

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Save the index
    index_path = os.path.join(output_dir, 'house_descriptions_faiss_index')
    faiss.write_index(db.index, index_path)

    # Create metadata
    metadata = [{'id': idx, 'description': desc} for idx, desc in enumerate(descriptions)] # idx is the 'database' key

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
    main(args.path_to_data, args.output_dir, args.embedding_type)
