// Dashboard data caching utility
// Stores dashboard data in localStorage for instant loading on return visits
// Strategy: Always show cached data immediately, then fetch fresh data in background

const CACHE_KEY_PREFIX = "dashboard_cache_team_";

/**
 * Get the cache key for the current team
 * @returns {string | null} Cache key or null if no team_id in session
 */
function getCacheKey() {
  const teamId = sessionStorage.getItem("team_id");
  if (!teamId) return null;
  return `${CACHE_KEY_PREFIX}${teamId}`;
}

/**
 * Get cached dashboard data if available
 * @returns {object | null} The cached dashboard data, or null if not available
 */
export function getCachedDashboard() {
  try {
    const cacheKey = getCacheKey();
    if (!cacheKey) return null;

    const cached = localStorage.getItem(cacheKey);
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
    const cacheKey = getCacheKey();
    if (!cacheKey) return;

    localStorage.setItem(cacheKey, JSON.stringify(data));
  } catch (e) {
    console.warn("Failed to cache dashboard:", e);
  }
}

/**
 * Clear the dashboard cache (e.g., on logout)
 */
export function clearDashboardCache() {
  const cacheKey = getCacheKey();
  if (cacheKey) {
    localStorage.removeItem(cacheKey);
  }
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
