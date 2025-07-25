from smartrun.envc.envc2 import EnvComplete

e = EnvComplete()
p = e.get_current_env()
print(p)
print(e().get())
