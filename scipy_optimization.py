from scipy.optimize import minimize
from food_options import f, f_scipy
import numpy as np
import pandas as pd


breakfast_options = pd.read_csv('breakfast.csv', index_col='options')
lunch_options = pd.read_csv('lunch.csv', index_col='options')
dinner_options = pd.read_csv('dinner.csv', index_col='options')
nutrition_constraints = pd.read_csv('constraints.csv', index_col='constraints')
all_options = pd.concat([breakfast_options, lunch_options, dinner_options])
A = all_options.to_numpy()

def use_scipy_to_optimize(max_carbon_footprint=None):
    options = None

    constraints = []
    for i in range(70):
        def c(x, i=i):
            return x[i]
        constraints.append({'type': 'ineq', 'fun': c})

    def c(x):
        return x[:len(breakfast_options)] @ np.array(breakfast_options['energy']) - 300
    constraints.append({'type': 'ineq', 'fun': c})

    def c(x):
        return x[len(breakfast_options):len(lunch_options) + len(breakfast_options)] @ np.array(lunch_options['energy']) - 300
    constraints.append({'type': 'ineq', 'fun': c})

    def c(x):
        return x[-len(dinner_options):] @ np.array(dinner_options['energy']) - 300
    constraints.append({'type': 'ineq', 'fun': c})

    for i in np.arange(2, A.shape[1]):
        def c(x, i=i):
            return x @ A[:,i] - nutrition_constraints.loc['min'][i-2]
        constraints.append({'type': 'ineq', 'fun': c})

    for i in np.arange(2, A.shape[1]):
        def c(x, i=i):
            return -x @ A[:,i] + nutrition_constraints.loc['max'][i-2]
        constraints.append({'type': 'ineq', 'fun': c})

    if max_carbon_footprint is not None:
        def c(x):
            return -x @ A[:,1] + max_carbon_footprint
        constraints.append({'type': 'ineq', 'fun': c})

    sol = minimize(f_scipy, np.ones(70), options=options, constraints=constraints)
    return sol

def display_solution(x):
    print([round(xx) for xx in x])
    print(f_scipy(x))
    print([str(round(count)) + " " + option for count, option in zip(x[x>0.4], all_options[x>0.4].index)])
    f(list(map(round, x)), print_final=True)

if __name__=="__main__":
    sol = use_scipy_to_optimize()
    display_solution(sol.x)
    sol = use_scipy_to_optimize()
    display_solution(sol.x)
    sol = use_scipy_to_optimize()
    display_solution(sol.x)