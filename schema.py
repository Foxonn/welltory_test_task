import json
import typing
import os

PATH_PROJECT_DIR = os.path.abspath(os.path.curdir)
PATH_SCHEMAS_FOLDER = os.path.join(PATH_PROJECT_DIR, 'task_folder/schema')


def get_files_schema() -> typing.List[os.DirEntry]:
    sf = PATH_SCHEMAS_FOLDER

    if not os.path.isdir(sf):
        raise Exception(f"Directory '{sf}' not found!")

    schemas = [f for f in os.scandir(sf) if f.name.endswith('schema')]

    if not schemas:
        raise Exception(f"Directory '{sf}' don`t have schema files")

    return schemas


def read_schema(raw_schema: os.DirEntry) -> dict:
    with open(raw_schema.path, mode='r') as fp:
        schema = json.load(fp)

    return {'event': raw_schema.name.split('.')[0], 'schema': schema, }


def get_schemas():
    _ = dict()

    for s in get_files_schema():
        schema = read_schema(s)

        _.setdefault(schema['event'], schema)

    return _


if __name__ == '__main__':
    for schema in get_schemas().items():
        print(schema)
