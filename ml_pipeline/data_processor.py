import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.neighbors import NearestNeighbors
import os

INDIAN_STATES_COORDS = {
    'Andaman and Nicobar Islands': (11.7401, 92.6586),
    'Andhra Pradesh': (15.9129, 79.7400),
    'Arunachal Pradesh': (28.2180, 94.7278),
    'Assam': (26.2006, 92.9376),
    'Bihar': (25.0961, 85.3131),
    'Chandigarh': (30.7333, 76.7794),
    'Chhattisgarh': (21.2787, 81.8661),
    'Dadra and Nagar Haveli': (20.1809, 73.0169),
    'Goa': (15.2993, 74.1240),
    'Gujarat': (22.2587, 71.1924),
    'Haryana': (29.0588, 76.0856),
    'Himachal Pradesh': (31.1048, 77.1734),
    'Jammu and Kashmir ': (33.7782, 76.5762),
    'Jharkhand': (23.6102, 85.2799),
    'Karnataka': (15.3173, 75.7139),
    'Kerala': (10.8505, 76.2711),
    'Madhya Pradesh': (22.9734, 78.6569),
    'Maharashtra': (19.7515, 75.7139),
    'Manipur': (24.6637, 93.9063),
    'Meghalaya': (25.4670, 91.3662),
    'Mizoram': (23.1645, 92.9376),
    'Nagaland': (26.1584, 94.5624),
    'Odisha': (20.9517, 85.0985),
    'Puducherry': (11.9416, 79.8083),
    'Punjab': (31.1471, 75.3412),
    'Rajasthan': (27.0238, 74.2179),
    'Sikkim': (27.5330, 88.5122),
    'Tamil Nadu': (11.1271, 78.6569),
    'Telangana ': (18.1124, 79.0193),
    'Tripura': (23.9408, 91.9882),
    'Uttar Pradesh': (26.8467, 80.9462),
    'Uttarakhand': (30.0668, 79.0193),
    'West Bengal': (22.9868, 87.8550),
}

class AgriculturalDataProcessor:
    def __init__(self):
        self.scaler = StandardScaler()
        self.encoders = {}
        self.is_fitted = False
        self.knn = NearestNeighbors(n_neighbors=1)

    def load_dataset(self, data_path="Dataset"):
        final_file = os.path.join(data_path, "Final_Dataset_after_temperature.csv")
        fert_file = os.path.join(data_path, "Fertilizer.csv")
        
        df_agri = pd.read_csv(final_file)
        df_fert = pd.read_csv(fert_file)
        
        df_agri['Crop'] = df_agri['Crop'].str.strip().str.lower()
        df_fert['Crop'] = df_fert['Crop'].str.strip().str.lower()
        
        df = pd.merge(df_agri, df_fert, on='Crop', how='left')
        
        for col in ['N', 'P', 'K', 'pH']:
            df[col] = df[col].fillna(df[col].median())
            
        df['State_Name'] = df['State_Name'].str.strip()
        df['latitude'] = df['State_Name'].map(lambda x: INDIAN_STATES_COORDS.get(x, (20.5937, 78.9629))[0])
        df['longitude'] = df['State_Name'].map(lambda x: INDIAN_STATES_COORDS.get(x, (20.5937, 78.9629))[1])
        
        # Cleanup any remaining NaNs
        df = df.dropna(subset=['Yield_ton_per_hec', 'rainfall', 'temperature'])
        
        return df

    def fit_transform(self, df):
        target = df['Yield_ton_per_hec'].values
        features_df = df.copy()
        
        features_df['precipitation'] = features_df['rainfall']
        features_df['soil_ph'] = features_df['pH']
        features_df['soil_nutrients'] = features_df['N'] + features_df['P'] + features_df['K']
        features_df['humidity'] = 60.0 # Placeholder since dataset lacks it natively
        
        cat_cols = ['Crop']
        for col in cat_cols:
            le = LabelEncoder()
            features_df[col] = le.fit_transform(features_df[col].astype(str))
            self.encoders[col] = le
            
        self.num_cols = ['temperature', 'humidity', 'precipitation', 'soil_ph', 'soil_nutrients', 'latitude', 'longitude', 'Crop']
        X = features_df[self.num_cols].values
        
        X_scaled = self.scaler.fit_transform(X)
        self.is_fitted = True
        
        self.knn.fit(features_df[['latitude', 'longitude']].values)
        
        return X_scaled, target, self.num_cols

    def preprocess_request(self, data_dict):
        df = pd.DataFrame([data_dict])
        
        if 'crop_type' in df.columns:
            df['Crop'] = df['crop_type'].str.strip().str.lower()
        else:
            df['Crop'] = 'rice' # fallback
            
        for col in ['Crop']:
            if col in self.encoders:
                try:
                    df[col] = self.encoders[col].transform(df[col].astype(str))
                except ValueError:
                    df[col] = 0
            else:
                df[col] = 0
                
        # Fill any missing expected cols
        for col in self.num_cols:
            if col not in df.columns:
                df[col] = 0
                
        X = df[self.num_cols].values
        
        if self.is_fitted:
            X_scaled = self.scaler.transform(X)
        else:
            X_scaled = X
            
        return X_scaled
