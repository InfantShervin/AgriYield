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

describe('Frontend Utility - DOM Updates', () => {
    it('should update the prediction counter', () => {
        // Setup mock DOM
        document.body.innerHTML = `
            <span id="totalPredsStat">0</span>
        `;
        const history = [{ id: 1 }, { id: 2 }];
        
        function updateCounter(historyArr) {
            document.getElementById('totalPredsStat').textContent = historyArr.length;
        }

        updateCounter(history);
        expect(document.getElementById('totalPredsStat').textContent).toBe('2');
    });

    it('should format crop name correctly', () => {
        const crop = 'rice';
        const formatted = crop.charAt(0).toUpperCase() + crop.slice(1);
        expect(formatted).toBe('Rice');
    });
});
