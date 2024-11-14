import sys 
from gnuradio import gr, blocks, osmosdr

class SDR_Collector(gr.top_block): 
	def __init__(self, frequency, sample_rate, output_filename):
		gr.top_block.__init__(self)
		
		#Osmocom SDR source 
		self.source = osmosdr.source(args="numchan=1")
		self.source.set_sample_rate(sample_rate)
		self.source.set_center_freq(frequency)
		
		#File sink for saving data 
		self.sink = blocks.file_sink(gr.sizeof_gr_complex, output_filename)
		
		#Connect the source to sink 
		self.connect(self.source,self.sink)
		
if __name__ == "__main__": 
	
	frequency = int(sys.argv[1])
	sample_rate = int(sys.argv[2])
	output_filename = sys.argv[3]
	
	tb = SDR_Collector(frequency, sample_rate, output_filename) 
	
	#start and  run the flowgraph 
	tb.start()
	tb.wait()
	
	
