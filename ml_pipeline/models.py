import numpy as np
from sklearn.ensemble import RandomForestRegressor, StackingRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import Kernel, Matern, Hyperparameter
import xgboost as xgb
from sklearn.linear_model import RidgeCV
from scipy.special import kv, gamma
from sklearn.metrics.pairwise import pairwise_distances

class BesselKKernel(Kernel):
    """
    Custom BesselK Kernel for spatial relationships as defined in the paper.
    k(x_i, x_j) = (2^(1-nu) / Gamma(nu)) * ( (sqrt(2nu)*r/l)^nu * K_nu(sqrt(2nu)*r/l) )
    """
    def __init__(self, length_scale=1.0, nu=1.5):
        self.length_scale = length_scale
        self.nu = nu
        
    def __call__(self, X, Y=None, eval_gradient=False):
        X = np.atleast_2d(X)
        if Y is None:
            dists = pairwise_distances(X, metric='euclidean')
        else:
            dists = pairwise_distances(X, Y, metric='euclidean')
            
        dists[dists == 0.0] = np.finfo(float).eps
        
        scaled_dists = (np.sqrt(2 * self.nu) * dists) / self.length_scale
        
        coeff = (2 ** (1 - self.nu)) / gamma(self.nu)
        term1 = (scaled_dists ** self.nu)
        term2 = kv(self.nu, scaled_dists)
        
        K = coeff * term1 * term2
        
        if Y is None:
            np.fill_diagonal(K, 1.0)
            
        if eval_gradient:
            # For simplicity, returning zero gradients; in practice, optimizing length_scale
            # would require actual analytical gradients. We configure optimizer=None in GPR.
            return K, np.zeros((K.shape[0], K.shape[1], 1))
            
        return K

    def diag(self, X):
        return np.ones(X.shape[0])

    def is_stationary(self):
        return True

def create_ensemble_model():
    """
    Creates the Stacking Ensemble Model mentioned in the paper:
    1. Random Forest (Stability)
    2. XGBoost (High accuracy)
    3. MLP (Non-linear)
    4. GPR with Matern Kernel (Smooth)
    5. GPR with BesselK Kernel (Spatial)
    Meta-learner: RidgeCV
    """
    
    # 1. Random Forest
    rf = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
    
    # 2. XGBoost
    xgb_model = xgb.XGBRegressor(n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42)
    
    # 3. MLP Neural Network (with early stopping mimicking dropout/regularization)
    mlp = MLPRegressor(hidden_layer_sizes=(128, 64), activation='relu', max_iter=500, early_stopping=True, random_state=42)
    
    # 4. GPR with Matern Kernel
    gpr_matern = GaussianProcessRegressor(kernel=Matern(nu=1.5), random_state=42)
    
    # 5. GPR with custom BesselK Kernel
    # Since we lack analytic gradients for the custom kernel, we turn off L-BFGS-B optimizer
    gpr_besselk = GaussianProcessRegressor(kernel=BesselKKernel(length_scale=1.0, nu=1.5), optimizer=None, random_state=42)
    
    # Base estimators for stacking
    estimators = [
        ('rf', rf),
        ('xgb', xgb_model),
        ('mlp', mlp),
        ('gpr_matern', gpr_matern),
        ('gpr_besselk', gpr_besselk)
    ]
    
    # Meta learner: RidgeCV
    ensemble = StackingRegressor(
        estimators=estimators,
        final_estimator=RidgeCV(),
        cv=5, # 5-Fold Cross Validation as specified in paper
        n_jobs=-1
    )
    
    return ensemble
