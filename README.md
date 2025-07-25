[![Python Package](https://github.com/SermetPekin/smartrun/actions/workflows/python-package.yml/badge.svg?2)](https://github.com/SermetPekin/smartrun/actions/workflows/python-package.yml)
[![PyPI](https://img.shields.io/pypi/v/smartrun)](https://img.shields.io/pypi/v/smartrun) ![PyPI Downloads](https://static.pepy.tech/badge/smartrun?2)![t](https://img.shields.io/badge/status-maintained-yellow.svg) [![](https://img.shields.io/github/license/SermetPekin/smartrun.svg)](https://github.com/SermetPekin/smartrun/blob/master/LICENSE.md) [![](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/) 


# smartrun
*Run any Python script in a clean, disposable virtual environment — automatically.*


# smartrun 🚀

**Run Python and Jupyter files with zero setup, zero pollution. Just run it.**

`smartrun` scans your script or notebook, detects the required third-party packages, creates (or reuses) an isolated environment, installs what’s missing — and runs your code.

✅ No more `ModuleNotFoundError`  
✅ No more cluttered global `site-packages`  
✅ Just clean, reproducible execution — every time

## Features

- 🧪 Supports both `.py` and `.ipynb` files
- 🔍 Automatically detects and resolves imports
- 🛠️ Uses `venv` or fast `uv` environments (if available)
- 📦 Installs only what's needed, only when needed
- 💡 Reuses environments smartly to save time

---
## Installation
```bash
pip install smartrun
```
> **Requires Python 3.10+**
---

## Usage

```bash

smartrun your_script.py

```

## Notebook

```bash

smartrun your_notebook.ipynb

```

## Example file that we want to run

```python
#some_file.py
import numpy as np
import pandas as pd
from rich import print 

df = pd.DataFrame(np.random.randn(5, 3), columns=list("ABC"))
print("Data:")
print(df, end="\n\n")
print("Column means:")
print(df.mean())

```

## Create an environment 
✅ Create an environment : Windows / macOS / Linux
```bash

smartrun env .venv

```
✅ Activate the environment:
Windows

```bash

 .venv\Scripts\activate

```
<details>
 <summary>🐧 macOS/Linux</summary> 
✅ Activate the environment: macOS/Linux

```bash

 source .venv/bin/activate

```

</details> 

<details>
  <summary>🪟 Windows</summary>
  ✅ Activate the environment:
Windows

```bash

.venv\Scripts\activate

```

</details> 

Tip: smartrun will automatically create and manage a virtual environment if none is activated — but you're always free to bring your own.

✅ Run the script: Windows / macOS / Linux
```bash

 smartrun some_file.py

```



✅ Run the jupyter file: Windows / macOS / Linux
```bash

 smartrun some_file.ipynb

```


### Data Science Examples

<details><summary>🌸 Iris dataset analysis</summary>



```python 
# iris.py
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

# Load data
df = sns.load_dataset('iris')

# Show first few rows and summary
print(df.head(), end="\n\n")
print(df.describe(), end="\n\n")

# Plot pairwise relationships
sns.pairplot(df, hue='species')
plt.savefig('iris_pairplot.png')

```

```bash

smartrun iris.py

```

</details> 

<details><summary>🐼 Titanic Dataset demo</summary>



```python

# titanic.ipynb
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Load dataset from GitHub
url = 'https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv'
df = pd.read_csv(url)

# Basic stats
print(df[['Survived', 'Pclass', 'Sex']].groupby(['Pclass', 'Sex']).mean())

# Plot survival by class
sns.countplot(data=df, x='Pclass', hue='Survived')
plt.title('Survival Count by Passenger Class')
plt.savefig('titanic_survival_by_class.png')
print("Saved plot → titanic_survival_by_class.png")


```

```bash

smartrun titanic.ipynb

```

</details> 


If the dependencies aren’t installed yet, `smartrun` will fetch them automatically.

## Why smartrun?

Because setup should never block you from running great code.
Whether you're experimenting, prototyping, or sharing — smartrun ensures your script runs smoothly, without dependency drama.


## Contributing


Contributions are welcome! 🧑‍💻

If you’ve got ideas, bug fixes, or improvements — feel free to open an issue or a pull request. Let’s make smartrun even smarter together.


## License

BSD 3‑Clause — see `LICENSE` for details.  

---


