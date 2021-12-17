import pandas as pd
import numpy as np

breakfast_options = pd.read_csv('breakfast.csv')
lunch_options = pd.read_csv('lunch.csv')
dinner_options = pd.read_csv('dinner.csv')
constraints = pd.read_csv('constraints.csv', index_col='constraints')


print(breakfast_options.loc['dairy smoothie']['fibre'])

# nutrient_vals = [energy, protein, fat .....]
# nutrient_penalties = min(nutrient_vals, 0)
# f = [(x1*c1 + x2*c2 + ....... + xi*ci) + (x1*cf1 + x2*cf2 + ....... + xi*cfi) + nutrient_penalties] +

# breakfast_cost = np.dot(x, np.array(breakfast_options['cost']))

def f(x):
    xb = x[0:len(breakfast_options)]
    xl = x[len(breakfast_options):len(lunch_options)+len(breakfast_options)]
    xd = x[len(lunch_options)+len(breakfast_options):len(x)]

    breakfast_cost = np.dot(xb, np.array(breakfast_options['cost']))
    lunch_cost = np.dot(xl, np.array(lunch_options['cost']))
    dinner_cost = np.dot(xd, np.array(dinner_options['cost']))
    breakfast_carbon = np.dot(xb, np.array(breakfast_options['carbon']))
    lunch_carbon = np.dot(xl, np.array(lunch_options['carbon']))
    dinner_carbon = np.dot(xd, np.array(dinner_options['carbon']))

    carbon_weighting = 4

    penalties = get_penalties(xb, xl, xd)

    f = breakfast_cost + lunch_cost + dinner_cost + carbon_weighting*(breakfast_carbon + lunch_carbon + dinner_carbon) + penalties
    return f


def get_penalties(xb, xl, xd):

    penalties = []
    total_nutrients = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    for i in range(len(xb)): # for each food option at breakfast
        option_quantity = xb[i]
        if option_quantity: # if we are having any of this food option at breakfast today (aka in this iteration)
            option_nutrients = [breakfast_options.iloc[i]['energy'], breakfast_options.iloc[i]['protein'],
                            breakfast_options.iloc[i]['carbs'], breakfast_options.iloc[i]['fibre'],
                            breakfast_options.iloc[i]['fat'], breakfast_options.iloc[i]['sat_fat'],
                            breakfast_options.iloc[i]['cholesterol'], breakfast_options.iloc[i]['calcium'],
                            breakfast_options.iloc[i]['iron'], breakfast_options.iloc[i]['sodium'],
                            breakfast_options.iloc[i]['potassium']]
            for j in range(len(total_nutrients)):
                total_nutrients[j] = total_nutrients[j] + (option_nutrients[j]*option_quantity)

    for i in range(len(xl)):  # for each food option at lunch
        option_quantity = xl[i]
        if option_quantity:  # if we are having any of this food option at lunch today (aka in this iteration)
            option_nutrients = [lunch_options.iloc[i]['energy'], lunch_options.iloc[i]['protein'],
                                lunch_options.iloc[i]['carbs'], lunch_options.iloc[i]['fibre'],
                                lunch_options.iloc[i]['fat'], lunch_options.iloc[i]['sat_fat'],
                                lunch_options.iloc[i]['cholesterol'], lunch_options.iloc[i]['calcium'],
                                lunch_options.iloc[i]['iron'], lunch_options.iloc[i]['sodium'],
                                lunch_options.iloc[i]['potassium']]
            for j in range(len(total_nutrients)):
                total_nutrients[j] = total_nutrients[j] + (option_nutrients[j] * option_quantity)

    for i in range(len(xd)):  # for each food option at dinner
        option_quantity = xd[i]
        if option_quantity:  # if we are having any of this food option at dinner today (aka in this iteration)
            option_nutrients = [dinner_options.iloc[i]['energy'], dinner_options.iloc[i]['protein'],
                                dinner_options.iloc[i]['carbs'], dinner_options.iloc[i]['fibre'],
                                dinner_options.iloc[i]['fat'], dinner_options.iloc[i]['sat_fat'],
                                dinner_options.iloc[i]['cholesterol'], dinner_options.iloc[i]['calcium'],
                                dinner_options.iloc[i]['iron'], dinner_options.iloc[i]['sodium'],
                                dinner_options.iloc[i]['potassium']]
            for j in range(len(total_nutrients)):
                total_nutrients[j] = total_nutrients[j] + (option_nutrients[j] * option_quantity)

    for i in range(len(total_nutrients)):
        intake = total_nutrients[i]
        min_val = constraints.loc['min'][i]
        max_val = constraints.loc['max'][i]
        if intake < min_val:
            penalties.append((min_val-intake)/min_val)
        elif intake > max_val:
            penalties.append((intake-max_val)/max_val)

    return sum(penalties)




