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
