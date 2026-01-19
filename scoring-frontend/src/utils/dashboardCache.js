// Dashboard data caching utility
// Stores dashboard data in localStorage for instant loading on return visits

const CACHE_KEY = "dashboard_cache";
const CACHE_TIMESTAMP_KEY = "dashboard_cache_timestamp";
const CACHE_MAX_AGE = 5 * 60 * 1000; // 5 minutes - data older than this will still show but trigger refresh

/**
 * Get cached dashboard data if available
 * @returns {{ data: object, isStale: boolean } | null}
 */
export function getCachedDashboard() {
  try {
    const cached = localStorage.getItem(CACHE_KEY);
    const timestamp = localStorage.getItem(CACHE_TIMESTAMP_KEY);
    
    if (!cached) return null;
    
    const data = JSON.parse(cached);
    const age = Date.now() - parseInt(timestamp || "0", 10);
    const isStale = age > CACHE_MAX_AGE;
    
    return { data, isStale };
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
    localStorage.setItem(CACHE_TIMESTAMP_KEY, Date.now().toString());
  } catch (e) {
    console.warn("Failed to cache dashboard:", e);
  }
}

/**
 * Clear the dashboard cache (e.g., on logout)
 */
export function clearDashboardCache() {
  localStorage.removeItem(CACHE_KEY);
  localStorage.removeItem(CACHE_TIMESTAMP_KEY);
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
