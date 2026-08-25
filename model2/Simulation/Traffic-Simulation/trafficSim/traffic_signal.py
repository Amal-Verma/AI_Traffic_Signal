import sys
import os

# Add the path to the 'Algorithm' directory
sys.path.insert(1, os.path.abspath(os.path.join(__file__, './../../../../Algorithm')))

# Now import the CycleCalc module
import CycleCalc
import CycleCalc2

# Set TRAFFICSIM_DEBUG=1 to get the per-step controller trace back.
DEBUG = bool(os.environ.get('TRAFFICSIM_DEBUG'))

# Baseline controller: the same four-phase structure the adaptive controller
# falls back to, but with green split evenly instead of by demand.
#
# It carries the same all-red clearance the adaptive cycle pays (two halts per
# cycle). Without that the baseline gets more usable green per cycle than the
# adaptive controller can ever get, which flatters it badly once the
# intersection saturates and throughput becomes green-time bound.
ALL_RED = (False,) * 12

FIXED_GREENS = [
    (True,  True,  True,  False, False, False, False, False, False, False, False, True),
    (False, False, True,  True,  True,  True,  False, False, False, False, False, False),
    (False, False, False, False, False, True,  True,  True,  True,  False, False, False),
    (False, False, False, False, False, False, False, False, True,  True,  True,  True),
]
FIXED_CYCLE = [
    FIXED_GREENS[0], FIXED_GREENS[1], ALL_RED,
    FIXED_GREENS[2], FIXED_GREENS[3], ALL_RED,
]


def fixed_timer(model):
    """Even green split, minus the same clearance time the adaptive cycle pays."""
    halts = 2
    green = (model.cycle_time - halts * model.halt_time) / len(FIXED_GREENS)
    return model.prefix_sum([green, green, model.halt_time,
                             green, green, model.halt_time])


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

        # True  -> CycleCalc2 allocates green by measured demand
        # False -> fixed-time baseline, even split
        self.adaptive = True

    def set_adaptive(self, adaptive):
        """Switches controller and restarts the cycle from phase 0."""
        self.adaptive = adaptive
        self.current_cycle_index = 0
        self.model2.counter = 0
        if adaptive:
            # Let the next completed cycle re-seed from live counts
            self.model2.isfirstcycle = True
        else:
            self.cycle = list(FIXED_CYCLE)
            self.timer = fixed_timer(self.model2)

    def init_properties(self):
        for i in range(len(self.roads)):
            for road in self.roads[i]:
                road.set_traffic_signal(self, i)

    @property
    def current_cycle(self):
        return self.cycle[self.current_cycle_index]
    
    def update(self, sim):
        self.model2.counter += (1 / 60)
        if DEBUG:
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

                if self.adaptive:
                    # self.cycle, self.timer = self.model2.call(sim.carsCount)
                    self.cycle, self.timer = self.model2.call(sim.carsCount,sim.lanewiseCount)
                else:
                    # Fixed-time baseline: same phases and same total cycle
                    # length every time, regardless of what the counts say.
                    self.cycle = list(FIXED_CYCLE)
                    self.timer = fixed_timer(self.model2)

                # Counts are consumed once per cycle either way, so the two
                # modes see identical demand measurement.
                sim.update_cars_count([0,0,0,0])
                sim.update_lanewise_count([[0,0,0], [0,0,0], [0,0,0], [0,0,0]])

                if DEBUG:
                    print(sim.carsCount)
                    print(sim.lanewiseCount)
                    print(self.cycle)
                    print(self.timer)
                    newarr = list(self.timer)
                    for i in reversed(range(1,len(self.timer))):
                        newarr[i] -= newarr[i-1]
                    print(newarr)

        if(len(self.roads) < 4):
            self.current_cycle_index = 3
