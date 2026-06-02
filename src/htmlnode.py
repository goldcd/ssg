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

    #I've commented out my overly verbose version. repr should just be a simple one-liner
    """
    def __repr__(self):
        output=""
        output+=f"\nTag: {self.tag}\n"
        output+=f"Value: {self.value}\n"
        if self.children is not None:
            for i in self.children:
                output+=f'Child: {i}\n'
        output+=self.props_to_html()
        return output
    """
    def __repr__(self):
        return f"HTMLNode({self.tag}, {self.value}, children: {self.children}, {self.props})"            


    def to_html(self):
        raise NotImplementedError
    
    def props_to_html(self):
        if self.props is None or self.props=="":
            return ""
        
        built_html=""
        for i in self.props:
            built_html+=f' {i}="{self.props[i]}"'
        return built_html
    
class LeafNode(HTMLNode):

    def __init__(self, tag, value, props:dict|None=None):
        super().__init__(tag, value, None, props)
    
    def to_html(self):
        if self.value is None:
            raise ValueError("Value must be set for a Leaf Node")
        elif self.tag is None:
            return self.value
        else:
            #Simply stick the value between the two htmlified
            return f'<{self.tag}{self.props_to_html()}>{self.value}</{self.tag}>'
        
    def __repr__(self):
        return f"LeafNode({self.tag}, {self.value}, {self.props})"     
    
class ParentNode(HTMLNode):

    def __init__(self, tag, children, props:dict|None=None):
        super().__init__(tag, None, children, props)

    def to_html(self):
        if self.tag is None:
            raise ValueError('Parent Node must have a tag specified')
        if self.children is None:
            raise ValueError('Parent Node must have children')
        
        #open the parent tag and include any props
        output=f'<{self.tag}{self.props_to_html()}>'
        #then generate the child HTML
        for i in self.children:
            output+=i.to_html()
        #close it
        output+=f'</{self.tag}>'
        return output


        
