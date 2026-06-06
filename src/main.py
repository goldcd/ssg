from textnode import TextNode
#can only import methods/objects without dot notation, but you can use dot on the from clause
from os import listdir, mkdir, getcwd
from os.path import exists, join, isfile, isdir
from shutil import copy, rmtree
from inline_markdown import markdown_to_html_node
import io
import sys

def main():

    #Let the the basepath be passed in as a parameter on launch
    #[0] is what pything is actually executing, so [1] is whatever comes next (if exists)
    if len(sys.argv) > 1:
        passed_basepath = sys.argv[1]
    else:
        passed_basepath = "/"

    #Clear out the public folder and repopulate it from static folder
    copy_static()
    #Now generate the page
    generate_pages_recursive("content/", "template.html", "docs/", passed_basepath)

def copy_static():
    #Define the paths we want our app to operate on
    src_path = "static"
    dest_path = "docs"
    
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

#Just slurp the contents of a file and return it
def get_file(path:str)->str:
    #Pull in a file and return the content
    file = io.open(path)
    file_content = file.read()
    file.close()
    return file_content

#Write a file
def put_file(path:str, content:str):
    #need to open it with a write flag if you.. well want to write to it..
    file = io.open(path,'w')
    file.write(content)
    file.close()

def generate_page(from_path, template_path, dest_path, passed_basepath):

    #Say what we're doing
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")

    #Load in the from and template paths
    content, template =  get_file(from_path), get_file(template_path)

    #Convert the markdown content to html node
    html_node = markdown_to_html_node(content)

    #Now convert this to html
    html = html_node.to_html()

    #Grab the title from the md
    title = extract_title(content)

    #Merge the title and content into the HTML template
    template = template.replace("{{ Title }}",title)
    template = template.replace("{{ Content }}",html)

    #Now we're letting the user specify a basepath for the site, we need to alter the prefix on image and anchor URLS to include this
    template = template.replace('href="/',f'href="{passed_basepath}')
    template = template.replace('src="/',f'src="{passed_basepath}') 
    
    #Now write out the updated template to the destination
    put_file(dest_path,template)

#Crawl for all the content files we might want to parse
def generate_pages_recursive(dir_path_content, template_path, dest_dir_path, passed_basepath):
    
    for item in listdir(dir_path_content):

        #Get fully qualified paths/files for everything you find, and work out if it's a file (or a directory)
        fq_item = join(dir_path_content,item)
        fq_target = join(dest_dir_path,item)
        is_file, is_dir = isfile(fq_item), isdir(fq_item)

        #We just want to get the .md files
        if is_file and fq_item[-3:]==".md": 
            #Now generate the HTML in the output

            #Need to switch the suffix from .md to .html
            fq_target = fq_target[:-3]+".html"

            print (f"FOUND AN MD! {fq_item}")
            print (f"generate_page({fq_item}, {template_path}, {fq_target})")
            generate_page(fq_item, template_path, fq_target, passed_basepath)
        
        #If the item is a directory, then recursively call this function for it
        if is_dir:
            #Add the directory to the path, and iterate
            updated_dir_path_content = join(dir_path_content,item)
            updated_dest_dir_path = join(dest_dir_path,item)

            print (f"Switching to {updated_dir_path_content} / {updated_dest_dir_path}")

            #First make the directory in the target
            mkdir(updated_dest_dir_path)

            #Then process it
            generate_pages_recursive (updated_dir_path_content, template_path, updated_dest_dir_path, passed_basepath)

main()