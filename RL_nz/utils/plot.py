import matplotlib.pyplot as plt

def plot_results(data, ylabel, xlabel='Episode'):
    plt.plot(data, label=ylabel)
    plt.legend()
    plt.xlabel('Time' if isinstance(ylabel, int) else xlabel)
    plt.ylabel('Power Level' if isinstance(ylabel, int) else ylabel)
    plt.title(ylabel)
    plt.show()