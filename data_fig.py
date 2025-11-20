import matplotlib.pyplot as plt
import numpy as np
from fractions import Fraction
from matplotlib.ticker import MultipleLocator

def data_fig(data):
    plt.rcParams['font.family'] = 'Arial Unicode MS'
    fig, ax = plt.subplots()

    # setup the data
    display_list = [item["display"] for item in data]
    data = [Fraction(item["numerator"], item["denominator"]) for item in data]
    print(data)
    num = np.array(data)
    print(num)
    number_list = [f"數字{i + 1}" for i in range(len(data))]

    # Create horizontal bars
    color_list = ['skyblue', 'lightgreen', 'salmon', 'red', 'yellow']
    color = color_list[:len(data)]
    ax.barh(number_list, width=num, color=color)
    for i, (value, text) in enumerate(zip(num, display_list)):
        ax.text(value, i, text, ha='left', va='center', fontsize=12)
    ax.xaxis.set_major_locator(MultipleLocator(1))

    # Return the chart
    return fig


def data_choice_fig(data, txt):
    plt.rcParams['font.family'] = 'Arial Unicode MS'
    fig, ax = plt.subplots()
    
    # setup the data
    display_list = [item["display"] for item in data]
    data = [Fraction(item["numerator"], item["denominator"]) for item in data]
    print(data)
    num = np.array(data)
    print(num)
    list_txt = [txt]
    number_list = [f"數字{i + 1}" for i in range(len(data) - 1)] + list_txt

    # Create horizontal bars
    color_list = ['skyblue', 'lightgreen', 'salmon', 'red', 'yellow']
    color = color_list[:len(data)]
    ax.barh(number_list, width=num, color=color)
    for i, (value, text) in enumerate(zip(num, display_list)):
        ax.text(value, i, text, ha='left', va='center', fontsize=12)
    ax.xaxis.set_major_locator(MultipleLocator(1))

    # Return the chart
    return fig
