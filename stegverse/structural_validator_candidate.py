"""Bounded, offline structural validation candidate; NEVER governance authorization."""
import hashlib
import json

DIALECT = "stegverse-bounded-v1"
MAX_SCHEMA_DEPTH = 32
MAX_INSTANCE_DEPTH = 256
SUPPORTED = {"type", "required", "properties", "additionalProperties", "items", "enum", "const", "minLength", "maxLength", "minimum", "maximum",
             "minItems", "maxItems", "uniqueItems"}
# Annotation-only keywords: accepted and ignored, as in 2020-12 they never affect validity.
ANNOTATIONS = {"title", "description", "$comment", "examples"}
# Root-only identity metadata (T12): no effect on validity. $schema must name exactly the
# dialect the ecosystem uses (all StegVerse-Labs/.github schemas declare it); anything else
# fails closed. Below the root both stay unsupported, since $ref/$defs resolution is not.
REFERENCE_DIALECT_URI = "https://json-schema.org/draft/2020-12/schema"
ROOT_IDENTITY = {"$schema", "$id"}
TYPES = {"null": lambda v: v is None, "boolean": lambda v: type(v) is bool,
         "integer": lambda v: type(v) is int, "number": lambda v: type(v) in (int, float),
         "string": lambda v: isinstance(v, str), "array": lambda v: isinstance(v, list),
         "object": lambda v: isinstance(v, dict)}

# Machine-readable compatibility contract. Every divergence from JSON Schema 2020-12
# is in the fail-closed direction: the candidate may reject what the reference
# accepts, never the reverse.
CONTRACT = {
    "dialect": DIALECT,
    "contract_version": "1.2",
    "supported_keywords": sorted(SUPPORTED),
    "annotation_keywords": sorted(ANNOTATIONS),
    "root_identity_keywords": {"$schema": REFERENCE_DIALECT_URI, "$id": "string"},
    "max_schema_depth": MAX_SCHEMA_DEPTH,
    "max_instance_depth": MAX_INSTANCE_DEPTH,
    "instance_values": "JSON only: null, bool, int, finite float, str, list, dict with str keys",
    "reference": "JSON Schema 2020-12 (jsonschema Draft202012Validator) as differential oracle only",
    "divergences_fail_closed": [
        "integer-valued floats such as 1.0 are not type integer",
        "boolean subschemas (true/false) are unsupported",
        "$ref, $defs and every keyword outside supported_keywords are rejected; $schema and $id only at the root",
        "$schema other than the 2020-12 URI is rejected",
        "external registries and dialects other than this one are rejected",
        "schemas nested deeper than max_schema_depth or not JSON-encodable are rejected",
        "instances that are not JSON values (NaN, Infinity, sets, tuples, bytes, non-string keys) are rejected",
        "instances nested deeper than max_instance_depth are rejected",
    ],
    "authority_effect": "NONE",
}

