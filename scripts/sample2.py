"""Generate a random DataFrame and calculate column means."""

import numpy as np
import pandas as pd
from rich import print

df = pd.DataFrame(np.random.randn(5, 3), columns=list("ABC"))
print("Data:")
print(df, end="\n\n")
print("Column means:")
print(df.mean())
