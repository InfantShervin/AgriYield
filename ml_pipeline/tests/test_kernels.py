import numpy as np
import pytest
from ml_pipeline.models import BesselKKernel

def test_besselk_kernel_diagonal():
    """Verify that the kernel diagonal is 1.0 (self-correlation)"""
    kernel = BesselKKernel(length_scale=1.0, nu=1.5)
    X = np.array([[1.0, 2.0], [3.0, 4.0]])
    K = kernel(X)
    assert np.allclose(np.diag(K), 1.0)

def test_besselk_kernel_symmetry():
    """Verify that the kernel matrix is symmetric"""
    kernel = BesselKKernel(length_scale=1.0, nu=1.5)
    X = np.random.rand(5, 2)
    K = kernel(X)
    assert np.allclose(K, K.T)

def test_besselk_kernel_distance_impact():
    """Verify that points further away have lower correlation"""
    kernel = BesselKKernel(length_scale=1.0, nu=1.5)
    X1 = np.array([[0.0, 0.0]])
    X2 = np.array([[0.1, 0.1]]) # Close
    X3 = np.array([[10.0, 10.0]]) # Far
    
    k_close = kernel(X1, X2)[0, 0]
    k_far = kernel(X1, X3)[0, 0]
    
    assert k_close > k_far
    assert k_far < 0.1 # Should be very low correlation at this distance
