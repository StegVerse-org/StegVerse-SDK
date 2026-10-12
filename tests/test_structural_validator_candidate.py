"""Deterministic structural validator differential and negative tests."""
import hashlib
import json
import unittest
from stegverse.structural_validator_candidate import CONTRACT, SUPPORTED, canonical_bytes, check_schema, validate

class StructuralValidatorCandidateTests(unittest.TestCase):
    def check_case(self, instance, schema, expected):
        digest = hashlib.sha256(canonical_bytes(schema)).hexdigest()
        actual = validate(instance, schema, digest)
        self.assertEqual(actual["valid"], expected)
        self.assertEqual(actual, validate(instance, schema, digest))
        self.assertEqual(actual["authority_effect"], "NONE")
        return actual

    def test_corpus(self):
        cases = [
            ({"a": "ok"}, {"type": "object", "required": ["a"], "properties": {"a": {"type": "string"}}}, True),
            ({}, {"type": "object", "required": ["a"]}, False),
            ({"a": 2}, {"type": "object", "properties": {"a": {"type": "string"}}}, False),
            ([1, 2], {"type": "array", "items": {"type": "integer"}}, True),
            ([1, "x"], {"type": "array", "items": {"type": "integer"}}, False),
            (False, {"type": "integer"}, False),
            (3, {"type": "number", "minimum": 4}, False),
            ("abc", {"type": "string", "minLength": 2}, True),
            ("a", {"type": "string", "minLength": 2}, False),
            ({"a/b": 1}, {"type": "object", "additionalProperties": False}, False),
            ("x", {"$ref": "#/$defs/x"}, False),
        ]
        for instance, schema, expected in cases:
            with self.subTest(instance=instance, schema=schema):
                self.check_case(instance, schema, expected)

    def test_fail_closed_unsupported_nested_schema_and_depth(self):
        schema = {"type": "object", "properties": {"child": {"$ref": "#/$defs/child"}}}
        result = self.check_case({"child": "value"}, schema, False)
        self.assertIn("UNSUPPORTED_KEYWORD:$ref", [e["code"] for e in result["errors"]])
        nested = {"type": "array", "items": {"type": "integer"}}
        for _ in range(34):
            nested = {"type": "array", "items": nested}
        instance = 1
        for _ in range(35):
            instance = [instance]
        result = self.check_case(instance, nested, False)
        self.assertIn("INVALID_SCHEMA_OR_DEPTH", [e["code"] for e in result["errors"]])

    def test_pointer_escape_and_required_diagnostics(self):
        schema = {"type": "object", "required": ["a/b~c"]}
        result = self.check_case({}, schema, False)
        self.assertEqual(result["errors"][0]["path"], "/a~1b~0c")
        self.assertEqual(result["errors"][0]["code"], "REQUIRED")

    def test_unvisited_schema_branches_fail_closed(self):
        cases = [
            ({}, {"properties": {"absent": {"$ref": "https://invalid.example/schema"}}}),
            ({}, {"properties": {"absent": {"type": "imaginary"}}}),
            ({}, {"items": {"unknownKeyword": True}}),
            ({}, {"required": ["x", "x"]}),
            ({}, {"enum": []}),
            ({}, {"properties": {"absent": {"minLength": -1}}}),
        ]
        for instance, schema in cases:
            with self.subTest(schema=schema):
                self.check_case(instance, schema, False)

    def test_rejects_wrong_digest(self):
        result = validate("x", {"type": "string"}, "0" * 64)
        self.assertEqual(result["errors"][0]["code"], "SCHEMA_DIGEST_MISMATCH")

    def test_rejects_unapproved_dialect_and_registry(self):
        schema = {"type": "string"}
        digest = hashlib.sha256(canonical_bytes(schema)).hexdigest()
        self.assertFalse(validate("x", schema, digest, "https://json-schema.org/draft/2020-12/schema")["valid"])
        self.assertFalse(validate("x", schema, digest, registry={})["valid"])

    def test_differential_against_jsonschema_when_available(self):
        try:
            from jsonschema import Draft202012Validator
        except ImportError:
            self.skipTest("Pinned reference validator not installed; differential verification unavailable")
        cases = [
            ({"a": "ok"}, {"type": "object", "required": ["a"], "properties": {"a": {"type": "string"}}}),
            ({}, {"type": "object", "required": ["a"]}),
            ([1, 2], {"type": "array", "items": {"type": "integer"}}),
            ([1, "x"], {"type": "array", "items": {"type": "integer"}}),
            (False, {"type": "integer"}),
            (True, {"enum": [1]}),
            (1, {"const": True}),
            ({"a/b": 1}, {"type": "object", "additionalProperties": False}),
            ("a", {"type": "string", "minLength": 2}),
        ]
        for instance, schema in cases:
            expected = Draft202012Validator(schema).is_valid(instance)
            self.check_case(instance, schema, expected)
    def test_const_and_enum_never_equate_booleans_with_numbers(self):
        # Python equates True with 1 and False with 0; JSON Schema does not.
        cases = [
            (1, {"const": True}), (0, {"const": False}), (True, {"const": 1}), (False, {"const": 0}),
            (True, {"const": 1.0}), ([True], {"const": [1]}), ({"a": True}, {"const": {"a": 1}}),
            (False, {"enum": [0]}), (1, {"enum": [True]}), (True, {"enum": [1, "a"]}),
            ([True], {"items": {"const": 1}}), ({"a": True}, {"properties": {"a": {"const": 1}}}),
        ]
        for instance, schema in cases:
            with self.subTest(instance=instance, schema=schema):
                self.assertEqual(self.check_case(instance, schema, False)["errors"][0]["code"],
                                 "ENUM" if "enum" in schema else "CONST")

    def test_const_and_enum_keep_json_numeric_equality(self):
        for instance, schema in ((1.0, {"const": 1}), (1, {"enum": [1.0]}), (True, {"const": True}),
                                 ([1, {"a": None}], {"const": [1, {"a": None}]})):
            with self.subTest(instance=instance, schema=schema):
                self.check_case(instance, schema, True)

    def test_generated_differential_never_accepts_what_reference_rejects(self):
        try:
            from jsonschema import Draft202012Validator
        except ImportError:
            self.skipTest("Pinned reference validator not installed; differential verification unavailable")
        values = [None, True, False, 0, 1, 2, 1.0, 1.5, -1, "", "a", "ab", [], [1], [True], ["x"],
                  {}, {"a": 1}, {"a": True}, {"a": "x"}, {"b": 1}]
        schemas = [{"type": t} for t in ("null", "boolean", "integer", "number", "string", "array", "object")]
        schemas += [{"const": c} for c in (True, False, 1, 0, 1.0, "a", None, [1], {"a": 1})]
        schemas += [{"enum": e} for e in ([0], [1], [True], [False], [1, "a"], [[1]], [{"a": 1}], [None])]
        schemas += [{"minimum": 1}, {"maximum": 1}, {"minLength": 1}, {"maxLength": 1},
                    {"type": "object", "required": ["a"]}, {"items": {"const": 1}},
                    {"type": "object", "properties": {"a": {"type": "integer"}}, "additionalProperties": False}]
        for schema in schemas:
            digest = hashlib.sha256(canonical_bytes(schema)).hexdigest()
            for instance in values:
                if validate(instance, schema, digest)["valid"]:
                    with self.subTest(instance=instance, schema=schema):
                        self.assertTrue(Draft202012Validator(schema).is_valid(instance))


    def test_schema_nesting_beyond_encoder_stack_fails_closed(self):
        schema = {}
        for _ in range(200000):
            schema = {"items": schema}
        for result in (validate([], schema, "0" * 64), check_schema(schema, "0" * 64)):
            self.assertEqual(result["errors"], [{"path": "", "code": "INVALID_SCHEMA_ENCODING"}])
            self.assertFalse(result["valid"])

    def test_schema_validity_is_checked_independently_of_any_instance(self):
        good = {"type": "object", "required": ["a"], "properties": {"a": {"type": "string", "maxLength": 3}}}
        bad = [
            ({"type": "imaginary"}, "UNSUPPORTED_TYPE"),
            ({"properties": {"a": {"$ref": "#/x"}}}, "UNSUPPORTED_KEYWORD:$ref"),
            ({"required": "a"}, "INVALID_REQUIRED"),
            ({"enum": []}, "INVALID_ENUM"),
            ({"maxLength": -1}, "INVALID_BOUND:maxLength"),
            ({"minimum": True}, "INVALID_BOUND:minimum"),
            ({"additionalProperties": {}}, "UNSUPPORTED_ADDITIONAL_PROPERTIES"),
            ({"items": True}, "INVALID_SCHEMA_OR_DEPTH"),
            ({"properties": []}, "INVALID_PROPERTIES"),
        ]
        result = check_schema(good, hashlib.sha256(canonical_bytes(good)).hexdigest())
        self.assertEqual((result["valid"], result["errors"], result["authority_effect"]), (True, [], "NONE"))
        for schema, code in bad:
            with self.subTest(schema=schema):
                result = check_schema(schema, hashlib.sha256(canonical_bytes(schema)).hexdigest())
                self.assertFalse(result["valid"])
                self.assertIn(code, [e["code"] for e in result["errors"]])
                self.assertEqual(result, check_schema(schema, result["schema_digest"]))

    def test_contract_matches_implementation_and_declares_no_authority(self):
        self.assertEqual(CONTRACT["supported_keywords"], sorted(SUPPORTED))
        self.assertEqual(CONTRACT["authority_effect"], "NONE")
        # Documented divergences are fail-closed: rejected here, accepted by the reference.
        for instance, schema in ((1.0, {"type": "integer"}), (True, {"items": False})):
            with self.subTest(schema=schema):
                self.assertFalse(validate(instance, schema, hashlib.sha256(canonical_bytes(schema)).hexdigest())["valid"])

    def test_schema_differential_never_admits_what_reference_metaschema_rejects(self):
        try:
            from jsonschema import Draft202012Validator
            from jsonschema.exceptions import SchemaError
        except ImportError:
            self.skipTest("Pinned reference validator not installed; differential verification unavailable")
        candidates = [
            {"type": "string"}, {"type": ["string", "null"]}, {"type": []}, {"type": "imaginary"},
            {"required": ["a", "a"]}, {"required": "a"}, {"required": [1]}, {"enum": []}, {"enum": 1},
            {"minLength": -1}, {"minLength": 1.5}, {"maxLength": "2"}, {"minimum": "1"}, {"maximum": None},
            {"properties": {"a": {"type": 1}}}, {"properties": []}, {"items": {"type": "integer"}},
            {"items": {"minLength": -2}}, {"additionalProperties": False}, {"additionalProperties": 0},
            {"const": None}, {"type": "object", "properties": {"a": {"enum": [[], {}]}}, "required": ["a"]},
        ]
        for schema in candidates:
            if check_schema(schema, hashlib.sha256(canonical_bytes(schema)).hexdigest())["valid"]:
                with self.subTest(schema=schema):
                    try:
                        Draft202012Validator.check_schema(schema)
                    except SchemaError as exc:
                        self.fail(f"candidate admitted a schema the reference metaschema rejects: {exc.message}")

if __name__ == "__main__":
    unittest.main()
