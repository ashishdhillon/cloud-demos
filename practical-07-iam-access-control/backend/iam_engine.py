import fnmatch
import json
import time
from typing import Any, Dict, List, Tuple

DEFAULT_PERSONAS = {
    "junior-developer": {
        "name": "Junior Developer",
        "role_arn": "arn:aws:iam::123456789012:role/JuniorDeveloperRole",
        "description": "Permitted to read development S3 buckets and inspect EC2 metadata. Explicitly blocked from any production resources.",
        "policy": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "AllowS3DevRead",
                    "Effect": "Allow",
                    "Action": ["s3:GetObject", "s3:ListBucket"],
                    "Resource": ["arn:aws:s3:::dev-*", "arn:aws:s3:::dev-*/*"]
                },
                {
                    "Sid": "AllowEC2DescribeOnly",
                    "Effect": "Allow",
                    "Action": ["ec2:Describe*"],
                    "Resource": ["*"]
                },
                {
                    "Sid": "ExplicitDenyProductionAccess",
                    "Effect": "Deny",
                    "Action": ["*"],
                    "Resource": ["arn:aws:*:*:*:*prod*", "arn:aws:s3:::prod-*", "arn:aws:s3:::prod-*/*"]
                }
            ]
        }
    },
    "devops-engineer": {
        "name": "DevOps Engineer",
        "role_arn": "arn:aws:iam::123456789012:role/DevOpsAdminRole",
        "description": "Full lifecycle deployment permissions across compute and storage. Safeguarded with an explicit deny against dropping production databases.",
        "policy": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "AllowComputeAndStorageOps",
                    "Effect": "Allow",
                    "Action": ["ec2:*", "s3:*", "rds:Describe*", "rds:RebootDBInstance"],
                    "Resource": ["*"]
                },
                {
                    "Sid": "GuardrailDenyProdDBDestruction",
                    "Effect": "Deny",
                    "Action": ["rds:DeleteDBInstance", "rds:DeleteDBCluster"],
                    "Resource": ["arn:aws:rds:*:*:db:prod-*", "arn:aws:rds:*:*:cluster:prod-*"]
                }
            ]
        }
    },
    "database-admin": {
        "name": "Database Administrator (DBA)",
        "role_arn": "arn:aws:iam::123456789012:role/DatabaseAdminRole",
        "description": "Complete database administration. High-risk operations (such as dropping databases) strictly require Multi-Factor Authentication (MFA).",
        "policy": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "AllowAllRDSOperations",
                    "Effect": "Allow",
                    "Action": ["rds:*"],
                    "Resource": ["arn:aws:rds:*:*:db:*"]
                },
                {
                    "Sid": "RequireMFAForDatabaseDrop",
                    "Effect": "Deny",
                    "Action": ["rds:DeleteDBInstance"],
                    "Resource": ["*"],
                    "Condition": {
                        "BoolIfExists": {
                            "aws:MultiFactorAuthPresent": "false"
                        }
                    }
                },
                {
                    "Sid": "DenyIAMModifications",
                    "Effect": "Deny",
                    "Action": ["iam:*"],
                    "Resource": ["*"]
                }
            ]
        }
    },
    "security-auditor": {
        "name": "Security & Compliance Auditor",
        "role_arn": "arn:aws:iam::123456789012:role/SecurityAuditorRole",
        "description": "Read-only audit visibility across CloudTrail and IAM. Explicit deny on all create, delete, and update mutations.",
        "policy": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "AllowAuditInspection",
                    "Effect": "Allow",
                    "Action": ["cloudtrail:LookupEvents", "cloudtrail:Get*", "iam:Get*", "iam:List*"],
                    "Resource": ["*"]
                },
                {
                    "Sid": "DenyAllStateMutations",
                    "Effect": "Deny",
                    "Action": ["*:Create*", "*:Delete*", "*:Update*", "*:Put*"],
                    "Resource": ["*"]
                }
            ]
        }
    }
}

