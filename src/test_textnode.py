import unittest
from textnode import TextNode, TextType, text_node_to_html_node

class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)

    def test_eq_with_url(self):
        node = TextNode("This is a text node", TextType.BOLD,"http://bobpitch.com")
        node2 = TextNode("This is a text node", TextType.BOLD, "http://bobpitch.com")
        self.assertEqual(node, node2)

    def test_not_eq_with_url(self):
        node = TextNode("This is a text node", TextType.BOLD,"http://bobpitch.com")
        node2 = TextNode("Flibble", TextType.BOLD, "http://bobpitch.com")
        self.assertNotEqual(node, node2)

    def test_url_default(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD, None)
        self.assertEqual(node, node2)

    def test_url_default2(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD, "http://bobpitch.com")
        self.assertNotEqual(node, node2)

    #This is a VERY rough way to return a test result, I should really look at the other assertions I can make.
    #But I just added this as I wanted to try something that wasn't the assertion classes above which were given in the examples
    def test_enumerated_testtype(self):
        try:
            node = TextNode("This is a text node", TextType.REALLYBIG)
        except:
            return self.assertTrue(True)
        return self.assertFalse(False)
    
    def test_text(self):
        node = TextNode("This is a text node", TextType.TEXT)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")
    

if __name__ == "__main__":
    unittest.main()