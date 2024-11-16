# %%
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
# from preprocess_python import scaler_features, scaler_target

# %%
# Load the TFLite model
interpreter = tf.lite.Interpreter(model_path='/Users/shishir/Downloads/cs667-project/aqi_prediction_model.tflite')
interpreter.allocate_tensors()

# Get input and output details
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()


# %%
data1 =pd.read_csv('/Users/shishir/Downloads/cs667-project/filtered_data.csv')

data1['Timestamp'] = pd.to_datetime(data1['Timestamp'])
data1 = data1.sort_values('Timestamp').set_index('Timestamp')

features = ['PM2.5 (µg/m³)', 'PM10 (µg/m³)','NH3 (µg/m³)','Benzene (µg/m³)','AT (°C)','RH (%)' ]
target=['AQI']
scaler_features = MinMaxScaler()
scaled_features = scaler_features.fit_transform(data1[features])

scaler_target = MinMaxScaler()
scaled_target = scaler_target.fit_transform(data1[target])

# %%
# Function to make a daily AQI prediction using TFLite model
def predict_next_day_aqi(new_data, historical_data, lookback=30):
    # Step 1: Append the new data to the historical dataset for feature columns only
    features = ['PM2.5 (µg/m³)', 'PM10 (µg/m³)','NH3 (µg/m³)','Benzene (µg/m³)','AT (°C)','RH (%)' ]
    data = pd.concat([historical_data, new_data])
    
    data = data[features]
    
    # Step 2: Normalize the updated feature data
    scaled_features = scaler_features.transform(data)
    scaled_features = pd.DataFrame(scaled_features, columns=features, index=data.index)
    
    # Step 3: Prepare the input sequence using the last 30 days of feature data
    input_sequence = scaled_features[-lookback:].values.reshape((1, lookback, len(features))).astype(np.float32)
    
    # Step 4: Set the input data for the interpreter and run the prediction
    interpreter.set_tensor(input_details[0]['index'], input_sequence)
    interpreter.invoke()
    
    # Step 5: Get the predicted AQI in scaled format and inverse transform to original scale
    predicted_aqi_scaled = interpreter.get_tensor(output_details[0]['index'])
    predicted_aqi = scaler_target.inverse_transform(predicted_aqi_scaled.reshape(-1, 1)).flatten()
    
    return predicted_aqi

# %%
# %%
# New data for the next day
new_data = pd.DataFrame({
    'PM2.5 (µg/m³)': [19],
    'PM10 (µg/m³)': [36],
    'NH3 (µg/m³)': [2],
    'Benzene (µg/m³)': [1],
    'AT (°C)': [25],
    'RH (%)': [50],
    'AQI': [53]  # The AQI is unknown as it is what we want to predict
}, index=[pd.to_datetime('2024-11-12')])


# %%

# Historical data
historical_data = pd.read_csv('/Users/shishir/Downloads/cs667-project/filtered_data.csv')

# Make prediction for the next day AQI
predicted_aqi = predict_next_day_aqi(new_data, historical_data)

print(f"Predicted AQI for the next day: {predicted_aqi}")


