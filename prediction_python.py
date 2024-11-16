# %%
import numpy as np
import pandas as pd
from tensorflow import keras
from sklearn.preprocessing import MinMaxScaler
from  preprocess_python import scaler_features,scaler_target

# %%
# Load the trained model
model = keras.models.load_model('/Users/shishir/Downloads/cs667-project/aqi_prediction_model.keras')

# %%
# Function to make a daily AQI prediction
def predict_next_day_aqi(new_data, historical_data, lookback=30):
    # Step 1: Append the new data to the historical dataset for feature columns only
    features = ['PM2.5 (µg/m³)', 'PM10 (µg/m³)','NH3 (µg/m³)','Benzene (µg/m³)','AT (°C)','RH (%)' ]
    data = pd.concat([historical_data, new_data])
    
    data=data[features]
    # Step 2: Normalize the updated feature data
    scaled_features = scaler_features.transform(data)
    scaled_features = pd.DataFrame(scaled_features, columns=features, index=data.index)
    # Step 3: Prepare the input sequence using the last 30 days of feature data
    input_sequence = scaled_features[-lookback:].values.reshape((1, lookback, len(features)))
    # Step 4: Predict the AQI for the next day (scaled AQI value)
    predicted_aqi_scaled = model.predict(input_sequence)
    # Step 5: Inverse transform the prediction to get AQI on the original scale
    # Use the target scaler for inverse transformation on the AQI prediction only
    predicted_aqi = scaler_target.inverse_transform(predicted_aqi_scaled.reshape(-1, 1)).flatten()
    
    return predicted_aqi


# %%
new_data = pd.DataFrame({
    'PM2.5 (µg/m³)': [19],
    'PM10 (µg/m³)': [36],
    'NH3 (µg/m³)': [2],
    'Benzene (µg/m³)': [1],
    'AT (°C)': [25],
    'RH (%)': [50],
    'AQI': [53]  # The AQI is unknown as it is what we want to predict
}, index=[pd.to_datetime('2024-11-12')])

# Make prediction for the next day AQI
historical_data=pd.read_csv('/Users/shishir/Downloads/cs667-project/filtered_data.csv')
predicted_aqi = predict_next_day_aqi(new_data, historical_data,)

print(f"Predicted AQI for the next day: {predicted_aqi}")


