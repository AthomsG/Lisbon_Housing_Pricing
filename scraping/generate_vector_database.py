from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
import pandas as pd
import pickle
import faiss
import os
import argparse

def main(path_to_data: str, output_dir: str):
    """
    This code automatically generates a vector database from the newly scraped data from the listings websites. 
    It reads the data from a CSV file, extracts the descriptions, and uses the OpenAIEmbeddings to convert these descriptions into vectors. 
    These vectors are then stored in a FAISS database for efficient similarity search. 
    Additionally, it creates metadata for each description (containing its index and the description itself) and saves it to a pickle file.
    """

    # Load the dataset
    df = pd.read_csv(path_to_data)

    # THIS IS A TEST
    df = df.iloc[:10]

    # Load OpenAI API key
    api_key = os.getenv('OPEN_API_KEY')

    # Get the list of descriptions
    descriptions = df['description'].tolist()

    # Initialize the embeddings object
    embeddings = OpenAIEmbeddings(api_key=api_key)

    # Create the FAISS database from descriptions
    db = FAISS.from_texts(descriptions, embeddings)

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
    args = parser.parse_args()
    main(args.path_to_data, args.output_dir)