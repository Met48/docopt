#! /usr/bin/env python
'''

r"""Usage: prog

"""
$ prog
{}

$ prog --xxx
"user-error"


r"""Usage: prog [options]

-a  All.

"""
$ prog
{"-a": false}

$ prog -a
{"-a": true}

$ prog -x
"user-error"


r"""Usage: prog [options]

--all  All.

"""
$ prog
{"--all": false}

$ prog --all
{"--all": true}

$ prog --xxx
"user-error"


r"""Usage: prog [options]

-v, --verbose  Verbose.

"""
$ prog --verbose
{"--verbose": true}

$ prog --ver
{"--verbose": true}

$ prog -v
{"--verbose": true}


r"""Usage: prog [options]

-p PATH

"""
$ prog -p home/
{"-p": "home/"}

$ prog -phome/
{"-p": "home/"}

$ prog -p
"user-error"


r"""Usage: prog [options]

--path <path>

"""
$ prog --path home/
{"--path": "home/"}

$ prog --path=home/
{"--path": "home/"}

$ prog --pa home/
{"--path": "home/"}

$ prog --pa=home/
{"--path": "home/"}

$ prog --path
"user-error"


r"""Usage: prog [options]

-p PATH, --path=<path>  Path to files.

"""
$ prog -proot
{"--path": "root"}


r"""Usage: prog [options]

   -p --path PATH  Path to files.

"""
$ prog -p root
{"--path": "root"}

$ prog --path root
{"--path": "root"}


r"""Usage: prog [options]

-p PATH  Path to files [default: ./]

"""
$ prog
{"-p": "./"}

$ prog -phome
{"-p": "home"}


r"""UsAgE: prog [options]

--path=<files>  Path to files
                [dEfAuLt: /root]

"""
$ prog
{"--path": "/root"}

$ prog --path=home
{"--path": "home"}


r"""usage: prog [options]

-a        Add
-r        Remote
-m <msg>  Message

"""
$ prog -a -r -m Hello
{"-a": true,
 "-r": true,
 "-m": "Hello"}

$ prog -armyourass
{"-a": true,
 "-r": true,
 "-m": "yourass"}

$ prog -a -r
{"-a": true,
 "-r": true,
 "-m": null}


r"""Usage: prog [options]

--version
--verbose

"""
$ prog --version
{"--version": true,
 "--verbose": false}

$ prog --verbose
{"--version": false,
 "--verbose": true}

$ prog --ver
"user-error"

$ prog --verb
{"--version": false,
 "--verbose": true}


r"""usage: prog [-a -r -m <msg>]

-a        Add
-r        Remote
-m <msg>  Message

"""
$ prog -armyourass
{"-a": true,
 "-r": true,
 "-m": "yourass"}


r"""usage: prog [-armmsg]

-a        Add
-r        Remote
-m <msg>  Message

"""
$ prog -a -r -m Hello
{"-a": true,
 "-r": true,
 "-m": "Hello"}


r"""usage: prog -a -b

-a
-b

"""
$ prog -a -b
{"-a": true, "-b": true}

$ prog -b -a
{"-a": true, "-b": true}

$ prog -a
"user-error"

$ prog
"user-error"


r"""usage: prog (-a -b)

-a
-b

"""
$ prog -a -b
{"-a": true, "-b": true}

$ prog -b -a
{"-a": true, "-b": true}

$ prog -a
"user-error"

$ prog
"user-error"


r"""usage: prog [-a] -b

-a
-b

"""
$ prog -a -b
{"-a": true, "-b": true}

$ prog -b -a
{"-a": true, "-b": true}

$ prog -a
"user-error"

$ prog -b
{"-a": false, "-b": true}

$ prog
"user-error"


r"""usage: prog [(-a -b)]

-a
-b

"""
$ prog -a -b
{"-a": true, "-b": true}

$ prog -b -a
{"-a": true, "-b": true}

$ prog -a
"user-error"

$ prog -b
"user-error"

$ prog
{"-a": false, "-b": false}


r"""usage: prog (-a|-b)

-a
-b

"""
$ prog -a -b
"user-error"

$ prog
"user-error"

$ prog -a
{"-a": true, "-b": false}

$ prog -b
{"-a": false, "-b": true}


r"""usage: prog [ -a | -b ]

-a
-b

"""
$ prog -a -b
"user-error"

$ prog
{"-a": false, "-b": false}

$ prog -a
{"-a": true, "-b": false}

$ prog -b
{"-a": false, "-b": true}


r"""usage: prog <arg>

"""
$ prog 10
{"<arg>": "10"}

$ prog 10 20
"user-error"

$ prog
"user-error"


r"""usage: prog [<arg>]

"""
$ prog 10
{"<arg>": "10"}

$ prog 10 20
"user-error"

$ prog
{"<arg>": null}


r"""usage: prog <kind> <name> <type>

"""
$ prog 10 20 40
{"<kind>": "10", "<name>": "20", "<type>": "40"}

$ prog 10 20
"user-error"

$ prog
"user-error"


r"""usage: prog <kind> [<name> <type>]

"""
$ prog 10 20 40
{"<kind>": "10", "<name>": "20", "<type>": "40"}

$ prog 10 20
{"<kind>": "10", "<name>": "20", "<type>": null}

$ prog
"user-error"


r"""usage: prog [<kind> | <name> <type>]

"""
$ prog 10 20 40
"user-error"

$ prog 20 40
{"<kind>": null, "<name>": "20", "<type>": "40"}

$ prog
{"<kind>": null, "<name>": null, "<type>": null}


r"""usage: prog (<kind> --all | <name>)

--all

"""
$ prog 10 --all
{"<kind>": "10", "--all": true, "<name>": null}

$ prog 10
{"<kind>": null, "--all": false, "<name>": "10"}

$ prog
"user-error"


r"""usage: prog [<name> <name>]

"""
$ prog 10 20
{"<name>": ["10", "20"]}

$ prog 10
{"<name>": ["10"]}

$ prog
{"<name>": []}


r"""usage: prog [(<name> <name>)]

"""
$ prog 10 20
{"<name>": ["10", "20"]}

$ prog 10
"user-error"

$ prog
{"<name>": []}


r"""usage: prog NAME...

"""
$ prog 10 20
{"NAME": ["10", "20"]}

$ prog 10
{"NAME": ["10"]}

$ prog
"user-error"


r"""usage: prog [NAME]...

"""
$ prog 10 20
{"NAME": ["10", "20"]}

$ prog 10
{"NAME": ["10"]}

$ prog
{"NAME": []}


r"""usage: prog [NAME...]

"""
$ prog 10 20
{"NAME": ["10", "20"]}

$ prog 10
{"NAME": ["10"]}

$ prog
{"NAME": []}


r"""usage: prog [NAME [NAME ...]]

"""
$ prog 10 20
{"NAME": ["10", "20"]}

$ prog 10
{"NAME": ["10"]}

$ prog
{"NAME": []}


r"""usage: prog (NAME | --foo NAME)

--foo

"""
$ prog 10
{"NAME": "10", "--foo": false}

$ prog --foo 10
{"NAME": "10", "--foo": true}

$ prog --foo=10
"user-error"


r"""usage: prog (NAME | --foo) [--bar | NAME]

--foo
--bar

"""
$ prog 10
{"NAME": ["10"], "--foo": false, "--bar": false}

$ prog 10 20
{"NAME": ["10", "20"], "--foo": false, "--bar": false}

$ prog --foo --bar
{"NAME": [], "--foo": true, "--bar": true}


r"""Naval Fate.

Usage:
  prog ship new <name>...
  prog ship [<name>] move <x> <y> [--speed=<kn>]
  prog ship shoot <x> <y>
  prog mine (set|remove) <x> <y> [--moored|--drifting]
  prog -h | --help
  prog --version

Options:
  -h --help     Show this screen.
  --version     Show version.
  --speed=<kn>  Speed in knots [default: 10].
  --moored      Mored (anchored) mine.
  --drifting    Drifting mine.

"""
$ prog ship Guardian move 150 300 --speed=20
{"--drifting": false,
 "--help": false,
 "--moored": false,
 "--speed": "20",
 "--version": false,
 "<name>": ["Guardian"],
 "<x>": "150",
 "<y>": "300",
 "mine": false,
 "move": true,
 "new": false,
 "remove": false,
 "set": false,
 "ship": true,
 "shoot": false}


r"""usage: prog --hello

"""
$ prog --hello
{"--hello": true}


r"""usage: prog [--hello=<world>]

"""
$ prog
{"--hello": null}

$ prog --hello wrld
{"--hello": "wrld"}


r"""usage: prog [-o]

"""
$ prog
{"-o": false}

$ prog -o
{"-o": true}


r"""usage: prog [-opr]

"""
$ prog -op
{"-o": true, "-p": true, "-r": false}

'''
#Simplejson is needed for Py2.5
try:
    import json
