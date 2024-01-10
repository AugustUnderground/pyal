"""
yal.core

Core components of the YAL parser.
"""

from dataclasses import dataclass, asdict
import re
import yaml
from pyparsing import Word, alphanums, nums, Group, Literal, OneOrMore, \
                        Suppress, Optional, Regex, ParseResults

_comment        = Regex(r'\/\/[^\n]*').suppress() \
                | Regex(r'\/\*(.*?)\*\/', flags=re.DOTALL).suppress()
_module_name    = Word(alphanums + "_")
_module_type    = Literal('STANDARD') | Literal('PAD') | Literal('GENERAL') \
                | Literal('PARENT') | Literal('FEEDTHROUGH')
_width          = Word(nums)
_height         = Word(nums)
_signal_name    = Word(alphanums + '_')
_terminal_type  = Literal('I') | Literal('O') | Literal('B') | Literal('PI') \
                | Literal('PO') | Literal('PB') | Literal('F') | Literal('PWR') \
                | Literal('GND')
_side           = Literal('BOTTOM') | Literal('RIGHT') \
                | Literal('TOP') | Literal('LEFT')
_layer          = Literal('PDIFF') | Literal('NDIFF') | Literal('POLY') \
                | Literal('METAL1') | Literal('METAL2')
_x_position     = Word(nums + '-')
_y_position     = Word(nums + '-')
_position       = Word(nums + '-')
_instance_name  = Word(alphanums + '_')
_x_location     = Word(nums + '-')
_y_location     = Word(nums + '-')
_current        = Word(nums + '.-')
_voltage        = Word(nums + '.-')
_maximum_length = Word(nums)
_reflection     = Literal('RFLNONE') | Literal('RFLY')
_rotation       = Literal('ROT0') | Literal('ROT90') \
                | Literal('ROT180') | Literal('ROT270')
_x              = Word(nums + '-')
_y              = Word(nums + '-')
_io             = Group( ( _signal_name('name') + _terminal_type('type')
                         + ( Group( _x_position('x') + _y_position('y')
                                  + Optional(_width('width') + _layer('layer')) )
                           | Group( _side('side') + _position('pos')
                                  + Optional(_width('width') + _layer('layer')) )))
                       + Optional('CURRENT' + _current('current'))
                       + Optional('VOLTAGE' + _voltage('voltage')) )
_ios            = OneOrMore(_io + Suppress(';'))
_dimension      = Group(_x + _y)
_dimensions     = OneOrMore(_dimension)
_network        = Group( _instance_name('name') + _module_name('module')
                       + OneOrMore(_signal_name)('signals') )
_networks       = OneOrMore(_network + Suppress(';'))
_placement      = _instance_name('name') \
                + Group( _x_location + _y_location('y')
                       + Optional(_reflection) + Optional(_rotation)
                       )('placement')
_placements     = OneOrMore(_placement + Suppress(';'))
_critnet        = _signal_name('name') + _maximum_length('len')
_critnets       = OneOrMore(_critnet + Suppress(';'))
_module         = Group( Literal('MODULE') + _module_name('name') + Suppress(';')
                       +     Literal('TYPE') + _module_type('type') + Suppress(';')
                       +     Literal('DIMENSIONS') + _dimensions('dims') + Suppress(';')
                       +     Suppress('IOLIST;')
                       +         _ios('terms')
                       +     Suppress('ENDIOLIST;')
                       +     Optional( Suppress('NETWORK;')
                                     + _networks('nets')
                                     + Suppress('ENDNETWORK;'))
                       +     Optional( Suppress('PLACEMENT;')
                                     + _placements('placements')
                                     + Suppress('ENDPLACEMENT;'))
                       +     Optional( Suppress('CRITICALNETS;')
                                     + _critnets('crits')
                                     + Suppress('ENDCRITICALNETS;'))
                       + Suppress('ENDMODULE;'))
grammar         = OneOrMore(_module).ignore(_comment)

@dataclass
class Network:
    '''
    The NETWORK section defines the internal connectivity for the module.
    '''
    instance_name: str
    module_name:   str
    signal_names:  list[str]

def make_network(parse_result: ParseResults) -> Network:
    '''
    Constructor for the `Network` data class.
    '''
    return Network( parse_result.get('name', 'NO NAME')
                  , parse_result.get('module', 'NO MODULE')
                  , list(parse_result.get('signals', [])) )

@dataclass
class Terminal:
    '''
    This is describes one element of the IOLIST.
    '''
    signal_name:   str
    terminal_type: str
    x_position:    int
    y_position:    int
    width:         int
    layer:         str
    position:      int
    size:          int
    side:          str

def make_terminal(parse_result: ParseResults) -> Terminal:
    '''
    Constructor for the `Terminal` data class.
    '''
    return Terminal( parse_result.get('name', 'NO NAME')
                   , parse_result.get('type', 'NO TYPE')
                   , parse_result.get('x', None)
                   , parse_result.get('y', None)
                   , parse_result.get('width', None)
                   , parse_result.get('layer', None)
                   , parse_result.get('position', None)
                   , parse_result.get('size', None)
                   , parse_result.get('side', None) )

@dataclass
class Module:
    '''
    A MODULE as defined by YAL.
    '''
    module_name:   str
    module_type:   str
    dimensions:    list[(int,int)]
    terminals:     list[Terminal]
    network:       dict[tuple[str,str],list[str]]
    placement:     dict[str,tuple[int,int,str,str]]
    critical_nets: dict[str,int]

def make_module(parse_result: ParseResults) -> Module:
    '''
    Constructor for the `Module` data class.
    '''
    return Module( parse_result.get('name', 'NO NAME')
                 , parse_result.get('type', 'NO TYPE')
                 , [tuple(map(int,d)) for d in parse_result.get('dims', [])]
                 , [make_terminal(t) for t in parse_result.get('terms', [])]
                 , [make_network(n) for n in parse_result.get('nets', [])]
                 , { p.get('name', 'NO NAME'): tuple(p.get('placement', []))
                     for p in parse_result.get('placements', []) }
                 , { c.get('name', 'NO NAME'): c.get('len')
                    for c in parse_result.get('crits', []) })

def parse(file_contents: str) -> list[Module]:
    '''
    Parse a YAL string.
    '''
    return [ make_module(pr) for pr in grammar.parseString(file_contents) ]

def read(file_name: str) -> list[Module]:
    '''
    Read .yal file and parse its content.
    '''
    with open(file_name, 'r') as yal_file:
        yal_input = yal_file.read()
    return parse(yal_input)

def as_dict(module: Module) -> dict:
    '''
    Convert a Module to a dictionary.
    '''
    mod_dict = asdict(module)
    mod_dict['dimensions'] = [{'x': x, 'y': y} for x,y in mod_dict['dimensions']]
    return mod_dict

def as_dicts(modules: list[Module]) -> dict:
    '''
    Convert a list of Modules to a list of dictionaries.
    '''
    return [ as_dict(m) for m in modules ]

def as_yaml(modules: list[Module]) -> str:
    '''
    Convert a list of modules to YAML.
    '''
    return yaml.dump([{'module' : m} for m in as_dicts(modules)])
