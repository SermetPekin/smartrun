# iris_analysis.py
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
