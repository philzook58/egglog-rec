import re
import glob
import os
import sys
import ast


def parse_term(term):
    if "(" not in term:
        return term.strip()
    name, args = term.split("(", 1)
    args = args.split(",")
    return (name, list(map(parse_term, args)))


# parse terms using python's parser. Ooh I'm a naughty boy.
# Edit: This was a bad idea.
def parse_term(term):
    mod = ast.parse(term.strip())

    def simple(expr):
        if isinstance(expr, ast.Name):
            return expr.id
        elif isinstance(expr, ast.Call):
            return expr.func.id, list(map(simple, expr.args))
        elif isinstance(expr, ast.UnaryOp):
            assert isinstance(expr.op, ast.Not)
            return "not", simple(expr.operand)
        # elif isinstance(expr, ast.BinaryOp):
            # if isinstance(expr.op, ast.Or):
            # return "not", simple(expr.operand)
        else:
            print(ast.dump(expr))
            print(type(expr))
            assert False
    return simple(mod.body[0].value)


def parse_rule(rule):
    print(rule)
    # conditional rules suck
    conds = []
    if "if " in rule:
        # conditions are of the form "if a = b AND-if p <> q AND-if foo(X) = d"
        rule, *whens = rule.split("if ")
        print("this when: ", whens)
        for when in whens:
            when = when.replace("AND-", "")
            if "=" in when:
                w1, w2 = when.split("=")   # re.split('=|->', when)  #
                w1 = parse_term(w1)
                w2 = parse_term(w2)
                when = ("=", w1, w2)
            elif "<>" in when:
                w1, w2 = when.split("<>")   # re.split('=|->', when)  #
                print(w2)
                w1 = parse_term(w1)
                w2 = parse_term(w2)
                when = ("!=", w1, w2)
            else:
                print(when)
                assert False
            conds.append(when)
    # print(rule.split("->"))
    lhs, rhs = rule.split("->")
    return parse_term(lhs), parse_term(rhs), conds


def parse_decl(decl):
    name, sort = decl.split(":")
    name = name.strip()
    ins, out = sort.split("->")
    ins = ins.split()
    out = out.strip()
    return name, ins, out


def parse_recspec(l):
    l = l.replace("REC-SPEC", "")
    if ":" in l:
        name, includes = l.split(":")
        includes = includes.split()
        return name.strip(), includes
    else:
        return l.strip(), []


def parse_file(name):
    data = {"SORTS": [], "CONS": [], "OPNS": [],
            "VARS": [], "RULES": [], "EVAL": []}
    field = None
    with open(name, 'r') as f:
        for line in f.readlines():
            line = line.split("#")[0]  # remove comments
            line = line.replace("'", "tick")  # python can't parse ticks
            line = line.replace("\"", "quote")
            # python keywords are annoying. Maybe my cute trick is dumb
            line = line.replace("or", "OR")
            line = line.replace("and", "AND")
            line = line.replace("not", "mynot")
            line = line.replace("true", "mytrue")
            line = line.replace("false", "myfalse")
            line = line.replace("union", "myunion")
            line = line.replace(";", ",")  # ; is altneraitve for ,?
            if line.isspace() or len(line) == 0:
                continue
            if "REC-SPEC" in line:
                data["REC-SPEC"] = parse_recspec(line)
                print("recspec", data["REC-SPEC"])
            elif "SORTS" in line:
                field = "SORTS"
            elif "CONS" in line:
                field = "CONS"
            elif "OPNS" in line:
                field = "OPNS"
            elif "VARS" in line:
                field = "VARS"
            elif "RULES" in line:
                field = "RULES"
            elif "EVAL" in line:
                field = "EVAL"
            elif "META" in line:
                field = "META"
            elif "END-SPEC" in line:
                field = "END-SPEC"

            elif field == "SORTS":
                data["SORTS"] += line.split()
            elif field == "CONS":
                data["CONS"].append(parse_decl(line))
            elif field == "OPNS":
                data["OPNS"].append(parse_decl(line))
            elif field == "VARS":
                data["VARS"].append(line.strip())
            elif field == "RULES":
                data["RULES"].append(parse_rule(line))
            elif field == "EVAL":
                data["EVAL"].append(parse_term(line))
    return data


def pp_term(term):
    if isinstance(term, str):
        return term
    args = " ".join(map(pp_term, term[1]))
    return f"({term[0]} {args})"


def pp_rule(lhs, rhs, conds):
    if len(conds) == 0:
        when = ""
    else:
        conds = " ".join(
            [f"({op} {pp_term(w1)} {pp_term(w2)})" for op, w1, w2 in conds])
        when = f":when ({conds})"
    return f"(rewrite {pp_term(lhs)} {pp_term(rhs)} {when})"


def pp_decl(decl):
    name, ins, out = decl
    ins = " ".join(ins)
    return f"(function {name} ({ins}) {out})"


def pp_eval(t):
    return f"""\
(push)
(define test {pp_term(t)})
(run 10000)
(pop)
"""


def pp_includes(includes):
    return "\n".join([f"(include \"egglog/lib/{name.lower()}.egg\")" for name in includes])


def pp_data(data):
    out = []
    # print(len(data["REC-SPEC"]))
    name, includes = data["REC-SPEC"]
    out.append(pp_includes(includes))
    for sort in data["SORTS"]:
        out.append(f"(datatype {sort})")
    for decl in data["CONS"]:
        out.append(pp_decl(decl))
    for decl in data["OPNS"]:
        out.append(pp_decl(decl))
    for lhs, rhs, when in data["RULES"]:
        out.append(pp_rule(lhs, rhs, when))
    for t in data["EVAL"]:
        out.append(pp_eval(t))
    return out


# Using os.walk()
for name in glob.glob('orig/**/*.rec', recursive=True):
    print(name)
    if "natlist" in name or "hanoi" in name:  # too many parens.
        continue
    data = parse_file(name)
    eggname = name.replace("orig", "egglog")
    eggname = eggname.replace(".rec", ".egg")
    print(eggname)
    with open(eggname, "w") as f:
        f.write("\n".join(pp_data(data)))

        """
for dirpath, dirs, files in os.walk('orig/lib'):
    for filename in files:
        fname = os.path.join(dirpath, filename)
        data = parse_file(fname)
        with open(os.path.join("egglog/lib", filename)) as f:
        for line in pp_data(data):
            """
