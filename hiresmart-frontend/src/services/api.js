// =======================================
// 🔥 BASE CONFIG
// =======================================
const BASE_URL = "https://hiresmarts-backend.onrender.com";


// =======================================
// 🔧 Helper: fetch with timeout + better errors
// =======================================
const fetchWithTimeout = async (url, options = {}, timeout = 30000) => {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
    });

    if (!response.ok) {
      const text = await response.text();
      throw new Error(text || "Request failed");
    }

    return response;
  } catch (err) {
    if (err.name === "AbortError") {
      throw new Error("Request timeout ⏳ (Render may be waking up)");
    }
    throw err;
  } finally {
    clearTimeout(id);
  }
};


// =======================================
// 🔹 Single Resume (Applicant Mode)
// =======================================
export const analyzeResume = async (file, jd) => {
  const formData = new FormData();
  formData.append("resume_file", file);
  formData.append("job_description", jd);

  const response = await fetchWithTimeout(`${BASE_URL}/match-resume`, {
    method: "POST",
    body: formData,
  });

  return await response.json();
};


// =======================================
// 🔹 Multiple Resumes (Recruiter Mode)
// =======================================
export const analyzeMultipleResumes = async (files, jd) => {
  const formData = new FormData();

  files.forEach((file) => {
    formData.append("files", file);
  });

  formData.append("job_description", jd);

  const response = await fetchWithTimeout(`${BASE_URL}/match-multiple`, {
    method: "POST",
    body: formData,
  });

  return await response.json();
};


// =======================================
// 🔥 DOWNLOAD PDF REPORT
// =======================================
export const downloadReport = async (results, companyName = "HireSmart AI") => {
  try {
    const formattedResults = results.map((r) => ({
      name: r.name,
      match_score: r.match_score,
      classification: r.classification,
      matched_skills: r.matched_skills || [],
      missing_skills: r.missing_skills || [],
    }));

    const response = await fetchWithTimeout(`${BASE_URL}/download-report`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        company_name: companyName,
        results: formattedResults,
      }),
    });

    const blob = await response.blob();

    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "HireSmart_Report.pdf";
    document.body.appendChild(a);
    a.click();
    a.remove();

  } catch (err) {
    console.error(err);
    alert(err.message || "PDF download failed ❌");
  }
};


// =======================================
// 💬 CHATBOT API (FIXED)
// =======================================
export const chatWithBot = async (message, results) => {
  const response = await fetchWithTimeout(`${BASE_URL}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      message: message,
      results: results,
    }),
  });

  return await response.json();
};