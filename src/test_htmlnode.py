import unittest
from htmlnode import HTMLNode, LeafNode

##METHODS HAVE TO START "test_" to be run by unittest. Class must take "unittest.TestCase" AND this file must have a test prefix

class TestHTMLNode(unittest.TestCase):
    def test_props_to_html(self):
        node = HTMLNode(props={"href": "https://www.google.com","target": "_blank"})
        expected_response =  ' href="https://www.google.com" target="_blank"'
        self.assertEqual(node.props_to_html(), expected_response)
        
    #I'm lazy, should work out how to check this..I shouldn't have made the repr multi-line verbose...
    def test_repr(self):
        node = HTMLNode(props={"href": "https://www.google.com","target": "_blank"})
        print(node)

    
    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")        

    def test_leaf1(self):
        leaf=LeafNode("p", "This is a paragraph of text.").to_html()
        expected_response = "<p>This is a paragraph of text.</p>"
        self.assertEqual(leaf,expected_response)

    def test_leaf2(self):
        leaf=LeafNode("a", "Click me!", {"href": "https://www.google.com"}).to_html()
        expected_response = '<a href="https://www.google.com">Click me!</a>'
        self.assertEqual(leaf,expected_response)



if __name__ == "__main__":
    unittest.main()