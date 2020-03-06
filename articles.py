#! /usr/bin/env python3
"""Articles module"""

import argparse
import datetime
import glob
import inspect
import os
import pprint
import urllib.parse

import yaml


class InvalidItem(Exception):
    """Raised when a value in an article attribute is incorrect"""


class InvalidMethod(Exception):
    """Raised when an invalid method is requested from the cli"""


class Articles:
    """"Articles class"""
    def __init__(self, directory):
        self.directory = directory
        self.source = os.path.join(directory, '*.yaml')

    def get_collection(self):
        """Returns a list of uri's to articles in the directory"""
        collection = []
        for path in glob.glob(self.source):
            basename = self.to_basename_from_path(path)
            article = {
                'slug': self.to_slug_from_basename(basename),
                'mtime': self.to_mtime(path)
            }

            collection.append(article)

        collection = sorted(collection, key=lambda i: i['mtime'], reverse=True)
        return collection

    def get_item(self, slug):
        """Returns a validated article item"""
        basename = self.to_basename_from_slug(slug)
        path = self.to_path_from_basename(basename)

        try:
            with open(path) as filehandle:
                item = yaml.load(filehandle, Loader=yaml.FullLoader)
        except FileNotFoundError:
            raise InvalidItem

        item['slug'] = slug
        item['mtime'] = self.to_mtime(path)

        return self.validate_item(item)

    def _get_method(self, name):
        if name.startswith('_'):
            raise InvalidMethod

        method = getattr(self, name, None)
        if (not method) or (not callable(method)):
            raise InvalidMethod

        return method

    @classmethod
    def main(cls, args=None):
        """When we call the module as from the cli this is the method we use
        to parse the arguments and instantiate the class"""

        positionals = [{
            'help': 'The method you wish to call',
            'name': 'method',
        }, {
            'help': 'Directory containing YAML article files',
            'name': 'directory'
        }]

        flags = {
            '--basename': {
                'help': "Common name for an article",
                'type': str
            },
            '--enabled': {
                'action': 'store_true',
                'help': "Attribute 'enabled' on article",
            },
            '--path': {
                'help': "Path to an article",
                'type': str
            },
            '--slug': {
                'help': "URI slug to pass to method",
                'type': str
            }
        }

        if not args:
            args = _parse_args(positionals, flags)

        articles = cls(args['directory'])

        # disabled W0212 as _get_method should not be callable from cli
        method = articles._get_method(args['method'])  # pylint: disable=W0212
        kwargs = _parse_kwargs(method, args)

        pprint.pprint(method(**kwargs))

        return cls

    @staticmethod
    def to_basename_from_path(path):
        """Render a basename from a path"""
        return os.path.splitext(os.path.basename(path))[0]

    @staticmethod
    def to_basename_from_slug(slug):
        """Render a basename from a slug"""
        return os.path.basename(urllib.parse.unquote(slug))

    @staticmethod
    def to_mtime(path):
        """Render the mtime for a path in %Y%m%d%H%M%S format"""
        return datetime.datetime.fromtimestamp(
            os.path.getmtime(path)).strftime("%Y%m%d%H%M%S")

    def to_path_from_basename(self, basename):
        """Render article path from basename"""
        return "{directory}/{basename}.yaml".format(directory=self.directory,
                                                    basename=basename)

    @staticmethod
    def to_slug_from_basename(basename):
        """Render uri slug from basename"""
        return urllib.parse.quote(
            "/articles/{basename}".format(basename=basename))

    @staticmethod
    def validate_item_body(body):
        """Returns body paragraphs as a list of strings"""
        if not isinstance(body, list):
            body = [body]

        tmp = []
        for paragraph in body:
            tmp.append(str(paragraph))

        return tmp

    @staticmethod
    def validate_item_enabled(enabled):
        """Ensures enabled is set to a bool otherwise raises an InvalidItem
        Exception"""
        if not isinstance(enabled, bool):
            raise InvalidItem

        return enabled

    def validate_item(self, item):
        """Validates each of the members in the article are set appropriately,
        if they aren't an InvalidItem error may be raised"""
        return {
            'body': self.validate_item_body(item['body']),
            'enabled': self.validate_item_enabled(item.get('enabled', True)),
            'mtime': item['mtime'],
            'slug': item['slug'],
            'title': str(item['title'])
        }


def _parse_args(positionals, flags):
    parser = argparse.ArgumentParser()
    for params in positionals:
        name = params.pop('name')
        parser.add_argument(name, **params)

    for flag, params in flags.items():
        parser.add_argument(flag, **params)

    return vars(parser.parse_args())


def _parse_kwargs(func, args):
    sig = inspect.signature(func)
    kwargs = {}
    for key, parameter in sig.parameters.items():
        if parameter.kind in (inspect.Parameter.POSITIONAL_OR_KEYWORD,
                              inspect.Parameter.KEYWORD_ONLY):
            value = args.get(key, None)
            if value is not None:
                kwargs[key] = value

    return kwargs


if __name__ == '__main__':
    Articles.main()
