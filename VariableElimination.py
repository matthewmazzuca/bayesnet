from BayesianNetwork import *
import itertools


def multiply_factors(factors):
    flist = list(factors)

    while(len(flist) > 1):
        freq_used = find_freq_used(flist)
        # Check for any constant factors

        if len(freq_used) == 0:
            flist = check_const_factors(freq_used, flist)


        # There is no constant factors
        togethers, products = no_const_factor(freq_used, flist)
        #Generate a new factor table from factors
        products, flist, togethers, newie_table = get_connect(togethers, flist, products)
        
        #Return new Factor table
        flist = make_fact_tab(products, flist, newie_table)
        
    # Return multiply factors
    return flist[0]

def make_fact_tab(products, flist, newie_table):
    '''
    This function makes the factor table and returns the factor list
    '''

    newie = Factor("Prod of {}".format(flist), products)
    newie.add_values(newie_table)
    flist = [newie]
    return flist

def get_connect(togethers, flist, products):
    '''
    Get the matches. Return factor list
    '''

    newie_table = []
    for pair in togethers:
        #Get connected sets

        connect = []
        for item in range(len(flist)):
            filters = [[],[]]
            # Find the appropriate filters

            for ind in range(len(products)):
                if products[ind] in flist[item].get_scope():
                    filters[0].append(products[ind])
                    filters[1].append(pair[ind])
            connected = get_combos(flist[item].get_scope(), filters)
            connect.append(connected)

        #Get all the products

        tot_products = list(itertools.product(*connect))
        for i in range(len(tot_products)):
            prodval = flist[0].get_value(tot_products[i][0])

            for j in range(len(tot_products[i])):
                # check if product value is zero
                if not prodval: 
                        break
                # this is the initial value, so do nothing
                if j == 0:
                    continue 
                else:
                    prodval = prodval * (flist[j].get_value(tot_products[i][j]))
            #Add appropriate new_entry

            new_entry = list(pair)
            new_entry.append(prodval)
            newie_table.append(new_entry)

    # return everything needed
    return products, flist, togethers, newie_table

def no_const_factor(freq_used, flist, implication=[], pairs = [], products = [], unfreq_used = []):

    '''
    this function maps each common var to each individual factor and returns the final profucts and the pais
    '''

    for f in flist:
        factor_implic = []
        for item in freq_used:
            factor_implic.append(f.get_scope().index(item))

        implication.append(f)
        pairs.append(get_combos(f.get_scope()))
        products = list(set(products).union(f.get_scope()))
        un_common = list(set(f.get_scope()).difference(freq_used))
        unfreq_used = list(set(unfreq_used).union(un_common))

    togethers = get_combos(products)
    return togethers, products

def check_const_factors(freq_used, flist):
    const = None
    for factor in flist:

        if len(factor.get_scope()) == 0:
            const = factor
            break
    # check to see if there are no constant factors

    if const != None: 
        other = None

        if const != flist[0]:
            other = flist[0]

        else:
            other = flist[1]

        # get the scope of the other factor
        pairs = get_combos(other.get_scope())
        newie_table = []

        # cycle through pairs and get associated value to add to new table new_entry
        for pair in pairs:
            new_entry = list(pair)
            value = const.get_value([]) * other.get_value(pair)
            new_entry.append(value)
            newie_table.append(new_entry)

        newie = Factor("Product of {} and {}".format(const, other), other.get_scope())

        # Add the table to the new factor
        newie.add_values(newie_table)

        # remobe constant  factor and other factor and add the new factor

        flist.remove(const)
        flist.remove(other)
        flist.append(newie)

    return flist

def find_freq_used(factors):
    '''
    given all the factors get an array of frequently used factors and return
    '''

    freq_used = None
    for factor in factors:

        if freq_used == None:
            freq_used = factor.get_scope()

        else:
            freq_used = list(set(freq_used).intersection(factor.get_scope()))

        if len(freq_used) == 0:
            break

    return freq_used
            
def get_combos(variables, filters=None):

    if filters == None:
        filters = [[None]]

    freq_used = [[]]

    for it in variables:

        if it in filters[0]:

            for item in freq_used:
                item.append(filters[1][filters[0].index(it)])

        else:
            ret_list = []

            for val in it.domain():

                for item in freq_used:

                    add_it = list(item)
                    add_it.append(val)
                    ret_list.append(add_it)

            freq_used = ret_list

    return freq_used

def restrict_factor(factor, variable, value):
    newie_table = []
    ind = factor.get_scope().index(variable)
    pairs = get_combos(factor.get_scope())

    for pair in pairs:

        if pair[ind] == value:
            new_entry = list(pair)
            new_entry.pop(ind)
            new_entry.append(factor.get_value(pair))
            newie_table.append(new_entry)

    new_scope = factor.get_scope()
    new_scope.pop(ind)

    restricted_factor = Factor("Restriction Implied:{};{};{}" \
                        .format(factor,variable,value),new_scope)

    restricted_factor.add_values(newie_table)
    return restricted_factor

    
def sum_out_variable(factor, variable):
    ind = factor.get_scope().index(variable)
    rem_scope = factor.get_scope()
    rem_scope.pop(ind)
    rem_pair = get_combos(rem_scope)
    newie_table = []

    for pair in rem_pair:
        pair_sum = 0

        for val in variable.domain():
            query = list(pair)
            query.insert(ind, val)
            pair_sum = pair_sum + factor.get_value(query)

        new_entry = list(pair)
        new_entry.append(pair_sum)
        newie_table.append(new_entry)

    sum_out_factor = Factor("Sum Out:{},{}".format(factor, variable),rem_scope)
    sum_out_factor.add_values(newie_table)
    return sum_out_factor

def get_distr(finals, pair_list, fin_sum):
    '''
    Get final distribution
    '''

    for pair in pair_list:
        fin_sum += finals.get_value(pair)
    distrib = []
    for pair in pair_list:
        if not fin_sum: 
            distrib.append(0)
        else:
            distrib.append(finals.get_value(pair)/fin_sum)

    return distrib

def evid_vars(evidenceVars, currents):
    '''
    Restrict appropriate factors given the appropriate evidence
    '''

    for evid in evidenceVars:
        restricts = list(currents)
        for factor in currents:
            if evid in factor.get_scope():
                newie = restrict_factor(factor, evid, evid.get_evidence())
                restricts.remove(factor)
                restricts.append(newie)
        currents = restricts
    return currents

def min_order_fill_fact(currents, queryVar):
    '''
    Return the min order filled factors from current factors and query variables
    '''

    ordering = min_fill_ordering(currents, queryVar)
    for elim_var in ordering:
        elim_flist = []
        for factor in currents:
            if elim_var in factor.get_scope():
                elim_flist.append(factor)
        compressed_factors = sum_out_variable(multiply_factors(elim_flist), elim_var)

        currents = list(set(currents).difference(elim_flist))
        currents.append(compressed_factors)
    return currents


def VariableElimination(net, queryVar, evidenceVars):
    
    
    currents = evid_vars(evidenceVars, net.factors())

    #min order fill factors using current factors and queryvariables
    currents = min_order_fill_fact(currents, queryVar)
    
    #multiply the factors to get the final values
    finals = multiply_factors(currents)

    # normalize, get sum and all value combination
    pair_list = get_combos(finals.get_scope())
    fin_sum = 0

    # return distribution
    return get_distr(finals, pair_list, fin_sum)




