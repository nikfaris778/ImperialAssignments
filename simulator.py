"""Assignment 2: Sound Simulator"""
import math
class Transducer:

    def __init__(self, x, y, t_array):
        self.x = x
        self.y = y
        self.t_array = t_array
        self.signal = len(self.t_array) * [0]

class Receiver(Transducer):

    def __init__(self, x, y, t_array):
        super().__init__(x, y, t_array)

class Emitter(Transducer):

    def __init__(self, x, y, t_array):
        super().__init__(x, y, t_array)

    def generate_signal(self, f_c, n_cycles, amplitude):
        """Generates the signal being emitted from the emitter"""

        time = 1/float(f_c) * n_cycles # time taken for the whole signal
        step = self.t_array[1] - self.t_array[0] # step of the array
        number_of_points = int(time/step) # number of points need to be sampled

        for i in range(number_of_points):
            self.signal[i] = amplitude * math.sin(2 * math.pi * f_c * self.t_array[i]) # update the list for the signal

        return self.signal

class SoundSimulator:
    """Simulates a sound wave being generated from an emitter.
    Returns a list of receiver signals in a 1-dimensional list
    """
    def __init__(self, emitters, receivers, t_array, sos=1500.0):
        self.emitters = emitters if emitters is not None else []
        self.receivers = receivers if receivers is not None else []
        self.t_array = t_array if t_array is not None else []
        self.sos = sos


    def run(self):
        """Runs the sound simulation. Iterates through all emitters and receivers,
        calculates the distance and determines the delay"""

        step = self.t_array[1] - self.t_array[0]
        for receiver in self.receivers:
            for emitter in self.emitters: # looping through all emitters and receivers
                distance = math.sqrt((emitter.x - receiver.x)**2 + (emitter.y - receiver.y)**2)
                point_of_delay = int((distance/self.sos)/step) # point where individual receiver signal starts

                for i in range(len(self.t_array) - point_of_delay):
                    receiver.signal[i+point_of_delay] += emitter.signal[i] * 1/distance  # the += takes care of superposition of signal

        return self.receivers

class BeamFormer:
    """Delay and sum algorithm which maps out where the emitter is in the space."""
    def __init__(self, receivers, x_array, y_array, t_array, sos=1500.0):
        self.receivers = receivers if receivers is not None else []
        self.x_array = x_array  if x_array is not None else []
        self.y_array = y_array if y_array is not None else []
        self.t_array = t_array if t_array is not None else []
        self.sos = sos
        self.field = [[[0.0]*len(t_array) for x in x_array] for y in y_array]  # 3-dimensional array


    def generate_field(self):
        """Generates a sampling field to get the acoustic source strength."""
        step = self.t_array[1] - self.t_array[0]
        for i, y  in enumerate(self.y_array):
            for j, x in enumerate(self.x_array): # iterate through x and y axes

                signal_sum = [0.0] * 2 * len(self.t_array)
                distances = [math.sqrt((receiver.x - x)**2 + (receiver.y - y)**2) for receiver in self.receivers]
                minimum = int((min(distances) / self.sos) / step) # minimum distance to one receiver, indexed

                # Check through each receiver and find the distance.
                for receiver_index, receiver in enumerate(self.receivers):
                    distance = distances[receiver_index]

                    # Calculate the delay and the index where that happens for each individual distance.
                    point_of_delay = int((distance / self.sos) / step)

                    # Adding "negative time" will solve the issue of lost data, where this just doubles the signal array
                    neg_time = [0.0] * len(self.t_array) + receiver.signal

                    for k in range(len(neg_time) - point_of_delay):
                        signal_sum[k] += neg_time[k+point_of_delay] * distance/len(self.receivers) # summing into q, with the delay taken into account

                # Puts the delayed and summed signal into the field, with respect to the minimum distance.
                self.field[i][j] = signal_sum[len(self.t_array)-minimum : -minimum]