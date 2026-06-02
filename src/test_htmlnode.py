import unittest
from htmlnode import HTMLNode

##METHODS HAVE TO START "test_" to be run by unittest. Class must take "unittest.TestCase" AND this file must have a test prefix

class TestHTMLNode(unittest.TestCase):
    def test_props_to_html(self):
        node = HTMLNode(props={"href": "https://www.google.com","target": "_blank"})
        expected_response =  ' href="https://www.google.com" target="_blank"'
        self.assertEqual(node.props_to_html(), expected_response)
        
    #I'm lazy, should work out how to check this..
    def test_repr(self):
        node = HTMLNode(props={"href": "https://www.google.com","target": "_blank"})
        print(node)

    def test_child(self):
        node = HTMLNode(t)

if __name__ == "__main__":
    unittest.main()