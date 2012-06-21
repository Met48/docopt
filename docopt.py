from copy import copy
import sys
import re


#Python 3 Compatibility
try:
    basestring
except NameError:
    basestring = str


class DocoptLanguageError(Exception):

    """Error in construction of usage-message by developer."""


class DocoptExit(SystemExit):

    """Exit in case user invoked program with incorrect arguments."""

    usage = ''

    def __init__(self, message=''):
        SystemExit.__init__(self, (message + '\n' + self.usage).strip())


class Node(object):
    def next(self, args, collected):
        return None


class Fragment(object):
    def __init__(self):
        self.tails = []

    def patch(self, node):
        raise NotImplementedError()

    def assemble(self):
        raise NotImplementedError()

    def __eq__(self, other):
        return repr(self) == repr(other)

    def __hash__(self):
        return hash(repr(self))

    @property
    def flat(self):
        if not hasattr(self, 'children'):
            return [self]
        return sum([c.flat for c in self.children], [])

    def __repr__(self):
        if hasattr(self, 'children'):
            return '%s(%s)' % (self.__class__.__name__, ', '.join(repr(c) for c in self.children))
        else:
            return '%s()' % self.__class__.__name__
    
    def fix_list_arguments(self):
        """Find arguments that should accumulate values and fix them."""
        either = [list(c.children) for c in self.either.children]
        for case in either:
            case = [c for c in case if case.count(c) > 1]
            for a in [e for e in case if isinstance(e, Argument)]:
                a.value = []
        return self

    @property
    def either(self):
        """Transform pattern into an equivalent, with only top-level Either."""
        # Currently the pattern will not be equivalent, but more "narrow",
        # although good enough to reason about list arguments.
        if not hasattr(self, 'children'):
            return Either(Required(self))
        else:
            ret = []
            groups = [[self]]
            while groups:
                children = groups.pop(0)
                types = [type(c) for c in children]
                if Either in types:
                    either = [c for c in children if type(c) is Either][0]
                    children.pop(children.index(either))
                    for c in either.children:
                        groups.append([c] + children)
                elif Required in types:
                    required = [c for c in children if type(c) is Required][0]
                    children.pop(children.index(required))
                    groups.append(list(required.children) + children)
                elif Optional in types:
                    optional = [c for c in children if type(c) is Optional][0]
                    children.pop(children.index(optional))
                    groups.append(list(optional.children) + children)
                elif OneOrMore in types:
                    oneormore = [c for c in children if type(c) is OneOrMore][0]
                    children.pop(children.index(oneormore))
                    groups.append(list(oneormore.children) * 2 + children)
                else:
                    ret.append(children)
            return Either(*[Required(*e) for e in ret])


class Literal(Node, Fragment):
    def __init__(self):
        Node.__init__(self)
        Fragment.__init__(self)
        self._next = None

    def next(self, args, collected):
        return self._next

    def patch(self, node):
        if not self._next:
            self._next = node
        else:
            for tail in self.tails:
                tail.patch(node)
        self.tails = [node]

    def assemble(self):
        return self


class Split(Literal):
    def __init__(self, out1=None, out2=None):
        Fragment.__init__(self)
        self.out1 = out1
        self.out2 = out2
        self._is_recursive = False

    def patch(self, node):
        if not self.out1:
            self.out1 = node
        if not self.out2:
            self.out2 = node
        for tail in self.tails:
            tail.patch(node)
        self.tails = [node]

    @property
    def flat(self):
        raise RuntimeError("Flat not computable after pattern is built.")

    def __repr__(self):
        if self._is_recursive:
            return 'Split(RecursiveNode, %r)' % (self.out2)
        else:
            return 'Split(%r, %r)' % (self.out1, self.out2)


