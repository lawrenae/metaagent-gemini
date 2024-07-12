#!/usr/bin/env python
# coding: utf-8
"""
@Time    : 2024/7/11 10:49
@Author  : lawrenae
@File    : test_amazon_scrapper
"""
import unittest

from amazon_reviews_scrapper import get_page_html, get_reviews_for, get_reviews_from_html, orchestrate_data_gathering

class TestAmazonScrapper(unittest.TestCase):
    url = "https://www.amazon.com/Dawn-Ultra-Dishwashing-Liquid-Original/product-reviews/B0BBPNPZTC/"

    with open("tests/frontend/Amazon.com_Customer_reviews.html", encoding="utf-8") as f:
        html = f.read()
    
    def test_get_reviews_from_html(self):
        self.assertIsNotNone(self.html)
    
        reviews = get_reviews_from_html(self.html)
        self.assertTrue(reviews)
        self.assertEqual(len(reviews), 10)
    
    def test_actually_retrieve_review_details_from_review(self):
        self.assertIsNotNone(self.html)
    
        reviews = get_reviews_from_html(self.html)
        data = orchestrate_data_gathering(reviews[0])
        self.assertIsNotNone(data)
        self.assertIsNotNone(data['review_text'])
        self.assertIsNotNone(data['review_date'])
        self.assertIsNotNone(data['review_title'])
        self.assertIsNotNone(data['review_stars'])
    
    def test_use_live_html_page(self):
        results = get_reviews_for(self.url)
        self.assertIsNotNone(results)
        self.assertEqual(len(results), 10)
        print (len(results))



if __name__ == '__main__':
    unittest.main()