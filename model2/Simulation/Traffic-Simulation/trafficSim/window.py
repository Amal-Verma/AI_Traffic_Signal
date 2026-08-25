import os
import pygame
from pygame import gfxdraw
import numpy as np

from .real_traffic import RealProfile
# Single source of truth for the body colours drawn per vehicle type
from .vehicle import RED, YELLOW, BLUE, ORANGE

def avg(l):
    return sum(l) / len(l) if len(l) > 0 else 0

class Window:
    # Entry roads per approach, lanes 1-3. Order matches the controller's
    # count buckets in CycleCalc2.getValDicts.
    APPROACH_ROADS = [[0, 12, 24], [3, 15, 27], [2, 14, 26], [1, 13, 25]]
    APPROACH_NAMES = ['West', 'North', 'East', 'South']

    HUD_HEIGHT = 512

    # Must match the colours Vehicle.set_default_config assigns
    VEHICLE_LEGEND = [
        ('Car', 'car', RED),
        ('Truck', 'truck', YELLOW),
        ('Bus', 'bus', BLUE),
        ('Motorcycle', 'motorcycle', ORANGE),
    ]

    # Named traffic patterns, as approach weights (W, N, E, S).
    SCENARIOS = [
        ('Balanced',        [0.25, 0.25, 0.25, 0.25]),
        ('Morning peak',    [0.55, 0.20, 0.10, 0.15]),
        ('Evening peak',    [0.10, 0.15, 0.55, 0.20]),
        ('North corridor',  [0.12, 0.52, 0.12, 0.24]),
    ]

    def __init__(self, sim, config={}):
        # Simulation to draw
        self.sim = sim

        # Set default configurations
        self.set_default_config()

        # Update configurations
        for attr, val in config.items():
            setattr(self, attr, val)

        # Check if launched with custom detected demand from model1_gui
        if os.environ.get('DETECTED_COUNTS'):
            try:
                counts = [float(x) for x in os.environ['DETECTED_COUNTS'].split(',')]
                total = sum(counts)
                if total > 0:
                    weights = [c / total for c in counts]
                    for gen in self.sim.generators:
                        gen.set_road_probabilities(weights)
                    self.scenario_name = (
                        f"W {int(counts[0])}   N {int(counts[1])}   "
                        f"E {int(counts[2])}   S {int(counts[3])}")
                    self.demand_source = 'detected'
            except Exception as exc:
                print(f"Failed to apply DETECTED_COUNTS: {exc}")
        
    def set_default_config(self):
        """Set default configuration"""
        self.width = 1280
        self.height = 820

        # Dark palette: bright vehicles read much better against it, and it
        # survives a washed-out projector far better than the old white.
        self.bg_color   = (16, 18, 25)
        self.C_ROAD     = (46, 52, 66)
        self.C_GRID     = (26, 29, 38)
        self.C_GRID_MAJ = (33, 37, 48)
        self.C_AXES     = (44, 49, 62)
        self.C_ARROW    = (86, 94, 116)

        self.C_PANEL    = (24, 28, 38)
        self.C_BORDER   = (52, 59, 76)
        self.C_TEXT     = (231, 237, 246)
        self.C_MUTED    = (138, 150, 172)
        self.C_ACCENT   = (125, 178, 255)
        self.C_GREEN    = (74, 222, 128)
        self.C_AMBER    = (251, 191, 36)
        self.C_RED      = (248, 113, 113)

        self.fps = 60
        self.zoom = 5
        self.offset = (0, 0)

        self.mouse_last = (0, 0)
        self.mouse_down = False

        # flip x axis
        self.flip_x = True

        self.show_help = True
        self.steps_per_update = 4

        # Real measured demand, loaded lazily so a missing data file can
        # never stop the synthetic scenarios from working.
        self.real = None
        self.real_hour = None

        # Where the current demand came from: 'synthetic', 'measured' (NYC
        # counts) or 'detected' (YOLO output handed over by model1_gui)
        self.demand_source = 'synthetic'

        # Live per-type tally, filled while drawing vehicles
        self._type_counts = {}
        self.font_bold = None
        self._panel_cache = {}
        self.scenario_name = self.SCENARIOS[0][0]

        # Cached static layer (grid + axes + roads). Rebuilt only on zoom/pan.
        self._static = None
        self._static_key = None

    def font_for(self, size, bold=False):
        """First font that exists on this machine, so it looks the same off-laptop."""
        return pygame.font.SysFont(
            'Inter,Segoe UI,DejaVu Sans,Arial', size, bold=bold)

    def mono_for(self, size):
        return pygame.font.SysFont(
            'JetBrains Mono,Consolas,DejaVu Sans Mono,Lucida Console', size)

    def ensure_fonts(self):
        """Builds fonts on first use, so draw() works from any entry point."""
        if getattr(self, 'font_bold', None) is not None:
            return
        pygame.font.init()
        self.text_font = self.mono_for(16)
        self.font = self.font_for(15)
        self.font_sm = self.font_for(13)
        self.font_bold = self.font_for(15, bold=True)
        self.font_mono = self.mono_for(15)


    def snapshot(self, path, seconds=180, steps_per_update=10):
        """Renders the interface offscreen to a PNG, without opening a window.

        Used by the detection GUI to show what the intersection looks like once
        the detected demand has been fed in. Runs the simulation forward far
        enough for queues to form, then saves a single frame.
        """
        self.screen = pygame.Surface((self.width, self.height))
        self.ensure_fonts()
        self.show_help = False   # keyboard hints are noise in a still image

        for _ in range(int(seconds * 60 / steps_per_update)):
            self.sim.run(steps_per_update)

        self.draw()
        pygame.image.save(self.screen, path)
        return path

    def loop(self, loop=None):
        """Shows a window visualizing the simulation and runs the loop function."""

        # Snapshot mode: render one frame offscreen and exit, so the detection
        # GUI can display the seeded intersection as an image.
        snap = os.environ.get('SNAPSHOT_PATH')
        if snap:
            self.snapshot(snap, seconds=float(os.environ.get('SNAPSHOT_SECONDS', 180)))
            return

        # Create a pygame window
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('Adaptive Traffic Signal Control')
        pygame.display.flip()

        # Fixed fps
        clock = pygame.time.Clock()

        # To draw text
        self.ensure_fonts()

        # Draw loop
        running = True
        while running:
            # Update simulation
            if loop and not self.sim.isPaused:
                loop(self.sim)

            # Draw simulation
            self.draw()

            # Update window
            pygame.display.update()
            clock.tick(self.fps)

            # Handle all events
            for event in pygame.event.get():
                # Quit program if window is closed
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_ESCAPE, pygame.K_q):
                        running = False
                    else:
                        self.handle_key(event.key)
                # Handle mouse events
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # If mouse button down
                    if event.button == 1:
                        # Left click
                        x, y = pygame.mouse.get_pos()
                        x0, y0 = self.offset
                        self.mouse_last = (x-x0*self.zoom, y-y0*self.zoom)
                        self.mouse_down = True
                    if event.button == 4:
                        # Mouse wheel up
                        self.zoom *=  (self.zoom**2+self.zoom/4+1) / (self.zoom**2+1)
                    if event.button == 5:
                        # Mouse wheel down 
                        self.zoom *= (self.zoom**2+1) / (self.zoom**2+self.zoom/4+1)
                elif event.type == pygame.MOUSEMOTION:
                    # Drag content
                    if self.mouse_down:
                        x1, y1 = self.mouse_last
                        x2, y2 = pygame.mouse.get_pos()
                        self.offset = ((x2-x1)/self.zoom, (y2-y1)/self.zoom)
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.mouse_down = False           

    def handle_key(self, key):
        sim = self.sim

        if key == pygame.K_SPACE:
            sim.resume() if sim.isPaused else sim.pause()

        elif key == pygame.K_t:
            # Switching controller starts a fresh measurement window, so the
            # numbers on screen always describe the mode currently running.
            sim.set_adaptive(not sim.is_adaptive)
            sim.reset_metrics()

        elif key == pygame.K_r:
            sim.reset_metrics()

        elif key == pygame.K_c:
            sim.clear_traffic()
            sim.reset_metrics()

        elif key in (pygame.K_LEFTBRACKET, pygame.K_RIGHTBRACKET):
            step = 5 if key == pygame.K_RIGHTBRACKET else -5
            rate = max(5, min(300, int(sim.vehicleRate) + step))
            for gen in sim.generators:
                gen.vehicle_rate = rate
            type(sim).vehicleRate = rate

        elif key in (pygame.K_MINUS, pygame.K_EQUALS, pygame.K_PLUS):
            # Simulated seconds per wall second. More cycles per minute of
            # demo means the A/B numbers settle sooner.
            step = -2 if key == pygame.K_MINUS else 2
            self.steps_per_update = max(1, min(24, self.steps_per_update + step))

        elif key == pygame.K_h:
            self.show_help = not self.show_help

        elif pygame.K_1 <= key <= pygame.K_4:
            name, weights = self.SCENARIOS[key - pygame.K_1]
            for gen in sim.generators:
                gen.set_road_probabilities(weights)
            self.real_hour = None
            self.demand_source = 'synthetic'
            self.scenario_name = name
            sim.reset_metrics()

        elif key == pygame.K_b:
            # Real deployed Bengaluru time-of-day plan
            if sim.set_mode('deployed'):
                sim.reset_metrics()

        elif key == pygame.K_5:
            # Real measured demand, starting at the busiest hour
            if self.load_real():
                self.set_real_hour(self.real.peak_hour())
                sim.reset_metrics()

        elif key in (pygame.K_COMMA, pygame.K_PERIOD):
            step = 1 if key == pygame.K_PERIOD else -1
            if self.real_hour is not None:
                # Step through the measured 24-hour demand curve
                self.set_real_hour((self.real_hour + step) % 24)
                sim.reset_metrics()
            elif sim.mode == 'deployed':
                # No measured demand loaded, but the deployed plan still
                # switches by time of day
                sim.hour = (sim.hour + step) % 24
                sim.set_mode('deployed')
                sim.reset_metrics()

    def load_real(self):
        """Loads the measured profile once; returns False if unavailable."""
        if self.real is None:
            try:
                self.real = RealProfile()
            except Exception as exc:
                # Never let a missing/broken data file break the demo
                print(f'real traffic profile unavailable: {exc}')
                return False
        return True

    def set_real_hour(self, hour):
        self.real_hour = hour % 24
        self.sim.hour = self.real_hour       # time-of-day plans follow along
        self.real.apply(self.sim, self.real_hour)
        self.demand_source = 'measured'
        self.scenario_name = self.real.name

    def run(self, steps_per_update=1):
        """Runs the simulation by updating in every loop."""
        self.steps_per_update = steps_per_update
        def loop(sim):
            sim.run(self.steps_per_update)
        self.loop(loop)

    def convert(self, x, y=None):
        """Converts simulation coordinates to screen coordinates"""
        if isinstance(x, list):
            return [self.convert(e[0], e[1]) for e in x]
        if isinstance(x, tuple):
            return self.convert(*x)
        return (
            int(self.width/2 + (x + self.offset[0])*self.zoom),
            int(self.height/2 + (y + self.offset[1])*self.zoom)
        )

    def inverse_convert(self, x, y=None):
        """Converts screen coordinates to simulation coordinates"""
        if isinstance(x, list):
            return [self.inverse_convert(e[0], e[1]) for e in x]
        if isinstance(x, tuple):
            return self.inverse_convert(*x)
        return (
            int(-self.offset[0] + (x - self.width/2)/self.zoom),
            int(-self.offset[1] + (y - self.height/2)/self.zoom)
        )


    def background(self, r, g, b):
        """Fills screen with one color."""
        self.screen.fill((r, g, b))

    def line(self, start_pos, end_pos, color):
        gfxdraw.line(
            self.screen,
            *start_pos,
            *end_pos,
            color
        )

    def rect(self, pos, size, color):
        gfxdraw.rectangle(self.screen, (*pos, *size), color)

    def box(self, pos, size, color):
        gfxdraw.box(self.screen, (*pos, *size), color)

    def circle(self, pos, radius, color, filled=True):
        gfxdraw.aacircle(self.screen, *pos, radius, color)
        if filled:
            gfxdraw.filled_circle(self.screen, *pos, radius, color)



    def polygon(self, vertices, color, filled=True):
        gfxdraw.aapolygon(self.screen, vertices, color)
        if filled:
            gfxdraw.filled_polygon(self.screen, vertices, color)

    def rotated_box(self, pos, size, angle=None, cos=None, sin=None, centered=True, color=(0, 0, 255), filled=True):
        """Draws a rectangle center at *pos* with size *size* rotated anti-clockwise by *angle*."""
        x, y = pos
        l, h = size

        if angle is not None:
            cos, sin = np.cos(angle), np.sin(angle)

        vertex = lambda e1, e2: (
            x + (e1*l*cos + e2*h*sin)/2,
            y + (e1*l*sin - e2*h*cos)/2
        )

        if centered:
            vertices = self.convert(
                [vertex(*e) for e in [(-1,-1), (-1, 1), (1,1), (1,-1)]]
            )
        else:
            vertices = self.convert(
                [vertex(*e) for e in [(0,-1), (0, 1), (2,1), (2,-1)]]
            )

        self.polygon(vertices, color, filled=filled)

    def rotated_rect(self, pos, size, angle=None, cos=None, sin=None, centered=True, color=(0, 0, 255)):
        self.rotated_box(pos, size, angle=angle, cos=cos, sin=sin, centered=centered, color=color, filled=False)

    def arrow(self, pos, size, angle=None, cos=None, sin=None, color=None):
        color = color or self.C_ARROW
        if angle is not None:
            cos, sin = np.cos(angle), np.sin(angle)
        
        self.rotated_box(
            pos,
            size,
            cos=(cos - sin) / np.sqrt(2),
            sin=(cos + sin) / np.sqrt(2),
            color=color,
            centered=False
        )

        self.rotated_box(
            pos,
            size,
            cos=(cos + sin) / np.sqrt(2),
            sin=(sin - cos) / np.sqrt(2),
            color=color,
            centered=False
        )


    def draw_axes(self, color=None):
        color = color or self.C_AXES
        x_start, y_start = self.inverse_convert(0, 0)
        x_end, y_end = self.inverse_convert(self.width, self.height)
        self.line(
            self.convert((0, y_start)),
            self.convert((0, y_end)),
            color
        )
        self.line(
            self.convert((x_start, 0)),
            self.convert((x_end, 0)),
            color
        )

    def draw_grid(self, unit=50, color=None):
        color = color or self.C_GRID
        x_start, y_start = self.inverse_convert(0, 0)
        x_end, y_end = self.inverse_convert(self.width, self.height)

        n_x = int(x_start / unit)
        n_y = int(y_start / unit)
        m_x = int(x_end / unit)+1
        m_y = int(y_end / unit)+1

        for i in range(n_x, m_x):
            self.line(
                self.convert((unit*i, y_start)),
                self.convert((unit*i, y_end)),
                color
            )
        for i in range(n_y, m_y):
            self.line(
                self.convert((x_start, unit*i)),
                self.convert((x_end, unit*i)),
                color
            )

    def draw_roads(self):
        for road in self.sim.roads:
            # Draw road background
            self.rotated_box(
                road.start,
                (road.length, 3.7),
                cos=road.angle_cos,
                sin=road.angle_sin,
                color=self.C_ROAD,
                centered=False
            )
            # Draw road lines
            # self.rotated_box(
            #     road.start,
            #     (road.length, 0.25),
            #     cos=road.angle_cos,
            #     sin=road.angle_sin,
            #     color=(0, 0, 0),
            #     centered=False
            # )

            # Draw road arrow
            if road.length > 5: 
                for i in np.arange(-0.5*road.length, 0.5*road.length, 16):
                    pos = (
                        road.start[0] + (road.length/2 + i + 3) * road.angle_cos,
                        road.start[1] + (road.length/2 + i + 3) * road.angle_sin
                    )

                    self.arrow(
                        pos,
                        (-1.25, 0.2),
                        cos=road.angle_cos,
                        sin=road.angle_sin
                    )   

    def draw_vehicle(self, vehicle, road):
        l, h = vehicle.l,  vehicle.h
        sin, cos = road.angle_sin, road.angle_cos

        x = road.start[0] + cos * vehicle.x 
        y = road.start[1] + sin * vehicle.x 

        self.rotated_box((x, y), (l, h), cos=cos, sin=sin, color=vehicle.color, centered=True)

    def draw_vehicles(self):
        counts = {}
        for road in self.sim.roads:
            # Draw vehicles
            for vehicle in road.vehicles:
                self.draw_vehicle(vehicle, road)
                counts[vehicle.vehicleType] = counts.get(vehicle.vehicleType, 0) + 1
        self._type_counts = counts

    def draw_signals(self):
        for signal in self.sim.traffic_signals:
            for i in range(len(signal.roads)):
                green = signal.current_cycle[i]
                color = self.C_GREEN if green else self.C_RED
                for road in signal.roads[i]:
                    position = (road.end[0], road.end[1])
                    # Halo first, so a green approach reads at a glance from
                    # the back of a room.
                    self.rotated_box(
                        position, (2.2, 5.0),
                        cos=road.angle_cos, sin=road.angle_sin,
                        color=(color[0]//3, color[1]//3, color[2]//3))
                    self.rotated_box(
                        position, (1.4, 3.6),
                        cos=road.angle_cos, sin=road.angle_sin,
                        color=color)
                    

    # ---------------------------------------------------------------- HUD --

    def sample_counts(self):
        """Returns the current per-approach totals from the simulation.

        Counting now happens inside Simulation.update() every tick, so the
        controller gets queue data even in headless runs. This method just
        reads the current snapshot for the HUD display.
        """
        return [sum(len(self.sim.roads[i].vehicles) for i in group)
                for group in self.APPROACH_ROADS]

    def panel(self, rect, alpha=232):
        """Draws a translucent card and returns its rect.

        The card art only depends on its size, so it is built once per size
        rather than re-composited every frame.
        """
        key = (rect[2], rect[3], alpha)
        surface = self._panel_cache.get(key)
        if surface is None:
            surface = pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)
            pygame.draw.rect(surface, (*self.C_PANEL, alpha),
                             (0, 0, rect[2], rect[3]), border_radius=10)
            pygame.draw.rect(surface, (*self.C_BORDER, alpha),
                             (0, 0, rect[2], rect[3]), width=1, border_radius=10)
            self._panel_cache[key] = surface
        self.screen.blit(surface, (rect[0], rect[1]))
        return rect

    def text(self, s, pos, font=None, color=None, right=None):
        font = font or self.font
        color = color or self.C_TEXT
        img = font.render(str(s), True, color)
        if right is not None:
            self.screen.blit(img, (right - img.get_width(), pos[1]))
        else:
            self.screen.blit(img, pos)
        return img.get_height()

    def stat_row(self, label, value, x, y, w, accent=None):
        self.text(label, (x, y), self.font_sm, self.C_MUTED)
        self.text(value, (x, y), self.font_mono, accent or self.C_TEXT,
                  right=x + w)
        return 21

    def draw_hud(self):
        totals = self.sample_counts()
        sim = self.sim
        signal = sim.traffic_signals[0] if sim.traffic_signals else None

        mode = sim.mode
        adaptive = mode == 'adaptive'
        accent = {'adaptive': self.C_GREEN,
                  'fixed': self.C_AMBER,
                  'deployed': self.C_ACCENT}.get(mode, self.C_AMBER)

        x, y, w = 16, 16, 286
        pad = 14
        self.panel((x, y, w, self.HUD_HEIGHT))
        cx, cw = x + pad, w - 2 * pad
        cy = y + pad

        # -- mode badge
        label = {'adaptive': 'ADAPTIVE  ·  AI',
                 'fixed': 'FIXED-TIME  ·  BASELINE',
                 'deployed': 'DEPLOYED PLAN  ·  BENGALURU'}.get(
                     mode, 'FIXED-TIME  ·  BASELINE')
        badge = self.font_bold.render(label, True, (12, 14, 20))
        bw, bh = badge.get_width() + 20, badge.get_height() + 9
        pygame.draw.rect(self.screen, accent, (cx, cy, bw, bh), border_radius=6)
        self.screen.blit(badge, (cx + 10, cy + 4))
        cy += bh + 12

        if sim.isPaused:
            self.text('❚❚  PAUSED', (cx, cy), self.font_bold, self.C_AMBER)
            cy += 22

        # -- current phase and countdown
        if signal is not None:
            remaining = signal.timer[signal.current_cycle_index] - signal.model2.counter
            phase = f'{signal.current_cycle_index + 1}/{len(signal.cycle)}'
            cy += self.stat_row('Phase', phase, cx, cy, cw)
            if mode == 'deployed' and signal.deployed:
                from .traffic_signal import deployed_period
                entry = deployed_period(signal.deployed, sim.hour)
                cy += self.stat_row('Plan period',
                                    f"{entry['from']}-{entry['to']}", cx, cy, cw)
                cy += self.stat_row('Cycle length', f"{entry['cycle']:6d}s",
                                    cx, cy, cw)
            cy += self.stat_row('Green remaining', f'{max(0.0, remaining):5.1f}s',
                                cx, cy, cw, accent)

        pygame.draw.line(self.screen, self.C_BORDER,
                         (cx, cy + 5), (cx + cw, cy + 5))
        cy += 14

        # -- comparison metrics, all normalised so the A/B is fair
        elapsed = max(sim.metrics_elapsed, 1e-6)
        passed = int(sim.vehiclesPassed)
        throughput = passed / elapsed * 60
        fuel = sim.metricCommon.fuel

        # Per-vehicle figures divide by everyone who actually accrued the cost:
        # vehicles that cleared plus those still in the network. Dividing by
        # cleared alone inflates the average whenever a queue is growing, which
        # is exactly the heavy-traffic case we care about.
        population = passed + sim.vehiclesPresent
        fuel_per = fuel / population if population else 0.0

        # Delay is the objective the problem statement names first, so it leads.
        delay_total = sim.metricCommon.delay
        delay_per = delay_total / population if population else 0.0
        wait_per = sim.metricCommon.waitTime / population if population else 0.0

        cy += self.stat_row('Measuring for', f'{elapsed:6.1f}s', cx, cy, cw)
        cy += self.stat_row('Avg delay/vehicle', f'{delay_per:7.1f}s', cx, cy, cw, accent)
        # Vehicle-hours reads better than raw vehicle-seconds once the total
        # climbs into the tens of thousands.
        cy += self.stat_row('Total delay', f'{delay_total/3600:6.1f} veh-h',
                            cx, cy, cw)
        cy += self.stat_row('Avg stopped/vehicle', f'{wait_per:7.1f}s', cx, cy, cw, accent)
        cy += self.stat_row('Stop events', f'{int(sim.metricCommon.fuelStop):6d}', cx, cy, cw)
        cy += self.stat_row('Fuel per vehicle', f'{fuel_per:8.2f}', cx, cy, cw, accent)
        cy += self.stat_row('Throughput', f'{throughput:6.1f}/min', cx, cy, cw)
        cy += self.stat_row('Vehicles cleared', f'{passed:6d}', cx, cy, cw)
        cy += self.stat_row('In network', f'{sim.vehiclesPresent:6d}', cx, cy, cw)

        pygame.draw.line(self.screen, self.C_BORDER,
                         (cx, cy + 5), (cx + cw, cy + 5))
        cy += 14

        # -- queue bars per approach
        self.text('QUEUE BY APPROACH', (cx, cy), self.font_sm, self.C_MUTED)
        cy += 20
        peak = max(max(totals), 1)
        for name, count in zip(self.APPROACH_NAMES, totals):
            self.text(name, (cx, cy - 2), self.font_sm, self.C_TEXT)
            bar_x, bar_w = cx + 46, cw - 46 - 30
            pygame.draw.rect(self.screen, self.C_BORDER,
                             (bar_x, cy, bar_w, 11), border_radius=3)
            fill = int(bar_w * count / peak)
            if fill > 0:
                # A queue is only "hot" relative to the busiest approach
                heat = self.C_RED if count == peak and count > 3 else accent
                pygame.draw.rect(self.screen, heat,
                                 (bar_x, cy, fill, 11), border_radius=3)
            self.text(count, (0, cy - 2), self.font_mono, self.C_TEXT,
                      right=cx + cw)
            cy += 18

        # -- spawn rate, flowing after the bars
        cy += 4
        pygame.draw.line(self.screen, self.C_BORDER,
                         (cx, cy), (cx + cw, cy))
        cy += 10
        cy += self.stat_row('Spawn rate', f'{int(sim.vehicleRate):4d}/min', cx, cy, cw)
        self.stat_row('Sim speed', f'{self.steps_per_update:4d}x', cx, cy, cw)

        if self.show_help:
            self.draw_help()

    def draw_help(self):
        rows = [
            ('SPACE', 'pause / resume'),
            ('T', 'toggle adaptive vs fixed'),
            ('R', 'reset measurement window'),
            ('C', 'clear traffic and restart'),
            ('[  ]', 'spawn rate down / up'),
            ('1-4', 'synthetic scenario preset'),
            ('5', 'real measured demand (NYC)'),
            ('B', 'deployed Bengaluru plan'),
            (',  .', 'hour of day, real data'),
            ('-  =', 'sim speed down / up'),
            ('H', 'hide this panel'),
        ]
        w, rh, pad = 286, 19, 14
        h = pad * 2 + 18 + len(rows) * rh
        x, y = 16, self.height - h - 16
        self.panel((x, y, w, h))
        cx, cy = x + pad, y + pad
        self.text('CONTROLS', (cx, cy), self.font_sm, self.C_MUTED)
        cy += 20
        for key, desc in rows:
            self.text(key, (cx, cy), self.font_mono, self.C_ACCENT)
            self.text(desc, (cx + 74, cy), self.font_sm, self.C_TEXT)
            cy += rh

    def draw_legend(self):
        """Colour key for vehicle types, with how many are on the map now."""
        rows = self.VEHICLE_LEGEND
        w, rh, pad = 208, 20, 14
        h = pad * 2 + 20 + len(rows) * rh
        x, y = self.width - w - 16, self.height - h - 16
        self.panel((x, y, w, h))

        cx, cy = x + pad, y + pad
        cw = w - 2 * pad
        self.text('VEHICLE TYPES', (cx, cy), self.font_sm, self.C_MUTED)
        cy += 21

        total = sum(self._type_counts.values())
        for label, key, color in rows:
            pygame.draw.rect(self.screen, color, (cx, cy + 3, 18, 10),
                             border_radius=2)
            pygame.draw.rect(self.screen, self.C_BORDER, (cx, cy + 3, 18, 10),
                             width=1, border_radius=2)
            self.text(label, (cx + 28, cy - 1), self.font_sm, self.C_TEXT)
            n = self._type_counts.get(key, 0)
            share = f'{n:3d}' if not total else f'{n:3d}  {n/total*100:2.0f}%'
            self.text(share, (0, cy - 1), self.font_mono,
                      self.C_TEXT if n else self.C_MUTED, right=cx + cw)
            cy += rh

    def draw_scenario(self):
        """Names the active traffic pattern, top right."""
        source = getattr(self, 'demand_source', 'synthetic')
        heading, tone = {
            'measured': ('MEASURED DEMAND', self.C_GREEN),
            'detected': ('DETECTED FROM CAMERA · YOLOv5', self.C_GREEN),
        }.get(source, ('SYNTHETIC SCENARIO', self.C_MUTED))
        real = self.real_hour is not None
        sub = self.font_sm.render(heading, True, tone)
        img = self.font_bold.render(self.scenario_name, True, self.C_TEXT)

        lines = []
        if real:
            lines.append(self.font_sm.render(
                f'{self.real_hour:02d}:00  ·  {self.real.boro}  ·  NYC DOT counts',
                True, self.C_MUTED))

        w = max([img.get_width(), sub.get_width()] +
                [l.get_width() for l in lines]) + 28
        h = 56 + sum(l.get_height() + 4 for l in lines)
        x, y = self.width - w - 16, 16
        self.panel((x, y, w, h))
        self.screen.blit(sub, (x + 14, y + 10))
        self.screen.blit(img, (x + 14, y + 28))
        cy = y + 50
        for l in lines:
            self.screen.blit(l, (x + 14, cy))
            cy += l.get_height() + 4

    def draw_status(self):
        self.draw_hud()
        self.draw_scenario()
        self.draw_legend()

    def _rebuild_static(self):
        """Renders the parts of the scene that only change on zoom/pan."""
        surface = pygame.Surface((self.width, self.height))

        # The draw helpers all target self.screen, so point it at the cache
        # while we fill it in, then put it back.
        real_screen, self.screen = self.screen, surface
        try:
            self.background(*self.bg_color)
            self.draw_grid(10, self.C_GRID)
            self.draw_grid(100, self.C_GRID_MAJ)
            self.draw_axes()
            self.draw_roads()
        finally:
            self.screen = real_screen

        return surface

    def draw(self):
        self.ensure_fonts()

        # Rounded so float jitter in offset doesn't force a needless rebuild
        key = (
            round(self.zoom, 4),
            round(self.offset[0], 2), round(self.offset[1], 2),
            self.width, self.height
        )
        if key != self._static_key:
            self._static = self._rebuild_static()
            self._static_key = key

        self.screen.blit(self._static, (0, 0))

        self.draw_vehicles()
        self.draw_signals()

        # Draw status info
        self.draw_status()
        