class Argument(Literal):
    def __init__(self, name, value=None):
        Literal.__init__(self)
        self.name = name
        self.value = value

    def next(self, args, collected):
        if not args:
            return None

        for i, arg in enumerate(args):
            if isinstance(arg, Argument):
                args.pop(i)
                if isinstance(self.value, list):
                    found = False
                    for i, v in enumerate(collected):
                        if not isinstance(v, Argument) or v.name != self.name:
                            continue
                        collected[i] = Argument(self.name, v.value + [arg.value])
                        found = True
                        break
                    if not found:
                        collected.append(Argument(self.name, [arg.value]))
                else:
                    collected.append(Argument(self.name, arg.value))
                return Literal.next(self, args, collected)
        return None

    def __repr__(self):
        return '%s(%r, %r)' % (self.__class__.__name__, self.name, self.value)


class Command(Literal):
    #TODO: Refactor using Argument base
    def __init__(self, name, value=False):
        Literal.__init__(self)
        self.name = name
        self.value = value

    def next(self, args, collected):
        if not args:
            return None

        for i, arg in enumerate(args):
            if isinstance(arg, Argument):
                if arg.value == self.name:
                    args.pop(i)
                    collected.append(Command(self.name, True))
                    return Literal.next(self, args, collected)
                else:
                    return None
        return None

    def __repr__(self):
        return '%s(%r, %r)' % (self.__class__.__name__, self.name, self.value)


class End(Node):
    def patch(self, node):
        pass


class Option(Literal):
    def __init__(self, short=None, long=None, argcount=0, value=False):
        Literal.__init__(self)
        assert argcount in (0, 1)
        self.short, self.long = short, long
        self.argcount, self.value = argcount, value
        self.value = None if value == False and argcount else value  # HACK

    @classmethod
    def parse(class_, option_description):
        short, long, argcount, value = None, None, 0, False
        options, _, description = option_description.strip().partition('  ')
        options = options.replace(',', ' ').replace('=', ' ')
        for s in options.split():
            if s.startswith('--'):
                long = s
            elif s.startswith('-'):
                short = s
            else:
                argcount = 1
        if argcount:
            matched = re.findall('\[default: (.*)\]', description, flags=re.I)
            value = matched[0] if matched else None
        return class_(short, long, argcount, value)

    def next(self, args, collected):
        i = len(args) - 1
        found = False
        while i >= 0:
            arg = args[i]
            if isinstance(arg, Option):
                if (self.short, self.long) == (arg.short, arg.long):
                    # collected.append(self)
                    args.pop(i)
                    found = True
            i -= 1
        if found:
            return Literal.next(self, args, collected)
        else:
            return None

    @property
    def name(self):
        return self.long or self.short

    def __repr__(self):
        return 'Option(%r, %r, %r, %r)' % (self.short, self.long,
                                           self.argcount, self.value)


class AnyOptions(Literal):
    def next(self, args, collected):
        i = len(args) - 1
        found = False
        while i >= 0:
            arg = args[i]
            if isinstance(arg, Option):
                args.pop(i)
                found = True
            i -= 1
        if found:
            return Literal.next(self, args, collected)
        else:
            return None


class Required(Fragment):
    def __init__(self, *children):
        Fragment.__init__(self)
        self.children = children

    def assemble(self):
        assembled = [c.assemble() for c in self.children]
        if not assembled:
            return Literal()
        root = assembled[0]
        previous = root
        for node in assembled[1:]:
            previous.patch(node)
            previous = node
        return root


class Optional(Fragment):
    def __init__(self, *children):
        Fragment.__init__(self)
        self.children = children

    def assemble(self):
        assert self.children
        if len(self.children) > 1:
            #Optional must apply to children individually
            root = Required(*[Optional(c) for c in self.children])
            return root.assemble()
        else:
            split = Split()
            split.out1 = self.children[0].assemble()
            split.tails = [split.out1]
            return split


class OneOrMore(Fragment):
    def __init__(self, *children):
        Fragment.__init__(self)
        self.children = children

    def assemble(self):
        assert self.children

        #Group multiple children into a Required node
        if len(self.children) > 1:
            res = Required(*self.children)
        else:
            res = self.children[0]

        res = res.assemble()
        #Extra node to prevent recursion when res is a Split
        dummy = Literal()
        dummy.patch(res)
        dummy = dummy.assemble()
        split = Split()
        split.out1 = dummy
        split._is_recursive = True
        assert not split.tails
        res.patch(split)
        return res


