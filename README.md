# PYAL

A quick and dirty parser for an even dirtier language. YAL is the language used
to describe the
[MCNC benchmark netlist circuits](https://s2.smu.edu/~manikas/Benchmarks/MCNC_Benchmark_Netlists.html).
See the
[YAL documentation](https://s2.smu.edu/~manikas/Benchmarks/YalDescription.txt)
for further details.

## Dependencies

- `pyparsing`
- `pyaml`

## Usage

The `example/example.yal` is taken from the
[YAL documentation](https://s2.smu.edu/~manikas/Benchmarks/YalDescription.txt).

Module:

```python
import yal

modules = yal.read('./example/example.yal')
```

See the [API documentation]() for more information.

CLI:

```
$ yal2yaml ./example/example.yal > ./exmaple/example.yaml
$ cat ./example/example.yal | yal2yaml > ./example/example.yaml
```

## Installation

From git with pip:

```
$ pip install git+https://github.com/augustunderground/pyal.git
```

From source with pip:

```
$ git clone https://github.com/augustunderground/pyal.git
$ cd pyal
$ pip install . --use-feature=in-tree-build
```

## Grammar

Due to the conflicting defintions of the YAL grammar a slightly revised version
is used here:

```
modulename    ::= [a-zA-Z0-9_]+ ;
moduletype    ::= "STANDARD" | "PAD" | "GENERAL" | "PARENT" | "FEEDTHROUGH" ;
width         ::= [0-9]+ ;
height        ::= [0-9]+ ;
signalname    ::= [a-zA-Z0-9_]+ ;
terminaltype  ::= "I" | "O" | "B" | "PI" | "PO" | "PB" | "F" | "PWR" | "GND" ;
side          ::= "BOTTOM" | "RIGHT" | "TOP" | "LEFT" ;
layer         ::= "PDIFF" | "NDIFF" | "POLY" | "METAL1" | "METAL2" ;
xposition     ::= -?[0-9]+ ;
yposition     ::= -?[0-9]+ ;
position      ::= -?[0-9]+ ;
instancename  ::= [a-zA-Z0-9_]+ ;
xlocation     ::= -?[0-9]+ ;
ylocation     ::= -?[0-9]+ ;
current       ::= -?[0-9]+(\.[0-9]+)? ;
voltage       ::= -?[0-9]+(\.[0-9]+)? ;
maximumlength ::= [0-9]+ ;
reflection    ::= "RFLNONE" | "RFLY" ;
rotation      ::= "ROT0" | "ROT90" | "ROT180" | "ROT270" ;
dimension     ::= x y ;
dimensions    ::= dimension+ ;
x             ::= -?[0-9]+ ;
y             ::= -?[0-9]+ ;
io            ::= signalname terminaltype ( xposition yposition [ width layer ] 
                                          | side position [ width layer ] )
                    [ "CURRENT" current ] [ "VOLTAGE" voltage ] ;
ios           ::= (io ';')+ ;
network       ::= instancename modulename signalname (net+) ;
networks      ::= (network ';')+ ; 
net           ::= [a-zA-Z0-9_]+ ;
placement     ::= instancename xlocation ylocation [reflection] [rotation] ;
placements    ::= (placement ';')+ ;
critnet       ::= signalname maximumlength ;
critnets      ::= (critnet ';')+ ;
module        ::= 'MODULE' modulename ';'
                    'TYPE' moduletype ';'
                    'DIMENSIONS' dimensions ';'
                    'IOLIST;'
                        ios
                    'ENDIOLIST;'
                    'NETWORK'
                        networks
                    'ENDNETWORK;'
                    ['PLACEMENT'
                        placements
                     'ENDPLACEMENT;']
                    ['CRITICALNETS;'
                        critnets
                     'ENDCRITICALNETS;']
                  'ENDMODULE;' ;
```
