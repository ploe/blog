#! /usr/bin/env python3
"""Articles unittest"""

import datetime
import glob
import os
import unittest
import urllib.parse

import articles


class TestArticles(unittest.TestCase):
    """Articles TestCase"""
    def setUp(self):
        self.directory = os.path.join('examples', 'unittest', 'articles')
        self.source = os.path.join(self.directory, "*.yaml")
        self.articles = articles.Articles(self.directory)

    def test_get_collection(self):
        """get_collection unittest"""
        self.articles = articles.Articles(self.directory)
        collection = self.articles.get_collection()

        examples = []
        for path in glob.glob(self.source):
            basename = os.path.splitext(os.path.basename(path))[0]
            slug = urllib.parse.quote(
                "/articles/{basename}".format(basename=basename))
            examples.append(slug)

        for article in collection:
            self.assertIn(article['slug'], examples)
            self.assertTrue(
                datetime.datetime.strptime(article['mtime'], "%Y%m%d%H%M%S"))

    def test_get_missing_item(self):
        """get_item unittest, expect InvalidItem failure"""
        invalid_item = False
        try:
            self.articles.get_item('zero')
        except articles.InvalidItem:
            invalid_item = True
        self.assertTrue(invalid_item)

    def test_get_valid_item(self):
        """get_item unittest"""
        item = self.articles.get_item('first')

        self.assertIsInstance(item['body'], list)
        self.assertIsInstance(item['enabled'], bool)
        self.assertTrue(
            datetime.datetime.strptime(item['mtime'], "%Y%m%d%H%M%S"))

        for key in ('slug', 'title'):
            self.assertIsInstance(item[key], str)

        for paragraph in item['body']:
            self.assertIsInstance(paragraph, str)

    def test_validate_item_body_from_str(self):
        """validate_item_body unittest, get list from str"""
        value = self.articles.validate_item_body('str')
        self.assertIsInstance(value, list)

    def test_invalid_item_enabled(self):
        """validate_item_enabled, expect InvalidItem failure"""
        invalid_item = False
        try:
            self.articles.validate_item_enabled('not bool')
        except articles.InvalidItem:
            invalid_item = True
        self.assertTrue(invalid_item)
