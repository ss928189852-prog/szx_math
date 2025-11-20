import matplotlib.pyplot as plt
import matplotlib.patches as patches
from fractions import Fraction
from math import gcd
from functools import reduce

# === LCM helpers ===
def lcm(a, b):
    return a * b // gcd(a, b)

def lcm_multiple(numbers):
    return reduce(lcm, numbers)

# === Draw one fraction bar ===
def draw_fraction_bar(ax, total_value, numerator, denominator, unit_denominator,
                      y_offset, x_offset, color, label_latex=None, show_label=True):
    total_width = float(total_value)
    #total_width = numerator / denominator
    block_width = total_width / unit_denominator
    num_blocks = numerator * (unit_denominator // denominator)
    unit_frac_latex = rf'$\dfrac{{1}}{{{unit_denominator}}}$'

    # Draw blocks
    for i in range(num_blocks):
        rect = patches.Rectangle(
            (x_offset + i * block_width, y_offset),
            block_width,
            0.4,
            edgecolor='black',
            facecolor=color
        )
        ax.add_patch(rect)
        ax.text(
            x_offset + i * block_width + block_width / 2,
            y_offset + 0.2,
            unit_frac_latex,
            ha='center',
            va='center',
            fontsize=9  # smaller unit label
        )

    # Draw full fraction label
    if show_label and label_latex:
        ax.text(x_offset - 0.15, y_offset + 0.2, label_latex, va='center', fontsize=11)

# === User input for 3 fractions ===
fraction_strs = [input(f"Enter fraction {i+1} (e.g., 3/6): ") for i in range(3)]

# === Parse original numerators/denominators and create LaTeX labels ===
fractions = [Fraction(f_str) for f_str in fraction_strs]
numerators = [int(f_str.split('/')[0]) for f_str in fraction_strs]
denominators = [int(f_str.split('/')[1]) for f_str in fraction_strs]
latex_labels_original = [rf'$\dfrac{{{n}}}{{{d}}}$' for n, d in zip(numerators, denominators)]

# === Compute LCM and equivalent numerators ===
common_denom = lcm_multiple(denominators)
equiv_numerators = [n * (common_denom // d) for n, d in zip(numerators, denominators)]
latex_labels_equiv = [rf'$\dfrac{{{n}}}{{{common_denom}}}$' for n in equiv_numerators]

# === Color palette (reused for both sides) ===
colors = ['lightcoral', 'lightblue', 'palegreen']

# === Plot setup ===
max_width = max(float(f) for f in fractions)
fig, ax = plt.subplots(figsize=(12, 4))
ax.set_xlim(-0.5, max_width * 2 + 1)
ax.set_ylim(0, 3)
ax.axis('off')

# === Draw original bars (left) ===
draw_fraction_bar(ax, fractions[0], numerators[0], denominators[0], denominators[0],
                  y_offset=2.0, x_offset=0.0, color=colors[0], label_latex=latex_labels_original[0])
draw_fraction_bar(ax, fractions[1], numerators[1], denominators[1], denominators[1],
                  y_offset=1.2, x_offset=0.0, color=colors[1], label_latex=latex_labels_original[1])
draw_fraction_bar(ax, fractions[2], numerators[2], denominators[2], denominators[2],
                  y_offset=0.4, x_offset=0.0, color=colors[2], label_latex=latex_labels_original[2])

# === Draw equivalent bars (right) ===
offset_right = max_width + 0.8
draw_fraction_bar(ax, fractions[0], numerators[0], denominators[0], common_denom,
                  y_offset=2.0, x_offset=offset_right, color=colors[0], label_latex=latex_labels_equiv[0])
draw_fraction_bar(ax, fractions[1], numerators[1], denominators[1], common_denom,
                  y_offset=1.2, x_offset=offset_right, color=colors[1], label_latex=latex_labels_equiv[1])
draw_fraction_bar(ax, fractions[2], numerators[2], denominators[2], common_denom,
                  y_offset=0.4, x_offset=offset_right, color=colors[2], label_latex=latex_labels_equiv[2])

# === Section headers ===
ax.text(max_width / 2 - 0.2, 2.6, "Original Fractions", ha='center', fontsize=13, fontweight='bold')
ax.text(offset_right + max_width / 2 - 0.2, 2.6,
        f"Converted Fractions with a Common Denominator",
        ha='center', fontsize=13, fontweight='bold')

plt.tight_layout()
plt.show()
