import { describe, it, expect } from 'vitest';

/**
 * Pure logic test for Yield Rating.
 * (This function is copied/imported from app.js logic)
 */
function getYieldRating(yield_val) {
  if (yield_val >= 8)   return { label: '🏆 Excellent Yield', color: '#22c55e' };
  if (yield_val >= 5)   return { label: '✅ Good Yield',      color: '#4ade80' };
  if (yield_val >= 3)   return { label: '🟡 Average Yield',   color: '#fbbf24' };
  return                       { label: '⚠️ Poor Yield',      color: '#f87171' };
}

describe('Frontend Logic - Yield Rating', () => {
    it('should return Excellent for yield >= 8', () => {
        const rating = getYieldRating(9.5);
        expect(rating.label).toContain('Excellent');
        expect(rating.color).toBe('#22c55e');
    });

    it('should return Good for yield between 5 and 7.9', () => {
        const rating = getYieldRating(6.2);
        expect(rating.label).toContain('Good');
    });

    it('should return Average for yield between 3 and 4.9', () => {
        const rating = getYieldRating(3.5);
        expect(rating.label).toContain('Average');
    });

    it('should return Poor for yield < 3', () => {
        const rating = getYieldRating(1.2);
        expect(rating.label).toContain('Poor');
        expect(rating.color).toBe('#f87171');
    });
});
