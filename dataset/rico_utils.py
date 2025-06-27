from collections.abc import Iterable
from .rico_models import RicoScreen, RicoActivity, ScreenInfo
from .convert_class_to_label import convert_class_to_text_label

# contains methods for collecting UI elements

def get_all_texts_from_node_tree(node):
    results = []
    if 'text' in node and isinstance(node['text'], Iterable):
        if node['text'] and node['text'].strip():
            results.append(node['text'])
    if 'children' in node and isinstance(node['children'], Iterable):
        for child_node in node['children']:
            if (isinstance(child_node, dict)):
                results.extend(get_all_texts_from_node_tree(child_node))
    return results

def get_all_labeled_texts_from_node_tree(node, in_list: bool, in_drawer: bool, testing):
    results = []
    text_class = 0
    if 'text' in node and isinstance(node['text'], Iterable):
        if node['text'] and node['text'].strip():
            text = node['text']
            if "class" in node:
                the_class = node["class"]
            elif "className" in node:
                the_class = node["className"]
            if the_class and the_class.strip():
                if the_class == 'TextView':
                    if node['clickable']:
                        text_class = 20
                    else:
                        text_class = 11
                else:
                    text_class = convert_class_to_text_label(the_class)
            if text_class==0 and (in_drawer or in_list):
                if in_drawer:
                    text_class = 25
                if in_list:
                    text_class = 24
            if node["bounds"]:
                bounds = node["bounds"]
            if testing and text_class==0:
                results.append([text, text_class, bounds, the_class])
            else:
                results.append([text, text_class, bounds])
    if 'children' in node and isinstance(node['children'], Iterable):
        for child_node in node['children']:
            if (isinstance(child_node, dict)):
                if text_class == 12:
                    in_list = True
                if text_class == 7:
                    in_drawer = True
                results.extend(get_all_labeled_texts_from_node_tree(child_node, in_list, in_drawer, testing))
    return results

def get_all_texts_from_rico_screen(rico_screen: RicoScreen):
    if rico_screen.activity is not None and rico_screen.activity.root_node is not None:
        return get_all_texts_from_node_tree(rico_screen.activity.root_node)

def get_all_labeled_texts_from_rico_screen(rico_screen: RicoScreen, testing=False):
    if rico_screen.activity is not None and rico_screen.activity.root_node is not None:
        return get_all_labeled_texts_from_node_tree(rico_screen.activity.root_node, False, False, testing)

# return a list that contains all abstracted UI information in a UI tree, structures are lost, and the tree is flattened into a list.
# the size of the list is unlimited
# format of each element in the list is [text:str, class_tag:int, pos&size:[x1,y1,x2,y2]]
def get_all_labeled_uis_from_node_tree(node, in_list: bool, in_drawer: bool, testing):
    extracted_uis = []
    class_tag = 0
    if 'text' in node and isinstance(node['text'], Iterable) and node['text'] and node['text'].strip():
        text = node['text']
    else: 
        text = ''
    if "class" in node:
        the_class = node["class"]
    elif "className" in node:
        the_class = node["className"]
    else:
        the_class = None
    if the_class and the_class.strip():
        if the_class == 'TextView':
            if node['clickable']:
                class_tag = 20
            else:
                class_tag = 11
        else:
            class_tag = convert_class_to_text_label(the_class)
    if class_tag==0 and (in_drawer or in_list):
        if in_drawer:
            class_tag = 25
        if in_list:
            class_tag = 24
    if node["bounds"]:
        bounds = node["bounds"]
    else:
        bounds = [0,0,0,0]
    if "visible-to-user" in node:
        visibility = node["visible-to-user"]
    elif "visible_to_user" in node:
        visibility = True #node["visible_to_user"]
    else:
        visibility = False
    if visibility and testing and class_tag==0:
        extracted_uis.append([text, class_tag, bounds, the_class])
    elif visibility:
        #[str, int, [bounds list(position and size)]]
        extracted_uis.append([text, class_tag, bounds]) # UI representation for current node
    if 'children' in node and isinstance(node['children'], Iterable):
        for child_node in node['children']:
            if (isinstance(child_node, dict)):
                if class_tag == 12:
                    in_list = True
                if class_tag == 7:
                    in_drawer = True
                extracted_uis.extend(get_all_labeled_uis_from_node_tree(child_node, in_list, in_drawer, testing))
    return extracted_uis

# return a list that contains all abstracted UI information in a UI tree, structures are lost, and the tree is flattened into a list.
# the size of the list is unlimited
# format of each element in the list is [text:str, class_tag:int, pos&size:[x1,y1,x2,y2]]
def get_all_labeled_uis_from_rico_screen(rico_screen: RicoScreen, testing=False):
    if rico_screen.activity is not None and rico_screen.activity.root_node is not None:
        return get_all_labeled_uis_from_node_tree(rico_screen.activity.root_node, False, False, testing)


