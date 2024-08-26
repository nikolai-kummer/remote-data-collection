import numpy as np

def extract_top_action(qmatrix_file):
    # Load the qmatrix from the .npy file
    qmatrix = np.load(qmatrix_file)

    # Extract the top action for each row
    top_actions = np.argmax(qmatrix, axis=1)

    return top_actions


action = extract_top_action('./results/models/2024-08-25_solar_collection_optimum_optimum_q_matrix.npy')

print('Finished running model_converter.py')
print(f"Length of action: {len(action)}")