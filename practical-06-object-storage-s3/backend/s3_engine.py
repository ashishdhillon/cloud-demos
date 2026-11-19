import hashlib
import hmac
import json
import mimetypes
import os
import shutil
import time
from collections import deque
from datetime import datetime, timezone
from threading import Lock

SECRET_KEY = os.environ.get("S3_SECRET_KEY", "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY")
ACCESS_KEY = os.environ.get("S3_ACCESS_KEY", "AKIAIOSFODNN7EXAMPLE")
STORAGE_ROOT = os.environ.get("STORAGE_ROOT", "/data/storage")
MAX_EVENTS = 200

class S3Engine:
    def __init__(self, storage_root: str = STORAGE_ROOT):
        self.storage_root = os.path.abspath(storage_root)
        os.makedirs(self.storage_root, exist_ok=True)
        self.meta_file = os.path.join(self.storage_root, "_metadata.json")
        self.lock = Lock()
        self.events: deque = deque(maxlen=MAX_EVENTS)
        self._load_meta()

    def _load_meta(self):
        if os.path.exists(self.meta_file):
            try:
                with open(self.meta_file, "r", encoding="utf-8") as f:
                    self.meta = json.load(f)
                self._last_mtime = os.path.getmtime(self.meta_file)
            except Exception:
                self.meta = {"buckets": {}}
                self._last_mtime = 0
        else:
            self.meta = {"buckets": {}}
            self._last_mtime = 0
        
        # Ensure default buckets
        if "production-assets" not in self.meta["buckets"]:
            self.create_bucket("production-assets", "Standard")
        if "secure-vault" not in self.meta["buckets"]:
            self.create_bucket("secure-vault", "Standard")

    def _sync_from_disk(self):
        if os.path.exists(self.meta_file):
            try:
                mtime = os.path.getmtime(self.meta_file)
                if mtime > getattr(self, "_last_mtime", 0):
                    with open(self.meta_file, "r", encoding="utf-8") as f:
                        self.meta = json.load(f)
                    self._last_mtime = mtime
            except Exception:
                pass

    def _save_meta(self):
        os.makedirs(os.path.dirname(self.meta_file), exist_ok=True)
        with open(self.meta_file, "w", encoding="utf-8") as f:
            json.dump(self.meta, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        self._last_mtime = os.path.getmtime(self.meta_file)

    def log_event(self, action: str, bucket: str, key: str = "", status: str = "200 OK", details: str = ""):
        event = {
            "timestamp": datetime.now(timezone.utc).strftime("%H:%M:%S"),
            "action": action,
            "bucket": bucket,
            "key": key,
            "status": status,
            "details": details
        }
        self.events.appendleft(event)

    def get_events(self):
        with self.lock:
            return list(self.events)

    def list_buckets(self):
        with self.lock:
            self._sync_from_disk()
            result = []
            for name, bdata in self.meta["buckets"].items():
                obj_count = len(bdata.get("objects", {}))
                total_bytes = sum(o.get("size", 0) for o in bdata.get("objects", {}).values())
                result.append({
                    "name": name,
                    "created_at": bdata.get("created_at"),
                    "storage_class": bdata.get("storage_class", "Standard"),
                    "object_count": obj_count,
                    "total_bytes": total_bytes
                })
            return result

    def create_bucket(self, name: str, storage_class: str = "Standard"):
        clean_name = "".join(c for c in name.lower() if c.isalnum() or c in "-.").strip("-.")
        if not clean_name:
            raise ValueError("Invalid bucket name")
        
        with self.lock:
            if clean_name in self.meta["buckets"]:
                return self.meta["buckets"][clean_name]
            
            b_path = os.path.join(self.storage_root, clean_name)
            os.makedirs(b_path, exist_ok=True)
            bdata = {
                "name": clean_name,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "storage_class": storage_class,
                "objects": {}
            }
            self.meta["buckets"][clean_name] = bdata
            self._save_meta()
            self.log_event("CreateBucket", clean_name, "", "200 OK", f"Class: {storage_class}")
            return bdata

    def list_objects(self, bucket: str):
        with self.lock:
            self._sync_from_disk()
            if bucket not in self.meta["buckets"]:
                return None
            objs = self.meta["buckets"][bucket].get("objects", {})
            return list(objs.values())

    def put_object(self, bucket: str, key: str, file_data: bytes, acl: str = "private", storage_class: str = "Standard"):
        with self.lock:
            if bucket not in self.meta["buckets"]:
                raise ValueError(f"Bucket {bucket} does not exist")
            
            b_dir = os.path.join(self.storage_root, bucket)
            os.makedirs(b_dir, exist_ok=True)
            f_path = os.path.join(b_dir, key)
            
            # Ensure subdirectories if key contains slashes
            os.makedirs(os.path.dirname(f_path), exist_ok=True)
            with open(f_path, "wb") as f:
                f.write(file_data)
                f.flush()
                os.fsync(f.fileno())

            etag = hashlib.md5(file_data).hexdigest()
            content_type, _ = mimetypes.guess_type(key)
            if not content_type:
                content_type = "application/octet-stream"

            obj_info = {
                "key": key,
                "bucket": bucket,
                "size": len(file_data),
                "etag": etag,
                "content_type": content_type,
                "acl": acl if acl in ["private", "public-read"] else "private",
                "storage_class": storage_class,
                "last_modified": datetime.now(timezone.utc).isoformat(),
                "downloads": 0
            }
            self.meta["buckets"][bucket]["objects"][key] = obj_info
            self._save_meta()
            self.log_event("PutObject", bucket, key, "200 OK", f"Size: {len(file_data)} bytes, ACL: {acl}")
            return obj_info

    def update_acl(self, bucket: str, key: str, acl: str):
        with self.lock:
            if bucket not in self.meta["buckets"] or key not in self.meta["buckets"][bucket]["objects"]:
                return None
            if acl not in ["private", "public-read"]:
                acl = "private"
            self.meta["buckets"][bucket]["objects"][key]["acl"] = acl
            self._save_meta()
            self.log_event("PutObjectAcl", bucket, key, "200 OK", f"New ACL: {acl}")
            return self.meta["buckets"][bucket]["objects"][key]

    def delete_object(self, bucket: str, key: str):
        with self.lock:
            if bucket not in self.meta["buckets"] or key not in self.meta["buckets"][bucket]["objects"]:
                return False
            f_path = os.path.join(self.storage_root, bucket, key)
            if os.path.exists(f_path):
                try:
                    os.remove(f_path)
                except Exception:
                    pass
            del self.meta["buckets"][bucket]["objects"][key]
            self._save_meta()
            self.log_event("DeleteObject", bucket, key, "204 No Content")
            return True

    def get_object(self, bucket: str, key: str):
        with self.lock:
            self._sync_from_disk()
            if bucket not in self.meta["buckets"] or key not in self.meta["buckets"][bucket]["objects"]:
                return None, None
            f_path = os.path.join(self.storage_root, bucket, key)
            if not os.path.exists(f_path):
                return None, None
            obj_info = self.meta["buckets"][bucket]["objects"][key]
            obj_info["downloads"] += 1
            self._save_meta()
            return f_path, obj_info

    def generate_presigned_url(self, bucket: str, key: str, expires_in_seconds: int = 30) -> dict:
        with self.lock:
            if bucket not in self.meta["buckets"] or key not in self.meta["buckets"][bucket]["objects"]:
                raise ValueError("Object does not exist")
            
        now_ts = int(time.time())
        expires = max(1, int(expires_in_seconds))
        canonical_string = f"{bucket}/{key}:{now_ts}:{expires}"
        sig = hmac.new(SECRET_KEY.encode(), canonical_string.encode(), hashlib.sha256).hexdigest()
        
        query_string = (
            f"X-Amz-Algorithm=AWS4-HMAC-SHA256"
            f"&X-Amz-Credential={ACCESS_KEY}"
            f"&X-Amz-Date={now_ts}"
            f"&X-Amz-Expires={expires}"
            f"&X-Amz-Signature={sig}"
        )
        url = f"/s3/{bucket}/{key}?{query_string}"
        
        self.log_event("GeneratePresignedUrl", bucket, key, "200 OK", f"Expires: {expires}s")
        return {
            "url": url,
            "expires_in": expires,
            "created_at": now_ts,
            "expires_at": now_ts + expires,
            "signature": sig
        }

    def verify_presigned_url(self, bucket: str, key: str, params: dict) -> tuple[bool, str, str]:
        date_str = params.get("X-Amz-Date")
        expires_str = params.get("X-Amz-Expires")
        sig = params.get("X-Amz-Signature")
        
        if not (date_str and expires_str and sig):
            return False, "AccessDenied", "Missing required security parameters."
        
        try:
            now_ts = int(time.time())
            created_ts = int(date_str)
            expires = int(expires_str)
        except ValueError:
            return False, "InvalidArgument", "Invalid date or expiration parameter."
            
        # Check signature authenticity
        canonical_string = f"{bucket}/{key}:{created_ts}:{expires}"
        expected_sig = hmac.new(SECRET_KEY.encode(), canonical_string.encode(), hashlib.sha256).hexdigest()
        
        if not hmac.compare_digest(sig, expected_sig):
            self.log_event("VerifyPresignedUrl", bucket, key, "403 Forbidden", "Invalid Signature")
            return False, "SignatureDoesNotMatch", "The request signature we calculated does not match the signature you provided."
            
        # Check expiration
        if now_ts > (created_ts + expires):
            time_diff = now_ts - (created_ts + expires)
            self.log_event("VerifyPresignedUrl", bucket, key, "403 Expired", f"Expired {time_diff}s ago")
            return False, "RequestExpired", f"Request has expired. URL was valid for {expires}s and expired {time_diff}s ago."
            
        self.log_event("VerifyPresignedUrl", bucket, key, "200 OK", "Valid presigned authorization")
        return True, "OK", ""

    def get_stats(self):
        with self.lock:
            self._sync_from_disk()
            total_buckets = len(self.meta["buckets"])
            total_objects = 0
            total_bytes = 0
            private_objects = 0
            public_objects = 0
            storage_classes = {}
            
            for b in self.meta["buckets"].values():
                for o in b.get("objects", {}).values():
                    total_objects += 1
                    total_bytes += o.get("size", 0)
                    if o.get("acl") == "public-read":
                        public_objects += 1
                    else:
                        private_objects += 1
                    sclass = o.get("storage_class", "Standard")
                    storage_classes[sclass] = storage_classes.get(sclass, 0) + 1
                    
            return {
                "total_buckets": total_buckets,
                "total_objects": total_objects,
                "total_bytes": total_bytes,
                "private_objects": private_objects,
                "public_objects": public_objects,
                "storage_classes": storage_classes
            }
