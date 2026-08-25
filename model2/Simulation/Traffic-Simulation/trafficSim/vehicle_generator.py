from .vehicle import Vehicle
from numpy.random import choice, uniform

import sys
import os

# Add the path to the 'Algorithm' directory
sys.path.insert(1, os.path.abspath(os.path.join(__file__, './../')))

# Now import the CycleCalc module
import configCustom


class VehicleGenerator:
    def __init__(self, sim, config={}):
        self.sim = sim

        # Set default configurations
        self.set_default_config()

        # Update configurations
        for attr, val in config.items():
            setattr(self, attr, val)

        # self.count = 0
        # self.countInterval = 1500
        # self.roadIndexs = [[1, 2, 3, 4, 21, 22, 23, 24, 41, 42, 43], 
        #                    [5, 6, 7, 8, 25, 26, 27, 28, 44, 45, 46],
        #                    [9, 10, 11, 12, 13, 14, 29, 30, 31, 32, 33, 34, 47, 48, 49, 50],
        #                    [15, 16, 17, 18, 19, 20, 35, 36, 37, 38, 39, 40, 51, 52, 53, 54]]
        
        # self.roadIndexs = [[3, 4, 21, 22, 41, 42, 43], 
        #                    [7, 8, 25, 26, 44, 45, 46],
        #                    [12, 13, 14, 29, 30, 31, 47, 48, 49, 50],
        #                    [18, 19, 20, 35, 36, 37, 51, 52, 53, 54]]
        
        # Entry road of each approach, per lane: [lane1, lane2, lane3].
        # Order is West, North, East, South to match the count buckets that
        # window.py fills and CycleCalc2 consumes.
        self.roadIndexs = [[0, 12, 24],   # West
                           [3, 15, 27],   # North
                           [2, 14, 26],   # East
                           [1, 13, 25]]   # South

        # print(config)
        self.config = configCustom.config()

        # Calculate properties
        self.init_properties()

    def set_default_config(self):
        """Set default configuration"""
        self.vehicle_rate = 20
        self.vehicles = [
            (1, {})
        ]
        self.last_added_time = 0

    def init_properties(self):
        # Group the configured paths by the road they start on, so an approach
        # can be chosen first and a route through it second.
        self.paths_by_start = {}
        for (weight, config) in self.vehicles:
            path = config.get('path')
            if not path:
                continue
            self.paths_by_start.setdefault(path[0], []).append((weight, config))

        self.upcoming_vehicle = self.generate_vehicle()

    def set_road_probabilities(self, pRoad):
        """Reweights the approaches (West, North, East, South)."""
        total = float(sum(pRoad))
        self.config.pRoad = [p / total for p in pRoad]

    def generate_vehicle(self):
        """Picks an approach by pRoad, a lane by pLane, then a route on that road.

        The approach and the route used to be selected by the same variable,
        which made pRoad/pLane have no real effect on where traffic appeared.
        """
        approach = self.roadIndexs[choice(len(self.roadIndexs), p=self.config.pRoad)]
        start_road = approach[choice(len(approach), p=self.config.pLane)]

        options = self.paths_by_start.get(start_road)
        if not options:
            return None

        r = uniform(0, sum(weight for weight, _ in options))
        for (weight, config) in options:
            r -= weight
            if r <= 0:
                return Vehicle(self.sim.metricCommon, config)
        return Vehicle(self.sim.metricCommon, options[-1][1])

    def update(self):
        """Add vehicles"""
        if self.upcoming_vehicle is None:
            self.upcoming_vehicle = self.generate_vehicle()
            if self.upcoming_vehicle is None:
                return

        if self.sim.t - self.last_added_time >= 60 / self.vehicle_rate:
            # If time elasped after last added vehicle is
            # greater than vehicle_period; generate a vehicle
            road = self.sim.roads[self.upcoming_vehicle.path[0]]      
            if len(road.vehicles) == 0\
               or road.vehicles[-1].x > self.upcoming_vehicle.s0 + self.upcoming_vehicle.l:
                # If there is space for the generated vehicle; add it
                self.upcoming_vehicle.time_added = self.sim.t
                road.vehicles.append(self.upcoming_vehicle)
                # Reset last_added_time and upcoming_vehicle
                self.last_added_time = self.sim.t
            self.upcoming_vehicle = self.generate_vehicle()

    def delete_all_vehicles(self):
        for road in self.sim.roads:
            road.vehicles.clear()
        self.last_added_time = 0
