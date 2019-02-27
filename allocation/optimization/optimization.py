from platypus import *
from .utils import *
import collections


def allocation(returns, risks, corr, initial_prices, time, value, max_quotes, actual_prices):

    def functions(q):
        weights = get_weights(q, initial_prices)
        constraints = [a for a in q]
        constraints.append((return_portfolio(returns, weights)+1)**time * portfolio_value(actual_prices, q))
        constraints.append((return_portfolio(returns, weights)+1)**time * portfolio_value(actual_prices, q))
        constraints.append(return_portfolio(returns, weights))
        constraints.append(risk_portfolio(weights, risks, corr))
        return [risk_portfolio(weights, risks, corr)], constraints

    problem = Problem(len(max_quotes), 1, len(max_quotes)+4)
    i = 0
    for asset in max_quotes:
        problem.types[i] = Real(0.00001, max_quotes[asset])
        i += 1

    problem.constraints[0:len(max_quotes)] = ">= 5"
    problem.constraints[len(max_quotes)] = ">="+str(value * 0.93)
    problem.constraints[len(max_quotes) + 1] = "<="+str(value)
    problem.constraints[len(max_quotes) + 2] = ">=" + str(0.015)
    problem.constraints[len(max_quotes) + 3] = "<=" + str(0.07)
    problem.function = functions

    algorithm = PAES(problem)
    algorithm.run(1000)

    feasible_solutions = [s for s in algorithm.result if s.feasible]

    return [feasible_solutions, algorithm.result]


def all_gt_ten(quotes):
    for asset in quotes:
        if quotes[asset] < 5:
            return False
    return True


def diff_quotes(quotes_1, quotes_2):
    i = 0
    for asset in quotes_1:
        val = quotes_1[asset] - quotes_2[i]
        if val > 10:
            quotes_1[asset] -= quotes_2[i]
        else:
            del quotes_1[asset]
        i += 1
    return quotes_1


import json


def optimize_ob(objectives, returns, risks, corr, initial_prices, max_quotes, actual_price):
   # print "max_quotes", max_quotes
#    print "returns", json.dumps(returns, indent=2)
  #  print "risks", json.dumps(risks, indent=2)
  #  print "initial price", json.dumps(initial_prices, indent=2)
 #   print "corr", corr
  #  print "actual price", actual_price

    for key in returns:
        returns[key] = collections.OrderedDict(sorted(returns[key].items()))
        risks[key] = collections.OrderedDict(sorted(risks[key].items()))
        initial_prices[key] = collections.OrderedDict(sorted(initial_prices[key].items()))
    max_quotes = collections.OrderedDict(sorted(max_quotes.items()))
    objectives = OrderedDict(sorted(objectives.items(), key=lambda index: index[1]['priority']))
    #print json.dumps(objectives, indent=2)
    for obk in objectives:
        #print objectives[obk]["priority"]
        if len(max_quotes) > 0:
            sols = allocation(returns[objectives[obk]["time_horizon"]], risks[objectives[obk]["time_horizon"]],
                              corr[objectives[obk]["time_horizon"]], initial_prices[objectives[obk]["time_horizon"]],
                              objectives[obk]["time_horizon"], objectives[obk]["value_minus_savings"],
                              max_quotes, actual_price)
            if sols[0]:
                feasible = True
                sol = sols[0][0]
            else:
                feasible = False
                sol = sols[1][0]
            print("value objective", objectives[obk]["value_minus_savings"])
            print("quote", sol.variables)
            print("constraints", sol.constraints)
            print("objectives", sol.objectives)
            sol_quote = dict()
            i = 0
            for asset in max_quotes:
                sol_quote[asset] = sol.variables[i]
                i += 1

            objectives[obk]["solution"] = {
                "quotes": sol_quote,
                "expected_return": sol.constraints[len(sol.constraints)-2],
                "expected_risk": sol.objectives[0],
                "feasible": feasible,
            }

            i = 0
            for asset in max_quotes:
                val = max_quotes[asset] - sol.variables[i]
                if val > 10:
                    max_quotes[asset] -= sol.variables[i]
                else:
                    #print "deleted", asset
                    del max_quotes[asset]
                    for obk1 in objectives:
                        del risks[objectives[obk1]["time_horizon"]][asset]
                        del returns[objectives[obk1]["time_horizon"]][asset]
                        del initial_prices[objectives[obk1]["time_horizon"]][asset]
                    del actual_price[asset]
                i += 1
    return objectives


