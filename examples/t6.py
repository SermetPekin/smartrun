from dataclasses import dataclass


@dataclass
class Options:
    venv_opt: bool = False
    venv: str = "x"

    def __str__(self):
        t = f"""
    venv : {self.venv}
"""
        return t


def change(opts):
    opts.venv = "asdfasdf"


o = Options()
print(o)
change(o)
print(o)
