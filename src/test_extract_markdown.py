import unittest
from inline_markdown import markdown_to_html_node, extract_markdown_images, extract_markdown_links, split_nodes_image, split_nodes_link, text_to_textnodes, markdown_to_blocks, BlockType, block_to_block_type
from textnode import TextNode, TextType
from main import extract_title
import inspect


class TestExtractMarkdown(unittest.TestCase):
    def test_extract_markdown_images(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)

    def test_extract_markdown_links(self):
        matches = extract_markdown_links(
            "This is text with a link [to boot dev](https://www.boot.dev)"
        )
        self.assertListEqual([("to boot dev", "https://www.boot.dev")], matches)



    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png) and some trailing text",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
                TextNode(" and some trailing text", TextType.TEXT),
            ],
            new_nodes,
        )


    def test_split_images_null_case(self):
        node = TextNode(
            "There is no image in this string",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("There is no image in this string", TextType.TEXT)
            ],
            new_nodes,
        )

    def test_split_image_only_string(self):
        node = TextNode(
            "![image](https://i.imgur.com/zjjcJKZ.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
            ],
            new_nodes,
        )


    def test_split_links(self):
        node = TextNode(
            "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev) and some trailing text",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is text with a link ", TextType.TEXT),
                TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"),
                TextNode(" and ", TextType.TEXT),
                TextNode("to youtube", TextType.LINK, "https://www.youtube.com/@bootdotdev"),
                TextNode(" and some trailing text", TextType.TEXT),
            ],
            new_nodes,
        )

    def test_split_links_dupes(self):
        node = TextNode(
            "This is text with a link [to boot dev](https://www.boot.dev) and [to boot dev](https://www.boot.dev) and some trailing text",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is text with a link ", TextType.TEXT),
                TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"),
                TextNode(" and ", TextType.TEXT),
                TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"),
                TextNode(" and some trailing text", TextType.TEXT),
            ],
            new_nodes,
        )

    def test_split_links_and_images(self):
        node = TextNode(
            "Now with both an ![image](https://i.imgur.com/zjjcJKZ.png) and a link [to boot dev](https://www.boot.dev)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        new_new_nodes = split_nodes_image(new_nodes)
        self.assertListEqual(
            [
                TextNode("Now with both an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and a link ", TextType.TEXT),
                TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"),
            ],
            new_new_nodes,
        )

    def test_all_together_now(self):
        input_string="This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        self.assertListEqual(
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("text", TextType.BOLD),
                TextNode(" with an ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" word and a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" and an ", TextType.TEXT),
                TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
                TextNode(" and a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev"),
            ],
            text_to_textnodes(input_string),
        )


    def test_markdown_to_blocks(self):
        #NB - you can't indent this text block, otherwise you get a load of tabs appearing in your string (which I don't want)
        #OH, and if you start it on a new line after the """, it'll make it lead with \n
        md = """This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

    def test_block_ident_paragraph_positive(self):
        md = """This is some generic
text without anything interesting of note
in it
Oh go on, I'll check in some stuff to confuse
1. sdsdsd
> sdsdsdsd
```
Hopefully that'll all be ignored 
"""
        self.assertEqual(block_to_block_type(md), BlockType.PARAGRAPH)


    def test_block_ident_heading_positive1(self):
        md = """# Title
Of my very exciting block
"""
        self.assertEqual(block_to_block_type(md), BlockType.HEADING)        

    def test_block_ident_heading_positive2(self):
        md = """### Title
#Of my very exciting block
acasdasdasdasdas
asdasdasdasd
sdsdsd
1.
"""
        self.assertEqual(block_to_block_type(md), BlockType.HEADING)        

    def test_block_ident_code_positive(self):
        md = """```
This is some
code```
"""
        self.assertEqual(block_to_block_type(md), BlockType.CODE)

    def test_block_ident_code_negative(self):
        md = """```
This is some
code``
"""
        self.assertEqual(block_to_block_type(md), BlockType.PARAGRAPH)        

    def test_block_ident_quote_positive(self):
        md = """> This is a good
> Quotation
>Block"""
        self.assertEqual(block_to_block_type(md), BlockType.QUOTE)        

    def test_block_ident_quote_negative(self):
        md = """> This is a good
Quotation
>Block"""
        self.assertEqual(block_to_block_type(md), BlockType.PARAGRAPH)  


    def test_block_ident_unordered_positive(self):
        md = """- This is an Item
