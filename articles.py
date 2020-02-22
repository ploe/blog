#! /usr/bin/env python3
"""Articles module"""

import argparse
import datetime
import glob
import os
import pprint
import sys
import urllib.parse

import yaml


class InvalidItem(Exception):
    """Raised when a value in an article attribute is incorrect"""

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

        with open(path) as filehandle:
            item = yaml.load(filehandle, Loader=yaml.FullLoader)

        item['slug'] = slug
        item['mtime'] = self.to_mtime(path)

        return self.validate_item(item)

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

def _main():
    parser = argparse.ArgumentParser()
    parser.add_argument("method", help="The method you wish to call")
    parser.add_argument("directory",
                        help="Directory containing YAML article files")
    args = parser.parse_args()

    articles = Articles(args.directory)

    method = args.method
    func = getattr(articles, method, None)
    if (not func) or (not callable(func)):
        prompt = "Invalid method {method}".format(method=method)
        sys.exit(prompt)

    pprint.pprint(func())


if __name__ == '__main__':
    _main()
