import json
import re
import threading
import time
import uuid

DEFAULT_HCL = """# Terraform Multi-Cloud Infrastructure as Code Manifest
terraform {
  required_version = ">= 1.8.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.45.0"
    }
    google = {
      source  = "hashicorp/google"
      version = "~> 5.24.0"
    }
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0.2"
    }
  }
}

# --- AWS Provider (Object Storage & Key Vault) ---
resource "aws_s3_bucket" "central_archive" {
  bucket        = "multicloud-central-archive"
  force_destroy = true

  tags = {
    Environment = "Production"
    ManagedBy   = "Terraform"
  }
}

resource "aws_s3_object" "app_config" {
  bucket  = aws_s3_bucket.central_archive.id
  key     = "configs/services.json"
  content = jsonencode({ "status" = "healthy", "version" = "2.4.0" })
}

# --- Google Cloud Provider (Analytics Bucket) ---
resource "google_storage_bucket" "analytics_lake" {
  name          = "gcp-analytics-data-lake"
  location      = "US-CENTRAL1"
  storage_class = "STANDARD"
}

# --- Docker Provider (Edge Application Container) ---
resource "docker_container" "frontend_portal" {
  name  = "multicloud-frontend-portal"
  image = "nginx:1.27-alpine"

  ports {
    internal = 80
    external = 8085
  }
}

output "s3_bucket_arn" {
  value = aws_s3_bucket.central_archive.arn
}

output "gcp_lake_url" {
  value = "gs://${google_storage_bucket.analytics_lake.name}"
}

output "portal_endpoint" {
  value = "http://localhost:8085"
}
"""