- And this is another one
- Last one, I promise"""
        self.assertEqual(block_to_block_type(md), BlockType.UNORDERED_LIST)        

    def test_block_ident_unordered_negative(self):
        md = """- This is an Item
Oops, this isn't an item. 
- Last one, I promise"""
        self.assertEqual(block_to_block_type(md), BlockType.PARAGRAPH)          

    def test_block_ident_ordered_positive(self):
        md = """1. Good Item
2. Another Good One
3. I just can't stop myself"""
        self.assertEqual(block_to_block_type(md), BlockType.ORDERED_LIST)     

    def test_block_ident_ordered_positive2(self):
        md = """1. Good Item
2. Another Good One
3. I just can't stop myself
4. Good Item
5. Another Good One
6. I just can't stop myself
7. Good Item
8. Another Good One
9. I just can't stop myself
10. Good Item
11. Another Good One
12. I just can't stop myself
13. Good Item
14. Another Good One
15. I just can't stop myself"""
        self.assertEqual(block_to_block_type(md), BlockType.ORDERED_LIST)               

    def test_block_ident_ordered_negative(self):
        md = """1. Good Item
Nooooo - this isn't an item. Even if I put 2. here
3. I just can't stop myself"""
        self.assertEqual(block_to_block_type(md), BlockType.PARAGRAPH) 

    def test_block_ident_ordered_negative(self):
        md = """2. Another Good One - Except I've started at 2. DOH!
3. I just can't stop myself"""
        self.assertEqual(block_to_block_type(md), BlockType.PARAGRAPH) 



    def test_single_paragraph(self):
        md = "This is a simple paragraph with no fancy formatting"
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is a simple paragraph with no fancy formatting</p></div>",
        )

    def test_multiple_paragraphs_with_inline(self):
        md = """
This is the **first** paragraph
that spans two lines

This is the _second_ paragraph with a `code` span
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is the <b>first</b> paragraph that spans two lines</p>"
            "<p>This is the <i>second</i> paragraph with a <code>code</code> span</p></div>",
    )        
        


    def test_headings(self):
        md = """
# Heading one

### Heading three with **bold**

###### Heading six
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><h1>Heading one</h1>"
            "<h3>Heading three with <b>bold</b></h3>"
            "<h6>Heading six</h6></div>",
        )



    def test_quote(self):
        md = """
> This is a quote
> that spans lines
> with _italic_ text
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><blockquote>This is a quote that spans lines with <i>italic</i> text</blockquote></div>",
        )


    def test_codeblock(self):
        md = "```\ndef greet(name):\n    print(name)\n```"
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            '<div><pre><code>def greet(name):\n    print(name)\n</code></pre></div>',
        )

    def test_codeblock_no_inline(self):
        md = "```\nThis _stays_ literal and **so** does this\n```"
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            '<div><pre><code>This _stays_ literal and **so** does this\n</code></pre></div>',
        )

    def test_unordered_list(self):
        md = """
- First item
- Second with **bold**
- Third with _italic_
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><ul>"
            "<li>First item</li>"
            "<li>Second with <b>bold</b></li>"
            "<li>Third with <i>italic</i></li>"
            "</ul></div>",
        )


    def test_ordered_list(self):
        md = """
1. First item
2. Second with **bold**
3. Third with _italic_
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><ol>"
            "<li>First item</li>"
            "<li>Second with <b>bold</b></li>"
            "<li>Third with <i>italic</i></li>"
            "</ol></div>",
        )


    #OK - this is clearly how I should have done them all.. still maybe I'll pay myself on lines of code..
    def test_md_title_extraction(self):

        print (f"\nTesting: {inspect.currentframe().f_code.co_name}")

        cases = [
            ("# This is my simple title", "This is my simple title", True),
            ("\n \n ##This is a decoy\n# This is my title\nAnd some random text", "This is my title", True),
            ("\n \n ##This is a decoy\n## This is my title\nAnd some random text", "This is my title", Exception),
            (
"""##This is a decoy
# This is my title
# And some random text
# """
            , "This is my title", True),    
                ]


        for case in cases:
            if case[2] is True:
                self.assertEqual (extract_title(case[0]), case[1])
            elif case[2] is False:
                self.assertNotEqual (extract_title(case[0]), case[1])
            elif case[2] is Exception:
                with self.assertRaises(Exception):
                    extract_title(case[0])



if __name__ == "__main__":
    unittest.main()