class Either(Fragment):
    def __init__(self, *children):
        Fragment.__init__(self)
        self.children = children

    def assemble(self):
        assembled = [c.assemble() for c in self.children]
        assert assembled
        assert len(assembled) > 1
        previous = Split(assembled[-2], assembled[-1])
        previous.tails = [assembled[-2], assembled[-1]]
        for node in assembled[:-2]:
            previous = Split(node, previous)
            previous.tails = [node, previous.out2]
        return previous


class TokenStream(list):

    def __init__(self, source, error):
        self += source.split() if isinstance(source, basestring) else source
        self.error = error

    def move(self):
        return self.pop(0) if len(self) else None

    def current(self):
        return self[0] if len(self) else None


def parse_long(tokens, options):
    raw, eq, value = tokens.move().partition('=')
    value = None if eq == value == '' else value
    opt = [o for o in options if o.long and o.long.startswith(raw)]
    if len(opt) < 1:
        if tokens.error is DocoptExit:
            raise tokens.error('%s is not recognized' % raw)
        else:
            o = Option(None, raw, (1 if eq == '=' else 0))
            options.append(o)
            return [o]
    if len(opt) > 1:
        raise tokens.error('%s is not a unique prefix: %s?' %
                         (raw, ', '.join('%s' % o.long for o in opt)))
    o = opt[0]
    opt = Option(o.short, o.long, o.argcount, o.value)
    if opt.argcount == 1:
        if value is None:
            if tokens.current() is None:
                raise tokens.error('%s requires argument' % opt.name)
            value = tokens.move()
    elif value is not None:
        raise tokens.error('%s must not have an argument' % opt.name)
    opt.value = value or True
    return [opt]


def parse_shorts(tokens, options):
    raw = tokens.move()[1:]
    parsed = []
    while raw != '':
        opt = [o for o in options
               if o.short and o.short.lstrip('-').startswith(raw[0])]
        if len(opt) > 1:
            raise tokens.error('-%s is specified ambiguously %d times' %
                              (raw[0], len(opt)))
        if len(opt) < 1:
            if tokens.error is DocoptExit:
                raise tokens.error('-%s is not recognized' % raw[0])
            else:
                o = Option('-' + raw[0], None)
                options.append(o)
                parsed.append(o)
                raw = raw[1:]
                continue
        o = opt[0]
        opt = Option(o.short, o.long, o.argcount, o.value)
        raw = raw[1:]
        if opt.argcount == 0:
            value = True
        else:
            if raw == '':
                if tokens.current() is None:
                    raise tokens.error('-%s requires argument' % opt.short[0])
                raw = tokens.move()
            value, raw = raw, ''
        opt.value = value
        parsed.append(opt)
    return parsed


def parse_pattern(source, options):
    tokens = TokenStream(re.sub(r'([\[\]\(\)\|]|\.\.\.)', r' \1 ', source),
                         DocoptLanguageError)
    result = parse_expr(tokens, options)
    if tokens.current() is not None:
        raise tokens.error('unexpected ending: %r' % ' '.join(tokens))
    return Required(*result)


def parse_expr(tokens, options):
    """expr ::= seq ( '|' seq )* ;"""
    seq = parse_seq(tokens, options)
    if tokens.current() != '|':
        return seq
    result = [Required(*seq)] if len(seq) > 1 else seq
    while tokens.current() == '|':
        tokens.move()
        seq = parse_seq(tokens, options)
        result += [Required(*seq)] if len(seq) > 1 else seq
    return [Either(*result)] if len(result) > 1 else result


def parse_seq(tokens, options):
    """seq ::= ( atom [ '...' ] )* ;"""
    result = []
    while tokens.current() not in [None, ']', ')', '|']:
        atom = parse_atom(tokens, options)
        if tokens.current() == '...':
            atom = [OneOrMore(*atom)]
            tokens.move()
        result += atom
    return result