class TerraformEngine:
    def __init__(self):
        self.lock = threading.RLock()
        self.hcl_code = DEFAULT_HCL.strip()
        self.is_initialized = True
        self.lineage = str(uuid.uuid4())
        self.serial = 1

        # Real in-memory state tracking
        self.tfstate = {
            "version": 4,
            "terraform_version": "1.8.5",
            "serial": self.serial,
            "lineage": self.lineage,
            "outputs": {},
            "resources": []
        }

        # Cloud Infrastructure Reality (Simulating the physical cloud providers)
        self.cloud_infrastructure = {}

        # Cloud drift flag
        self.drift_detected = False
        self.drift_details = None

        # Pre-seed initial deployment so dashboard opens with live state
        self._apply_initial_resources()

    def _apply_initial_resources(self):
        self.cloud_infrastructure = {
            "aws_s3_bucket.central_archive": {
                "id": "multicloud-central-archive",
                "arn": "arn:aws:s3:::multicloud-central-archive",
                "tags": {"Environment": "Production", "ManagedBy": "Terraform"}
            },
            "aws_s3_object.app_config": {
                "id": "configs/services.json",
                "bucket": "multicloud-central-archive",
                "content_length": 42
            },
            "google_storage_bucket.analytics_lake": {
                "id": "gcp-analytics-data-lake",
                "location": "US-CENTRAL1",
                "storage_class": "STANDARD"
            },
            "docker_container.frontend_portal": {
                "id": "container-7f9a21bc",
                "name": "multicloud-frontend-portal",
                "ports": "8085:80/tcp",
                "status": "running"
            }
        }
        self._sync_state_from_cloud()

    def _sync_state_from_cloud(self):
        self.tfstate["serial"] = self.serial
        self.tfstate["resources"] = []
        for key, attrs in self.cloud_infrastructure.items():
            parts = key.split(".")
            r_type = parts[0]
            r_name = parts[1]
            provider = "aws" if r_type.startswith("aws") else ("google" if r_type.startswith("google") else "docker")
            self.tfstate["resources"].append({
                "mode": "managed",
                "type": r_type,
                "name": r_name,
                "provider": f"provider[\"registry.terraform.io/hashicorp/{provider}\"]",
                "instances": [
                    {
                        "schema_version": 1,
                        "attributes": attrs
                    }
                ]
            })

        self.tfstate["outputs"] = {
            "s3_bucket_arn": {
                "value": self.cloud_infrastructure.get("aws_s3_bucket.central_archive", {}).get("arn", "N/A"),
                "type": "string"
            },
            "gcp_lake_url": {
                "value": f"gs://{self.cloud_infrastructure.get('google_storage_bucket.analytics_lake', {}).get('id', 'N/A')}",
                "type": "string"
            },
            "portal_endpoint": {
                "value": "http://localhost:8085",
                "type": "string"
            }
        }

    def get_status(self):
        with self.lock:
            return {
                "is_initialized": self.is_initialized,
                "hcl_code": self.hcl_code,
                "serial": self.serial,
                "resource_count": len(self.cloud_infrastructure),
                "drift_detected": self.drift_detected,
                "drift_details": self.drift_details,
                "tfstate": self.tfstate,
                "active_resources": self.cloud_infrastructure
            }

    def update_hcl(self, new_hcl: str):
        with self.lock:
            self.hcl_code = new_hcl.strip()
            return {"success": True}

    def run_init(self):
        with self.lock:
            self.is_initialized = True
            log = [
                "Initializing the backend...",
                "",
                "Initializing provider plugins...",
                "- Finding hashicorp/aws versions matching \"~> 5.45.0\"...",
                "- Finding hashicorp/google versions matching \"~> 5.24.0\"...",
                "- Finding kreuzwerker/docker versions matching \"~> 3.0.2\"...",
                "- Installing hashicorp/aws v5.45.0... (verified checksum)",
                "- Installing hashicorp/google v5.24.0... (verified checksum)",
                "- Installing kreuzwerker/docker v3.0.2... (verified checksum)",
                "",
                "Terraform has been successfully initialized!",
                "",
                "You may now begin working with Terraform. Try running \"terraform plan\" to see",
                "any changes that are required for your infrastructure."
            ]
            return {"output": "\n".join(log), "status": "success"}

    def run_plan(self):
        with self.lock:
            # Parse declared resources from HCL
            declared = re.findall(r'resource\s+"([^"]+)"\s+"([^"]+)"', self.hcl_code)
            declared_map = {f"{r[0]}.{r[1]}": (r[0], r[1]) for r in declared}

            current_keys = set(self.cloud_infrastructure.keys())
            declared_keys = set(declared_map.keys())

            to_add = declared_keys - current_keys
            to_destroy = current_keys - declared_keys
            to_change = []

            # Check if drift occurred
            drift_log = []
            if self.drift_detected:
                drift_log = [
                    "Note: Objects have changed outside of Terraform",
                    "",
                    "Terraform detected the following changes made outside of Terraform since the last \"terraform apply\":",
                    f"  # {self.drift_details['target']} has changed:",
                    f"    {self.drift_details['message']}",
                    "",
                    "Unless you have made equivalent changes to your configuration, or ignored the",
                    "relevant attributes using \"ignore_changes\", the following plan may include",
                    "actions to undo or reconcile these changes.",
                    "------------------------------------------------------------------------"
                ]
                to_change.append(self.drift_details["target"])

            plan_lines = []
            if drift_log:
                plan_lines.extend(drift_log)

            plan_lines.append("Terraform will perform the following actions:")
            plan_lines.append("")

            for k in to_add:
                r_type, r_name = declared_map[k]
                plan_lines.append(f"  # {k} will be created")
                plan_lines.append(f"  + resource \"{r_type}\" \"{r_name}\" {{")
                plan_lines.append(f"      + id          = (known after apply)")
                plan_lines.append(f"      + provider    = \"{r_type.split('_')[0]}\"")
                plan_lines.append(f"      + status      = \"provisioned\"")
                plan_lines.append(f"    }}")
                plan_lines.append("")

            for k in to_change:
                plan_lines.append(f"  # {k} will be updated in-place (reconcile drift)")
                plan_lines.append(f"  ~ resource \"{k.split('.')[0]}\" \"{k.split('.')[1]}\" {{")
                plan_lines.append(f"      ~ tags = {{")
                plan_lines.append(f"          + Environment = \"Production\"")
                plan_lines.append(f"        }}")
                plan_lines.append(f"    }}")
                plan_lines.append("")

            for k in to_destroy:
                plan_lines.append(f"  # {k} will be destroyed")
                plan_lines.append(f"  - resource \"{k.split('.')[0]}\" \"{k.split('.')[1]}\" {{")
                plan_lines.append(f"      - id = \"{self.cloud_infrastructure[k].get('id', 'N/A')}\"")
                plan_lines.append(f"    }}")
                plan_lines.append("")

            if not to_add and not to_destroy and not to_change:
                plan_lines = [
                    "No changes. Your infrastructure matches the configuration.",
                    "",
                    "Terraform has compared your real infrastructure against your configuration",
                    "and found no differences, so no changes need to be applied."
                ]

            summary = f"Plan: {len(to_add)} to add, {len(to_change)} to change, {len(to_destroy)} to destroy."
            plan_lines.append(summary)

            return {
                "output": "\n".join(plan_lines),
                "summary": summary,
                "to_add": list(to_add),
                "to_change": list(to_change),
                "to_destroy": list(to_destroy),
                "has_changes": bool(to_add or to_destroy or to_change)
            }

    def run_apply(self):
        with self.lock:
            plan = self.run_plan()
            if not plan["has_changes"]:
                return {
                    "output": "Apply complete! Resources: 0 added, 0 changed, 0 destroyed.\n\nOutputs:\n" + json.dumps(self.tfstate["outputs"], indent=2),
                    "status": "no_changes"
                }

            lines = ["terraform apply -auto-approve", ""]

            # Process additions
            for k in plan["to_add"]:
                r_type = k.split(".")[0]
                r_name = k.split(".")[1]
                lines.append(f"{k}: Creating...")
                # Simulate cloud provisioning
                item_id = f"{r_name}-{uuid.uuid4().hex[:6]}"
                attrs = {"id": item_id, "status": "active"}
                if "s3" in r_type:
                    attrs["arn"] = f"arn:aws:s3:::{item_id}"
                elif "docker" in r_type:
                    attrs["ports"] = "8085:80/tcp"

                self.cloud_infrastructure[k] = attrs
                lines.append(f"{k}: Creation complete after 1s [id={item_id}]")

            # Process changes / drift reconciliation
            for k in plan["to_change"]:
                lines.append(f"{k}: Modifying... [reconciling drift]")
                if k in self.cloud_infrastructure:
                    self.cloud_infrastructure[k]["tags"] = {"Environment": "Production", "ManagedBy": "Terraform"}
                lines.append(f"{k}: Modifications complete after 0s")

            # Process destructions
            for k in plan["to_destroy"]:
                lines.append(f"{k}: Destroying...")
                if k in self.cloud_infrastructure:
                    del self.cloud_infrastructure[k]
                lines.append(f"{k}: Destruction complete after 0s")

            self.drift_detected = False
            self.drift_details = None
            self.serial += 1
            self._sync_state_from_cloud()

            lines.append("")
            lines.append(f"Apply complete! Resources: {len(plan['to_add'])} added, {len(plan['to_change'])} changed, {len(plan['to_destroy'])} destroyed.")
            lines.append("")
            lines.append("Outputs:")
            for out_name, out_val in self.tfstate["outputs"].items():
                lines.append(f"{out_name} = \"{out_val['value']}\"")

            return {"output": "\n".join(lines), "status": "success", "serial": self.serial}

    def trigger_drift(self):
        """Simulates an engineer manually altering cloud resources outside Terraform (ClickOps)."""
        with self.lock:
            target = "aws_s3_bucket.central_archive"
            if target in self.cloud_infrastructure:
                self.drift_detected = True
                self.drift_details = {
                    "target": target,
                    "action": "Out-of-band Tag Deletion / Manual Console Edit",
                    "message": "~ tags = {\n    - \"Environment\" = \"Production\" -> null\n  }"
                }
                # Delete tag in reality
                self.cloud_infrastructure[target]["tags"] = {"ManagedBy": "Manual-ClickOps-User"}
                return {"drift_detected": True, "target": target}
            return {"error": "Target resource not active to drift"}

    def run_refresh(self):
        with self.lock:
            lines = [
                "aws_s3_bucket.central_archive: Refreshing state... [id=multicloud-central-archive]",
                "google_storage_bucket.analytics_lake: Refreshing state... [id=gcp-analytics-data-lake]",
                "docker_container.frontend_portal: Refreshing state... [id=container-7f9a21bc]"
            ]
            if self.drift_detected:
                lines.append(f"\n[!] Note: Drift detected in {self.drift_details['target']}!")
            else:
                lines.append("\n[✓] All resources in terraform.tfstate match real-world cloud APIs.")
            return {"output": "\n".join(lines)}

    def run_destroy(self):
        with self.lock:
            count = len(self.cloud_infrastructure)
            lines = ["terraform destroy -auto-approve", ""]
            for k in list(self.cloud_infrastructure.keys()):
                lines.append(f"{k}: Destroying...")
                del self.cloud_infrastructure[k]
                lines.append(f"{k}: Destruction complete after 0s")

            self.drift_detected = False
            self.drift_details = None
            self.serial += 1
            self._sync_state_from_cloud()

            lines.append("")
            lines.append(f"Destroy complete! Resources: {count} destroyed.")
            return {"output": "\n".join(lines), "status": "destroyed", "serial": self.serial}
