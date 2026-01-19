// Dashboard data caching utility
// Stores dashboard data in localStorage for instant loading on return visits
// Strategy: Always show cached data immediately, then fetch fresh data in background

const CACHE_KEY = "dashboard_cache";

/**
 * Get cached dashboard data if available
 * @returns {object | null} The cached dashboard data, or null if not available
 */
export function getCachedDashboard() {
  try {
    const cached = localStorage.getItem(CACHE_KEY);
    if (!cached) return null;
    return JSON.parse(cached);
  } catch (e) {
    console.warn("Failed to read dashboard cache:", e);
    return null;
  }
}

/**
 * Save dashboard data to cache
 * @param {object} data - Dashboard response data
 */
export function cacheDashboard(data) {
  try {
    localStorage.setItem(CACHE_KEY, JSON.stringify(data));
  } catch (e) {
    console.warn("Failed to cache dashboard:", e);
  }
}

/**
 * Clear the dashboard cache (e.g., on logout)
 */
export function clearDashboardCache() {
  localStorage.removeItem(CACHE_KEY);
}

/**
 * Prefetch dashboard data and cache it
 * Call this after login to have data ready when user navigates to dashboard
 * @returns {Promise<object | null>}
 */
export async function prefetchDashboard() {
  const token = sessionStorage.getItem("jwt_token");
  const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;
  
  if (!token) return null;
  
  try {
    const response = await fetch(`${BACKEND_URL}/dashboard`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    
    if (!response.ok) return null;
    
    const data = await response.json();
    cacheDashboard(data);
    return data;
  } catch (e) {
    console.warn("Dashboard prefetch failed:", e);
    return null;
  }
}
