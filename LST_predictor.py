from flask import Flask, request, jsonify
import joblib 
import pandas as pd
import sys 

# 1. ESSENTIAL CONFIGURATION

# Define the filenames used to save your objects
MODEL_FILENAME = 'lst_model.joblib'
COLUMNS_FILENAME = 'Xcolumn_names.joblib' # Name of the file containing feature list

# 2. MODEL AND COLUMNS LOADING (Executed once at startup)

try:
    # Load the model object
    MODEL = joblib.load(MODEL_FILENAME)
    
    # Load the list of feature names (e.g., ['BuiltUp_Pct', 'Green_Pct'])
    FEATURE_COLUMNS = joblib.load(COLUMNS_FILENAME) 
    
    print(f"SUCCESS: Model and {len(FEATURE_COLUMNS)} features loaded.")
    
except FileNotFoundError:
    # Print a clear error message and exit if files are missing
    print(f"ERROR: Could not find model files ({MODEL_FILENAME} or {COLUMNS_FILENAME}).")
    sys.exit(1) # Use sys.exit(1) to stop the program cleanly

except Exception as e:
    print(f"ERROR: Failed to load model or columns. Details: {e}")
    sys.exit(1)
    
# 3. FLASK APPLICATION SETUP

app = Flask(__name__)

# Define the API endpoint that listens for POST requests
@app.route('/predict_lst', methods=['POST'])
def handle_prediction():
    # --- NO ERROR CHECKING FOR SIMPLICITY ---
    # In a real app, you MUST add try/except blocks here for KeyError and ValueError.

    data = request.get_json()
    
    # Extract the features based on the expected JSON keys
    builtup = data['builtup_pct']
    green = data['green_pct']
    
    # Structure the input data correctly for the scikit-learn model
    # The 'columns' argument uses the loaded FEATURE_COLUMNS list.
    input_data = pd.DataFrame([[builtup, green]], columns=FEATURE_COLUMNS)
    
    # Get the prediction from the loaded model
    predicted_lst = MODEL.predict(input_data)[0]
    
    # Return the result as a simple JSON response
    return jsonify({
        'predicted_mean_lst_c': round(float(predicted_lst), 4)
    })

# 4. RUN THE API

if __name__ == '__main__':
    # Start the service
    print("\n--- Simple LST Prediction Service Running ---")
    app.run(debug=True, port=5000)