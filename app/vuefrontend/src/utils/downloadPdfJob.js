/**
 * Async PDF download via job enqueue + poll (Redis-backed backend).
 * Falls back to sync GET if job enqueue returns 503.
 */
import axios from "axios";
import { getAccessToken } from "@/auth/tokenHelpers";

const POLL_MS = 1000;
const MAX_WAIT_MS = 90000;
const REQUEST_TIMEOUT_MS = 30000;

function authHeaders() {
  return { Authorization: `Bearer ${getAccessToken()}` };
}

function isMobileDevice() {
  return (
    /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
      navigator.userAgent
    ) || window.innerWidth <= 768
  );
}

function openOrDownloadPdf(fileBase64, filename) {
  const byteCharacters = atob(fileBase64);
  const byteNumbers = new Array(byteCharacters.length);
  for (let i = 0; i < byteCharacters.length; i += 1) {
    byteNumbers[i] = byteCharacters.charCodeAt(i);
  }
  const blob = new Blob([new Uint8Array(byteNumbers)], {
    type: "application/pdf",
  });
  const url = window.URL.createObjectURL(blob);

  if (isMobileDevice()) {
    const link = document.createElement("a");
    link.href = url;
    link.download = filename || "document.pdf";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  } else {
    const win = window.open(url, "_blank");
    if (!win) {
      const link = document.createElement("a");
      link.href = url;
      link.download = filename || "document.pdf";
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  }

  setTimeout(() => window.URL.revokeObjectURL(url), 1000);
}

async function pollJob(jobId) {
  const started = Date.now();
  while (Date.now() - started < MAX_WAIT_MS) {
    const { data } = await axios.get(`/api/pdf/jobs/${jobId}/`, {
      headers: authHeaders(),
      timeout: REQUEST_TIMEOUT_MS,
    });
    if (data?.status === "ready" && data.file) {
      return data;
    }
    if (data?.status === "error") {
      throw new Error(data.detail || "PDF generation failed");
    }
    await new Promise((r) => setTimeout(r, POLL_MS));
  }
  throw new Error("PDF generation timed out");
}

async function syncGet(url) {
  const { data } = await axios.get(url, {
    headers: authHeaders(),
    timeout: MAX_WAIT_MS,
  });
  if (!data?.file) {
    throw new Error("No PDF file was returned from the server.");
  }
  return data;
}

/**
 * @param {object} opts
 * @param {string} opts.jobsUrl - POST to create job (e.g. /api/documents/5/pdf/jobs/)
 * @param {string} opts.syncUrl - GET fallback sync PDF
 * @param {object} [opts.jobsBody] - optional JSON body for POST (schedule range, etc.)
 * @param {string} [opts.fallbackFilename]
 */
export async function downloadPdfViaJob({
  jobsUrl,
  syncUrl,
  jobsBody = {},
  fallbackFilename = "document.pdf",
} = {}) {
  let data;
  try {
    const created = await axios.post(jobsUrl, jobsBody, {
      headers: authHeaders(),
      timeout: REQUEST_TIMEOUT_MS,
    });
    const jobId = created.data?.job_id;
    if (!jobId) {
      throw new Error("No job_id returned");
    }
    data = await pollJob(jobId);
  } catch (err) {
    const status = err?.response?.status;
    // Redis unavailable or job API missing → sync fallback
    if (status === 503 || status === 404 || status === 405) {
      data = await syncGet(syncUrl);
    } else if (!err?.response && syncUrl) {
      // network / unexpected — try sync once
      data = await syncGet(syncUrl);
    } else {
      throw err;
    }
  }

  openOrDownloadPdf(data.file, data.filename || fallbackFilename);
  return true;
}

export async function downloadTransactionPdfJob(documentId) {
  return downloadPdfViaJob({
    jobsUrl: `/api/documents/${documentId}/pdf/jobs/`,
    syncUrl: `/api/documents/${documentId}/pdf/`,
    fallbackFilename: `transaction_${documentId}.pdf`,
  });
}

export async function downloadMaterialRequestPdfJob(documentId) {
  return downloadPdfViaJob({
    jobsUrl: `/api/material-requests/${documentId}/pdf-jobs/`,
    syncUrl: `/api/material-requests/${documentId}/pdf/`,
    fallbackFilename: `MR-${documentId}.pdf`,
  });
}

export async function downloadContractPdfJob(contractId) {
  return downloadPdfViaJob({
    jobsUrl: `/api/contract-pdf/${contractId}/jobs/`,
    syncUrl: `/api/contract-pdf/${contractId}/`,
    fallbackFilename: `contract_${contractId}.pdf`,
  });
}

export async function downloadSchedulePdfJob(startAt, endAt) {
  return downloadPdfViaJob({
    jobsUrl: `/api/schedule-report/jobs/`,
    syncUrl: `/api/schedule-report/?start_at=${encodeURIComponent(
      startAt
    )}&end_at=${encodeURIComponent(endAt)}`,
    jobsBody: { start_at: startAt, end_at: endAt },
    fallbackFilename: `schedule_${startAt}_to_${endAt}.pdf`,
  });
}