def canonical_bytes(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode()

def json_equal(a, b):
    """JSON value equality: booleans are never numbers, 1 equals 1.0, containers compare deeply."""
    if isinstance(a, bool) or isinstance(b, bool):
        return type(a) is type(b) and a == b
    if type(a) in (int, float) and type(b) in (int, float):
        return a == b
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(json_equal(x, y) for x, y in zip(a, b))
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(json_equal(a[k], b[k]) for k in a)
    return type(a) is type(b) and a == b

def _equality_key(value):
    """Hashable key under JSON equality (1 == 1.0, True != 1); instance depth is already bounded."""
    if isinstance(value, bool):
        return ("bool", value)
    if type(value) in (int, float):
        return ("num", int(value) if float(value).is_integer() else value)
    if isinstance(value, list):
        return ("arr", tuple(_equality_key(v) for v in value))
    if isinstance(value, dict):
        return ("obj", tuple(sorted((k, _equality_key(v)) for k, v in value.items())))
    return (type(value).__name__, value)

def pointer(parts):
    return "".join("/" + str(p).replace("~", "~0").replace("/", "~1") for p in parts)

def _instance_finding(instance):
    """First non-JSON value or depth violation in the instance, found iteratively (no recursion)."""
    stack = [(instance, [], 0)]
    while stack:
        value, path, depth = stack.pop()
        if depth > MAX_INSTANCE_DEPTH:
            return {"path": pointer(path), "code": "INSTANCE_DEPTH_EXCEEDED"}
        if value is None or isinstance(value, (bool, str)) or type(value) is int:
            continue
        if type(value) is float:
            if value != value or value in (float("inf"), float("-inf")):
                return {"path": pointer(path), "code": "INVALID_INSTANCE_ENCODING"}
            continue
        if type(value) is list:
            stack.extend((item, path + [i], depth + 1) for i, item in reversed(list(enumerate(value))))
            continue
        if type(value) is dict:
            if any(type(k) is not str for k in value):
                return {"path": pointer(path), "code": "INVALID_INSTANCE_ENCODING"}
            stack.extend((value[k], path + [k], depth + 1) for k in sorted(value, reverse=True))
            continue
        return {"path": pointer(path), "code": "INVALID_INSTANCE_ENCODING"}
    return None

def _preflight(spec, path, error, depth=0):
    """Check every reachable subschema, including branches the instance never visits."""
    if depth > MAX_SCHEMA_DEPTH or not isinstance(spec, dict):
        error(path, "INVALID_SCHEMA_OR_DEPTH")
        return
    allowed = SUPPORTED | ANNOTATIONS | (ROOT_IDENTITY if depth == 0 else set())
    for key in sorted(spec.keys() - allowed):
        error(path, "UNSUPPORTED_KEYWORD:" + key)
    if depth == 0 and "$schema" in spec and spec["$schema"] != REFERENCE_DIALECT_URI:
        error(path, "UNSUPPORTED_DIALECT_URI")
    if depth == 0 and "$id" in spec and not isinstance(spec["$id"], str):
        error(path, "INVALID_IDENTITY:$id")
    types = spec.get("type")
    if types is not None:
        choices = types if isinstance(types, list) else [types]
        if not choices or any(not isinstance(t, str) or t not in TYPES for t in choices):
            error(path, "UNSUPPORTED_TYPE")
    if "required" in spec and (not isinstance(spec["required"], list) or
        any(not isinstance(k, str) for k in spec["required"]) or
        len(spec["required"]) != len(set(k for k in spec["required"] if isinstance(k, str)))):
        error(path, "INVALID_REQUIRED")
    if "enum" in spec and (not isinstance(spec["enum"], list) or not spec["enum"]):
        error(path, "INVALID_ENUM")
    if "additionalProperties" in spec and type(spec["additionalProperties"]) is not bool:
        error(path, "UNSUPPORTED_ADDITIONAL_PROPERTIES")
    for key in ("minLength", "maxLength"):
        if key in spec and (type(spec[key]) is not int or spec[key] < 0):
            error(path, "INVALID_BOUND:" + key)
    for key in ("minimum", "maximum"):
        if key in spec and type(spec[key]) not in (int, float):
            error(path, "INVALID_BOUND:" + key)
    for key in ("minItems", "maxItems"):
        if key in spec and (type(spec[key]) is not int or spec[key] < 0):
            error(path, "INVALID_BOUND:" + key)
    if "uniqueItems" in spec and type(spec["uniqueItems"]) is not bool:
        error(path, "INVALID_BOUND:uniqueItems")
    for key in ("title", "description", "$comment"):
        if key in spec and not isinstance(spec[key], str):
            error(path, "INVALID_ANNOTATION:" + key)
    if "examples" in spec and not isinstance(spec["examples"], list):
        error(path, "INVALID_ANNOTATION:examples")
    props = spec.get("properties", {})
    if not isinstance(props, dict) or any(not isinstance(k, str) for k in props):
        error(path, "INVALID_PROPERTIES")
    else:
        for k in sorted(props):
            _preflight(props[k], path + ["properties", k], error, depth + 1)
    if "items" in spec:
        _preflight(spec["items"], path + ["items"], error, depth + 1)

def _admit_schema(schema, schema_digest, dialect, registry):
    def refused(code):
        return {"valid": False, "errors": [{"path": "", "code": code}], "authority_effect": "NONE"}
    if dialect != DIALECT or registry is not None:
        return refused("UNSUPPORTED_DIALECT_OR_REGISTRY")
    try:
        actual = hashlib.sha256(canonical_bytes(schema)).hexdigest()
    except (TypeError, ValueError, RecursionError):
        # RecursionError: nesting beyond the encoder's stack is refused, never raised.
        return refused("INVALID_SCHEMA_ENCODING")
    if actual != schema_digest:
        return refused("SCHEMA_DIGEST_MISMATCH")
    errors = []
    _preflight(schema, [], lambda path, code: errors.append({"path": pointer(path), "code": code}))
    return {"valid": not errors, "errors": errors, "schema_digest": actual, "dialect": dialect, "authority_effect": "NONE"}

def check_schema(schema, schema_digest, dialect=DIALECT, registry=None):
    """Schema validity alone, independent of any instance. Returns findings, not ALLOW."""
    return _admit_schema(schema, schema_digest, dialect, registry)

def validate(instance, schema, schema_digest, dialect=DIALECT, registry=None):
    """Returns structural findings, not ALLOW. Unknown features fail closed."""
    admitted = _admit_schema(schema, schema_digest, dialect, registry)
    if admitted["errors"]:
        return admitted
    actual = admitted["schema_digest"]
    finding = _instance_finding(instance)
    if finding is not None:
        return {"valid": False, "errors": [finding], "schema_digest": actual, "dialect": dialect, "authority_effect": "NONE"}
    errors = []
    def error(path, code):
        errors.append({"path": pointer(path), "code": code})
    def visit(value, spec, path, depth=0):
        if depth > MAX_SCHEMA_DEPTH or not isinstance(spec, dict):
            error(path, "INVALID_SCHEMA_OR_DEPTH")
            return
        for key in sorted(spec.keys() - SUPPORTED - ANNOTATIONS - (ROOT_IDENTITY if depth == 0 else set())):
            error(path, "UNSUPPORTED_KEYWORD:" + key)
        types = spec.get("type")
        if types is not None:
            choices = types if isinstance(types, list) else [types]
            if not choices or any(not isinstance(t, str) or t not in TYPES for t in choices):
                error(path, "UNSUPPORTED_TYPE")
                return
            if not any(TYPES[t](value) for t in choices):
                error(path, "TYPE")
                return
        if "const" in spec and not json_equal(value, spec["const"]):
            error(path, "CONST")
        if "enum" in spec:
            if not isinstance(spec["enum"], list):
                error(path, "INVALID_ENUM")
            elif not any(json_equal(value, member) for member in spec["enum"]):
                error(path, "ENUM")
        if isinstance(value, dict):
            props = spec.get("properties", {})
            required = spec.get("required", [])
            if not isinstance(props, dict) or not isinstance(required, list) or any(not isinstance(k, str) for k in required):
                error(path, "INVALID_OBJECT_SCHEMA")
                return
            for k in sorted(required):
                if k not in value:
                    error(path + [k], "REQUIRED")
            extra = spec.get("additionalProperties", True)
            if extra not in (True, False) or type(extra) is not bool:
                error(path, "UNSUPPORTED_ADDITIONAL_PROPERTIES")
            for k in sorted(value):
                if k in props:
                    visit(value[k], props[k], path + [k], depth + 1)
                elif extra is False:
                    error(path + [k], "ADDITIONAL_PROPERTY")
        if isinstance(value, list) and "items" in spec:
            for i, item in enumerate(value):
                visit(item, spec["items"], path + [i], depth + 1)
        if isinstance(value, list):
            if "minItems" in spec and len(value) < spec["minItems"]:
                error(path, "MINITEMS")
            if "maxItems" in spec and len(value) > spec["maxItems"]:
                error(path, "MAXITEMS")
            if spec.get("uniqueItems") is True:
                seen = set()
                for item in value:
                    key = _equality_key(item)
                    if key in seen:
                        error(path, "UNIQUE_ITEMS")
                        break
                    seen.add(key)
        for key, kind in (("minLength", str), ("maxLength", str), ("minimum", (int, float)), ("maximum", (int, float))):
            if key not in spec:
                continue
            bound = spec[key]
            if key.endswith("Length"):
                if type(bound) is not int or bound < 0:
                    error(path, "INVALID_BOUND:" + key)
                elif isinstance(value, str) and ((key == "minLength" and len(value) < bound) or (key == "maxLength" and len(value) > bound)):
                    error(path, key.upper())
            elif type(bound) not in (int, float):
                error(path, "INVALID_BOUND:" + key)
            elif type(value) in (int, float) and ((key == "minimum" and value < bound) or (key == "maximum" and value > bound)):
                error(path, key.upper())
    visit(instance, schema, [])
    return {"valid": not errors, "errors": errors, "schema_digest": actual, "dialect": dialect, "authority_effect": "NONE"}
