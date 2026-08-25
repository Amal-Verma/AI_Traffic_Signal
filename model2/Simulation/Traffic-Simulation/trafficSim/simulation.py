from .road import Road
from .vehicle_generator import VehicleGenerator
from .traffic_signal import TrafficSignal

class Simulation:
    vehiclesPassed = 0
    vehiclesPresent = 0
    vehicleRate = 0
    isPaused = False

    # Entry roads per approach (lanes 1-3), order: West, North, East, South.
    # Matches the controller's count buckets in CycleCalc2.getValDicts.
    APPROACH_ROADS = [[0, 12, 24], [3, 15, 27], [2, 14, 26], [1, 13, 25]]

    def __init__(self,metricCommon, config={}):
        self.carsCount = [0,0,0,0]
        self.lanewiseCount = [[0,0,0], [0,0,0], [0,0,0], [0,0,0]]

        self.metricCommon = metricCommon

        # self.fuel = 0

        # Set default configuration
        self.set_default_config()

        # Update configuration
        for attr, val in config.items():
            setattr(self, attr, val)
    
    def update_cars_count(self, carsCount):
        self.carsCount = carsCount
    
    def update_lanewise_count(self,lanewiseCount):
        self.lanewiseCount = lanewiseCount

    def set_default_config(self):
        self.t = 0.0            # Time keeping
        self.metrics_t0 = 0.0   # Time the current measurement window started
        self.frame_count = 0    # Frame count keeping
        self.dt = 1/60          # Simulation time step
        self.roads = []         # Array to store roads
        self.generators = []
        self.traffic_signals = []
        self.iteration = 0      # n-th iteration (of sampling, if enabled)

    def create_road(self, start, end):
        road = Road(start, end)
        self.roads.append(road)
        return road

    def create_roads(self, road_list):
        for road in road_list:
            self.create_road(*road)

    def create_gen(self, config={}):
        gen = VehicleGenerator(self, config)
        self.generators.append(gen)
        Simulation.vehicleRate = gen.vehicle_rate
        return gen

    def create_signal(self, roads, config={}):
        roads = [[self.roads[i] for i in road_group] for road_group in roads]
        sig = TrafficSignal(roads, config)
        self.traffic_signals.append(sig)
        return sig

    def update(self):
        # Update every road
        for road in self.roads:
            road.update(self.dt)

        # Add vehicles
        for gen in self.generators:
            gen.update()

        # Feed the per-approach queue counts the signal controller reads.
        # Kept as peak-hold over the cycle: the controller zeroes these each
        # time it recomputes, so this records the worst queue since then.
        # This was previously done inside window.py's draw_status(), tying
        # control logic to rendering — headless runs got no count data.
        self._sample_counts()

        for signal in self.traffic_signals:
            signal.update(self)

        # Check roads for out of bounds vehicle
        for road in self.roads:
            # Several vehicles can clear the road in one step, so drain them all
            while len(road.vehicles) > 0 and road.vehicles[0].x >= road.length:
                vehicle = road.vehicles[0]
                # Remove it from its road first; it is either handed to the
                # next road or done with its path.
                road.vehicles.popleft()

                # If vehicle has a next road
                if vehicle.current_road_index + 1 < len(vehicle.path):
                    # Update current road to next road
                    vehicle.current_road_index += 1
                    # Move the same vehicle over, so its accumulated metrics
                    # and its shared metricCommon reference survive the hop.
                    vehicle.x = 0
                    next_road_index = vehicle.path[vehicle.current_road_index]
                    self.roads[next_road_index].vehicles.append(vehicle)
                else:
                    Simulation.vehiclesPassed += 1

                # if vehicle reached the end of the path
                # if vehicle.current_road_index + 1 == len(vehicle.path):
                #     Simulation.vehiclesPassed += 1
                    # print("Vehicle passed: " + str(Simulation.vehiclesPassed))

        # Check for the number of vehicles present
        Simulation.vehiclesPresent = 0
        for road in self.roads:
            Simulation.vehiclesPresent += len(road.vehicles)

        # Increment time
        self.t += self.dt
        self.frame_count += 1

        # Stop at certain time in seconds (for sampling purposes. Comment out if not needed)
        # self.time_limit = 300
        # if self.t >= self.time_limit:
        #     print("Traffic Signal Cycle Length: " + str(self.traffic_signals[0].cycle_length))
        #     print("Time: " + str(self.t))
        #     print("Vehicles Passed: " + str(Simulation.vehiclesPassed))
        #     print("Vehicles Present: " + str(Simulation.vehiclesPresent))
        #     print("Vehicle Rate: " + str(Simulation.vehicleRate))
        #     print("Traffic Density: " + str(Simulation.vehiclesPresent / (len(self.roads) * self.roads[0].length)))
        #     print("Iteration: " + str(self.iteration))

        #     # Add to CSV the time and vehicles passed
        #     # with open('data.csv', mode='a') as data_file:
        #     #     data_writer = csv.writer(data_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        #     #     data_writer.writerow([self.traffic_signals[0].cycle_length, Simulation.vehiclesPassed])

        #     # Reset time and vehicles passed
        #     self.t = 0.001
        #     gen.delete_all_vehicles()
        #     Simulation.vehiclesPassed = 0
        #     Simulation.vehiclesPresent = 0
        #     self.iteration += 1
        #     if self.iteration % 5 == 0:
        #         # Set all traffic signals to +1
        #         for signal in self.traffic_signals:
        #             signal.cycle_length += 1


    def run(self, steps):
        for _ in range(steps):
            self.update()

    def pause(self):
        self.isPaused = True

    def resume(self):
        self.isPaused = False

    @property
    def metrics_elapsed(self):
        """Seconds of simulated time since the last metrics reset."""
        return self.t - self.metrics_t0

    def reset_metrics(self):
        """Zeroes accumulated metrics so an A/B comparison starts clean."""
        Simulation.vehiclesPassed = 0
        self.metricCommon.fuel = 0
        self.metricCommon.fuelStop = 0
        self.metricCommon.delay = 0
        self.metricCommon.waitTime = 0
        self.metrics_t0 = self.t

    def clear_traffic(self):
        """Empties every road, for restarting a scenario from an empty map."""
        for road in self.roads:
            road.vehicles.clear()
        for gen in self.generators:
            gen.last_added_time = self.t
        Simulation.vehiclesPresent = 0

    def set_adaptive(self, adaptive):
        """Switches every signal between the adaptive and fixed-time controller."""
        for signal in self.traffic_signals:
            signal.set_adaptive(adaptive)

    @property
    def is_adaptive(self):
        return all(s.adaptive for s in self.traffic_signals)

    def _sample_counts(self):
        """Peak-hold per-approach queue counts for the signal controller."""
        lanewise = [[len(self.roads[i].vehicles) for i in group]
                    for group in self.APPROACH_ROADS]
        totals = [sum(group) for group in lanewise]

        for i in range(len(self.carsCount)):
            self.carsCount[i] = max(totals[i], self.carsCount[i])

        for i in range(4):
            for j in range(3):
                self.lanewiseCount[i][j] = max(
                    self.lanewiseCount[i][j], lanewise[i][j])