import time
from random import random as rand
from pylsl import StreamInfo, StreamOutlet

info = StreamInfo('BioSemi', 'EEG', 8, 100, 'float32', 'myuid34234')
outlet = StreamOutlet(info)

print("now sending data...")
while True:
    mysample = [rand(), rand(), rand(), rand(), rand(), rand(), rand(), rand()]
    outlet.push_sample(mysample)
    time.sleep(0.01)