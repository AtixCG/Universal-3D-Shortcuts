import numpy as np


def get_ob_selection_mask(select_mask, inside_mask, mode):
    # https://stackoverflow.com/questions/33384529/difference-between-numpy-logical-and-and
    if mode == 'SET':
        select = inside_mask
    elif mode == 'ADD':
        select = select_mask | inside_mask
    elif mode == 'SUB':
        select = select_mask & ~inside_mask
    elif mode == 'XOR':
        select = select_mask ^ inside_mask
    else:  # mode == 'AND'
        select = select_mask & inside_mask
    return select


def get_mesh_selection_mask(elem, shape, inside_mask, mode):
    # https://stackoverflow.com/questions/33384529/difference-between-numpy-logical-and-and
    if mode == 'SET':
        select = inside_mask
    elif mode == 'ADD':
        select = np.zeros(shape, "?")
        elem.foreach_get("select", select)
        select = select | inside_mask
    elif mode == 'SUB':
        select = np.zeros(shape, "?")
        elem.foreach_get("select", select)
        select = select & ~inside_mask
    elif mode == 'XOR':
        select = np.zeros(shape, "?")
        elem.foreach_get("select", select)
        select = select ^ inside_mask
    else:  # mode == 'AND'
        select = np.zeros(shape, "?")
        elem.foreach_get("select", select)
        select = select & inside_mask
    return select
