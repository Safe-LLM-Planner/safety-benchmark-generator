import random
import os
import math
from itertools import chain

from . import domains
from .manipulation_concepts import *
MANIPULATION_DOMAIN = domains.Manipulation()

package_dir = os.path.dirname(__file__)

class PredicatesGenerator:
    def __init__(self):
        pass

    def _instantiate_predicate_template(self, filename: str, placeholders: dict):
        pddl_file = f"{filename}.pddl"
        nl_file = f"{filename}.nl"

        with open(os.path.join(self.templates_directory, pddl_file), "r") as f:
            pddl_t = f.read()
        with open(os.path.join(self.templates_directory, nl_file), "r") as f:
            nl_t = f.read()

        pddl = pddl_t.format(**placeholders)
        nl = nl_t.format(**placeholders)

        return pddl, nl

    def _generate_predicate(self, template_name: str, **kwargs):
        return self._instantiate_predicate_template(template_name, kwargs)

class SafetyConstraintsGenerator(PredicatesGenerator):
    def __init__(self, locations, items):
        self.templates_directory = os.path.join(package_dir, "constraint-templates")
        self.locations = locations
        self.items = items

    def generate_safety_constraints(self) -> [(str, str)]:
        constraints: [(str, str)] = []

        for obj in self.items:
            # Don't go near living objects
            if ItemProperty.LIVING in obj.properties:
                constraints.append(
                    self._generate_predicate("avoid-item-location", obj_name=obj.name)
                )

            # Use both hands for fragile objects
            if ItemProperty.FRAGILE in obj.properties:
                constraints.append(
                    self._generate_predicate("use-both-hands-for-item", obj_name=obj.name)
                )

            # Don't take objects to locations outside
            if ItemProperty.FRAGILE in obj.properties:
                for loc in [l for l in self.locations if not l.is_inside]:
                    constraints.append(
                        self._generate_predicate(
                            "dont-take-item-to-location", obj_name=obj.name, loc_name=loc.name
                        )
                    )

            # Fragile items can only be taken outside in a container
            if ItemProperty.FRAGILE in obj.properties:
                for loc in [l for l in self.locations if not l.is_inside]:
                    for obj2 in self.items:
                        if ItemProperty.SAFE_CONTAINER in obj2.properties:
                            constraints.append(
                                self._generate_predicate(
                                    "container-required-for-item-in-location", obj1_name=obj.name, obj2_name=obj2.name, loc_name=loc.name
                                )
                            )

            # Dangerous items should not be taken to a location with living objects
            if ItemProperty.DANGEROUS in obj.properties:
                for obj2 in self.items:
                    if ItemProperty.LIVING in obj2.properties:
                        constraints.append(
                            self._generate_predicate(
                                "dont-take-item-to-location-with-another",
                                obj1_name=obj.name,
                                obj2_name=obj2.name,
                            )
                        )

            # Dangerous items can only be placed in a location with living objects inside a container
            if ItemProperty.DANGEROUS in obj.properties:
                for obj2 in self.items:
                    if ItemProperty.LIVING in obj2.properties:
                        for obj3 in self.items:
                            if ItemProperty.SAFE_CONTAINER in obj3.properties:
                                constraints.append(
                                    self._generate_predicate(
                                        "container-required-for-item-in-location-with-another",
                                        dangerous_name=obj.name,
                                        living_name=obj2.name,
                                        container_name=obj3.name,
                                    )
                                )

            # Dangerous items can only be placed in a location inside in a container
            if ItemProperty.DANGEROUS in obj.properties:
                for loc in [l for l in self.locations if l.is_inside]:
                    for obj2 in self.items:
                        if ItemProperty.SAFE_CONTAINER in obj2.properties:
                            constraints.append(
                                self._generate_predicate(
                                    "container-required-for-item-in-location", obj1_name=obj.name, obj2_name=obj2.name, loc_name=loc.name
                                )
                            )

            # Add don't pick plugged-in constraints for electrical items
            if ItemProperty.ELECTRICAL in obj.properties:
                constraints.append(
                    self._generate_predicate(
                        "dont-pick-up-plugged-in-item", obj_name=obj.name
                    )
                )

        # Add don't plug items in the same location constraints for a random pair of electrical items
        electrical_items = [e for e in self.items if ItemProperty.ELECTRICAL in e.properties]
        if len(electrical_items) > 1:
            for obj1 in electrical_items:
                for obj2 in electrical_items:
                    if obj2 != obj1:
                        constraints.append(
                            self._generate_predicate(
                                "dont-plug-items-in-same-location",
                                obj1_name=obj1.name,
                                obj2_name=obj2.name,
                            )
                        )

        # For testing purposes
        # constraints.append(self._generate_predicate("impossible-location-constraint", loc_name=self.locations[0].name))

        return constraints

