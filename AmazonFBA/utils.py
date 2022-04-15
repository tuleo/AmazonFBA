import json
import streamlit as st
from typing import Dict, List, Type
from products import Products

class NoNiechesData(Exception):
    pass

def save_nieches(path:str, 
                 nieches_data:Dict[str, Type[Products]]) -> None:
    """
    Saves the nieches information into .json  format

    Parameters:
        path: save path 
        nieches_data: data of the analysed product nieches
    """
    dict_ = {}
    for niech_name, products in nieches_data.items():
        dict_[niech_name] = products.into_list_dict()
    with open(path, "w") as f:
        json.dump(dict_, f)
        
def load_nieches(path:str) -> Dict[str, Type[Products]]:
    """
    Load the nieches information

    Parameters:
        path: path of the .json file
    """
    try:
        with open(path, "r") as f:
            nieches_data_loaded = json.load(f)
        nieches_data = {}
        for niech_name, products_dict in nieches_data_loaded.items():
            nieches_data[niech_name] = Products.init_from_list_dict(products_dict)
        return nieches_data
    except FileNotFoundError:
        raise NoNiechesData("No Nieches Data on the given path")
