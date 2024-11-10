from pymilvus import (
    connections,
    utility,
    FieldSchema,
    CollectionSchema,
    DataType,
    Collection,
)
from pymilvus.exceptions import ConnectionNotExistException
from llama_index.vector_stores.milvus import MilvusVectorStore
from llama_index.core import VectorStoreIndex, StorageContext
import numpy as np

class MilvusDatabase:
    def __init__(self, host="127.0.0.1", port=19530, dimension=1024):
        # Initialisation du contexte de stockage avec Milvus
        self.vector_store = None

        # Try to connect to MilvusVectorStore
        self.vector_store = MilvusVectorStore(host=host, port=port, dim=dimension)
        try:
            connections.connect("default", host=host, port=port)
            print("Connection to Milvus successful.")
            print(f"Connected to Milvus on {host}:{port} with dim  {dimension}")
        except ConnectionNotExistException as e:
            # Exception for Milvus
            print(f"Failed to connect to Milvus: {e}")
            return
        except Exception as e:
            # Capture other execeptions
            print(f"An unexpected error occurred: {e}")
            return

        self.storage_context = StorageContext.from_defaults(
            vector_store=self.vector_store
        )

        self.index_collection = None
        self.index_documents = None
        self.document = None
        self.collection = None
        self.index_params = {"index_type": "IVF_FLAT", "params": {"nlist": 100}}

    def get_storage_context(self):
        return self.storage_context

    def create_collection(self, collection_name, field, description):

        schema = CollectionSchema(
            fields=field, description=description, storage_context=self.storage_context
        )

        # Create collection
        self.collection = Collection(name=collection_name, schema=schema)
        print(f"The collection '{collection_name}' has been created.")

    def add_document(self, document):
        self.document = document

    def insert_vectors(self, vectors):
        # Insert value in vectors
        if hasattr(self, "collection"):
            ids = self.collection.insert(vectors)
            print(f"Vectors successfully inserted, IDs: {ids}")
        else:
            print("The collection has not been created.")

    def create_index_collection(
        self,
        collection_name,
        field_name,
        index_type="IVF_FLAT",
        metric_type="L2",
        nlist=100,
    ):
        if self.collection is not None:

            index_params = {
                "index_type": index_type,
                "metric_type": metric_type,
                "params": {"nlist": nlist},
            }
            self.collection.create_index(
                field_name=field_name, index_params=index_params
            )
            print("Index collection created successfully.")

        else:
            print(f"Collection '{collection_name}' not exist")
            return

    def create_index_document(self, documents):
        """Creates an index for documents."""
        if documents is not None:
            # Create an index for the provided documents using the storage context
            self.index_documents = VectorStoreIndex.from_documents(
                documents, storage_context=self.storage_context
            )
            print("Document index created successfully.")
        else:
            print("No documents provided for index creation.")

        return self.index_documents

    def insert_data(self, collection_name, data_vectors):
        # get collection
        collection = Collection(collection_name)

        # Insert vectors
        num_vectors = len(data_vectors)
        ids = collection.insert([data_vectors])
        print(f"{num_vectors} vectors insert to '{collection_name}'.")
        return ids

    def search_vectors(self, collection_name, query_vectors, top_k=5):
        # Get collections
        collection = Collection(collection_name)

        # Search for the nearest vectors
        search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
        results = collection.search(
            data=query_vectors,
            anns_field="vector",
            param=search_params,
            limit=top_k,
        )

        # Show results
        for i, result in enumerate(results):
            print(f"Résultats pour le vecteur de requête {i}:")
            for match in result:
                print(f"ID: {match.id}, Distance: {match.distance}")
        return results

    def drop_collection(self, collection_name):
        # Delete the collection
        collection = Collection(collection_name)
        collection.drop()
        print(f"Collection '{collection_name}' deleted.")


# Exemple d'utilisation
if __name__ == "__main__":
    rng = np.random.default_rng(seed=19530)

    # Initi database
    db = MilvusDatabase()

    """fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=dimension)
    ]"""
    # vectors = np.random.random((1, 128)).astype(np.float32).tolist()

    fields = [
        FieldSchema(
            name="pk",
            dtype=DataType.VARCHAR,
            is_primary=True,
            auto_id=False,
            max_length=100,
        ),
        FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=128),
    ]

    db.create_collection(
        "testCollection", fields, "Collection de vecteurs de caractéristiques"
    )

    row = {"pk": "19530", "vector": rng.random((1, 128), np.float32)[0]}
    db.insert_vectors(row)
    # index = db.create_index_document(document)

    db.create_index_collection("testCollection", "vector")
