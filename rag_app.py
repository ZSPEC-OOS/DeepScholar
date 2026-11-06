import os
import hmac
from functools import wraps
from flask import Flask, request, jsonify, render_template, Response
from openai import OpenAI

app = Flask(__name__, template_folder="rag_templates")
app.config["MAX_CONTENT_LENGTH"] = 45 * 1024 * 1024
MODEL = os.environ.get("OPENAI_MODEL", "gpt-4.1-mini")

def protected(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        password = os.environ.get("APP_PASSWORD")
        if not password:
            return jsonify(error="APP_PASSWORD is not configured in Render."), 503
        auth = request.authorization
        if not (auth and hmac.compare_digest(auth.password or "", password)):
            return Response("Authentication required", 401, {"WWW-Authenticate": 'Basic realm="RAG Studio"'})
        return fn(*args, **kwargs)
    return wrapper

def client():
    if not os.environ.get("OPENAI_API_KEY"):
        raise ValueError("Set OPENAI_API_KEY in the Render environment.")
    return OpenAI(api_key=os.environ["OPENAI_API_KEY"], timeout=180)

def fail(e):
    app.logger.exception("RAG request failed")
    return jsonify(error=str(e)), 400

@app.get("/health")
def health():
    return jsonify(ok=True)

@app.get("/")
@protected
def home():
    return render_template("index.html")

@app.post("/api/library")
@protected
def library():
    try:
        c = client()
        store_id = (request.json or {}).get("store_id")
        if store_id:
            v = c.vector_stores.retrieve(store_id)
        else:
            v = c.vector_stores.create(name="RAG Studio Scientific Library")
        return jsonify(id=v.id, name=v.name, counts=v.file_counts.model_dump())
    except Exception as e:
        return fail(e)

@app.post("/api/upload")
@protected
def upload():
    try:
        store_id = request.form.get("store_id")
        upload_file = request.files.get("file")
        if not store_id or not upload_file or not upload_file.filename.lower().endswith(".pdf"):
            return jsonify(error="Provide a library and a PDF."), 400
        c = client()
        f = c.files.create(file=(upload_file.filename, upload_file.stream, "application/pdf"), purpose="assistants")
        linked = c.vector_stores.files.create_and_poll(vector_store_id=store_id, file_id=f.id)
        if linked.status != "completed":
            return jsonify(error="Indexing status: " + linked.status), 422
        return jsonify(filename=upload_file.filename, file_id=f.id, status=linked.status)
    except Exception as e:
        return fail(e)

@app.post("/api/search")
@protected
def search():
    try:
        data = request.get_json(force=True)
        q = (data.get("query") or "").strip()
        if not q or not data.get("store_id"):
            return jsonify(error="Provide a question and library ID."), 400
        found = client().vector_stores.search(vector_store_id=data["store_id"], query=q, max_num_results=12)
        items = []
        for hit in found.data:
            content = "\n".join(getattr(part, "text", "") for part in hit.content)
            items.append(dict(filename=hit.filename, score=round(hit.score or 0, 3), text=content[:2200]))
        return jsonify(results=items)
    except Exception as e:
        return fail(e)

@app.post("/api/write")
@protected
def write():
    try:
        data = request.get_json(force=True)
        task = (data.get("task") or "").strip()
        if not task or not data.get("store_id"):
            return jsonify(error="Provide a writing instruction and library ID."), 400
        draft = (data.get("draft") or "")[:30000]
        instructions = (
            "You are a precise scientific research writer. Use the indexed PDF library to "
            "substantiate scientific claims; distinguish supported evidence from inference. "
            "Do not invent citations, DOIs, page numbers, or quotations. "
            "Use source citations provided by the file_search tool. "
            "If evidence is inadequate, explicitly say so. "
            "Return clean Markdown, with clear headings when appropriate. "
            "Respect the user's requested transformation of the current draft. "
            "Do not present an incomplete retrieval as an exhaustive review."
        )
        result = client().responses.create(
            model=MODEL,
            instructions=instructions,
            input="REQUEST:\n"+task+"\n\nCURRENT DRAFT (may be empty):\n"+draft,
            tools=[{"type":"file_search","vector_store_ids":[data["store_id"]],"max_num_results":15}],
            include=["file_search_call.results"],
            max_output_tokens=4000
        )
        citations = []
        seen = set()
        for output in result.output:
            if getattr(output, "type", "") == "message":
                for part in getattr(output, "content", []):
                    for a in getattr(part, "annotations", []):
                        if getattr(a, "type", "") == "file_citation":
                            key = (a.file_id, a.filename)
                            if key not in seen:
                                seen.add(key)
                                citations.append({"filename":a.filename,"file_id":a.file_id})
        return jsonify(text=result.output_text, citations=citations)
    except Exception as e:
        return fail(e)

if __name__ == "__main__":
    app.run(port=int(os.environ.get("PORT", 10000)))
