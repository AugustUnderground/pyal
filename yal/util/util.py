"""
yal.util

Utility functions for YAL Modules in Python
"""

from random import randrange
from .. import core

def _init_participant():
    return { 'idx':         None
           , 'xmin':        0
           , 'ymin':        0
           , 'width':       0
           , 'height':      0
           , 'clashes':     {}
           , 'aversions':   {}
           , 'inference':   0
           , 'connections': {}
           , 'turmoil':     0
           , 'wounds':      [] }

def randomize_placement( participant:dict, x_bound: int = 120, y_bound: int = 120
                       ) -> dict:
    """
    Randomize the placement of a participant within a given boundary.

    Arguemnts:

        `participant`: The participant whose placement will be randomized

        `x_bound`: X-Axis upper limit. (optional, default = 120)

        `y_bound`: Y-Axis upper limit. (optional, default = 120)
    """
    x_limit = x_bound - participant['width']
    y_limit = y_bound - participant['height']
    x_min   = randrange(0,x_limit,1)
    y_min   = randrange(0,y_limit,1)
    return participant | { 'xmin': x_min, 'ymin': y_min }

def as_participant( module: core.Module, opt_fields: list[str] = None
                  ) -> dict:
    """
    Convert a `Module` dataclass object to a `dict` participant.

    Arguments:

        `module`: The `Module` object to convert

        `opt_fields`: Optional field names (as string) from `Module` to retain
            in the participant dict. Options are 'module_type', 'dimensions',
            'terminals', 'network', 'placement' and 'critical_nets'. Default is
            `None`.

    Return:

        A dictionary of the form:

        ```
        { 'idx':         Module.module_name
        , 'xmin':        <lower left x coordinate>
        , 'ymin':        <lower left y coordinate>
        , 'width':       <width of module>
        , 'height':      <height of module>
        , 'clashes':     {}
        , 'aversions':   {}
        , 'inference':   0
        , 'connections': {}
        , 'turmoil':     0
        , 'wounds':      [] }
        ```
    """

    dims        = sorted(module.dimensions)
    x_min,y_min = dims[0]
    x_max,y_max = dims[-1]
    width       = x_max - x_min
    height      = y_max - y_min
    mod_dict    = {k: v for k,v in core.as_dict(module).items()
                        if (opt_fields and k in opt_fields)}
    participant = mod_dict | _init_participant() \
                | { 'idx':    module.module_name
                  , 'width':  width
                  , 'height': height
                  , 'xmin':   x_min
                  , 'ymin':   y_min }
    return participant

def as_participants( modules: list[core.Module]
                   , rng_placement: bool = True
                   , module_type: bool   = False
                   , dimensions: bool    = False
                   , terminals: bool     = False
                   , network: bool       = True
                   , placement: bool     = False
                   , critical_nets: bool = False
                   ) -> list[dict]:
    """
    Read a .yal file and convert it to a list of dictionaries.

    Arguemnts:

        `modules`: A list of `Module` objects.

        `rng_placement`: A boolean indicating whether the initial placement
            shall be randomized. (optional, default = True)

        `module_type`: Whether to retain the 'module_type' field (optional, default = False)

        `dimensions`: Whether to retain the 'dimensions' field (optional, default = False)

        `terminals`: Whether to retain the 'terminals' field (optional, default = False)

        `network`: Whether to retain the 'network' field (optional, default = True)

        `placement`: Whether to retain the 'placement' field (optional, default = False)

        `critical_nets`: Whether to retain the 'critical_nets' field (optional, default = False)
    """

    all_fields = zip( [ module_type, dimensions, terminals
                      , network, placement, critical_nets ]
                    , [ 'module_type', 'dimensions', 'terminals'
                      , 'network', 'placement', 'critical_nets' ] )

    fields = [f for c,f in list(all_fields) if c]

    parts = [as_participant(m, opt_fields=fields) for m in modules]

    if rng_placement:
        bound        = [p for p in parts if p['idx'] == 'bound']
        x_bound      = bound[0]['width'] if bound else 120
        y_bound      = bound[0]['height'] if bound else 120
        rng_parts    = [ randomize_placement(p, x_bound = x_bound
                                              , y_bound = y_bound )
                         for p in parts if p['idx'] != 'bound' ]
        participants = (rng_parts + bound) if bound else rng_parts

    else:
        participants = parts

    return participants
