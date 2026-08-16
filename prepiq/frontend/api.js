const Api = (() => {
  function getAccessToken() {
    return localStorage.getItem("access_token");
  }

  async function request(path, options = {}) {
    const headers = options.headers || {};
    const token = getAccessToken();
    if (token && !options.skipAuth) {
      headers["Authorization"] = `Bearer ${token}`;
    }
    if (options.json) {
      headers["Content-Type"] = "application/json";
      options.body = JSON.stringify(options.json);
    }

    const res = await fetch(`${API_BASE}${path}`, { ...options, headers });

    if (res.status === 401 && !options._retried) {
      // access token likely expired — try refreshing once, then retry the call
      const refreshed = await tryRefresh();
      if (refreshed) {
        return request(path, { ...options, _retried: true });
      }
    }

    if (!res.ok) {
      let detail = "Request failed";
      try {
        const err = await res.json();
        detail = err.detail || detail;
      } catch (_) {}
      throw new Error(detail);
    }

    if (res.status === 204) return null;
    return res.json();
  }

  async function tryRefresh() {
    const refreshToken = localStorage.getItem("refresh_token");
    if (!refreshToken) return false;
    try {
      const res = await fetch(`${API_BASE}/auth/refresh`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });
      if (!res.ok) return false;
      const data = await res.json();
      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("refresh_token", data.refresh_token);
      return true;
    } catch (_) {
      return false;
    }
  }

  return {
    get: (path) => request(path, { method: "GET" }),
    post: (path, json) => request(path, { method: "POST", json }),
    postForm: (path, formData) => request(path, { method: "POST", body: formData }),
    getAccessToken,
  };
})();
