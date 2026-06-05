from textnode import TextNode
#can only import methods/objects without dot notation, but you can use dot on the from clause
from os import listdir, mkdir, getcwd
from os.path import exists, join, isfile, isdir
from shutil import copy, rmtree
from inline_markdown import markdown_to_html_node
import io

def main():
    #Clear out the public folder and repopulate it from static folder
    copy_static()
    #Now generate the page
    generate_page("content/index.md", "template.html", "public/index.html")

def copy_static():
    #Define the paths we want our app to operate on
    src_path = "static"
    dest_path = "public"
    
    print("Starting Site Distribution")


    #Be a good boy, and check these are valid
    if (isdir (join(getcwd(), src_path)), isdir(join(getcwd(), dest_path))) == (True, True):
        absolute_src_path, absolute_dest_path = join(getcwd(), src_path), join(getcwd(), dest_path)
        print ("File Paths look good")
    else:
        print ("File Paths DON'T look good")
        raise Exception("Check your source and target directories exist - I couldn't find them")

    #First we want to delete the destination directory, before we rebuild it.
    rmtree(absolute_dest_path)
    mkdir(absolute_dest_path)
    print ("Cleaned Dest Directory")

    #Now we want to copy everything from the src into the dest
    copy_tree(absolute_src_path,absolute_dest_path)



#Function I can recursively call to copy from one dir to another
def copy_tree(src:str,dest:str):
    
    #Loop everything in the src
    for item in listdir(src):
        fq_item = join(src,item)
        is_file = isfile(fq_item)
        print(f"Item: {fq_item} isFile: {is_file}")

        #If the item is a file, just copy it
        if is_file: #It just evaluates to True, so this is all you need, and you keep on adding "is True"
            copy(fq_item,dest)
            print(f"Copied {fq_item} to {dest}")
        #If the item is a directory, then recursively call this function for it
        else:
            new_src = join(src,item)
            new_dest = join(dest,item)
            
            #Need to first create this dir in the target:
            
            mkdir(new_dest)
            print (f"Created new dir: {new_dest}")

            print(f"Iterating copy from: {new_src} to: {new_dest}")
            copy_tree (new_src, new_dest)

#function to return the title (if it exists) from a piece of markdown chucked in (I.E. Text found after the first line starting "# ")
def extract_title(markdown:str):
    #Split text on new lines
    markdown_lines = markdown.split("\n")
    for markdown_line in markdown_lines:
        if markdown_line[0:2] == "# ":
            return markdown_line[2:]

    raise Exception("Wasn't able to find a title")

def get_file(path:str)->str:
    #Pull in a file and return the content
    file = io.open(path)
    file_content = file.read()
    file.close()
    return file_content


def generate_page(from_path, template_path, dest_path):

    #Say what we're doing
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")

    #Load in the from and template paths
    content, template =  get_file(from_path), get_file(template_path)

    #Convert the markdown content to html node
    html_node = markdown_to_html_node(content)

    #Now convert this to html
    html = html_node.to_html()

    print (html)
    
    


main()