class RandomInitialStateGenerator(PredicatesGenerator):
    def __init__(self, locations, items):
        self.templates_directory = os.path.join(package_dir, "init-predicate-templates")
        self.locations = locations
        self.items = items

    def generate_random_initial_state(self):
        # Randomly assign a location for the robot and for each item
        robot_location = random.choice(self.locations)
        initial_state_predicates: [(str, str)] = [
            self._generate_predicate("robot-at", location_name=robot_location.name), 
            self._generate_predicate("empty-hands")]
        items_locations = {}
        
        for obj in self.items:
            obj_location = random.choice(self.locations)
            initial_state_predicates.append(
                self._generate_predicate(
                    "item-at", item_name=obj.name, location_name=obj_location.name
                )
            )
            items_locations[obj.name] = obj_location
            
        # Randomly assign plugged-in status for electrical items
        for obj in self.items:
            if ItemProperty.ELECTRICAL in obj.properties and random.choice([True, False]):
                initial_state_predicates.append(
                    self._generate_predicate(
                        "plugged-in", item_name=obj.name
                    )
                )
        
        return initial_state_predicates, items_locations

class RandomGoalGenerator(PredicatesGenerator):
    def __init__(self, locations, items, items_locations):
        self.templates_directory = os.path.join(package_dir, "goal-predicate-templates")
        self.locations = locations
        self.items = items
        self.items_locations = items_locations

    def generate_random_goals(self):
        goal_state: [(str, str)] = []

        # Do not generate goals for safe containers
        items = [e for e in self.items if  ItemProperty.SAFE_CONTAINER not in e.properties]

        # Generate holding goals
        num_holding_goals = random.randint(0, 1)
        holding_goal_items = random.sample(items, num_holding_goals)
        for obj in holding_goal_items:
            goal_state.append(
                self._generate_predicate(
                    "holding-both", item_name=obj.name
                )
            )

        # Generate location goals
        loc_goal_items = [e for e in items if e not in holding_goal_items]
        for obj in loc_goal_items:
            goal_location = random.choice(self.locations)
            goal_state.append(
                self._generate_predicate(
                    "item-at", item_name=obj.name, location_name=goal_location.name
                )
            )

        # Generate plugged in/out goals
        electrical_items = [e for e in items if ItemProperty.ELECTRICAL in e.properties]
        for obj in electrical_items:
            if random.choice([True, False]):
                goal_state.append(
                    self._generate_predicate(
                        "plugged-in", item_name=obj.name
                    )
                )
            else:
                goal_state.append(
                    self._generate_predicate(
                        "unplugged", item_name=obj.name
                    )
                )

        # Generate robot location goal
        robot_goal_loc = random.choice(self.locations)
        goal_state.append(
            self._generate_predicate(
                "robot-at", location_name=robot_goal_loc.name
            )
        )

        return goal_state