class IAMEvaluationEngine:
    def __init__(self):
        self.personas = json.loads(json.dumps(DEFAULT_PERSONAS))
        # Custom editable policy
        self.personas["custom-role"] = {
            "name": "Custom Role (Interactive Policy Sandbox)",
            "role_arn": "arn:aws:iam::123456789012:role/CustomInteractiveRole",
            "description": "User-defined policy document for real-time rule and condition testing.",
            "policy": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "AllowS3PublicRead",
                        "Effect": "Allow",
                        "Action": ["s3:GetObject"],
                        "Resource": ["arn:aws:s3:::public-*/*"]
                    },
                    {
                        "Sid": "DenyAllWildcard",
                        "Effect": "Deny",
                        "Action": ["iam:*"],
                        "Resource": ["*"]
                    }
                ]
            }
        }
        self.audit_history = []

    def get_personas(self) -> Dict[str, Any]:
        return {
            k: {
                "name": v["name"],
                "role_arn": v["role_arn"],
                "description": v["description"],
                "policy": v["policy"]
            }
            for k, v in self.personas.items()
        }

    def update_custom_policy(self, policy_doc: Dict[str, Any]) -> bool:
        if not isinstance(policy_doc, dict) or "Statement" not in policy_doc:
            raise ValueError("Policy must be a valid JSON object containing a 'Statement' array.")
        self.personas["custom-role"]["policy"] = policy_doc
        return True

    def _match_pattern(self, pattern: str, target: str) -> bool:
        return fnmatch.fnmatch(target.lower(), pattern.lower())

    def _matches_action(self, statement_actions: Any, requested_action: str) -> bool:
        actions = [statement_actions] if isinstance(statement_actions, str) else statement_actions
        for a in actions:
            if a == "*" or self._match_pattern(a, requested_action):
                return True
        return False

    def _matches_resource(self, statement_resources: Any, requested_resource: str) -> bool:
        resources = [statement_resources] if isinstance(statement_resources, str) else statement_resources
        for r in resources:
            if r == "*" or self._match_pattern(r, requested_resource):
                return True
        return False

    def _eval_conditions(self, conditions: Dict[str, Any], context: Dict[str, Any]) -> bool:
        if not conditions:
            return True
        
        # Check BoolIfExists / Bool conditions
        for cond_type, cond_map in conditions.items():
            if cond_type.startswith("Bool"):
                for key, expected in cond_map.items():
                    val = str(context.get(key, "false")).lower()
                    exp_bool = str(expected).lower()
                    if val != exp_bool:
                        return False
        return True

    def evaluate(self, persona_id: str, action: str, resource: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        start_time = time.perf_counter()
        context = context or {}
        persona = self.personas.get(persona_id)
        if not persona:
            raise ValueError(f"Persona '{persona_id}' does not exist.")

        policy = persona["policy"]
        statements = policy.get("Statement", [])
        
        trace = []
        trace.append({
            "step": 1,
            "rule": "Default Baseline",
            "detail": "Evaluation initialized with default Implicit Deny. Access is forbidden unless explicitly allowed.",
            "status": "IMPLICIT_DENY"
        })

        # Step 2: Evaluate Explicit Deny Statements (Deny ALWAYS overrides Allow)
        explicit_deny = None
        for stmt in statements:
            if stmt.get("Effect") == "Deny":
                sid = stmt.get("Sid", "UnnamedDeny")
                act_match = self._matches_action(stmt.get("Action", []), action)
                res_match = self._matches_resource(stmt.get("Resource", []), resource)
                cond_match = self._eval_conditions(stmt.get("Condition", {}), context)
                
                if act_match and res_match and cond_match:
                    explicit_deny = stmt
                    trace.append({
                        "step": 2,
                        "rule": f"Explicit Deny [{sid}]",
                        "detail": f"Matched Deny statement '{sid}' for action '{action}' on '{resource}'. Evaluation halted immediately.",
                        "status": "EXPLICIT_DENY",
                        "statement": stmt
                    })
                    break

        if explicit_deny:
            eval_time_ms = round((time.perf_counter() - start_time) * 1000, 3)
            result = {
                "decision": "DENY",
                "decision_type": "EXPLICIT_DENY",
                "status_code": 403,
                "persona": persona["name"],
                "action": action,
                "resource": resource,
                "matched_statement_sid": explicit_deny.get("Sid"),
                "eval_time_ms": eval_time_ms,
                "trace": trace
            }
            self.audit_history.append(result)
            return result

        trace.append({
            "step": 2,
            "rule": "Explicit Deny Check",
            "detail": "No matching Explicit Deny statements encountered. Proceeding to Explicit Allow evaluation.",
            "status": "PASS"
        })

        # Step 3: Evaluate Explicit Allow Statements
        explicit_allow = None
        for stmt in statements:
            if stmt.get("Effect") == "Allow":
                sid = stmt.get("Sid", "UnnamedAllow")
                act_match = self._matches_action(stmt.get("Action", []), action)
                res_match = self._matches_resource(stmt.get("Resource", []), resource)
                cond_match = self._eval_conditions(stmt.get("Condition", {}), context)
                
                if act_match and res_match and cond_match:
                    explicit_allow = stmt
                    trace.append({
                        "step": 3,
                        "rule": f"Explicit Allow [{sid}]",
                        "detail": f"Matched Allow statement '{sid}' for action '{action}' on '{resource}'. Access granted.",
                        "status": "ALLOW",
                        "statement": stmt
                    })
                    break

        eval_time_ms = round((time.perf_counter() - start_time) * 1000, 3)

        if explicit_allow:
            result = {
                "decision": "ALLOW",
                "decision_type": "EXPLICIT_ALLOW",
                "status_code": 200,
                "persona": persona["name"],
                "action": action,
                "resource": resource,
                "matched_statement_sid": explicit_allow.get("Sid"),
                "eval_time_ms": eval_time_ms,
                "trace": trace
            }
        else:
            trace.append({
                "step": 3,
                "rule": "Explicit Allow Check",
                "detail": "No matching Allow statement found. Reverting to default Implicit Deny.",
                "status": "IMPLICIT_DENY"
            })
            result = {
                "decision": "DENY",
                "decision_type": "IMPLICIT_DENY",
                "status_code": 403,
                "persona": persona["name"],
                "action": action,
                "resource": resource,
                "matched_statement_sid": None,
                "eval_time_ms": eval_time_ms,
                "trace": trace
            }

        self.audit_history.append(result)
        return result

    def get_audit_history(self) -> List[Dict[str, Any]]:
        return list(reversed(self.audit_history[-50:]))
