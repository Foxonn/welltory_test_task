import os
import json

from schema import PATH_PROJECT_DIR, get_schemas

PATH_FILES_JSON = os.path.join(PATH_PROJECT_DIR, 'task_folder/event')

TABLE_TYPES = {
    'array': 'list',
    'boolean': 'bool',
    'object': 'dict',
    'string': 'str',
    'number': ['float', 'int'],
    'integer': 'int',
    'null': 'NoneType',
}


def _get_json_files():
    pfj = PATH_FILES_JSON

    if not os.path.isdir(pfj):
        raise Exception(f"Directory '{pfj}' not found!")

    files = [f for f in os.scandir(pfj) if f.name.endswith('.json')]

    if not files:
        raise Exception(f"Directory '{pfj}' don`t have json files")

    return files


def _read_json_file(file: os.DirEntry):
    with open(file.path, mode='r') as fp:
        file = json.load(fp)

    return file or None


def _validate_fields_and_values(schema, data: dict, errors):
    required_fields = schema.get('required')
    properties = schema.get('properties')
    properties_fields = properties.keys()

    if needs := set(required_fields) - set(list(data.keys())):
        errors.append(
            f"'{list(data.keys())}' don't have required field(s): {needs}"
        )

    for prop_field in (properties_fields - needs):
        type_field = properties.get(prop_field).get('type', None)
        sources = data.get(prop_field)

        if type_field == 'array':
            type_items = properties.get(prop_field).get('items', None)

            if _validate_type(prop_field, type_field, data, sources, errors):
                for source in sources:
                    _validate_fields_and_values(type_items, source, errors)
        else:
            _validate_type(prop_field, type_field, data, sources, errors)


def _translate_type(field_types):
    if isinstance(field_types, list):
        return [TABLE_TYPES.get(type_) for type_ in field_types if
                TABLE_TYPES.get(type_, None)]
    return TABLE_TYPES.get(field_types, None)


def _validate_type(prop_field, type_field, data, sources, errors):
    translate_types = _translate_type(type_field)

    if translate_types:
        if type(sources).__name__ not in translate_types:
            errors.append(
                f"'{data}', field '{prop_field}' have wrong type, "
                f"expected: '{type_field}'"
            )
            return False
    else:
        errors.append(f"'{sources}', have undefined type: '{type_field}'")
        return False

    return True


def _validate_json_file(obj_file: os.DirEntry, schemas):
    file = _read_json_file(obj_file)
    errors = list()

    if not file:
        raise Exception(f"File '{obj_file.name}' is invalid.")

    event = file.get('event', None)

    if not event:
        raise Exception(f"Schema with event '{event}' not found.")

    schema = schemas.get(event, None)

    if not schema:
        raise Exception(f"Event '{event}' not found.")

    if data := file.get('data', None):
        _validate_fields_and_values(schema['schema'], data, errors)
    else:
        raise Exception(f"{file}, 'data' is null or not found.")

    return errors


def run_validate_json_files(schemas):
    files = _get_json_files()

    for f in files:
        try:
            _validate_json_file(f, schemas)
        except Exception as err:
            print(err)
            print(f.name)


def generate_report(schemas):
    files = _get_json_files()

    with open('report.txt', mode='w', encoding='utf-8') as fp:
        for f in files:
            try:
                errors = _validate_json_file(f, schemas)

                for e in errors:
                    fp.write('Error: %s\n' % e)

                if errors:
                    fp.write('File: %s\n' % f.name)
                    fp.write('*' * 20 + '\n')

            except Exception as e:
                fp.write('Error: %s\n' % e)
                fp.write('File: %s\n' % f.name)
                fp.write('*' * 20 + '\n')


if __name__ == '__main__':
    schemas = get_schemas()
    generate_report(schemas)
