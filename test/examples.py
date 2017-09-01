"""Examples to test the parser and unparser."""

import typing as t


def prepare_examples(templates: t.Mapping[str, str]) -> t.Dict[str, str]:
    """Insert comments into given code examples according to several patterns."""
    zeroth_comment = 'zero'
    comments = ('one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten')
    examples = {}
    for template_name, template in templates.items():
        template_lines = template.splitlines(keepends=False)
        for zeroth in (False, True):
            for eol in (False, True):
                example_lines = []
                if zeroth:
                    example_lines.append('# ' + zeroth_comment)
                for template_line, comment in zip(template_lines, comments):
                    if eol:
                        example_lines.append(template_line + '  # ' + comment)
                    else:
                        example_lines += [template_line, '# ' + comment]
                name = \
                    template_name + ' with' + (' eol' if eol else '') + ' comments' \
                    + (' and starting comment' if zeroth else '')
                example = '\n'.join(example_lines)
                examples[name] = example
    return examples


TEMPLATES = {
    'empty': """""",
    '1 assignment': """a = 1""",
    '3 assignments': """a = 1
b = 2
c = 3""",
    'inline empty list': """[]""",
    'empty list': """[
    ]""",
    'inline 1-elem list': """[1]""",
    'inline 3-elem list': """[1, 2, 3]""",
    '3-elem list': """[
    1,
    2,
    3
    ]""",
    'inline 1-elem set': """{1}""",
    '1-elem set': """{
    1
    }""",
    'inline 3-elem set': """{1, 2, 3}""",
    '3-elem set': """{
    1,
    2,
    3
    }""",
    'inline empty dict': """{}""",
    'empty dict': """{
    }""",
    'inline dict': """{'a': 1, 'b': 2, 'c': 3}""",
    'dict': """{
    'a': 1,
    'b': 2,
    'c': 3
    }""",
    'inline call': """call(1, 2, 3)""",
    'call': """call(
    1,
    2,
    3
    )""",
    'inline call with kwargs': """call(1, 2, 3, a=1, b=2, c=3)""",
    'call with kwargs': """call(
    1,
    2,
    3,
    a=1,
    b=2,
    c=3
    )""",
    'inline function definition': """def fun(): pass""",
    'function definition': """def fun(
        ):
    pass"""}

EXAMPLES = prepare_examples(TEMPLATES)

FAILING_TEMPLATES = {
    'function definition with args': """def fun(
        a,
        b
        ):
    pass""",
    'function definition with kwargs': """def fun(
        a,
        b,
        c=3,
        d=4
        ):
    pass""",
    'function definition with star-args': """def fun(
        a,
        b,
        c=3,
        d=4,
        *args
        ):
    pass""",
    'function definition with star-kargs': """def fun(
        a,
        b,
        *args,
        c=3,
        d=4,
        **kwargs
        ):
    pass"""}

FAILING_EXAMPLES = prepare_examples(FAILING_TEMPLATES)
