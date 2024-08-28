import numpy as np

def extract_top_action(qmatrix_file):
    # Load the qmatrix from the .npy file
    qmatrix = np.load(qmatrix_file)

    # Extract the top action for each row
    top_actions = np.argmax(qmatrix, axis=1)

    # convert the numpy array to a dict of index->action
    top_actions = {i: a for i, a in enumerate(top_actions)}
    return top_actions

def generate_h_file(state_action_dict, output_file):
    with open('StateActionMap.h', 'w') as f:
        f.write("#ifndef STATEACTIONMAP_H\n")
        f.write("#define STATEACTIONMAP_H\n\n")
        f.write('#include "AgentHelper.h"\n\n')
        f.write("void AgentHelper::initializeStateActionMap() {\n")
        for key, value in state_action_dict.items():
            f.write(f"    stateActionMap[{key}] = {value};\n")
        f.write("}\n\n")
        f.write("#endif // STATEACTIONMAP_H\n")

# state_to_action_map = extract_top_action('./results/models/2024-08-25_solar_collection_optimum_optimum_q_matrix.npy')
state_to_action_map = extract_top_action('./../../RL_nz/results/models/2024-08-25_solar_collection_optimum_optimum_q_matrix.npy')
generate_h_file(state_to_action_map, 'StateActionMap.h')

print('Finished running model_converter.py')
print(f"Length of action: {len(state_to_action_map)}")