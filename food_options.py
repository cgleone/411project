import pandas as pd
import numpy as np

breakfast_options = pd.read_csv('breakfast.csv')
lunch_options = pd.read_csv('lunch.csv')
dinner_options = pd.read_csv('dinner.csv')
constraints = pd.read_csv('constraints.csv', index_col='constraints')
current_year = 2030   # either 2020, 2030, or 2040
carbon_2020 = 10.866077868092553

# nutrient_vals = [energy, protein, fat .....]
# nutrient_penalties = min(nutrient_vals, 0)
# f = [(x1*c1 + x2*c2 + ....... + xi*ci) + (x1*cf1 + x2*cf2 + ....... + xi*cfi) + nutrient_penalties] +

# breakfast_cost = np.dot(x, np.array(breakfast_options['cost']))

def f(x, print_final=False):
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

    penalties = get_penalties(xb, xl, xd, print_final=print_final)
    if print_final:
        print_food_choices(xb, xl, xd)
        print("Carbon footprint total (kgCO2): {}".format(breakfast_carbon + lunch_carbon + dinner_carbon))
        print("Cost total ($): {}".format(breakfast_cost + lunch_cost + dinner_cost))


    f = (breakfast_cost + lunch_cost + dinner_cost) + carbon_weighting*(breakfast_carbon + lunch_carbon + dinner_carbon) + 10000*penalties
    #f = penalties
    return f


def get_penalties(xb, xl, xd, print_final=False):

    penalties = {}
    total_nutrients = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    breakfast_cals = 0
    lunch_cals = 0
    dinner_cals = 0

    for i in range(len(xb)): # for each food option at breakfast
        option_quantity = round(xb[i], 0)
        if option_quantity > 0: # if we are having any of this food option at breakfast today (aka in this iteration)
            option_nutrients = [breakfast_options.iloc[i]['energy'], breakfast_options.iloc[i]['protein'],
                            breakfast_options.iloc[i]['carbs'], breakfast_options.iloc[i]['fibre'],
                            breakfast_options.iloc[i]['fat'], breakfast_options.iloc[i]['sat_fat'],
                            breakfast_options.iloc[i]['cholesterol'], breakfast_options.iloc[i]['calcium'],
                            breakfast_options.iloc[i]['iron'], breakfast_options.iloc[i]['sodium'],
                            breakfast_options.iloc[i]['potassium']]
            for j in range(len(total_nutrients)):
                total_nutrients[j] = total_nutrients[j] + (option_nutrients[j]*option_quantity)
            breakfast_cals = breakfast_cals + option_nutrients[0]*option_quantity

    for i in range(len(xl)):  # for each food option at lunch
        option_quantity = round(xl[i], 0)
        if option_quantity > 0:  # if we are having any of this food option at lunch today (aka in this iteration)
            option_nutrients = [lunch_options.iloc[i]['energy'], lunch_options.iloc[i]['protein'],
                                lunch_options.iloc[i]['carbs'], lunch_options.iloc[i]['fibre'],
                                lunch_options.iloc[i]['fat'], lunch_options.iloc[i]['sat_fat'],
                                lunch_options.iloc[i]['cholesterol'], lunch_options.iloc[i]['calcium'],
                                lunch_options.iloc[i]['iron'], lunch_options.iloc[i]['sodium'],
                                lunch_options.iloc[i]['potassium']]
            for j in range(len(total_nutrients)):
                total_nutrients[j] = total_nutrients[j] + (option_nutrients[j] * option_quantity)
            lunch_cals = lunch_cals + option_nutrients[0]*option_quantity

    for i in range(len(xd)):  # for each food option at dinner
        option_quantity = round(xd[i], 0)
        if option_quantity > 0:  # if we are having any of this food option at dinner today (aka in this iteration)
            option_nutrients = [dinner_options.iloc[i]['energy'], dinner_options.iloc[i]['protein'],
                                dinner_options.iloc[i]['carbs'], dinner_options.iloc[i]['fibre'],
                                dinner_options.iloc[i]['fat'], dinner_options.iloc[i]['sat_fat'],
                                dinner_options.iloc[i]['cholesterol'], dinner_options.iloc[i]['calcium'],
                                dinner_options.iloc[i]['iron'], dinner_options.iloc[i]['sodium'],
                                dinner_options.iloc[i]['potassium']]
            for j in range(len(total_nutrients)):
                total_nutrients[j] = total_nutrients[j] + (option_nutrients[j] * option_quantity)
            dinner_cals = dinner_cals + option_nutrients[0]*option_quantity

    # cals = total_nutrients[0]
    # min_val = constraints.loc['min'][0]
    # max_val = constraints.loc['max'][0]
    # if cals < min_val:
    #     penalties['nutrient {} low'.format(0)] = ((min_val - cals) / min_val)
    # elif cals > max_val:
    #     penalties['nutrient {} high'.format(0)] = ((cals - max_val) / max_val)

    for i in range(len(total_nutrients)):
        intake = total_nutrients[i]
        min_val = constraints.loc['min'][i]
        max_val = constraints.loc['max'][i]
        if intake < min_val:
            penalties['nutrient {} low'.format(i)] = (min_val-intake)/min_val
        elif intake > max_val:
            penalties['nutrient {} high'.format(i)] = (intake-max_val)/max_val

    meal_balance_error = 0
    for meal_cals in [breakfast_cals, lunch_cals, dinner_cals]:
        if meal_cals < 300:
            meal_balance_error = meal_balance_error + (300 - meal_cals)
    penalties["meal balance"] = meal_balance_error

    negative_error = 0
    for x in [xb, xl, xd]:
        for x_i in x:
            if x_i < -0.1:
                negative_error = negative_error + (-x_i)

    penalties["negative"] = 100000 * negative_error

    if print_final:
        print(penalties)
        print("Total Nutrients today: {}".format([round(a, 1) for a in total_nutrients]))

    for key in penalties.keys():
        if "nutrient" in key:
            penalties[key] = penalties[key]*1000

    if carbon_constraint():
        carbon

    return sum([p for p in penalties.values()])


def print_food_choices(xb, xl, xd):

    print("\nBreakfast:")
    breakfast_cals = 0
    for i in range(len(xb)):
        quantity = round(xb[i], 0)
        item = breakfast_options.iloc[i][0]
        if quantity:
            print("{} {}".format(quantity, item))
            breakfast_cals += (breakfast_options.iloc[i][3] * quantity)
    print("Calories in meal: {}".format(breakfast_cals))

    print("\nLunch:")
    lunch_cals = 0
    for i in range(len(xl)):
        quantity = round(xl[i], 0)
        item = lunch_options.iloc[i][0]
        if quantity:
            print("{} {}".format(quantity, item))
            lunch_cals += (lunch_options.iloc[i][3]*quantity)
    print("Calories in meal: {}".format(lunch_cals))

    print("\nDinner:")
    dinner_cals = 0
    for i in range(len(xd)):
        quantity = round(xd[i], 0)
        item = dinner_options.iloc[i][0]
        if quantity:
            print("{} {}".format(quantity, item))
            dinner_cals += (dinner_options.iloc[i][3]*quantity)
    print("Calories in meal: {}".format(dinner_cals))

def carbon_constraint():
    if current_year == 2020:
        return 0
    elif current_year == 2030:
        return carbon_2020*0.97
    elif current_year == 2040:
        return carbon_2020*0.93
    else:
        print("Invalid Year Entered - Assuming Year is 2020 and no carbon constraint is present")
        return 0

