import sys
import os

# Add the path to the 'Algorithm' directory
sys.path.insert(1, os.path.abspath(os.path.join(__file__, './../../../../Algorithm')))

# Now import the CycleCalc module
import CycleCalc
import CycleCalc2


class TrafficSignal:
    def __init__(self, roads, config={}):
        # self.model2 = CycleCalc.Manager()
        self.model2 = CycleCalc2.Manager()
        # Initialize roads
        self.roads = roads
        # Set default configuration
        self.set_default_config()

        # Update configuration
        for attr, val in config.items():
            setattr(self, attr, val)
        # Calculate properties
        self.init_properties()

    def set_default_config(self):
        # self.cycle = [(True, False, False, False), (False, True, False, False), (False, False, True, False), (False, False, False, True)]
        self.cycle = [(True, True, True, True, True, True, False, False, False, False, False, False),]
        self.timer = [(i + 1) / 2 for i in range(len(self.cycle))]

        self.slow_distance = 50
        self.slow_factor = 0.4
        self.stop_distance = 12
        self.cycle_length = 1

        self.cycle_count = 0

        self.current_cycle_index = 0

        self.last_t = 0

    def init_properties(self):
        for i in range(len(self.roads)):
            for road in self.roads[i]:
                road.set_traffic_signal(self, i)

    @property
    def current_cycle(self):
        return self.cycle[self.current_cycle_index]
    
    def update(self, sim):
        self.model2.counter += (1 / 60)
        print(round(self.model2.counter, 4), self.current_cycle_index, end='\r')
        # print(self.timer)
        # randomize the cycle length after every cycle
        if(self.model2.counter > self.timer[self.current_cycle_index]):
            # self.cycle_length = 5
            # self.cycle_count = 0
        # k = (sim.t // cycle_length) % 4
            self.current_cycle_index = self.current_cycle_index + 1
            if self.current_cycle_index >= len(self.cycle):
                self.current_cycle_index = 0
                self.model2.counter = 0
                
                # self.cycle, self.timer = self.model2.call(sim.carsCount)
                self.cycle, self.timer = self.model2.call(sim.carsCount,sim.lanewiseCount)
                print(sim.carsCount)
                print(sim.lanewiseCount)
                sim.update_cars_count([0,0,0,0])
                sim.update_lanewise_count([[0,0,0], [0,0,0], [0,0,0], [0,0,0]])
                print(self.cycle)
                print(self.timer)
                newarr = list(self.timer)
                for i in reversed(range(1,len(self.timer))):
                    newarr[i] -= newarr[i-1]
                print(newarr)

        if(len(self.roads) < 4):
            self.current_cycle_index = 3
