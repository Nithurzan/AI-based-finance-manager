from bson import ObjectId

# Helper function to serialize a single MongoDB document
def serialize_document(document):
    if not document:
        return None
    document["_id"] = str(document["_id"])  # Convert ObjectId to string
    return document

# Helper function to serialize a list of MongoDB documents
def serialize_documents(documents):
    return [serialize_document(doc) for doc in documents]