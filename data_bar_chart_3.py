import matplotlib.pyplot as plt
import matplotlib.patches as patches
from fractions import Fraction
from math import gcd
from functools import reduce

from sympy.codegen.ast import integer


# === LCM helpers ===
def lcm(a, b):
    return a * b // gcd(a, b)


def lcm_multiple(numbers):
    return reduce(lcm, numbers)



def draw_fraction_bar(ax, numerator, denominator, unit_denominator,
                      y_offset, x_offset, color, label_latex=None, show_label=True):
    total_width = float(numerator/denominator)
    print(total_width)
    # block_width = total_width / unit_denominator
    block_width = 1 / unit_denominator
    num_blocks = numerator * (unit_denominator // denominator)
    # unit_frac_latex = rf'$\dfrac{{1}}{{{unit_denominator}}}$'

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
        # ax.text(
        #     x_offset + i * block_width + block_width / 2,
        #     y_offset + 0.2,
        #     unit_frac_latex,
        #     ha='center',
        #     va='center',
        #     fontsize=9  # smaller unit label
        # )

    # Draw full fraction label
    if show_label and label_latex:
        ax.text(x_offset - 0.7, y_offset + 0.2, label_latex, va='center', fontsize=11)

# === Draw one fraction bar with integer part handling ===
def draw_integer_bar(ax, whole_num,
                      y_offset, x_offset, color, label_latex=None, show_label=True):
    # 绘制整数部分
    for i in range(whole_num):
        rect = patches.Rectangle(
            (x_offset + i, y_offset),
            1.0,
            0.4,
            edgecolor='black',
            facecolor=color,
            alpha=0.3  # 半透明显示整数部分
        )
        ax.add_patch(rect)
        ax.text(
            x_offset + i + 0.5,
            y_offset + 0.2,
            '1',
            ha='center',
            va='center',
            fontsize=10
        )
    # 绘制分数标签
    if show_label and label_latex:
        ax.text(x_offset - 0.15, y_offset + 0.2, label_latex, va='center', fontsize=11)

def data_fig_original(data):
    plt.rcParams['font.family'] = 'Microsoft YaHei'
    # === Parse original numerators/denominators and create LaTeX labels ===
    fractions = [Fraction(item["numerator"], item["denominator"]) for item in data]
    numerators = [item["numerator"] for item in data]
    denominators = [item["denominator"] for item in data]


    # 为假分数创建带整数部分的LaTeX标签
    integer_num = []
    latex_labels_original = []
    latex_integer_labels_original = []
    for i in range(len(numerators)):
    # for n, d in zip(numerators, denominators):
    #     whole = n // d
    #     remainder = n % d
        n = numerators[i]
        d = denominators[i]
        whole = n // d
        remainder = n % d
        if whole == 0:
            integer_num.append(0)
            latex_integer_labels_original.append('0')
            latex_labels_original.append(rf'$\dfrac{{{n}}}{{{d}}}$（{n}個$\dfrac{{{1}}}{{{d}}}$）')
        elif remainder == 0:
            integer_num.append(whole)
            latex_integer_labels_original.append(rf'{whole}')
            latex_labels_original.append('0')
            numerators[i] = 0
            f_str = rf'0/{d}'
            fractions[i] = Fraction(f_str)
        else:
            integer_num.append(whole)
            latex_integer_labels_original.append(rf'{whole}')
            latex_labels_original.append(rf'$\dfrac{{{remainder}}}{{{d}}}$（{remainder}個$\dfrac{{{1}}}{{{d}}}$）')
            numerators[i] -= whole * d
            f_str = rf'{numerators[i]}/{d}'
            fractions[i] = Fraction(f_str)

    # === Compute LCM and equivalent numerators ===
    # common_denom = lcm_multiple(denominators)
    # equiv_numerators = [n * (common_denom // d) for n, d in zip(numerators, denominators)]
    # latex_labels_equiv = [rf'$\dfrac{{{n}}}{{{common_denom}}}$' for n in equiv_numerators]

    # === Color palette ===
    colors = ['lightcoral', 'lightblue', 'palegreen']

    # === Plot setup ===
    max_width_integer = max(int(f) for f in latex_integer_labels_original)
    max_width_fraction = max(float(f) for f in fractions)
    max_width = max_width_integer + max_width_fraction
    fig, ax = plt.subplots(figsize=(14, 4))  # 增加图形宽度以容纳整数部分
    
    # 添加主标题
    fig.suptitle('題目分數示意圖', fontsize=16, fontweight='bold', color='#2E86AB')
    
    ax.set_xlim(-0.5, max_width * 2 + 3)  # 扩展x轴范围
    ax.set_ylim(0, 3)
    ax.axis('off')


    has_non_zero = False
    for label in latex_integer_labels_original:
        if label != '0':
            has_non_zero = True
            break
    if has_non_zero:
        # print(latex_integer_labels_original)
        # draw_integer_bar(ax, integer_num[0], y_offset=2.0, x_offset=0.0, color=colors[0], label_latex=latex_integer_labels_original[0])
        # draw_integer_bar(ax, integer_num[1], y_offset=1.2, x_offset=0.0, color=colors[1], label_latex=latex_integer_labels_original[1])
        # draw_integer_bar(ax, integer_num[2], y_offset=0.4, x_offset=0.0, color=colors[2], label_latex=latex_integer_labels_original[2])
        for i in range(len(fractions)):
            draw_integer_bar(ax, integer_num[i], y_offset=2.0 - 0.8 * i, x_offset=0.0,
                             color=colors[i], label_latex=latex_integer_labels_original[i])

        # === Draw original bars (left) ===
        offset_right = max_width_integer + 2.0

        # draw_fraction_bar(ax, numerators[0], denominators[0], denominators[0],
        #                   y_offset=2.0, x_offset=offset_right, color=colors[0], label_latex=latex_labels_original[0])
        # draw_fraction_bar(ax, numerators[1], denominators[1], denominators[1],
        #                   y_offset=1.2, x_offset=offset_right, color=colors[1], label_latex=latex_labels_original[1])
        # draw_fraction_bar(ax, numerators[2], denominators[2], denominators[2],
        #                   y_offset=0.4, x_offset=offset_right, color=colors[2], label_latex=latex_labels_original[2])
        for i in range(len(fractions)):
            draw_fraction_bar(ax, numerators[i], denominators[i], denominators[i], y_offset=2.0 - 0.8 * i, x_offset=offset_right,
                             color=colors[i], label_latex=latex_labels_original[i])


        # === Section headers ===
        ax.text(max_width / 2, 2.6, "整數部分", ha='center', fontsize=13, fontweight='bold')
        ax.text(offset_right + max_width / 2, 2.6,"分數部分", ha='center', fontsize=13, fontweight='bold')
        
        # 动态设置底部提示的位置
        # 获取当前y轴的最大值和图表高度
        y_max = ax.get_ylim()[1]
        fig_height_inches = fig.get_size_inches()[1]
        dpi = fig.dpi
        bottom_padding_points = 20  # 底部padding，单位为点(points)
        bottom_padding_inches = bottom_padding_points / dpi
        
        # 计算底部提示位置
        text_y_position = -bottom_padding_inches/fig_height_inches * y_max
        
        # 添加底部提示
        fig.text(0.5, text_y_position, '點擊右側按鈕可全屏查看圖片或退出全屏', 
                 ha='center', fontsize=10, color='#666666', style='italic', fontweight='bold')

    else:
        # === Draw original bars (left) ===
        # draw_fraction_bar(ax, numerators[0], denominators[0], denominators[0],
        #                   y_offset=2.0, x_offset=0.0, color=colors[0], label_latex=latex_labels_original[0])
        # draw_fraction_bar(ax, numerators[1], denominators[1], denominators[1],
        #                   y_offset=1.2, x_offset=0.0, color=colors[1], label_latex=latex_labels_original[1])
        # draw_fraction_bar(ax, numerators[2], denominators[2], denominators[2],
        #                   y_offset=0.4, x_offset=0.0, color=colors[2], label_latex=latex_labels_original[2])
        for i in range(len(fractions)):
            draw_fraction_bar(ax, numerators[i], denominators[i], denominators[i], y_offset=2.0 - 0.8 * i, x_offset=0.0,
                             color=colors[i], label_latex=latex_labels_original[i])


        # === Section headers ===
        ax.text(max_width / 2, 2.6, "分數部分", ha='center', fontsize=13, fontweight='bold')
        
        # 动态设置底部提示的位置
        # 获取当前y轴的最大值和图表高度
        y_max = ax.get_ylim()[1]
        fig_height_inches = fig.get_size_inches()[1]
        dpi = fig.dpi
        bottom_padding_points = 20  # 底部padding，单位为点(points)
        bottom_padding_inches = bottom_padding_points / dpi
        
        # 计算底部提示位置
        text_y_position = -bottom_padding_inches/fig_height_inches * y_max
        
        # 添加底部提示
        fig.text(0.5, text_y_position, '點擊右側按鈕可全屏查看圖片或退出全屏', 
                 ha='center', fontsize=10, color='#666666', style='italic', fontweight='bold')
        
    return fig



def data_fig_final(data, option_data):
    plt.rcParams['font.family'] = 'Microsoft YaHei'
    # === Parse original numerators/denominators and create LaTeX labels ===
    fractions = [Fraction(item["numerator"], item["denominator"]) for item in data]
    numerators = [item["numerator"] for item in data]
    denominators = [item["denominator"] for item in data]
    fractions_option = [Fraction(option_data["numerator"], option_data["denominator"])]
    numerators_option = option_data["numerator"]
    denominators_option = option_data["denominator"]
    whole_option = numerators_option // denominators_option
    remainder_option = numerators_option % denominators_option




    # 为假分数创建带整数部分的LaTeX标签
    integer_num = []
    latex_labels_original = []
    latex_integer_labels_original = []
    for i in range(len(numerators)):
    # for n, d in zip(numerators, denominators):
    #     whole = n // d
    #     remainder = n % d
        n = numerators[i]
        d = denominators[i]
        whole = n // d
        remainder = n % d
        if whole == 0:
            integer_num.append(0)
            latex_integer_labels_original.append('0')
            latex_labels_original.append(rf'$\dfrac{{{n}}}{{{d}}}$（{n}個$\dfrac{{{1}}}{{{d}}}$）')
        elif remainder == 0:
            integer_num.append(whole)
            latex_integer_labels_original.append(rf'{whole}')
            latex_labels_original.append('0')
            numerators[i] = 0
            f_str = rf'0/{d}'
            fractions[i] = Fraction(f_str)
        else:
            integer_num.append(whole)
            latex_integer_labels_original.append(rf'{whole}')
            latex_labels_original.append(rf'$\dfrac{{{remainder}}}{{{d}}}$（{remainder}個$\dfrac{{{1}}}{{{d}}}$）')
            numerators[i] -= whole * d
            f_str = rf'{numerators[i]}/{d}'
            fractions[i] = Fraction(f_str)

    print(latex_integer_labels_original)
    print(latex_labels_original)
    print(fractions)



    # === Compute LCM and equivalent numerators ===
    common_denom = lcm_multiple(denominators)
    equiv_numerators = [n * (common_denom // d) for n, d in zip(numerators, denominators)]
    latex_labels_equiv = [rf'$\dfrac{{{n}}}{{{common_denom}}}$（{n}個$\dfrac{{{1}}}{{{common_denom}}}$）' for n in equiv_numerators]

    # === Color palette ===
    colors = ['lightcoral', 'lightblue', 'palegreen']

    # === Plot setup ===
    max_width_integer = max(int(f) for f in latex_integer_labels_original)
    max_width_fraction = max(float(f) for f in fractions)
    max_width = max_width_integer + max_width_fraction
    fig, ax = plt.subplots(figsize=(14, 4))  # 增加图形宽度以容纳整数部分
    
    # 添加主标题
    fig.suptitle('答案分數示意圖', fontsize=16, fontweight='bold', color='#2E86AB')
    
    ax.set_xlim(-0.5, max_width * 2 + 3)  # 扩展x轴范围
    ax.set_ylim(-3, 3)
    ax.axis('off')
    if numerators_option == 0:
        draw_integer_bar(ax, numerators_option, y_offset=-1.5, x_offset=0.0, color=colors[0],
                         label_latex='0')
        ax.text(0.5, -0.8, "整數部分", ha='center', fontsize=13, fontweight='bold')
        ax.text(1.5, -0.3, "正確答案", ha='center', fontsize=13, fontweight='bold')
    elif whole_option == 0:
        print(rf"正确答案分子是{numerators_option},分子是{denominators_option}")
        draw_fraction_bar(ax, numerators_option, denominators_option, denominators_option, y_offset=-1.5, x_offset=0.0, color=colors[0],
                          label_latex=rf'$\dfrac{{{numerators_option}}}{{{denominators_option}}}$（{numerators_option}個$\dfrac{{{1}}}{{{denominators_option}}}$）')
        ax.text(0.5, -0.8, "分數部分", ha='center', fontsize=13, fontweight='bold')
        ax.text(1.5, -0.3, "正確答案", ha='center', fontsize=13, fontweight='bold')
    elif remainder_option ==0:
        draw_integer_bar(ax, numerators_option, y_offset=-1.5, x_offset=0.0, color=colors[0],label_latex= numerators_option)
        ax.text(0.5, -0.8, "整數部分", ha='center', fontsize=13, fontweight='bold')
        ax.text(1.5, -0.3, "正確答案", ha='center', fontsize=13, fontweight='bold')
    else:
        draw_integer_bar(ax, whole_option, y_offset=-1.5, x_offset=0.0, color=colors[0],
                         label_latex=whole_option)
        draw_fraction_bar(ax, remainder_option, denominators_option, denominators_option, y_offset=-1.5, x_offset=whole_option + 2.0, color=colors[0],
                          label_latex=rf'$\dfrac{{{remainder_option}}}{{{denominators_option}}}$（{remainder_option}個$\dfrac{{{1}}}{{{denominators_option}}}$）')
        ax.text(whole_option + 2.0, -0.8, "分數部分", ha='center', fontsize=13, fontweight='bold')
        ax.text(0.5, -0.8, "整數部分", ha='center', fontsize=13, fontweight='bold')
        ax.text(1.5, -0.3, "正確答案", ha='center', fontsize=13, fontweight='bold')

    # 在正确答案图绘制完成后，添加底部提示
    # 动态设置底部提示的位置
    # 获取当前y轴的最大值和图表高度
    y_max = ax.get_ylim()[1]
    fig_height_inches = fig.get_size_inches()[1]
    dpi = fig.dpi
    bottom_padding_points = 20  # 底部padding，单位为点(points)
    bottom_padding_inches = bottom_padding_points / dpi
    
    # 计算底部提示位置
    text_y_position = -bottom_padding_inches/fig_height_inches * y_max
    
    # 添加底部提示
    fig.text(0.5, text_y_position, '點擊右側按鈕可全屏查看圖片或退出全屏', 
             ha='center', fontsize=10, color='#666666', style='italic', fontweight='bold')

    has_non_zero = False
    for label in latex_integer_labels_original:
        if label != '0':
            has_non_zero = True
            break
    if has_non_zero:
        # print(latex_integer_labels_original)
        # draw_integer_bar(ax, integer_num[0], y_offset=2.0, x_offset=0.0, color=colors[0], label_latex=latex_integer_labels_original[0])
        # draw_integer_bar(ax, integer_num[1], y_offset=1.2, x_offset=0.0, color=colors[1], label_latex=latex_integer_labels_original[1])
        # draw_integer_bar(ax, integer_num[2], y_offset=0.4, x_offset=0.0, color=colors[2], label_latex=latex_integer_labels_original[2])
        for i in range(len(fractions)):
            draw_integer_bar(ax, integer_num[i], y_offset=2.0 - 0.8 * i, x_offset=0.0,
                             color=colors[i], label_latex=latex_integer_labels_original[i])



        # === Draw original bars (left) ===
        offset_right_1 = max_width_integer + 2.0

        # draw_fraction_bar(ax, numerators[0], denominators[0], denominators[0],
        #                   y_offset=2.0, x_offset=offset_right_1, color=colors[0], label_latex=latex_labels_original[0])
        # draw_fraction_bar(ax, numerators[1], denominators[1], denominators[1],
        #                   y_offset=1.2, x_offset=offset_right_1, color=colors[1], label_latex=latex_labels_original[1])
        # draw_fraction_bar(ax, numerators[2], denominators[2], denominators[2],
        #                   y_offset=0.4, x_offset=offset_right_1, color=colors[2], label_latex=latex_labels_original[2])

        for i in range(len(fractions)):
            draw_fraction_bar(ax, numerators[i], denominators[i], denominators[i],
                              y_offset=2.0 - 0.8 * i, x_offset=offset_right_1,
                              color=colors[i], label_latex=latex_labels_original[i])

        # === Draw equivalent bars (right) ===
        offset_right_2 = max_width_integer + 4.0  # 增加右侧偏移量
        # draw_fraction_bar(ax, numerators[0], denominators[0], common_denom,
        #                   y_offset=2.0, x_offset=offset_right_2, color=colors[0], label_latex=latex_labels_equiv[0])
        # draw_fraction_bar(ax, numerators[1], denominators[1], common_denom,
        #                   y_offset=1.2, x_offset=offset_right_2, color=colors[1], label_latex=latex_labels_equiv[1])
        # draw_fraction_bar(ax, numerators[2], denominators[2], common_denom,
        #                   y_offset=0.4, x_offset=offset_right_2, color=colors[2], label_latex=latex_labels_equiv[2])

        for i in range(len(fractions)):
            draw_fraction_bar(ax, numerators[i], denominators[i], common_denom,
                              y_offset=2.0 - 0.8 * i, x_offset=offset_right_2,
                              color=colors[i], label_latex=latex_labels_equiv[i])

        # === Section headers ===
        ax.text(max_width / 3, 2.6, "整數部分", ha='center', fontsize=13, fontweight='bold')
        ax.text(offset_right_1 + max_width / 3, 2.6,"分數部分", ha='center', fontsize=13, fontweight='bold')
        ax.text(offset_right_2 + max_width / 3, 2.6,
                f"最小公倍數({common_denom})",
                ha='center', fontsize=13, fontweight='bold')
        
        # 动态设置底部提示的位置
        # 获取当前y轴的最大值和图表高度
        y_max = ax.get_ylim()[1]
        fig_height_inches = fig.get_size_inches()[1]
        dpi = fig.dpi
        bottom_padding_points = 20  # 底部padding，单位为点(points)
        bottom_padding_inches = bottom_padding_points / dpi
        
        # 计算底部提示位置
        text_y_position = -bottom_padding_inches/fig_height_inches * y_max
        
        # 添加底部提示
        fig.text(0.5, text_y_position, '點擊右側按鈕可全屏查看圖片或退出全屏', 
                 ha='center', fontsize=10, color='#666666', style='italic', fontweight='bold')
    else:
        # === Draw original bars (left) ===
        # draw_fraction_bar(ax, numerators[0], denominators[0], denominators[0],
        #                   y_offset=2.0, x_offset=0.0, color=colors[0], label_latex=latex_labels_original[0])
        # draw_fraction_bar(ax, numerators[1], denominators[1], denominators[1],
        #                   y_offset=1.2, x_offset=0.0, color=colors[1], label_latex=latex_labels_original[1])
        # draw_fraction_bar(ax, numerators[2], denominators[2], denominators[2],
        #                   y_offset=0.4, x_offset=0.0, color=colors[2], label_latex=latex_labels_original[2])

        for i in range(len(fractions)):
            draw_fraction_bar(ax, numerators[i], denominators[i], denominators[i],
                              y_offset=2.0 - 0.8 * i, x_offset=0.0,
                              color=colors[i], label_latex=latex_labels_original[i])

        # === Draw equivalent bars (right) ===
        offset_right = max_width + 2.0  # 增加右侧偏移量
        # draw_fraction_bar(ax, numerators[0], denominators[0], common_denom,
        #                   y_offset=2.0, x_offset=offset_right, color=colors[0], label_latex=latex_labels_equiv[0])
        # draw_fraction_bar(ax, numerators[1], denominators[1], common_denom,
        #                   y_offset=1.2, x_offset=offset_right, color=colors[1], label_latex=latex_labels_equiv[1])
        # draw_fraction_bar(ax, numerators[2], denominators[2], common_denom,
        #                   y_offset=0.4, x_offset=offset_right, color=colors[2], label_latex=latex_labels_equiv[2])

        for i in range(len(fractions)):
            draw_fraction_bar(ax, numerators[i], denominators[i], common_denom,
                              y_offset=2.0 - 0.8 * i, x_offset=offset_right,
                              color=colors[i], label_latex=latex_labels_equiv[i])

        # === Section headers ===
        ax.text(max_width / 2, 2.6, "分數部分", ha='center', fontsize=13, fontweight='bold')
        ax.text(offset_right + max_width / 2, 2.6,
                f"最小公倍數({common_denom})",
                ha='center', fontsize=13, fontweight='bold')
        
        # 动态设置底部提示的位置
        # 获取当前y轴的最大值和图表高度
        y_max = ax.get_ylim()[1]
        fig_height_inches = fig.get_size_inches()[1]
        dpi = fig.dpi
        bottom_padding_points = 20  # 底部padding，单位为点(points)
        bottom_padding_inches = bottom_padding_points / dpi
        
        # 计算底部提示位置
        text_y_position = -bottom_padding_inches/fig_height_inches * y_max
        
        # 添加底部提示
        fig.text(0.5, text_y_position, '點擊右側按鈕可全屏查看圖片或退出全屏', 
                 ha='center', fontsize=10, color='#666666', style='italic', fontweight='bold')
    return fig
    # plt.tight_layout()
    # plt.show()