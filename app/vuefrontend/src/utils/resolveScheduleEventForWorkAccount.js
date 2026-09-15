import axios from "axios";

function matchesWorkAccount(event, workAccountId) {
  const wa = event?.work_account;
  if (wa == null) return false;
  if (typeof wa === "number") return wa === workAccountId;
  if (typeof wa === "object" && wa.id != null) return wa.id === workAccountId;
  return wa === workAccountId;
}

/**
 * Resolves a schedule event id for a work account using /api/my-events/.
 * Picks the most recent event (by date) among matches.
 * Returns null when no linked event exists.
 */
export async function resolveScheduleEventForWorkAccount(workAccountId, title = "") {
  if (!workAccountId) return null;

  const matches = [];
  const searchParam = title ? `&search=${encodeURIComponent(title)}` : "";
  let page = 1;
  let hasNext = true;

  while (hasNext && page <= 10) {
    const { data } = await axios.get(`/api/my-events/?page=${page}${searchParam}`);
    const results = Array.isArray(data?.results) ? data.results : [];
    matches.push(...results.filter((event) => matchesWorkAccount(event, workAccountId)));

    if (!data?.next) {
      hasNext = false;
    } else {
      page += 1;
    }
  }

  if (!matches.length) return null;

  matches.sort((a, b) => {
    const dateA = a?.date ? new Date(a.date).getTime() : 0;
    const dateB = b?.date ? new Date(b.date).getTime() : 0;
    return dateB - dateA;
  });

  return matches[0]?.id ?? null;
}

export const WORK_ORDER_VIEWER_TABS = [
  { id: "chat", label: "Chat for Job" },
  { id: "notes", label: "Notes" },
  { id: "folder", label: "Folder" },
  { id: "contracts", label: "Contracts" },
  { id: "transactions", label: "Transactions" },
];

export const WORK_ORDER_VIEWER_TAB_IDS = WORK_ORDER_VIEWER_TABS.map((tab) => tab.id);
