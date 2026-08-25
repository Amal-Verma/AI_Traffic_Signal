class config():
  def __init__(self):
    self.pRoad = [0.6, 0.1, 0.2, 0.1]
    self.pLane = [0.25, 0.50, 0.25]

    # car, truck, bus, motorcycle - India-realistic mix, matching the
    # proportions documented in Vehicle.set_default_config
    self.vehicles = [0.2, 0.05, 0.05, 0.7]

    self.vehicle_rate = 75

class metrix():
  def __init__(self):
    self.fuel = 0
    self.fuelStop = 0
    # Delay against free-flow, and time spent fully stopped. Both in
    # vehicle-seconds, summed over every vehicle in the network.
    self.delay = 0
    self.waitTime = 0