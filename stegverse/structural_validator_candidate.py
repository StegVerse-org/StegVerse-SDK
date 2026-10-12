"""Bounded, offline structural validation candidate; NEVER governance authorization."""
import hashlib
import json

SUPPORTED = {"type", "required", "properties", "additionalProperties", "items", "enum", "const", "minLength", "maxLength", "minimum", "maximum"}
TYPES = {"null": lambda v: v is None, "boolean": lambda v: type(v) is bool,
         "integer": lambda v: type(v) is int, "number": lambda v: type(v) in (int, float),
         "string": lambda v: isinstance(v, str), "array": lambda v: isinstance(v, list),
         "object": lambda v: isinstance(v, dict)}

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

def pointer(parts):
    return "".join("/" + str(p).replace("~", "~0").replace("/", "~1") for p in parts)

def validate(instance, schema, schema_digest, dialect="stegverse-bounded-v1", registry=None):
    """Returns structural findings, not ALLOW. Unknown features fail closed."""
    if dialect != "stegverse-bounded-v1" or registry is not None:
        return {"valid": False, "errors": [{"path": "", "code": "UNSUPPORTED_DIALECT_OR_REGISTRY"}], "authority_effect": "NONE"}
    try:
        actual = hashlib.sha256(canonical_bytes(schema)).hexdigest()
    except (TypeError, ValueError):
        return {"valid": False, "errors": [{"path": "", "code": "INVALID_SCHEMA_ENCODING"}], "authority_effect": "NONE"}
    if actual != schema_digest:
        return {"valid": False, "errors": [{"path": "", "code": "SCHEMA_DIGEST_MISMATCH"}], "authority_effect": "NONE"}
    errors = []
    def error(path, code):
        errors.append({"path": pointer(path), "code": code})
    def visit(value, spec, path, depth=0):
        if depth > 32 or not isinstance(spec, dict):
            error(path, "INVALID_SCHEMA_OR_DEPTH")
            return
        for key in sorted(spec.keys() - SUPPORTED):
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
