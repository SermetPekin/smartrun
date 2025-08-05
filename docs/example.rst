SmartRun
========

Example: Titanic Survival Analysis
----------------------------------

This example demonstrates how **SmartRun** automatically installs required packages from inline comments in standard Python or Jupyter files.

SmartRun parses the following comment for dependencies:

.. code-block:: python

   # smartrun: pandas>=2.0 seaborn>=0.11 matplotlib>=3.5

Source Code
~~~~~~~~~~~

.. code-block:: python

   # smartrun: pandas>=2.0 seaborn>=0.11 matplotlib>=3.5

   import pandas as pd
   import seaborn as sns
   import matplotlib.pyplot as plt

   # Load dataset from GitHub
   url = "https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv"
   df = pd.read_csv(url)

   # Basic stats
   print(df[["Survived", "Pclass", "Sex"]].groupby(["Pclass", "Sex"]).mean())

   # Plot survival by class
   sns.countplot(data=df, x="Pclass", hue="Survived")
   plt.title("Survival Count by Passenger Class")
   output_path = "titanic_survival_by_class.png"
   plt.savefig(output_path)

   print(f"✅ Saved plot → {output_path}")

How to Run
~~~~~~~~~~

Use SmartRun with any `.py` or `.ipynb` file containing inline requirements:

.. code-block:: bash

   smartrun titanic.py

Or generate HTML output from a notebook:

.. code-block:: bash

   smartrun --html analysis.ipynb

What It Does
~~~~~~~~~~~~

- ✅ Installs `pandas`, `seaborn`, and `matplotlib` automatically (if missing)
- 📊 Prints survival statistics by passenger class and gender
- 🖼️ Saves a plot as ``titanic_survival_by_class.png``

Tip: You can also exclude or override packages with `--exc` or `--inc`.

.. code-block:: bash

   smartrun titanic.py --exc seaborn
   smartrun titanic.py --inc openpyxl
