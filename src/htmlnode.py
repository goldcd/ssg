class HTMLNode:
    """
    The HTMLNode class should have 4 data members set in the constructor:
    tag - A string representing the HTML tag name (e.g. "p", "a", "h1", etc.)
    value - A string representing the value of the HTML tag (e.g. the text inside a paragraph)
    children - A list of HTMLNode objects representing the children of this node
    props - A dictionary of key-value pairs representing the attributes of the HTML tag. For example, a link (<a> tag) might have {"href": "https://www.google.com"}
    Perhaps counterintuitively, every data member should be optional and default to None:
    An HTMLNode without a tag will just render as raw text
    An HTMLNode without a value will be assumed to have children
    An HTMLNode without children will be assumed to have a value
    An HTMLNode without props simply won't have any attributes
    """
    def __init__(self, tag=None, value=None, children=None, props:dict|None=None):
        self.tag=tag
        self.value=value
        self.children=children
        self.props=props

    #I went too verbose here. Suggested solution was just:
    #return f"HTMLNode({self.tag}, {self.value}, children: {self.children}, {self.props})"
    def __repr__(self):
        output=""
        output+=f"\nTag: {self.tag}\n"
        output+=f"Value: {self.value}\n"
        if self.children is not None:
            for i in self.children:
                output+=f'Child: {i}\n'
        output+=self.props_to_html()
        return output
            


    def to_html(self):
        raise NotImplementedError
    
    def props_to_html(self):
        if self.props is None or self.props=="":
            return ""
        
        built_html=""
        for i in self.props:
            built_html+=f' {i}="{self.props[i]}"'
        return built_html
    
