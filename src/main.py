from textnode import TextNode
#can only import methods/objects without dot notation, but you can use dot on the from clause
from os import listdir, mkdir, getcwd
from os.path import exists, join, isfile, isdir
from shutil import copy, rmtree

def main():
    #my_test_node = TextNode("This is some anchor text", "link", "https://www.boot.dev")
    #print (my_test_node)
    copy_static()

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


main()