import matplotlib.pyplot as plt
import matplotlib.patches as patches
from fractions import Fraction

def draw_fraction_bar(ax, fraction, original_str, y_offset, color):
    # Extract numerator and denominator from the original string (not simplified)
    num_str, denom_str = original_str.split('/')
    num_blocks = int(num_str)
    denom_blocks = int(denom_str)
    block_size = 1 / denom_blocks

    unit_frac_latex = rf'$\dfrac{{1}}{{{denom_str}}}$'
    full_frac_latex = rf'$\dfrac{{{num_str}}}{{{denom_str}}}$'

    # Draw unit blocks with LaTeX labels
    for i in range(num_blocks):
        rect = patches.Rectangle(
            (i * block_size, y_offset),
            block_size,
            0.4,
            edgecolor='black',
            facecolor=color
        )
        ax.add_patch(rect)
        ax.text(
            i * block_size + block_size / 2,
            y_offset + 0.2,
            unit_frac_latex,
            ha='center',
            va='center',
            fontsize=14
        )

    # Draw the full unsimplified fraction on the left
    ax.text(-0.2, y_offset + 0.2, full_frac_latex, va='center', fontsize=14)

# === Get user input for three fractions ===
fraction_str1 = input("Enter first fraction (e.g., 5/8): ")
fraction_str2 = input("Enter second fraction (e.g., 3/4): ")
fraction_str3 = input("Enter third fraction (e.g., 2/3): ")

# Convert to Fraction objects for layout (but display original values)
frac1 = Fraction(fraction_str1)
frac2 = Fraction(fraction_str2)
frac3 = Fraction(fraction_str3)

# Determine widest bar to set x-axis limit
max_length = max(float(frac1), float(frac2), float(frac3))

# === Create plot ===
fig, ax = plt.subplots(figsize=(9, 4))
ax.set_xlim(-0.5, max_length + 1)
ax.set_ylim(0, 3)
ax.axis('off')

# Draw three bars using original unsimplified fraction strings
draw_fraction_bar(ax, frac1, original_str=fraction_str1, y_offset=2.0, color='lightcoral')
draw_fraction_bar(ax, frac2, original_str=fraction_str2, y_offset=1.2, color='lightblue')
draw_fraction_bar(ax, frac3, original_str=fraction_str3, y_offset=0.4, color='palegreen')

plt.title("Visual Representation of Three Fractions (No Simplification)", fontsize=14)
plt.tight_layout()
plt.show()
