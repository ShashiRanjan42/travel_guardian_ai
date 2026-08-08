const API_ROOT = import.meta.env.VITE_API_URL || '/api/v1';

const token = () => localStorage.getItem('guardian_access_token');

async function request(path, options = {}) {
  const headers = { ...(options.headers || {}) };
  if (options.body) headers['Content-Type'] = 'application/json';
  if (token()) headers.Authorization = `Bearer ${token()}`;
  const response = await fetch(`${API_ROOT}${path}`, { ...options, headers });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(payload.detail || 'Request failed');
  return payload.data ?? payload;
}

const toUser = (user, accessToken) => ({
  id: user.id, name: user.full_name, email: user.email,
  role: user.role === 'ops_agent' ? 'OPS' : 'CUSTOMER', tier: 'Guardian',
  travellerId: user.traveller_id, accessToken,
});

const toIncident = (alert, detail) => ({
  id: alert.id, itinerary_id: alert.booking_id, customer_name: alert.traveller_name,
  title: alert.headline, description: `${alert.disruption_type} disruption affecting ${alert.destination}.`,
  type: alert.disruption_type, severity: alert.severity, severity_score: alert.severity_score,
  status: alert.status === 'RESOLVED' ? 'RECOVERED' : 'RECOVERY_PROPOSED',
  recovery_plans: (detail?.options || []).map((option) => ({
    id: option.id, title: option.label, description: option.summary,
    cost_delta: option.cost_delta_inr, time_delta: option.time_delta_minutes,
    status: option.status, confidence: option.confidence,
  })),
});

const toItinerary = (booking, incident) => ({
  id: booking.id, title: `${booking.origin} → ${booking.destination}`,
  status: booking.status?.toUpperCase() || 'ACTIVE',
  risk_score: incident?.severity_score || 15, risk_level: incident?.severity || 'LOW',
  start_date: booking.start_date, end_date: booking.end_date, leg_count: 1,
  customer: { id: booking.traveller?.id, name: booking.traveller?.full_name || 'Traveller', email: booking.traveller?.email || '', tier: 'Guardian' },
  legs: [{ id: `${booking.id}-leg`, leg_type: 'TRIP', sequence_order: 1, title: `${booking.origin} → ${booking.destination}`, operator: 'Wayfare protected booking', code: booking.pnr, origin: booking.origin, destination: booking.destination, departure_time: booking.start_date, arrival_time: booking.end_date, status: booking.status?.toUpperCase() || 'CONFIRMED' }],
  incidents: incident ? [incident] : [],
});

export const api = {
  async login(email, password) {
    const data = await request('/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) });
    return toUser(data.user, data.access_token);
  },
  async loadDashboard() {
    const [bookingsResponse, alertsResponse, analytics] = await Promise.all([request('/ops/bookings'), request('/ops/alerts'), request('/ops/dashboard/summary')]);
    const alerts = alertsResponse.items || [];
    const detailedAlerts = await Promise.all(alerts.map(async (alert) => {
      try { return [alert.id, await request(`/ops/alerts/${alert.id}`)]; } catch { return [alert.id, null]; }
    }));
    const detailById = Object.fromEntries(detailedAlerts);
    const incidents = alerts.map((alert) => toIncident(alert, detailById[alert.id]));
    const incidentByBooking = Object.fromEntries(incidents.map((incident) => [incident.itinerary_id, incident]));
    const traces = await Promise.all(alerts.map(async (alert) => {
      try { return await request(`/ops/alerts/${alert.id}/trace`); } catch { return []; }
    }));
    const agentLogs = traces.flat().map((trace) => ({
      agent_name: trace.agent,
      status: trace.status,
      duration_ms: trace.duration_ms,
      reasoning: trace.reasoning,
    }));
    return { itineraries: (bookingsResponse.items || []).map((booking) => toItinerary(booking, incidentByBooking[booking.id])), incidents, analytics, agentLogs };
  },
  approvePlan(incidentId, planId, bookingId, role) {
    if (role === 'OPS') return request(`/ops/alerts/${incidentId}/options/${planId}/approve`, { method: 'POST', body: '{}' });
    return request(`/traveller/bookings/${bookingId}/alerts/${incidentId}/select`, { method: 'POST', body: JSON.stringify({ option_id: planId }) });
  },
  async createBooking(payload) {
    const draft = await request('/book/draft', { method: 'POST', body: JSON.stringify(payload) });
    return request(`/book/draft/${draft.draft_id}/confirm`, { method: 'POST', body: JSON.stringify(payload) });
  },
  searchDestinations(query) {
    return request(`/book/destinations/search?q=${encodeURIComponent(query)}`);
  },
  getCurrentWeather(latitude, longitude) {
    return request(`/weather/current?latitude=${encodeURIComponent(latitude)}&longitude=${encodeURIComponent(longitude)}`);
  },
  checkLegWeather(legId) {
    return request(`/weather/check-leg/${legId}`, { method: 'POST', body: '{}' });
  },
  injectDisruption(scenarioId) {
    return request('/demo/inject-disruption', { method: 'POST', body: JSON.stringify({ scenario_id: scenarioId }) });
  },
  resetDemo() {
    return request('/demo/reset', { method: 'POST', body: '{}' });
  },
};