def founds_allocation(objectives, founds, niter):

    def funct(vars):
        funct = []
        for i in range(0, len(objectives)):
            funct.append((objectives[i]["value_minus_savings"]/vars[i])**(1.0/objectives[i]["time_horizon"])-1.0)
        funct.append(-sum(vars))
        return funct, [sum(vars) - founds, ]

    types = []
    for i in range(0, len(objectives)):
        types.append(Real(objectives[i]["value_minus_savings"]/(1+objectives[i]["alfa"])**objectives[i]["time_horizon"],
                          objectives[i]["value_minus_savings"]))
    problem = Problem(len(objectives), len(objectives)+1, 1)

    problem.types[:] = types
    problem.constraints[:] = "<=0"
    problem.function = funct

    algorithm = PAES(problem)
    algorithm.run(niter)

    feasible_solutions = [s for s in algorithm.result if s.feasible]

    return [feasible_solutions, algorithm.result, nondominated(algorithm.result)]


def budgeting(founds, yearly_savings, objectives, niter=1000):
    saving = 0
    objectives = sorted(objectives, key=lambda k: k['time_horizon'])
    for i in range(0, len(objectives)):
        if i == 0:
            saving += objectives[i]["time_horizon"]*yearly_savings
        else:
            saving += (objectives[i]["time_horizon"]-objectives[i-1]["time_horizon"])*yearly_savings
        if objectives[i]["value"] - saving <= 0:
            #print(objectives[i]["value"], objectives[i]["value"] - saving, saving)
            saving -= objectives[i]["value"]
            objectives[i]["savings_required"] = objectives[i]["value"]
            objectives[i]["value_minus_savings"] = 0
        else:
            objectives[i]["value_minus_savings"] = objectives[i]["value"] - saving
            objectives[i]["savings_required"] = saving
            saving = 0
    objectives_gt_zero = [objective for objective in objectives if objective["value_minus_savings"] > 0]
    objectives_lt_zero = [objective for objective in objectives if objective["value_minus_savings"] == 0]
    #print(json.dumps(objectives_lt_zero, indent=2))
    for ob in objectives_lt_zero:
        ob["investment_required"] = 0
        ob["annualized_return_supposed"] = 0
    if len(objectives_gt_zero) > 0:
        sols = founds_allocation(objectives_gt_zero, founds, niter)
        if len(sols[0]) > 0:
            sol = sols[0][0]
            for i in range(0, len(sol.variables)):
                objectives_gt_zero[i]["investment_required"] = sol.variables[i]
                objectives_gt_zero[i]["annualized_return_supposed"] = sol.objectives[i]
            info = "Solutions found"
        else:
            sol = sols[1][0]
            for i in range(0, len(sol.variables)):
                objectives_gt_zero[i]["investment_required"] = sol.variables[i]
                objectives_gt_zero[i]["annualized_return_supposed"] = sol.objectives[i]
            info = "Solutions not found"
        sol = dict()
        sol["info"] = info
        sol["objectives"] = objectives_gt_zero + objectives_lt_zero
    else:
        sol = dict()
        sol["info"] = "Solutions found"
        sol["objectives"] = objectives_lt_zero
    return sol


def budgeting_loop(founds, yearly_savings, objectives):
    info = "Solutions not found"
    while info == "Solutions not found":
        obi = budgeting(founds, yearly_savings, objectives)
        info = obi["info"]
        if info == "Solutions not found":
            minP = 5
            founded = False
            while minP > 0 and founded is False:
                for i in range(0, len(objectives)):
                    if objectives[i]["priority"] == minP:
                        #obietivoElm = obiettivi[i]
                        del objectives[i]
                        founded = True
                        break
                minP -= 1
    return obi
