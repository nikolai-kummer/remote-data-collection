import numpy as np
import matplotlib.pyplot as plt

def solar_intensity(time_minute: int) -> float:
    """
    Approximates the solar intensity for a given time in minutes.
    
    :param time_minute: Time in minutes (0 to 1440).
    :return: Approximated solar intensity.
    """
    # Constants
    solar_noon = 780  # Approx 1:00 PM in minutes
    sunrise = 240     # Approx 5:00 AM in minutes
    sunset = 1320     # Approx 9:00 PM in minutes

    # Normalize time to a scale of -1 to 1 for the sinusoidal function
    # where -1 represents sunrise, 1 represents sunset, and 0 is solar noon
    normalized_time = (time_minute - solar_noon) / (sunset - sunrise)

    # Sinusoidal function to approximate solar intensity
    intensity = np.cos(np.pi * normalized_time) ** 2

    # Adjust intensity to be zero before sunrise and after sunset
    intensity = intensity if sunrise <= time_minute <= sunset else 0

    return intensity


if __name__ == '__main__':
    print('Running sim_functions.py...')

    # Generate a plot for visualization
    times = np.arange(0, 1440)  # Minutes in a day
    intensities = [solar_intensity(t) for t in times]

    plt.figure(figsize=(10, 5))
    plt.plot(times, intensities)
    plt.xlabel('Time (minutes)')
    plt.ylabel('Solar Intensity')
    plt.title('Approximate Solar Intensity Throughout the Day')
    plt.grid(True)
    plt.show()

    print('Done!')
