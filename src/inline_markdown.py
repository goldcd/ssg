import re
from textnode import TextNode, TextType, text_node_to_html_node
from enum import Enum
from htmlnode import HTMLNode, ParentNode, LeafNode

#Enumeration to classify pieces of text as .md markup types
class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"


def split_nodes_delimiter(old_nodes: list[TextNode], delimiter: str, text_type: TextType) -> list[TextNode]:
    output=[]
    for old_node in old_nodes:
        #If we get a textnode on the input list, that isn't marked as text, just stick it on the output list 'as is'
        if old_node.text_type != TextType.TEXT:
            output.append(old_node)
        #If it does have a TextType of Text, then we need to see if we should split it down into multiple text types
        #I believe we've been told that there's only going to be one type of non-text block we need to extract from this (no nested tags)
        #OH FFS - this whole function just handles one type of markup at a time.. so that's way simpler.. no wonder I was confused..
        else:
            #So first of all split this node up into a list of strings.
            split_node = old_node.text.split(delimiter)
            #Now let's perform some checks.
            #If we only end up with one item on the list, there was nothing to split, so just put it on the output
            if len(split_node)==1:
                output.append(old_node)
            #If we have an even number of pieces, we know we had an odd number of delimiters - so throw an error
            elif len(split_node)%2==0:
                raise Exception(f"Unbalanced number of delimiters found in {old_node.text}")
            else:
                #Now we can loop through the chunks, altering our behaviour based on whether or not their odd or even
                for i in range(len(split_node)):
                    #Odd - these are our sections we want to tag. And the rest we just add as text
                    if i%2!=0:
                        new_fragment=TextNode(text=split_node[i], text_type=text_type)
                    else:
                        new_fragment=TextNode(text=split_node[i], text_type=TextType.TEXT)
                    if len(new_fragment.text)>0:                    
                        output.append(new_fragment) 
    return output



##Functions to strip URLS and text out of links and images in MD
def extract_markdown_images(text):
    #This was the solution provided as a tip 
    return re.findall(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)",text)
    #THis was my simpler one.. but seemingly not great for reasons I don't understand.. :)
    #return re.findall(r"\[(.*?)\]\((.*?)\)",text)

def extract_markdown_links(text):
    return re.findall(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)",text)

def split_nodes_image(old_nodes: list[TextNode]) -> list[TextNode]:
    output = []
    #Loop through the list of nodes passed in
    for old_node in old_nodes:
        #If it's already been marked as non-text, we don't want to reprocess it
        if old_node.text_type != TextType.TEXT:
            output.append(old_node)
        else:
            check_images = extract_markdown_images(old_node.text)
            #If we didn't find any images, just put this back onto the output list, and check the next old node
            if len(check_images)==0:
                output.append(old_node)
            #We now need to break up the old_node into images and text nodes
            else:
                #Copy all the text from the node into a string, which we're going to now break down
                remaining_text=old_node.text
                #Now iterate through the node text, for each image we have (it's at least 1)
                for image in check_images:
                    alt=image[0]
                    url=image[1]

                    #Split the string on the current image
                    before, after = remaining_text.split(f"![{alt}]({url})", 1)

                    #if there was text before the image, made a node for it:
                    if len(before)>0:
                        output.append(TextNode(text=before, text_type=TextType.TEXT))
                    
                    #Then add the image node:
                    output.append(TextNode(text=alt, url=url, text_type=TextType.IMAGE))

                    #Finally, update the remaining text with whatever was after the current image, and iterate again
                    remaining_text = after
                
                #If we had any text after the last image in the node, add this.
                if len(remaining_text) > 0:
                    output.append(TextNode(text=remaining_text, text_type=TextType.TEXT))
    return output


def split_nodes_link(old_nodes: list[TextNode]) -> list[TextNode]:
    output = []
    #Loop through the list of nodes passed in
    for old_node in old_nodes:
        #If it's already been marked as non-text, we don't want to reprocess it
        if old_node.text_type != TextType.TEXT:
            output.append(old_node)
        else:
            check_links = extract_markdown_links(old_node.text)
            #If we didn't find any links, just put this back onto the output list, and check the next old node
            if len(check_links)==0:
                output.append(old_node)
            #We now need to break up the old_node into links and text
            else:
                #Copy all the text from the node into a string, which we're going to now break down
                remaining_text=old_node.text
                #Now iterate through the node text, for each image we have (it's at least 1)
                for link in check_links:
                    txt=link[0]
                    url=link[1]

                    #Split the string on the current link
                    before, after = remaining_text.split(f"[{txt}]({url})", 1)

                    #if there was text before the link, made a node for it:
                    if len(before)>0:
                        output.append(TextNode(text=before, text_type=TextType.TEXT))
                    
                    #Then add the link node:
                    output.append(TextNode(text=txt, url=url, text_type=TextType.LINK))

                    #Finally, update the remaining text with whatever was after the current link, and iterate again
                    remaining_text = after
                
                #If we had any text after the last link in the node, add this.
                if len(remaining_text) > 0:
                    output.append(TextNode(text=remaining_text, text_type=TextType.TEXT))
    return output

