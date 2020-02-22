#! /usr/bin/env python3
"""Articles unittest"""

import datetime
import glob
import os
import unittest
import urllib.parse

from articles import Articles


class TestArticles(unittest.TestCase):
    """Articles TestCase"""
    def setUp(self):
        self.directory = os.path.join('examples', 'unittest', 'articles')
        self.source = os.path.join(self.directory, "*.yaml")

    def test_get_collection(self):
        """get_collection unittest"""
        articles = Articles(self.directory)
        collection = articles.get_collection()

        examples = []
        for path in glob.glob(self.source):
            basename = os.path.splitext(os.path.basename(path))[0]
            slug = urllib.parse.quote(
                "/articles/{basename}".format(basename=basename))
            examples.append(slug)

        for article in collection:
            self.assertTrue(article['slug'] in examples)
            self.assertTrue(
                datetime.datetime.strptime(article['mtime'], "%Y%m%d%H%M%S"))

    def test_get_valid_item(self):
        """get_item unittest"""
        articles = Articles(self.directory)

        item = articles.get_item('first')

        self.assertTrue(isinstance(item['body'], list))
        self.assertTrue(isinstance(item['enabled'], bool))
        self.assertTrue(
            datetime.datetime.strptime(item['mtime'], "%Y%m%d%H%M%S"))

        for key in ('slug', 'title'):
            self.assertTrue(isinstance(item[key], str))

        for paragraph in item['body']:
            self.assertTrue(isinstance(paragraph, str))
