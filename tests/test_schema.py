"""Small test to validate the finding example against the JSON schema."""
import json
import unittest
from pathlib import Path
from jsonschema import validate, ValidationError

ROOT = Path(__file__).resolve().parents[1]

class TestFindingSchema(unittest.TestCase):
    def test_example_matches_schema(self):
        schema = json.loads((ROOT / 'schemas' / 'finding.schema.json').read_text(encoding='utf-8'))
        example = json.loads((ROOT / 'examples' / 'finding_example.json').read_text(encoding='utf-8'))
        try:
            validate(instance=example, schema=schema)
        except ValidationError as e:
            self.fail(f'Example finding does not match schema: {e}')

if __name__ == '__main__':
    unittest.main()