def parse_atom(tokens, options):
    """atom ::= '(' expr ')' | '[' expr ']' | 'options'
             | long | shorts | argument | command ;
    """
    token = tokens.current()
    result = []
    if token == '(':
        tokens.move()
        result = [Required(*parse_expr(tokens, options))]
        if tokens.move() != ')':
            raise tokens.error("Unmatched '('")
        return result
    elif token == '[':
        tokens.move()
        result = [Optional(*parse_expr(tokens, options))]
        if tokens.move() != ']':
            raise tokens.error("Unmatched '['")
        return result
    elif token == 'options':
        tokens.move()
        return [AnyOptions()]
    elif token.startswith('--') and token != '--':
        return parse_long(tokens, options)
    elif token.startswith('-') and token not in ('-', '--'):
        return parse_shorts(tokens, options)
    elif token.startswith('<') and token.endswith('>') or token.isupper():
        return [Argument(tokens.move())]
    else:
        return [Command(tokens.move())]


def parse_args(source, options):
    tokens = TokenStream(source, DocoptExit)
    # options = copy(options)
    parsed = []
    while tokens.current() is not None:
        if tokens.current() == '--':
            return parsed + [Argument(None, v) for v in tokens]
        elif tokens.current().startswith('--'):
            parsed += parse_long(tokens, options)
        elif tokens.current().startswith('-') and tokens.current() != '-':
            parsed += parse_shorts(tokens, options)
        else:
            parsed.append(Argument(None, tokens.move()))
    return parsed


def parse_doc_options(doc):
    return [Option.parse('-' + s) for s in re.split('^ *-|\n *-', doc)[1:]]


def printable_usage(doc):
    usage_split = re.split(r'([Uu][Ss][Aa][Gg][Ee]:)', doc)
    if len(usage_split) < 3:
        raise DocoptLanguageError('"usage:" (case-insensitive) not found.')
    if len(usage_split) > 3:
        raise DocoptLanguageError('More than one "usage:" (case-insensitive).')
    return re.split(r'\n\s*\n', ''.join(usage_split[1:]))[0].strip()


def formal_usage(printable_usage):
    pu = printable_usage.split()[1:]  # split and drop "usage:"

    return '( ' + ' '.join(') | (' if s == pu[0] else s for s in pu[1:]) + ' )'


def extras(help, version, options, doc):
    if help and any((o.name in ('-h', '--help')) and o.value for o in options):
        print(doc.strip())
        exit()
    if version and any(o.name == '--version' and o.value for o in options):
        print(version)
        exit()


class Dict(dict):
    def __repr__(self):
        return '{%s}' % ',\n '.join('%r: %r' % i for i in sorted(self.items()))


def build_pattern(pattern):
    pattern = pattern.assemble()
    pattern.patch(End())
    return pattern


def traverse(root, args):
    next = []

    def append(next, node, args, collected):
        if isinstance(node, Split):
            append(next, node.out1, args, collected)
            append(next, node.out2, copy(args), copy(collected))
        else:
            next.append((node, args, collected))

    append(next, root, copy(args), [])
    current = next

    while current:
        next = []
        for node, args, collected in current:
            if isinstance(node, End) and not args:
                return collected
            next_node = node.next(args, collected)
            if next_node:
                append(next, next_node, args, collected)
        current = next

    return False


def docopt(doc, argv=sys.argv[1:], help=True, version=None):
    DocoptExit.usage = docopt.usage = usage = printable_usage(doc)
    pot_options = parse_doc_options(doc)
    root_node = parse_pattern(formal_usage(usage), options=pot_options)
    flat = root_node.flat  # Must be retrieved before pattern is built
    root_node.fix_list_arguments()
    root_node = build_pattern(root_node)
    argv = parse_args(argv, options=pot_options)
    extras(help, version, argv, doc)
    arguments = traverse(root_node, argv)
    if arguments is not False:
        options = [o for o in argv if type(o) is Option]
        pot_arguments = [a for a in flat
                         if type(a) in [Argument, Command]]
        return Dict((a.name, a.value) for a in
                    (pot_options + options + pot_arguments + arguments))
    raise DocoptExit()
