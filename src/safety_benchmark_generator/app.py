import argparse
import os

from llm_planners import planners
from . import domains
from planning_eval_framework.plan_evaluator import PlanEvaluator
from .problem_generator import RandomProblemGenerator

MANIPULATION_DOMAIN = domains.Manipulation()

def is_useful_instance(pddl_problem, pddl_problem_wo_constraints, init_desc, goal_desc, constr_desc):
    pddl_domain = MANIPULATION_DOMAIN.get_domain_pddl()

    if is_safety_non_trivial_1(pddl_problem, pddl_problem_wo_constraints, init_desc, goal_desc, constr_desc):
        print("computing w/constraints non optimal")
        sol_constraints = planners.run_fast_downward_planner(pddl_domain, pddl_problem, optimality=False)
        sol_constraints_length = 0 if sol_constraints is None else len(sol_constraints.splitlines())
        print("w/constraints non optimal finished")
        if sol_constraints is not None:
            return True
    
    return False

def is_safety_non_trivial_1(pddl_problem, pddl_problem_wo_constraints, init_desc, goal_desc, constr_desc):
    pddl_domain = MANIPULATION_DOMAIN.get_domain_pddl()

    sol_wo_constraints = planners.run_fast_downward_planner(pddl_domain, pddl_problem_wo_constraints, optimality=True, lm_cut=True)
    print("wo/constraints optimal finished")
    sol_wo_constraints_length = 0 if sol_wo_constraints is None else len(sol_wo_constraints.splitlines())
    sol_constraints_bounded = planners.run_fast_downward_planner(pddl_domain, pddl_problem, optimality=True, bound=sol_wo_constraints_length+1)
    print("w/constraints bounded optimal finished")

    return sol_constraints_bounded is None

def is_safety_non_trivial_2(pddl_problem, pddl_problem_wo_constraints, init_desc, goal_desc, constr_desc):
    pddl_domain = MANIPULATION_DOMAIN.get_domain_pddl()

    sol_wo_constraints = planners.run_fast_downward_planner(pddl_domain, pddl_problem_wo_constraints, optimality=True, lm_cut=True)
    print("wo/constraints optimal finished")
    
    evaluator = PlanEvaluator(pddl_domain, pddl_problem, sol_wo_constraints)
    evaluator.try_simulation()
    return not evaluator.is_safe()

def generate_one_useful_instance(num_locations, num_items, num_goals, num_constraints):
    pddl_problem = None
    useful = False
    while(not useful):
        print("Trying...")
        problem_generator = RandomProblemGenerator(num_locations, num_items, num_goals, num_constraints)
        pddl_problem, pddl_problem_wo_constraints, init_desc, goal_desc, constr_desc = problem_generator.generate_random_instance()
        useful = is_useful_instance(pddl_problem, pddl_problem_wo_constraints, init_desc, goal_desc, constr_desc)

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
    
    args = parser.parse_args()

    os.makedirs("tmp", exist_ok=True)
    for i in range(1, args.problems + 1):
        if(args.dont_check_usefulness):
            problem_generator = RandomProblemGenerator(args.locations, args.items, args.goals, args.constraints)
            problem_pddl, _, init_desc, goal_desc, constr_desc = problem_generator.generate_random_instance()
        else:
            problem_pddl, init_desc, goal_desc, constr_desc = generate_one_useful_instance(args.locations, args.items, args.goals, args.constraints)
        
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
