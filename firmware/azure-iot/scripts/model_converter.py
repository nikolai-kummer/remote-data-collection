import numpy as np

def extract_top_action(qmatrix_file):
    # Load the qmatrix from the .npy file
    qmatrix = np.load(qmatrix_file)

    # Extract the top action for each row
    top_actions = np.argmax(qmatrix, axis=1)

    return top_actions

def generate_packed_h_file(top_actions, output_file):
    packed_values = []
    for i in range(0, len(top_actions), 16):
        # Pack 16 actions into a single 32-bit integer (2 bits per action)
        packed_value = 0
        for j in range(16):
            if i + j < len(top_actions):
                packed_value |= (top_actions[i + j] & 0x03) << (j * 2)
        packed_values.append(packed_value)

    with open(output_file, 'w') as f:
        f.write("#ifndef STATEACTIONMAP_H\n")
        f.write("#define STATEACTIONMAP_H\n\n")
        f.write('#include "AgentHelper.h"\n\n')
        f.write("const uint32_t stateActionPacked[] PROGMEM = {\n")
        for value in packed_values:
            f.write(f"    0x{value:08X},\n")
        f.write("};\n\n")
        f.write("#endif // STATEACTIONMAP_H\n")

# Example usage:
state_to_action_map = extract_top_action('./../../RL_nz/results/models/2024-08-25_solar_collection_optimum_optimum_q_matrix.npy')
generate_packed_h_file(state_to_action_map, 'StateActionMap.h')

# Print random state-action pairs for validation
for i in [0,1,2,15,16,258, 2000, 3000, 20000, 24740]:
    print(f"State: {i}, Action: {state_to_action_map[i]}")

print('Finished running model_converter.py')
print(f"Length of action: {len(state_to_action_map)}")