def text_to_textnodes(text)-> list[TextNode]:
    #Chuck all the text into one giant node on a new list
    input_node = [TextNode(text=text, text_type=TextType.TEXT)]
     #Now blast it through my slicers - I really don't want to have to debug this if it fucks up (but I'll be very happy if this works first time)
    
    #Now work through the non-leaf items
    input_node=split_nodes_delimiter(input_node, "**",TextType.BOLD)
    input_node=split_nodes_delimiter(input_node, "_",TextType.ITALIC)
    input_node=split_nodes_delimiter(input_node, "`",TextType.CODE)

    #Finally do the link and image tagging, and return it 
    return split_nodes_image(split_nodes_link(input_node))
   
def markdown_to_blocks(markdown:str) ->list[str]:
    
    #Split the input text into a list of strings, based on a "double new line" (is this assuming no spaces?)
    split_blocks = markdown.split("\n\n")

    #list for cleaned output
    cleaned_blocks = []

    #Iterate through these blocks to clean them up
    for block in split_blocks:
        #Remove leading and trailing spaces on the block
        output_block = block.strip()
        
        #If the block isn't empty, add it to the output
        if len(output_block) > 0:
            cleaned_blocks.append(output_block)

    return cleaned_blocks

def block_to_block_type(markdown:str) -> BlockType:

    #Headings start with 1-6 # characters, followed by a space and then the heading text.
    
    #Is this a heading block, with 1-6 hashes and a space at the start?
    if len(re.findall(r"^(#{1,6} +.)",markdown)) > 0:
        return BlockType.HEADING
    #startswith(("# ", "## ", "### ", "#### ", "##### ", "###### ")) Would have been a FAR better bit of logic..
    #Or if I'd insisted on using regex, I should have been easier to use "if re.match(r"^#{1,6} .+", markdown):"
    
    #Multiline Code blocks must start with 3 backticks and a newline, then end with 3 backticks.
    
    #If string starts ```<new line> and ends ```. The ^ and $ pin the match to the start and end of the string.
    #[\s\S]* Just means "any number of any characters" - * by itself, would actually indicate an unlimited number of the preceeding \n - that tripped me right up. I fucking hate regex. Every time I pick it up, I hate it again.
    if len(re.findall(r"^(`{3}\n[\s\S]*`{3})$",markdown)) > 0:
        return BlockType.CODE
    
    #Every line in a quote block must start with a "greater-than" character: > followed by the quote text. 
    #A space after > is allowed but not required.

    #Every line in an unordered list block must start with a - character, followed by a space.

    #No idea if I was supposed to be using regex before now, as this doesn't seem a good match.
    #Now I'm here, clearly in the previous one I should have just used .startswith and .endswith.. FFS.. Still, good practice.

    #split input on new lines
    split_markdown = markdown.split("\n")
    quote_line_count=0
    unordered_list_count=0
    #Loop the lines and see what they start with
    for line in split_markdown:
        if line.startswith(">"):
            quote_line_count+=1
        elif line.startswith("- "):
            unordered_list_count+=1
    #If as many lines starting > were found, as there were lines
    if quote_line_count == len(split_markdown):
        return BlockType.QUOTE
    elif unordered_list_count == len(split_markdown):
        return BlockType.UNORDERED_LIST
    
    #Every line in an ordered list block must start with a number followed by a . character and a space. 
    # The number must start at 1 and increment by 1 for each line.
    
    #OK, different logic, so I'll treat myself to a new loop..
    #Loop the lines and see what they start with
    current_number = None
    ordered_list_count = 0
    for line in split_markdown:
        #Does the line start with digits then ". "? And remember you need \. just . means ANY character (seemingly)
        leading_order_str = re.findall(r"^(\d{1,}\. )",line)
        #For "unlimited digits" you could also use \d+

        #Do we find something that looks like it's a ordered list item
        if len(leading_order_str) > 0:
            #Now find what the actual number was - removing the ". ", SHOULD just give us an integer..
            leading_order = int(leading_order_str[0].strip(". "))
            
            #Can't assume the numbering starts at 1, so if we haven't seen a number before, set it now and we'll start counting from here
            #Actually, the f'in question said I had to validate that we start at one, so I'm going to be making this code messy..
            if current_number is None:
                #Hastily sticking in an if, to check it's 1 (but without this, I think any number would have worked)
                if leading_order == 1:
                    current_number = leading_order
                    #Mark we've found a valid (first) line
                    ordered_list_count +=1
            #Else a number was already set
            else:
                #So we know we have a number from this block. If it's one more than we had before, it's another valid line
                if current_number +1 == leading_order:
                    ordered_list_count +=1
                    current_number = leading_order 

    #If every line was a nice in-sequence number, I think we know it's an ordered list
    if ordered_list_count == len(split_markdown):
        return BlockType.ORDERED_LIST
    
    #At this point, we should have picked up anything interesting, so can just say it's a normal paragraph
    return BlockType.PARAGRAPH

                    
