# script.py

from matplotlib import pyplot		# you may use whatever plotting library of software you want
									# you will need to install this module before using it
									# https://matplotlib.org/stable/index.html
import time
from simulator import *

def main():

	# ---------------------------------------------------------------
	# setup the 'clock' with which the simulation will be run
	t1 = time.time()
	t_delta = 0.1e-6								# time step size [seconds]
	t_N = 800										# number of time points

	t_array = [t_i*t_delta for t_i in range(t_N)]	# the master clock, array of time [seconds]

	sos = 1500.0									# speed of sound [metres/second]


	# ---------------------------------------------------------------
	# setup receivers and emitters

	# arrange a linear order of receivers from -0.04 m to 0.04 m
	receiver_positions = [[receiver_x / 1000.0, 0.04] for receiver_x in range(-40, 41, 2)]

	emitters = []
	receivers = []

	emitters.append(Emitter(0, 0, t_array))

	signal = emitters[0].generate_signal(1e6, 5, 1)
	# signal = emitters[].generate_signal(1e6,5,1)

	fig, axs = pyplot.subplots(1)
	axs.plot(t_array, signal)
	axs.set_xlabel('time (seconds)')
	axs.set_ylabel('amplitude')
	pyplot.show()

	for pos in receiver_positions:
		receivers.append(Receiver(pos[0], pos[1], t_array))

	# ---------------------------------------------------------------
	# run the simulation

	simulation = SoundSimulator(emitters, receivers, t_array, sos)
	receivers = simulation.run()

	img = []
	for i in range(len(receivers)):
		img.append(receivers[i].signal)

	fig, axs = pyplot.subplots(1)
	imgplot = axs.imshow(img)
	axs.set_aspect(20)
	axs.set_xlabel('time point')
	axs.set_ylabel('receiver number')
	fig.colorbar(imgplot)
	pyplot.show()

	# ---------------------------------------------------------------
	# set the field of view from which we will visualise sound

	x_range = [-0.02, 0.02]							# x-axis range [metres]
	x_N = 51										# number of points along x axis
	x_delta = abs(x_range[0]-x_range[1])/(x_N-1)	# step size along x axis [metres]

	y_range = [-0.02, 0.02]							# y-axis range [metres]
	y_N = 51						# number of points along y axis
	y_delta = abs(y_range[0]-y_range[1])/(y_N-1)	# step size along y axis [metres]

	x_array = []
	for i in range(x_N):
		x_array.append(x_range[0]+i*x_delta)


	y_array = []
	for i in range(y_N):
		y_array.append(y_range[0]+i*y_delta)


	# ---------------------------------------------------------------
	# reconstruct a field, where sound may be located

	beam_former = BeamFormer(receivers, x_array, y_array, t_array, sos)
	beam_former.generate_field()

	fig, axs = pyplot.subplots(1)
	axs.plot(beam_former.field[25][25])

	img = []
	for j in range(len(y_array)):
		row = []
		for i in range(len(x_array)):
			row.append(min(beam_former.field[j][i]))
		img.append(row)

	fig, axs = pyplot.subplots(1)
	imgplot = axs.imshow(img, origin='lower', extent=[x_array[0]*1000, x_array[-1]*1000, y_array[0]*1000, y_array[-1]*1000])
	axs.set_xlabel('x-axis (mm)')
	axs.set_ylabel('y-axis (mm)')
	fig.colorbar(imgplot)
	pyplot.show()
	t2 = time.time()
	print(t2-t1)

if __name__ == '__main__':
	main()