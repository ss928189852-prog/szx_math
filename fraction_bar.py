import matplotlib.pyplot as plt
import numpy as np

# Define fractions: 3/4 + 5/8 and 3/4 - 5/8
fraction1 = (3, 4)  # 3/4
fraction2 = (5, 8)  # 5/8

# Find Least Common Denominator (LCD)
lcd = np.lcm(fraction1[1], fraction2[1])  # LCD of 4 and 8 is 8

# Convert fractions to equivalent fractions with LCD
num1 = fraction1[0] * (lcd // fraction1[1])  # 3/4 → 6/8
num2 = fraction2[0] * (lcd // fraction2[1])  # 5/8 → 5/8

# Sum and Difference
sum_result = num1 + num2  # 6/8 + 5/8 = 11/8 (Improper Fraction)
diff_result = max(num1 - num2, 0)  # 6/8 - 5/8 = 1/8

# Create a figure
fig, axes = plt.subplots(2, 1, figsize=(6, 4))

# **Addition Visualization**
axes[0].barh(2, num1, left=0, color='blue', edgecolor='black', label=f"3/4 → {num1}/{lcd}")
axes[0].barh(1, num2, left=0, color='green', edgecolor='black', label=f"5/8 → {num2}/{lcd}")
axes[0].barh(0, sum_result, left=0, color='red', edgecolor='black', label=f"Sum: {sum_result}/{lcd}")
axes[0].set_xlim(0, lcd*2)
axes[0].set_yticks([2, 1, 0])
#axes[0].set_yticklabels(["3/4", "5/8", "Result"])
axes[0].set_yticklabels([r"$\frac{3}{4}$", r"$\frac{5}{8}$", "Result"])

axes[0].set_title("Fraction Addition")
axes[0].legend()

# **Subtraction Visualization**
axes[1].barh(2, num1, left=0, color='blue', edgecolor='black', label=f"3/4 → {num1}/{lcd}")
axes[1].barh(1, num2, left=0, color='green', edgecolor='black', label=f"5/8 → {num2}/{lcd}")
axes[1].barh(0, diff_result, left=0, color='orange', edgecolor='black', label=f"Difference: {diff_result}/{lcd}")
axes[1].set_xlim(0, lcd)
axes[1].set_yticks([2, 1, 0])
axes[1].set_yticklabels(["3/4", "5/8", "Result"])
axes[1].set_title("Fraction Subtraction")

plt.tight_layout()
plt.show()
