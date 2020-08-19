from n_sided_polygon import polygon
from scipy import spatial
from copy import deepcopy

class PointAndOptionManager:
    def __init__(self, dimensions, options_left, options_right, FPS, hub_radius):
        # Screen and overlay dimensions.
        self.screenwidth = dimensions["screenwidth"]
        self.screenheight = dimensions["screenheight"]
        self.overlay_width = dimensions["overlay_width"]
        self.overlay_height = dimensions["overlay_height"]

        # Options and option properties
        self.left_options = {0: options_left[0], 1: options_left[1]}
        self.right_options = {0: options_right[0], 1: options_right[1]}
        self.num_options = len(self.left_options[0])

        # Polygon radius and points
        self.radius = hub_radius
        self.left_hub_center = self.screenwidth // 4
        self.right_hub_center = (self.screenwidth // 4) * 3
        self.half_screenheight = self.screenheight // 2

        # Points storage.
        self.left_points = polygon(sides=self.num_options,radius=self.radius, 
                                    translation=[self.left_hub_center, self.half_screenheight])
        
        self.right_points = polygon(sides=self.num_options, radius=self.radius, 
                                    translation=[self.right_hub_center, self.half_screenheight])

        self.cursor = {"l_x": 0, "l_y": 0, "r_x": 0, "r_y": 0}

        # Adding idle axis as an answer for nearest neighbour
        self.answers = {"left_0": deepcopy(self.left_options[0]), "left_1": deepcopy(self.left_options[1]),
                        "right_0": deepcopy(self.right_options[0]), "right_1": deepcopy(self.right_options[1])}

        for key in self.answers.keys():
            self.answers[key].append("IDLE")

        self.points_for_answers = {"left": [], "right": []}

        # A second split into milliseconds.
        self.opt_count = 0
        # Num option buffer slots to check for unique in set.
        self.opt_max = self.get_timekey_slots(FPS=FPS)
        self.opt_buf = {"left": [0 for i in range(self.opt_max)], "right": [0 for i in range(self.opt_max)]}
        self.opt_last = {"left": 0, "right": 0}

        self.key_state = {"left_0": {}, "left_1": {}, "right_0": {}, "right_1": {}}
        for key in self.answers:
            for val in range(len(self.answers[key])):
                self.key_state[key][val] = False
        
        for key in self.key_state.keys():
            val = len(self.key_state[key])
            self.key_state[key][val] = True



        self.last_selected = {"left": None, "right": None}


    def update_cursor(self, l_x, l_y, r_x, r_y):
        self.cursor["l_x"] = l_x
        self.cursor["l_y"] = l_y
        self.cursor["r_x"] = r_x
        self.cursor["r_y"] = r_y

    def get_cursor(self):
        l_x = self.cursor["l_x"]
        l_y = self.cursor["l_y"]
        r_x = self.cursor["r_x"]
        r_y = self.cursor["r_y"]
        return l_x, l_y, r_x, r_y

    def update_idle_points(self, idle_axis):
        # Adding idle axis as a point for nearest neighbour
        self.points_for_answers["left"] = deepcopy(self.left_points)
        self.points_for_answers["right"] = deepcopy(self.right_points)
        self.points_for_answers["left"].append((idle_axis[0], idle_axis[1]))
        self.points_for_answers["right"].append((idle_axis[2], idle_axis[3]))

    def get_closest_points(self):
        # If closest to idle, ignore.
        l_distance,l_index = spatial.KDTree(self.points_for_answers["left"]).query([(self.cursor["l_x"], self.cursor["l_y"])])
        r_distance,r_index = spatial.KDTree(self.points_for_answers["right"]).query([(self.cursor["r_x"], self.cursor["r_y"])])
        l_index, r_index = l_index[0], r_index[0]

        return {"left_0": self.answers["left_0"][l_index], "right_0": self.answers["right_0"][r_index],
                "left_1": self.answers["left_1"][l_index], "right_1": self.answers["right_1"][r_index]}

    def update(self, variant=0):
        variant = str(variant)
        closest_points = self.get_closest_points()

        for key in closest_points.keys():
            # Check if key ends with variant number.
            if key[-1] == variant:
                # Take away the "_0" or "_1"
                buf_key = key[:-2]
                # The minus one for using it as an index.
                if self.opt_count < self.opt_max:
                    self.opt_last[buf_key] = closest_points[key]
                    self.opt_buf[buf_key][self.opt_count] = closest_points[key]
                    self.opt_count += 1
                else:
                    self.opt_last[buf_key] = closest_points[key]
                    self.opt_count = 0
                    self.opt_buf[buf_key][self.opt_count] = closest_points[key]

    def get_timekey_slots(self, key_delay=250, FPS=60):
        time_slot = 1000 // FPS
        time_counter = 0
        # This is out of a second in ms, i.e. 1000 slots.
        slot_count = 0
        for i in range(1000):
            if time_counter < key_delay:
                time_counter += time_slot
                slot_count += 1
        
        return slot_count

    def print_option(self, supress_idle=True):
        l_set, r_set = set(self.opt_buf["left"]), set(self.opt_buf["right"])
        uniq_l = len(l_set) == 1
        uniq_r = len(r_set) == 1
        if uniq_l:
            if (self.opt_last["left"] == "IDLE") != supress_idle:
                if self.opt_last["left"] != self.last_selected["left"]:
                    self.last_selected["left"] = self.opt_last["left"]
                    print(self.opt_last["left"])
        if uniq_r:
            if (self.opt_last["right"] == "IDLE") != supress_idle:
                if self.opt_last["right"] != self.last_selected["right"]:
                    self.last_selected["right"] = self.opt_last["right"]
                    print(self.opt_last["right"])