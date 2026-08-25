"""Real measured traffic demand, used to drive the simulation.

The bundled profile is NYC DOT's Automated Traffic Volume Counts for the
crossing of Junction Boulevard and Northern Boulevard in Queens: two arterials
where all four approaches were actually counted. Volumes are 15-minute
observations aggregated to vehicles/hour and averaged over the counted days.

This is separate from the synthetic scenarios in Window.SCENARIOS, which are
illustrative shapes rather than measurements.
"""

import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
DEFAULT_PROFILE = os.path.join(DATA_DIR, 'nyc_junction_northern.json')

# Sim approach order: West, North, East, South
APPROACH_ORDER = ['West', 'North', 'East', 'South']


class RealProfile:
    """A measured 24-hour demand curve for one intersection."""

    def __init__(self, path=DEFAULT_PROFILE):
        with open(path) as fh:
            raw = json.load(fh)

        self.intersection = raw['intersection']
        self.boro = raw.get('boro', '')
        self.source = raw['source']
        self.caveat = raw.get('caveat', '')
        self.days_counted = raw.get('days_counted', {})

        # hours[h] = [West, North, East, South] vehicles/hour
        profile = raw['profile']
        self.hours = [[float(profile[a][h]) for a in APPROACH_ORDER]
                      for h in range(24)]

    @property
    def name(self):
        who = self.intersection.title().replace(' And ', ' & ')
        return f'{who}'

    def total_per_hour(self, hour):
        return sum(self.hours[hour % 24])

    def rate(self, hour):
        """Spawn rate in vehicles/minute at this hour, as measured."""
        return max(1, round(self.total_per_hour(hour) / 60.0))

    def weights(self, hour):
        """Approach mix at this hour, normalised over West/North/East/South."""
        counts = self.hours[hour % 24]
        total = sum(counts)
        if total <= 0:
            return [0.25] * 4
        return [c / total for c in counts]

    def peak_hour(self):
        return max(range(24), key=self.total_per_hour)

    def apply(self, sim, hour):
        """Points the generators at the measured demand for this hour."""
        weights = self.weights(hour)
        rate = self.rate(hour)
        for gen in sim.generators:
            gen.set_road_probabilities(weights)
            gen.vehicle_rate = rate
        type(sim).vehicleRate = rate
        return weights, rate