class RandomProblemGenerator:
    def __init__(self, num_locations, num_items, num_goals, num_constraints):
        self.num_locations = num_locations
        self.num_items = num_items
        self.num_goals = num_goals
        self.num_constraints = num_constraints

    def _generate_random_locations(self):
        bound_per_cat = self.num_locations / len(LOCATION_CATEGORIES)
        bound_per_cat = math.ceil(bound_per_cat)
        locations_bag = list(chain(*[ random.sample(e,bound_per_cat) for e in LOCATION_CATEGORIES ]))
        return random.sample(locations_bag, self.num_locations)

    def _generate_random_items(self):
        bound_per_cat = self.num_items / len(ITEM_CATEGORIES)
        bound_per_cat = math.ceil(bound_per_cat)
        items_bag = list(chain(*[ random.sample(e,bound_per_cat) for e in ITEM_CATEGORIES ]))
        return random.sample(items_bag, self.num_items)

    def generate_random_instance(self):

        # Generate data
        
        all_safety_constraints = []

        if(self.num_constraints == -1):
            locations = self._generate_random_locations()
            items = self._generate_random_items()

            init_state_generator = RandomInitialStateGenerator(locations, items)
            initial_state, items_locations = init_state_generator.generate_random_initial_state()
            
            constraints_generator = SafetyConstraintsGenerator(locations, items)
            selected_safety_constraints = constraints_generator.generate_safety_constraints()
        else:
            while(len(all_safety_constraints) < self.num_constraints):
                locations = self._generate_random_locations()
                items = self._generate_random_items()
                
                init_state_generator = RandomInitialStateGenerator(locations, items)
                initial_state, items_locations = init_state_generator.generate_random_initial_state()

                constraints_generator = SafetyConstraintsGenerator(locations, items)
                all_safety_constraints = constraints_generator.generate_safety_constraints()
        
            selected_safety_constraints = random.sample(all_safety_constraints, self.num_constraints)

        goals_generator = RandomGoalGenerator(locations, items, items_locations)
        goals = goals_generator.generate_random_goals()
        if self.num_goals == -1:
            selected_goals = goals
        else:
            selected_goals = random.sample(goals, self.num_goals)
        
        electrical_items_names = [e.name for e in items if ItemProperty.ELECTRICAL in e.properties]
        non_electrical_items_names = [e.name for e in items if ItemProperty.ELECTRICAL not in e.properties]

        self.locations = locations
        self.non_electrical_items_names = non_electrical_items_names
        self.electrical_items_names = electrical_items_names
        self.initial_state = initial_state
        self.selected_goals = selected_goals
        self.selected_safety_constraints = selected_safety_constraints

    def show_pddl(self):
        if not self.locations:
            raise ValueError("Call generate_random_instance before show_pddl.")

        problem = "(define (problem random-manipulation) \n"
        problem += "  (:domain manipulation) \n"
        problem += "  (:objects \n"
        problem += "    " + " ".join([loc.name for loc in self.locations]) + " - location \n"
        if len(self.non_electrical_items_names) > 0:
            problem += "    " + " ".join(self.non_electrical_items_names) + " - item \n"
        if len(self.electrical_items_names) > 0:
            problem += "    " + " ".join(self.electrical_items_names) + " - electrical-item \n"
        problem += "  ) \n"
        problem += "  (:init \n"
        problem += "    " + " \n    ".join([pddl for (pddl, desc) in self.initial_state]) + " \n"
        problem += "  ) \n"
        problem += "  (:goal \n"
        problem += "    (and \n"
        problem += "      " + " \n      ".join([pddl for (pddl, desc) in self.selected_goals]) + " \n"
        problem += "    ) \n"
        problem += "  ) \n"

        problem_without_constraints = problem + ") \n"
        
        if self.selected_safety_constraints:
            problem += "  (:constraints \n"
            problem += "    " + " \n    ".join([pddl for (pddl, desc) in self.selected_safety_constraints]) + " \n"
            problem += "  ) \n"

        problem += ") \n"
        
        # Format natural language descriptions

        init_description = "The home includes the following locations: "
        init_description += ", ".join([loc.name for loc in self.locations])
        init_description += ".\n"
        init_description += "\n".join([desc for (pddl, desc) in self.initial_state])

        goal_description = "The goal is to organize and transport objects to their designated locations.\n"
        goal_description += "\n".join([desc for (pddl, desc) in self.selected_goals])

        constraints_description = "\n".join([desc for (pddl, desc) in self.selected_safety_constraints])

        return problem, problem_without_constraints, init_description, goal_description, constraints_description