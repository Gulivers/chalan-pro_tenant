// Este script define una función para añadir un "ticket" firmado a una URL, utilizado típicamente para autenticar conexiones WebSocket ante el backend.
// El ticket se solicita mediante un POST a '/api/auth/ws-ticket/' y se agrega como query param (?ticket=...) a la URL recibida.
// Útil para proteger canales WS donde el login JWT no se puede enviar por header.

import axios from "axios";

export async function withWsTicket(url) {
  if (!url) return url; // Si no hay URL, devuelve igual.
  const { data } = await axios.post("/api/auth/ws-ticket/"); // Solicita el ticket firmado al backend.
  const ticket = encodeURIComponent(data?.ticket || ""); // Sanitiza el ticket.
  const join = url.includes("?") ? "&" : "?"; // Decide si concatena con ? o &.
  return `${url}${join}ticket=${ticket}`; // Devuelve la URL con ticket como query param.
}
