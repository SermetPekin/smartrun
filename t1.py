from smartrun.package_name import PackageName, split_package_name


def t_split_package_name():
    # Test examples
    test_cases = [
        "pandas",
        "pandas==1.0",
        "pandas<=1.0.1",
        "pandas>=1.5.0",
        "numpy~=1.20.0",
        "requests!=2.28.0",
        "django<4.0",
        "flask>2.0",
        "python>3.8",
    ]
    for case in test_cases:
        p = PackageName(case)
        print(p)
        # name, version = split_package_name(case)
        # print(f"{case:15} -> name: '{name}', version: '{version}'")


t_split_package_name()
