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

def random_color() -> str:
    """
    Generate a random color.
    """
    col = format(randrange(0, int(2 ** 24 - 1), 1), 'x')
    return f'#{col}'

def randomize_placement( participant:dict, x_bound: int = 120, y_bound: int = 120
                       ) -> dict:
    """
    Randomize the placement of a participant within a given boundary.

    Arguments:

    - `participant`: The participant whose placement will be randomized
    - `x_bound`: X-Axis upper limit. (optional, default = `120`)
    - `y_bound`: Y-Axis upper limit. (optional, default = `120`)
    """
    x_limit = x_bound - participant['width']
    y_limit = y_bound - participant['height']
    x_min   = randrange(0,x_limit,1)
    y_min   = randrange(0,y_limit,1)
    return participant | { 'xmin': x_min, 'ymin': y_min }

def as_participant( module: core.Module, opt_fields: list[str] = None
                  , colorize: bool = True ) -> dict:
    """
    Convert a `yal.core.Module` dataclass object to a `dict` participant.

    Arguments:

    - `module`: The `yal.core.Module` object to convert
    - `opt_fields`: Optional field names (as string) from `yal.core.Module`
        to retain in the participant dict. Options are `'module_type'`,
        `'dimensions'`, `'terminals'`, `'network'`, `'placement'` and
        `'critical_nets'`. (optional, default is `None`)
    - `colorize`: Whether to add a random color to the participant. Otherwise
        the `'color'` field is `None`. (optional, default = True)

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
    , 'connections': {<other idx>: <weight>}
    , 'turmoil':     0
    , 'wounds':      [] }
    ```
    """

    dims        = sorted(module.dimensions)
    x_min,y_min = dims[0]
    x_max,y_max = dims[-1]
    width       = x_max - x_min
    height      = y_max - y_min
    idx         = module.module_name
    mod_dict    = {k: v for k,v in core.as_dict(module).items()
                        if (opt_fields and k in opt_fields)}
    participant = mod_dict | _init_participant() \
                | { 'idx':    idx
                  , 'width':  width
                  , 'height': height
                  , 'xmin':   x_min
                  , 'ymin':   y_min
                  , 'color':  random_color() if colorize and (idx != 'bound') else None }

    return participant

def connects(participant: dict, participants: list[dict]) -> dict[str,int]:
    """
    Weighted connections between participants

    Arguments:

    - `participant`: The participant in question

    - `participants`: Other participants (can include the former)

    Return:

    A dictionary of the form:

    ```
    {'other participant': <weight of connection>}
    ```
    """
    name = participant['module_name']
    sigs = set(participant.get('signal_names', []))
    cons =  { p['module_name']: len((set(p.get('signal_names', [])) & sigs) - {'G', 'P'})
              for p in participants if p['module_name'] not in [name, 'bound'] }
    return cons

def as_participants( modules: list[core.Module]
                   , rng_placement: bool = True
                   , colorize: bool      = True
                   , module_type: bool   = False
                   , dimensions: bool    = False
                   , terminals: bool     = False
                   , network: bool       = True
                   , placement: bool     = False
                   , critical_nets: bool = False
                   ) -> list[dict]:
    """
    Convert a list of `yal.core.Module`s to a list of dictionaries.

    Arguments:

    - `modules`: A list of `yal.core.Module` objects.
    - `rng_placement`: A boolean indicating whether the initial placement
        shall be randomized. (optional, default = `True`)
    - `colorize`: Whether to add a random color to the participant (optional, default = `True`)
    - `module_type`: Whether to retain the `yal.core.Module.module_type` field
        (optional, default = `False`)
    - `dimensions`: Whether to retain the `yal.core.Module.dimensions` field
        (optional, default = `False`)
    - `terminals`: Whether to retain the `yal.core.Module.terminals` field
        (optional, default = `False`)
    - `network`: Whether to retain the `yal.core.Module.network` field
        (optional, default = `True`)
    - `placement`: Whether to retain the `yal.core.Module.placement`
        field (optional, default = `False`)
    - `critical_nets`: Whether to retain the `yal.core.Module.critical_nets` field
        (optional, default = `False`)

    Return:
    
    A list of participant dictionaries.
    """

    all_fields = zip( [ module_type, dimensions, terminals
                      , network, placement, critical_nets ]
                    , [ 'module_type', 'dimensions', 'terminals'
                      , 'network', 'placement', 'critical_nets' ] )

    fields = [f for c,f in list(all_fields) if c]

    parts = [as_participant(m, opt_fields=fields, colorize=colorize) for m in modules]

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

    bound   = [p for p in participants if p['idx'] == 'bound']
    network = bound[0].get('network', []) if bound else []
    cons    = {n['module_name'] : connects(n, network) for n in network}

    return [p | {'connections': cons.get(p['idx'])} for p in participants]
