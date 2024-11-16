# %%
import pandas as pd
from sklearn.model_selection import train_test_split

# Define file paths for AQI and pollutant data
years = [2023,2022]
aqi_files = {
    2023:"/Users/shishir/Downloads/cs667-project/AQI DATA/AQI_daily_city_level_kanpur_2023_kanpur_2023.xlsx",
    2022: "/Users/shishir/Downloads/cs667-project/AQI DATA/AQI_daily_city_level_kanpur_2022_kanpur_2022.xlsx",
   
}
pollutant_files = {
    2023:"/Users/shishir/Downloads/cs667-project/POLLUTANT DATA/Raw_data_1Day_2023_site_5500_FTI_Kidwai_Nagar_Kanpur_UPPCB_1Day.csv",
    2022: "/Users/shishir/Downloads/cs667-project/POLLUTANT DATA/Raw_data_1Day_2022_site_5500_FTI_Kidwai_Nagar_Kanpur_UPPCB_1Day.csv",
  
}

# Prepare an empty list to store merged data for each year
merged_yearly_data = []

# Month mapping for reshaping AQI data
month_mapping = {
    "January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6, 
    "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12
}

# Loop through each year to load, process, and merge data
for year in years:
    # Load AQI and pollutant data for the year
    aqi_data = pd.read_excel(aqi_files[year])
    pollutant_data = pd.read_csv(pollutant_files[year])
    
    # Convert the timestamp in pollutant data to datetime and set as index
    pollutant_data['Timestamp'] = pd.to_datetime(pollutant_data['Timestamp'])
    pollutant_data.set_index('Timestamp', inplace=True)
    pollutant_data_interpolated = pollutant_data.interpolate(method='time')
    # Resample pollutant data to daily averages
    daily_pollutant_data = pollutant_data.resample('D').mean().reset_index()
    
    # Reshape AQI data to long format
    aqi_data = aqi_data.rename(columns={"Date": "Day"})
    aqi_long = pd.melt(aqi_data, id_vars=['Day'], var_name='Month', value_name='AQI')
    aqi_long['Month'] = aqi_long['Month'].map(month_mapping)
    aqi_long['Year'] = year
    # Clean the data to remove any non-numeric values
    aqi_long = aqi_long.dropna(subset=['Day', 'Month', 'Year'])  # Drop rows with missing values in date columns
    aqi_long['Day'] = pd.to_numeric(aqi_long['Day'], errors='coerce')
    aqi_long['Month'] = pd.to_numeric(aqi_long['Month'], errors='coerce')
    aqi_long['Year'] = pd.to_numeric(aqi_long['Year'], errors='coerce')
    aqi_long = aqi_long.dropna(subset=['Day', 'Month', 'Year'])  # Drop rows where conversion failed

    # Convert to datetime
    aqi_long['Date'] = pd.to_datetime(aqi_long[['Year', 'Month', 'Day']], errors='coerce')
    aqi_long = aqi_long.dropna(subset=['Date'])  # Drop rows where date conversion failed
    aqi_long.drop(['Year', 'Month', 'Day'], axis=1, inplace=True)

    # Merge daily pollutant data with AQI data
    merged_data = pd.merge(daily_pollutant_data, aqi_long, left_on='Timestamp', right_on='Date')
    merged_data.drop(columns=['Date'], inplace=True)
    # Append merged data to the list
    merged_yearly_data.append(merged_data)

# Concatenate all years into a single DataFrame
combined_data = pd.concat(merged_yearly_data, ignore_index=True)
combined_data=combined_data.fillna(0, inplace=False)

# Display the final merged data structure
# combined_data.to_csv('/Users/shishir/Downloads/cs667-project/combined_data.csv', index=False)
# print(combined_data.head())
columns_to_keep = ['Timestamp', 'PM2.5 (µg/m³)', 'PM10 (µg/m³)' ,'AQI']

filtered_data = combined_data[columns_to_keep]
print(filtered_data.head())
filtered_data.to_csv('/Users/shishir/Downloads/cs667-project/filtered_data.csv', index=False)

# Perform time-based interpolation to fill NaN values



# %%
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split


# %%
# Load the dataset (assuming 'filtered_combined_data.csv' has required columns)
data = pd.read_csv('/Users/shishir/Downloads/cs667-project/filtered_data.csv')
timestamps = data['Timestamp'].reset_index(drop=True)
# Sort data by timestamp

# Keep a separate Timestamp column

# Select relevant columns
features = ['PM2.5 (µg/m³)', 'PM10 (µg/m³)','AQI']
data = data[features]
print(data.head())

# %%
lagged_data = pd.read_csv('/Users/shishir/Downloads/cs667-project/lagged_data.csv')

# %%
X = lagged_data.drop(columns=['AQI'])  # All columns except the target
y = lagged_data['AQI']  # Target column


# %%
# Split while respecting time order
split_ratio = 0.8
split_index = int(len(X) * split_ratio)
X_train, X_test = X[:split_index], X[split_index:]
y_train, y_test = y[:split_index], y[split_index:]


# %%
rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)


# %%
predictions = rf_model.predict(X_test)
rmse = mean_squared_error(y_test, predictions, squared=False)
print(f"RMSE: {rmse}")


# %%
import joblib
joblib.dump(rf_model, '/Users/shishir/Downloads/cs667-project/rf_model.pkl')

# %%



