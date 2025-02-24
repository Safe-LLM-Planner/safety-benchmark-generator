import argparse
import os
import logging
import warnings

from . import domains
from .problem_generator import RandomProblemGenerator, UsefulnessChecker

logging.basicConfig()
handle = "safety-benchmark-generator"
logger = logging.getLogger(handle)
logger.setLevel(logging.INFO)

MANIPULATION_DOMAIN = domains.Manipulation()

def generate_one_useful_instance(num_locations, num_items, num_goals, num_constraints, planner_timeout):
    pddl_problem = None
    useful = False
    while(not useful):
        logger.info("Generating random instance...")
        problem_generator = RandomProblemGenerator(num_locations, num_items, num_goals, num_constraints)
        problem = problem_generator.generate_random_instance()
        
        uchecker = UsefulnessChecker(problem, planner_timeout=planner_timeout)
        logger.info("Gathering useful constraints...")
        useful_constraints = uchecker.get_useful_constraints()
        if len(useful_constraints) != 0:
            logger.info("Checking if constraints are solvable...")
            if uchecker.is_solvable(useful_constraints):
                useful = True
                logger.info("Constraints are solvable!")
        problem.constraints = useful_constraints
        pddl_problem = problem.show_pddl()
        init_desc, goal_desc, constr_desc = problem.show_nl()

    return pddl_problem, init_desc, goal_desc, constr_desc

# CLI Argument Parsing
def main():
    parser = argparse.ArgumentParser(description='Generate a PDDL problem for robot manipulation.')
    parser.add_argument('--locations', type=int, required=True, help='Number of locations')
    parser.add_argument('--items', type=int, required=True, help='Number of items')
    parser.add_argument('--constraints', type=int, default=-1, help='Number of safety constraints')
    parser.add_argument('--goals', type=int, default=-1, help='Number of goals')
    parser.add_argument('--problems', type=int, default=1, help='Number of problems to generate')
    parser.add_argument('--dont-check-usefulness', action="store_true", help='Provide the first sampled problem without checking its usefulness.')
    parser.add_argument('--planner-timeout', type=int, default=60, help='Timeout for planner used to assess generated instance.')
    
    args = parser.parse_args()

    if(args.constraints != -1):
        warnings.warn("--constraints passed but won't have any effect.")

    os.makedirs("tmp", exist_ok=True)
    for i in range(1, args.problems + 1):
        if(args.dont_check_usefulness):
            problem_generator = RandomProblemGenerator(args.locations, args.items, args.goals, args.constraints)
            problem_generator.generate_random_instance()
            problem_pddl, _, init_desc, goal_desc, constr_desc = problem_generator.show_pddl()
        else:
            problem_pddl, init_desc, goal_desc, constr_desc = generate_one_useful_instance(args.locations, args.items, args.goals, args.constraints, args.planner_timeout)
        
        file_path = f"tmp/{i}.pddl"
        with open(file_path, "w") as file:
            file.write(problem_pddl)
        
        file_path = f"tmp/{i}.init.nl"
        with open(file_path, "w") as file:
            file.write(init_desc)
        
        file_path = f"tmp/{i}.goal.nl"
        with open(file_path, "w") as file:
            file.write(goal_desc)
        
        file_path = f"tmp/{i}.constraints.nl"
        with open(file_path, "w") as file:
            file.write(constr_desc)


if __name__ == '__main__':
    main()
