"""Add a new version to a local patch definition.

Usage: python scripts/add_version.py <title-id> <version.json>

Edits definitions/<title-id>.json in place; commit and push to deploy.
"""
from datetime import datetime, timezone
import json
import os
import sys

from jsonschema import validate, ValidationError

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

with open(os.path.join(ROOT, 'schemas', 'schema_version.json'), 'r') as f_obj:
    version_schema = json.load(f_obj)


def fail(message):
    print(f'ERROR: {message}', file=sys.stderr)
    sys.exit(1)


def main():
    if len(sys.argv) != 3:
        fail('Usage: python scripts/add_version.py <title-id> <version.json>')

    title, version_file = sys.argv[1], sys.argv[2]

    with open(version_file, 'r') as f_obj:
        data = json.load(f_obj)

    try:
        validate(data, version_schema)
    except ValidationError as error:
        fail(f"Validation Error in submitted JSON : {error.message} "
             f"for path: /{'/'.join([str(i) for i in error.path])}")

    path = os.path.join(ROOT, 'definitions', f'{title}.json')
    if not os.path.exists(path):
        fail(f'Not Found: The patch definition does not exist: {path}')

    with open(path, 'r') as f_obj:
        patch_definition = json.load(f_obj)

    if data['version'] in [i['version'] for i in patch_definition['patches']]:
        fail(f"The version '{data['version']}' already exists in the patch "
             f"definition")

    patch_definition['patches'].insert(0, data)
    patch_definition['lastModified'] = \
        datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    patch_definition['currentVersion'] = data['version']

    with open(path, 'w') as f_obj:
        json.dump(patch_definition, f_obj, indent=2)
        f_obj.write('\n')

    print(f"Successfully added version '{data['version']}' to '{title}'")


if __name__ == '__main__':
    main()