except ImportError:
    import simplejson as json
import sys
from subprocess import Popen, PIPE, STDOUT


def generate_cases(ids=None):
    #This is a generator to support integration with py.test
    index = 0
    for fixture in __doc__.split('r"""'):
        doc, _, body = fixture.partition('"""')
        for case in body.split('$')[1:]:
            index += 1
            if ids is not None and index not in ids:
                continue
            argv, _, expect = case.strip().partition('\n')
            prog, _, argv = argv.strip().partition(' ')
            assert prog == 'prog', repr(prog)

            yield index, argv, doc, expect


def check_case(testee, argv, doc, expect):
    p = Popen(testee + ' ' + argv,
              stdout=PIPE, stdin=PIPE, stderr=STDOUT, shell=True)
    #Encode and decode needed for bytes conversion in Py3k
    result = p.communicate(input=doc.encode())[0].decode()

    py_result = json.loads(result)
    py_expect = json.loads(expect)

    assert py_result == py_expect, py_result


def main(testee, ids):
    summary = ''
    for index, argv, doc, expect in generate_cases(ids):
        try:
            check_case(testee, argv, doc, expect)
        except:
            #Compatibility, 2.5 through 3.x
            #This is the only way to support 2.5 (can't use "Exception as e")
            # and 3.x (can't use "Exception, e")
            ExceptionClass, e = sys.exc_info()[:2]

            if ExceptionClass is AttributeError:
                summary += 'F'
                print((' %d: FAILED ' % index).center(79, '='))
                print('r"""%s"""' % doc)
                print('$ prog %s\n' % argv)
                print('result>' + str(e))
                print('expect>' + expect)
            else:
                summary += 'J'
                print((' %d: BAD JSON ' % index).center(79, '='))
                print('r"""%s"""' % doc)
                print('$ prog %s\n' % argv)
                print('result>' + str(e))
                print('expect>' + expect)
        else:
            summary += '.'

    print((' %d / %d ' % (summary.count('.'), len(summary))).center(79, '='))
    print(summary)


if __name__ == '__main__':
    testee = (sys.argv[1] if len(sys.argv) >= 2 else
            exit('Usage: language_agnostic_tester.py ./path/to/executable/testee [ID ...]'))
    ids = [int(x) for x in sys.argv[2:]] if len(sys.argv) > 2 else None

    main(testee, ids)

