"""Build the static patch server into ./public for Netlify.

- Validates every definitions/<id>.json against the full definition schema.
- Writes public/patch/<id>.json, public/software.json and public/status.json.
- Copies the status page from static/ into public/.

Any error exits non-zero so Netlify keeps the previous deploy live.
"""
from datetime import datetime, timezone
import json
import os
import shutil
import sys

from jsonschema import validate, ValidationError

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFINITIONS_DIR = os.path.join(ROOT, 'definitions')
SCHEMA_FILE = os.path.join(ROOT, 'schemas', 'schema_full_definition.json')
PUBLIC_DIR = os.path.join(ROOT, 'public')
STATIC_DIR = os.path.join(ROOT, 'static')

with open(SCHEMA_FILE, 'r') as f_obj:
    definition_schema = json.load(f_obj)


def fail(message):
    print(f'ERROR: {message}', file=sys.stderr)
    sys.exit(1)


def validate_definition(data, source):
    try:
        validate(data, definition_schema)
    except ValidationError as error:
        fail(f"Validation Error in {source}: {error.message} "
             f"for path: /{'/'.join([str(i) for i in error.path])}")


def load_local_definitions():
    definitions = dict()
    if not os.path.isdir(DEFINITIONS_DIR):
        return definitions

    for filename in sorted(os.listdir(DEFINITIONS_DIR)):
        if not filename.endswith('.json'):
            continue

        path = os.path.join(DEFINITIONS_DIR, filename)
        try:
            with open(path, 'r') as f_obj:
                data = json.load(f_obj)
        except json.JSONDecodeError as error:
            fail(f'{path} is not valid JSON: {error}')

        validate_definition(data, path)

        title = filename[:-len('.json')]
        if data['id'] != title:
            fail(f"The filename '{filename}' does not match the patch "
                 f"definition ID '{data['id']}'")

        print(f"Loaded local definition '{title}'")
        definitions[title] = data

    return definitions


def title_list(definitions):
    return [
        {
            'name': data['name'],
            'publisher': data['publisher'],
            'lastModified': data['lastModified'],
            'currentVersion': data['currentVersion'],
            'id': data['id']
        }
        for data in definitions.values()
    ]


def main():
    definitions = load_local_definitions()

    if os.path.exists(PUBLIC_DIR):
        shutil.rmtree(PUBLIC_DIR)
    shutil.copytree(STATIC_DIR, PUBLIC_DIR)
    os.makedirs(os.path.join(PUBLIC_DIR, 'patch'))

    for title, data in definitions.items():
        with open(os.path.join(PUBLIC_DIR, 'patch', f'{title}.json'),
                  'w') as f_obj:
            json.dump(data, f_obj)

    with open(os.path.join(PUBLIC_DIR, 'software.json'), 'w') as f_obj:
        json.dump(title_list(definitions), f_obj)

    with open(os.path.join(PUBLIC_DIR, 'status.json'), 'w') as f_obj:
        json.dump({
            'builtAt': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
            'titles': len(definitions)
        }, f_obj)

    print(f'Built {len(definitions)} patch definition(s) into {PUBLIC_DIR}')


if __name__ == '__main__':
    main()
