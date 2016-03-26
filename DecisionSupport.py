#Implement the function DecisionSupport
'''
For this question you may use the code from part 1

Note however that part 2 will be marked independent of part 1

The solution for VariableElimination.py will be used for testing part2 instead
of the copy you submit. 
'''

from MedicalBayesianNetwork import * 
from VariableElimination import * 

'''
Parameters:
             medicalNet - A MedicalBayesianNetwork object                        

             patient    - A Patient object
                          The patient to calculate treatment-outcome
                          probabilites for
Return:
         -A factor object

         This factor should be a probability table relating all possible
         Treatments to all possible outcomes
'''
def DecisionSupport(medicalNet, patient):
    medicalNet.set_evidence_by_patient(patient)
    elim_vars = list(set(set(set(medicalNet.net.variables()).difference(medicalNet.getTreatmentVars()).difference(medicalNet.getOutcomeVars()))).difference(patient.evidenceVariables()))
    current_factors = medicalNet.net.factors() #A running list of all factors of interest
    #Restrict factors based on evidence
    for var in patient.evidenceVariables():
        restricted_factors = list(current_factors)
        for factor in current_factors:
            if var in factor.get_scope():
                new_factor = restrict_factor(factor, var, var.get_evidence())
                restricted_factors.remove(factor)
                restricted_factors.append(new_factor)
        current_factors = restricted_factors
    #Eliminate variables not in the final factor
    for var in elim_vars:
        #Get all factors with var
        factors_with_var = []
        iter_list = list(current_factors)
        for factor in iter_list:
            if var in factor.get_scope():
                factors_with_var.append(factor)
                current_factors.remove(factor)
        new_factor = sum_out_variable(multiply_factors(factors_with_var), var)
        current_factors.append(new_factor)
    final_factor = multiply_factors(current_factors)
    #Normalize with respect to each treatment option
    treatment_combos = get_all_value_combinations(medicalNet.getTreatmentVars())
    for treatment_combo in treatment_combos:
        treatment_sum = 0
        matches = get_all_value_combinations(final_factor.get_scope(), [medicalNet.getTreatmentVars(),treatment_combo])
        for match in matches:
            treatment_sum += final_factor.get_value(match)
        #Overwrite entries with normalized value
        for match in matches:
            if treatment_sum is not 0:
                final_factor.add_value_at_assignment(final_factor.get_value(match)/treatment_sum, match)
    return final_factor

def get_all_value_combinations(variables, filter_array=None):
    '''
    Given an ordered list of variables, returns a list of lists containing
    every combination of possible values within the variable domains, in
    the order of the given list.
    
    Filter is a list of two lists. The first list is a list of variables
    and the second is a list of values to filter for. The index of the
    variables must match the values.
    '''
    if filter_array is None:
        filter_array = [[None]]
    return_list = [[]]
    for var in variables:
        if var in filter_array[0]:
            for item in return_list:
                item.append(filter_array[1][filter_array[0].index(var)])
        else:
            new_list = []
            for value in var.domain():
                for item in return_list:
                    new_item = list(item)
                    new_item.append(value)
                    new_list.append(new_item)
            return_list = new_list
    return return_list