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




def extract_markdown_images(text):
    #This was the solution provided as a tip 
    return re.findall(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)",text)
    #THis was my simpler one.. but seemingly not great for reasona I don't understand.. :)
    #return re.findall(r"\[(.*?)\]\((.*?)\)",text)

def extract_markdown_links(text):
    return re.findall(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)",text)