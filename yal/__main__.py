"""
CLI entry point for YAL to YAML convertion
"""

import sys
from argparse import ArgumentParser
from .core import parse, as_yaml

def main():
    '''
    Convert YAL to YAML. Run `yal2yaml --help` for more information
    '''
    parser = ArgumentParser( prog = 'yal2yaml' , description='Convert YAL to YAML')
    parser.add_argument('file_name', nargs='?', help='Input file (optional, accepts stdin)')
    args   = parser.parse_args()
    if args.file_name:
        try:
            with open(args.file_name, 'r') as file:
                yal_input = file.read()
        except FileNotFoundError:
            print(f'No such file: f{args.file_name}')
            return 1
    else:
        yal_input = sys.stdin.read()
    print(as_yaml(parse(yal_input)))
    return 0

if __name__ == '__main__':
    sys.exit(main())
