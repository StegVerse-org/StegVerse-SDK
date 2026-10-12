"""Deterministic structural validator differential and negative tests."""
import hashlib
import json
import unittest
from stegverse.structural_validator_candidate import validate, canonical_bytes

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
            ("a", {"type": "string", "minLength": 2}),
        ]
        for instance, schema in cases:
            expected = Draft202012Validator(schema).is_valid(instance)
            self.check_case(instance, schema, expected)

if __name__ == "__main__":
    unittest.main()
