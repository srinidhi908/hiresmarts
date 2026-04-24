import { useState } from "react";
import { analyzeResume } from "../services/api";

export default function Applicant() {
  const [file, setFile] = useState(null);
  const [jd, setJd] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  // CHAT
  const [chat, setChat] = useState([]);
  const [input, setInput] = useState("");

  // =========================
  // 🔍 ANALYZE
  // =========================
  const handleSubmit = async () => {
    if (!file || !jd) {
      alert("Please upload resume and enter job description");
      return;
    }

    try {
      setLoading(true);
      const data = await analyzeResume(file, jd);
      setResult(data);

      // 🔥 Auto first AI message
      setChat([
        {
          sender: "bot",
          text: "Analysis completed! Ask me how to improve your resume 🚀",
        },
      ]);
    } catch {
      alert("Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  // =========================
  // 🤖 SMART CHATBOT (NO API)
  // =========================
  const handleSend = () => {
    if (!input || !result) return;

    const userMsg = { sender: "user", text: input };
    setChat((prev) => [...prev, userMsg]);

    let reply = "Try asking about skills, score, or improvements 🚀";

    const msg = input.toLowerCase();

    if (msg.includes("missing")) {
      reply = `You are missing: ${result.missing_skills.join(", ")}`;
    } else if (msg.includes("improve")) {
      reply = result.suggestions?.join(" ") || "Add more relevant skills.";
    } else if (msg.includes("score")) {
      reply = `Your match score is ${result.match_score_percent}%`;
    } else if (msg.includes("apply")) {
      reply =
        result.match_score_percent >= 70
          ? "Yes! You are a strong candidate 💪"
          : "Improve your skills before applying.";
    }

    const botMsg = { sender: "bot", text: reply };

    setTimeout(() => {
      setChat((prev) => [...prev, botMsg]);
    }, 500);

    setInput("");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-yellow-50">

      {/* HEADER */}
      <div className="bg-gradient-to-r from-blue-500 to-cyan-500 text-white py-10 rounded-b-3xl shadow-md">
        <div className="text-center">
          <h1 className="text-3xl md:text-4xl font-bold">
            🚀 HireSmart – Applicant Mode
          </h1>
          <p className="mt-2 text-sm md:text-base opacity-90">
            Analyze your resume and improve your chances
          </p>
        </div>
      </div>

      {/* MAIN */}
      <div className="p-6 md:p-10 -mt-6">
        <div className="max-w-6xl mx-auto grid md:grid-cols-2 gap-10">

          {/* LEFT */}
          <div className="space-y-6">

            {/* Upload */}
            <div className="bg-white/80 p-5 rounded-2xl shadow border">
              <p className="font-semibold mb-2">Upload Resume</p>
              <input type="file" onChange={(e) => setFile(e.target.files[0])} />
              {file && (
                <p className="text-xs text-gray-600 mt-2 truncate">
                  {file.name}
                </p>
              )}
            </div>

            {/* JD */}
            <div className="bg-white/80 p-5 rounded-2xl shadow border">
              <p className="font-semibold mb-2">Job Description</p>

              <textarea
                className="w-full p-3 border rounded-lg"
                rows="4"
                placeholder="e.g. python, java, sql..."
                onChange={(e) => setJd(e.target.value)}
              />

              <button
                onClick={handleSubmit}
                disabled={loading}
                className="mt-4 w-full bg-gradient-to-r from-blue-500 to-cyan-500 text-white py-2 rounded-lg hover:scale-[1.02] transition"
              >
                {loading ? "Analyzing..." : "Analyze Resume 🚀"}
              </button>
            </div>
          </div>

          {/* RIGHT */}
          <div>
            <h3 className="text-2xl font-semibold mb-4">
              Analysis Result
            </h3>

            {!result && (
              <div className="bg-white p-6 rounded-2xl shadow text-center text-gray-400">
                No analysis yet
              </div>
            )}

            {result && (
              <>
                {/* RESULT CARD */}
<div className="bg-white p-6 rounded-2xl shadow space-y-5 border">

  {/* SCORE */}
  <div>
    <p className="text-lg font-semibold flex items-center gap-2">
      📊 Match Score: {result.match_score_percent}%
    </p>

    {/* 🔥 Dynamic Color Bar */}
    <div className="w-full bg-gray-200 h-3 rounded-full mt-3">
      <div
        className={`h-3 rounded-full transition-all duration-500 ${
          result.classification === "Suitable"
            ? "bg-green-500"
            : result.classification === "Moderate"
            ? "bg-yellow-500"
            : "bg-red-500"
        }`}
        style={{ width: `${result.match_score_percent}%` }}
      />
    </div>
  </div>

  {/* STATUS */}
  <div>
    <p
      className={`font-semibold ${
        result.classification === "Suitable"
          ? "text-green-600"
          : result.classification === "Moderate"
          ? "text-yellow-600"
          : "text-red-600"
      }`}
    >
      Status: {result.classification}
    </p>
  </div>

  {/* 🔥 RESUME STRENGTH */}
  <div>
    <p className="text-gray-800 font-medium">
      Resume Strength:{" "}
      <span className="font-semibold">
        {result.match_score_percent >= 70
          ? "Strong 💪"
          : result.match_score_percent >= 40
          ? "Average ⚡"
          : "Weak ❌"}
      </span>
    </p>
  </div>

  <hr />

  {/* MATCHED */}
  <div>
    <p className="font-semibold mb-2">✅ Matched Skills:</p>
    <div className="flex flex-wrap gap-2">
      {result.matched_skills.map((s, i) => (
        <span
          key={i}
          className="bg-green-100 text-green-700 px-3 py-1 rounded-full text-xs"
        >
          {s}
        </span>
      ))}
    </div>
  </div>

  {/* MISSING */}
  <div>
    <p className="font-semibold mb-2">❌ Missing Skills:</p>
    <div className="flex flex-wrap gap-2">
      {result.missing_skills.map((s, i) => (
        <span
          key={i}
          className="bg-red-100 text-red-700 px-3 py-1 rounded-full text-xs"
        >
          {s}
        </span>
      ))}
    </div>
  </div>

  <hr />

  {/* 🔥 SUGGESTIONS */}
  <div>
    <p className="font-semibold mb-2 flex items-center gap-2">
      💡 Suggestions
    </p>

    <ul className="list-disc ml-5 text-sm text-gray-700 space-y-1">
      {result.suggestions?.map((s, i) => (
        <li key={i}>{s}</li>
      ))}
    </ul>
  </div>

</div>

                {/* CHATBOT */}
                <div className="bg-white p-6 rounded-2xl shadow mt-6">
                  <h4 className="font-semibold mb-3">💬 AI Assistant</h4>

                  <div className="h-44 overflow-y-auto bg-gray-50 p-3 rounded-lg mb-3">
                    {chat.map((msg, i) => (
                      <div
                        key={i}
                        className={`mb-2 ${
                          msg.sender === "user"
                            ? "text-right"
                            : "text-left"
                        }`}
                      >
                        <span
                          className={`inline-block px-3 py-1 rounded-lg text-sm ${
                            msg.sender === "user"
                              ? "bg-blue-500 text-white"
                              : "bg-gray-200"
                          }`}
                        >
                          {msg.text}
                        </span>
                      </div>
                    ))}
                  </div>

                  <div className="flex gap-2">
                    <input
                      value={input}
                      onChange={(e) => setInput(e.target.value)}
                      className="flex-1 border p-2 rounded-lg text-sm"
                      placeholder="Ask about your resume..."
                    />
                    <button
                      onClick={handleSend}
                      className="bg-blue-500 text-white px-4 rounded-lg"
                    >
                      Send
                    </button>
                  </div>
                </div>
              </>
            )}
          </div>

        </div>
      </div>
    </div>
  );
}