import os
import uuid
from flask import Flask, Response, jsonify, request, send_file
from werkzeug.utils import secure_filename
from s3_engine import S3Engine

app = Flask(__name__)
engine = S3Engine()

def xml_error(code: str, message: str, resource: str, status_code: int = 403):
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Error>
    <Code>{code}</Code>
    <Message>{message}</Message>
    <Resource>{resource}</Resource>
    <RequestId>{uuid.uuid4()}</RequestId>
</Error>"""
    return Response(xml, status=status_code, mimetype="application/xml")

@app.get("/health")
def health():
    return jsonify({"status": "healthy", "service": "s3-mock-engine"})

@app.get("/api/stats")
def get_stats():
    return jsonify(engine.get_stats())

@app.get("/api/events")
def get_events():
    return jsonify({"events": engine.get_events()})

@app.get("/api/buckets")
def list_buckets():
    return jsonify({"buckets": engine.list_buckets()})

@app.post("/api/buckets")
def create_bucket():
    data = request.get_json(silent=True) or {}
    name = data.get("name", "").strip()
    storage_class = data.get("storage_class", "Standard")
    if not name:
        return jsonify({"error": "Bucket name is required"}), 400
    try:
        bucket = engine.create_bucket(name, storage_class)
        return jsonify({"bucket": bucket}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.get("/api/buckets/<bucket>/objects")
def list_objects(bucket):
    objs = engine.list_objects(bucket)
    if objs is None:
        return jsonify({"error": "Bucket not found"}), 404
    return jsonify({"bucket": bucket, "objects": objs})

@app.post("/api/buckets/<bucket>/objects")
def upload_object(bucket):
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files["file"]
    if not file.filename:
        return jsonify({"error": "No file selected"}), 400
    
    filename = secure_filename(file.filename)
    acl = request.form.get("acl", "private")
    storage_class = request.form.get("storage_class", "Standard")
    
    try:
        data = file.read()
        obj = engine.put_object(bucket, filename, data, acl, storage_class)
        return jsonify({"object": obj}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.post("/api/buckets/<bucket>/objects/<path:key>/acl")
def update_acl(bucket, key):
    data = request.get_json(silent=True) or {}
    acl = data.get("acl", "private")
    updated = engine.update_acl(bucket, key, acl)
    if not updated:
        return jsonify({"error": "Object not found"}), 404
    return jsonify({"object": updated})

@app.post("/api/buckets/<bucket>/objects/<path:key>/presign")
def generate_presigned_url(bucket, key):
    data = request.get_json(silent=True) or {}
    expires_in = data.get("expires_in", 30)
    try:
        result = engine.generate_presigned_url(bucket, key, expires_in)
        return jsonify(result)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

@app.delete("/api/buckets/<bucket>/objects/<path:key>")
def delete_object(bucket, key):
    success = engine.delete_object(bucket, key)
    if not success:
        return jsonify({"error": "Object not found"}), 404
    return jsonify({"success": True})

# Direct S3 Endpoint
@app.get("/s3/<bucket>/<path:key>")
def get_s3_object(bucket, key):
    resource_path = f"/{bucket}/{key}"
    
    # 1. Check Presigned URL Query Parameters
    if "X-Amz-Signature" in request.args:
        valid, code, msg = engine.verify_presigned_url(bucket, key, request.args.to_dict())
        if not valid:
            return xml_error(code, msg, resource_path, status_code=403)
        
        file_path, obj_info = engine.get_object(bucket, key)
        if not file_path:
            return xml_error("NoSuchKey", "The specified key does not exist.", resource_path, 404)
        
        return send_file(
            file_path,
            mimetype=obj_info.get("content_type", "application/octet-stream"),
            as_attachment=False,
            download_name=key
        )

    # 2. Check Static Object ACL
    file_path, obj_info = engine.get_object(bucket, key)
    if not file_path:
        engine.log_event("GetObject", bucket, key, "404 Not Found", "Key does not exist")
        return xml_error("NoSuchKey", "The specified key does not exist.", resource_path, 404)

    if obj_info.get("acl") == "public-read":
        engine.log_event("GetObject", bucket, key, "200 OK", "Public Read Access Granted")
        return send_file(
            file_path,
            mimetype=obj_info.get("content_type", "application/octet-stream"),
            as_attachment=False,
            download_name=key
        )
    else:
        engine.log_event("GetObject", bucket, key, "403 Forbidden", "Access Denied: Object ACL is private")
        return xml_error(
            "AccessDenied",
            "Access Denied. Object ACL is private. Please use an authenticated request or generate an expiring Presigned URL.",
            resource_path,
            status_code=403
        )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
