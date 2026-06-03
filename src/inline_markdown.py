import re
from textnode import TextNode, TextType


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
    #THis was my simpler one.. but seemingly not great for reasona I don't understand.. :)
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
   
    