import os
import pickle
import numpy as np
import pandas as pd
import warnings
from ml_pipeline.data_processor import AgriculturalDataProcessor
from ml_pipeline.models import create_ensemble_model
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

warnings.filterwarnings('ignore')

def main():
    print("--- Starting ML Training Pipeline ---")
    processor = AgriculturalDataProcessor()
    
    print("Loading datasets...")
    df = processor.load_dataset("Dataset")
    
    # Process max 20,000 rows to keep training time reasonable and fit in memory for GPR O(N^3)
    df = df.sample(min(20000, len(df)), random_state=42)
    print(f"Executing robust training on {len(df)} sampled rows to maximize R² score...")
    
    print("Preprocessing data...")
    X, y, cols = processor.fit_transform(df)
    print(f"Features shape: {X.shape}, Target shape: {y.shape}")
    
    print("Initializing models...")
    model = create_ensemble_model()
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print(f"Training Stacking Ensemble with 5-Fold CV on {len(X_train)} samples...")
    model.fit(X_train, y_train)
    
    print("Evaluating models...")
    y_pred = model.predict(X_test)
    
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    
    print("\n--- Model Evaluation ---")
    print(f"R² Score : {r2:.4f}")
    print(f"MAE      : {mae:.4f}")
    print(f"RMSE     : {rmse:.4f}")
    
    print("Saving models to ml_pipeline/...")
    with open("ml_pipeline/ensemble_model.pkl", "wb") as f:
        pickle.dump(model, f)
        
    with open("ml_pipeline/processor.pkl", "wb") as f:
        pickle.dump(processor, f)
        
    print("Training completed successfully.")

if __name__ == "__main__":
    main()