def markdown_to_html_node(markdown:str) -> HTMLNode:
    #List of the top level HTML nodes I want to put under the root HTML node I'll return
    root_node_children = []
    #Split the giant piece of markdown passed in, into blocks of markdown simply on paragraph divisions
    md_blocks = markdown_to_blocks(markdown)

        

    #Loop through these .md blocks
    for md_block in md_blocks:

        #For each one, get the classification of it
        block_type = block_to_block_type(md_block)
   
        #If the block's a paragraph, get the children and then put them into a parent_node that aligns with this current block
        if block_type == BlockType.PARAGRAPH:
            #We were just asked to replace new lines with a space - I don't like it, but it's what it wanted me to do..
            children = text_to_children(md_block.replace("\n"," "))
            node = ParentNode("p", children)
            root_node_children.append(node)
        elif block_type == BlockType.HEADING:
            #we need to determine the size of the heading
            header_level = 0
            for i in range(len(md_block)):
                if md_block[i] == "#":
                    header_level+=1
                else:
                    break
            tag="h"+str(header_level)
            #Now trim off this header
            #Add 1, as we should have a space after the header ###'s
            md_block=md_block[header_level+1:]
            children = text_to_children(md_block)
            node = ParentNode(tag, children)
            root_node_children.append(node)
        elif block_type == BlockType.QUOTE:
            #Need to strip off the "> " from the start of each line
            #First need to split the blocks into lines, we as need to clean off the "> " prefix from each one
            lines = md_block.split("\n")
            cleaned_lines = []
            for line in lines:
                #Clean off any leading > and then strip to remove space
                cleaned_lines.append(line.lstrip(">").strip())
            content = " ".join(cleaned_lines)
            children = text_to_children(content)
            node = ParentNode("blockquote", children)
            root_node_children.append(node)
        elif block_type == BlockType.CODE:
            #Pull the actual code out of the '''\n and ''' code limits
            code = md_block[4:-3]
            #Create the node containing the code:
            code_node = text_node_to_html_node(TextNode(code, TextType.TEXT))
            #Then nest it in <pre><code> tags
            node = ParentNode("code", [code_node])
            pre_node = ParentNode("pre", [node])
            root_node_children.append(pre_node)
        elif block_type == BlockType.UNORDERED_LIST:
            items = md_block.split("\n")   # each line is one item
            li_nodes = []
            for item in items:
                text = item[2:]            # strip the "- " marker
                children = text_to_children(text)
                li_nodes.append(ParentNode("li", children))
            node = ParentNode("ul", li_nodes)
            root_node_children.append(node)
        elif block_type == BlockType.ORDERED_LIST:
            items = md_block.split("\n")
            li_nodes = []
            for item in items:
                text = item.split(". ", 1)[1]
                children = text_to_children(text)
                li_nodes.append(ParentNode("li", children))
            node = ParentNode("ol", li_nodes)
            root_node_children.append(node)
                
    return ParentNode(tag="div", children=root_node_children)



def text_to_children(text: str) -> list[HTMLNode]:

    text_nodes = text_to_textnodes(text)
    children = []
    for text_node in text_nodes:
        # convert each one and append it
        html_node = text_node_to_html_node(text_node)
        children.append(html_node)
    return children

