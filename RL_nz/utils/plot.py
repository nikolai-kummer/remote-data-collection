import matplotlib.pyplot as plt

def plot_results(data, label):
    plt.plot(data, label=label)
    plt.legend()
    plt.xlabel('Time' if isinstance(label, int) else 'Episode')
    plt.ylabel('Power Level' if isinstance(label, int) else label)
    plt.title(label)
    plt.show()