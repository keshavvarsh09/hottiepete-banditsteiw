// Configurable backend base URL (set window.BACKEND_BASE_URL via config.js for Vercel)
const API = (window.BACKEND_BASE_URL || "http://localhost:8000");
const main = document.getElementById("main");
const nav = document.getElementById("nav");

async function api(path, opts = {}) {
  const r = await fetch(API + path, opts);
  if (!r.ok) throw new Error(await r.text());
  const ct = r.headers.get("content-type") || "";
  return ct.includes("application/json") ? r.json() : r;
}

// ---- shared helpers used by the editor views ----
const val = (id) => (document.getElementById(id) || {}).value || "";
const post = (obj) => ({
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(obj),
});
const bgSelect = (bgs) => `<label class="muted">Background</label>
  <select id="bg">${(bgs || []).map((b) => `<option value=\"${b.path}\">${b.category} / ${b.name}</option>`).join("")}</select>`;
const subSelect = () => `<label class="muted">Subtitle style</label>
  <select id="substyle">${["Default","TikTok","Cinema","Bold","Colorful","Cyberpunk","Soft","Cartoon","Haze"].map((s) => `<option>${s}</option>`).join("")}</select>`;

async function renderProject(type, data, name) {
  const proj = await api("/api/projects", post({ name: name || type, type, data }));
  const { job_id } = await api(`/api/projects/${proj.id}/render`, { method: "POST" });
  pollJob(job_id);
}

nav.addEventListener("click", (e) => {
  const a = e.target.closest("a[data-view]");
  if (!a) return;
  document.querySelectorAll("#nav a").forEach((x) => x.classList.remove("active"));
  a.classList.add("active");
  render(a.dataset.view);
});

const stub = (title, note) => `<div class="card"><h1>${title}</h1>
  <p class="muted">${note}</p><span class="tag">Scaffolded — TODO</span></div>`;

async function render(view) {
  if (views[view]) return views[view]();
  main.innerHTML = stub(view, "This generator is scaffolded; full flow coming.");
}

const views = {
  home: async () => {
    const vids = await api("/api/videos").catch(() => []);
    const chars = await api("/api/characters").catch(() => []);
    const bgs = await api("/api/backgrounds").catch(() => []);
    main.innerHTML = `
      <div class="card"><h1>hottiepete banditsteiw 🎬</h1>
        <p class="muted">Self-hosted AI short-video generator &mdash; 9:16 vertical, 1080&times;1920.</p>
        <div class="banner">✨ Draggable character placement &bull; 9 subtitle presets &bull; word-level karaoke captions</div>
        <div class="stats-row">
          <div class="stat-box"><span class="stat-num">${(vids||[]).length}</span><span class="stat-label">Videos</span></div>
          <div class="stat-box"><span class="stat-num">${(chars||[]).length}</span><span class="stat-label">Characters</span></div>
          <div class="stat-box"><span class="stat-num">${(bgs||[]).length}</span><span class="stat-label">Backgrounds</span></div>
        </div>
        <h2>Generate</h2>
        <div class="grid">
          <div class="card home-card" data-goto="dialogue"><span class="home-icon">🎭</span><strong>Dialogue Video</strong><p class="muted">Two-character AI scripts with TTS, B-roll, and karaoke subs.</p></div>
          <div class="card home-card" data-goto="reddit"><span class="home-icon">📰</span><strong>Reddit Video</strong><p class="muted">Narrate a Reddit post card over a looping background.</p></div>
          <div class="card home-card" data-goto="twitter"><span class="home-icon">🐦</span><strong>Twitter Video</strong><p class="muted">Sequence of tweet cards, narrated with captions.</p></div>
          <div class="card home-card" data-goto="voiceover"><span class="home-icon">🎙️</span><strong>AI Voiceover</strong><p class="muted">Single-voice narration with centered word-level captions.</p></div>
          <div class="card home-card" data-goto="split"><span class="home-icon">📱</span><strong>Split Video</strong><p class="muted">Brain-rot stacked layout — main clip top, gameplay bottom.</p></div>
          <div class="card home-card" data-goto="textstories"><span class="home-icon">💬</span><strong>Text Stories</strong><p class="muted">Animated iMessage-style chat bubble conversations.</p></div>
          <div class="card home-card" data-goto="captions"><span class="home-icon">📝</span><strong>AI Captions</strong><p class="muted">Upload any video, auto-transcribe, burn centered captions.</p></div>
          <div class="card home-card" data-goto="isolation"><span class="home-icon">🎧</span><strong>Voice Isolation</strong><p class="muted">Demucs-powered vocal separation from background noise.</p></div>
        </div>
      </div>`;
    main.querySelectorAll(".home-card[data-goto]").forEach(c => c.addEventListener("click", () => {
      const v = c.dataset.goto;
      document.querySelectorAll("#nav a").forEach(x => {
        x.classList.toggle("active", x.dataset.view === v);
      });
      render(v);
    }));
  },

  projects: async () => {
    const list = await api("/api/projects").catch(() => []);
    main.innerHTML = `<div class="card"><h1>My Projects</h1>
      <input id="psearch" placeholder="Search projects..." />
      <button id="newp">New Project</button>
      <div class="grid" style="margin-top:16px">${
        (list || []).map((p) => `<div class=\"card\"><span class=\"tag\">${p.type}</span>
          <h2>${p.name}</h2><p class=\"muted\">Updated ${new Date(p.updated_at).toLocaleString()}</p></div>`).join("") ||
        '<p class="muted">No projects yet.</p>'
      }</div></div>`;
    document.getElementById("newp").onclick = () => render("dialogue");
  },

  videos: async () => {
    const list = await api("/api/videos").catch(() => []);
    main.innerHTML = `<div class="card"><h1>Rendered Videos</h1>${
      (list || []).map((v) => `<div class=\"card\"><h2>render_${v.id}.mp4</h2>
        <span class=\"tag\">${v.status}</span>
        <p class=\"muted\">${new Date(v.created_at).toLocaleString()}</p>
        <a class=\"btn\" href=\"${API}/api/jobs/${v.id}/download\">Download</a></div>`).join("") ||
      '<p class="muted">No rendered videos yet.</p>'
    }</div>`;
  },

  dialogue: async () => {
    const chars = await api("/api/characters").catch(() => []);
    const bgs = await api("/api/backgrounds").catch(() => []);
    main.innerHTML = `<div class="card"><h1>Dialogue Video</h1>
      <p class="muted">Topic → script → voices → background → place characters → render.</p>
      <input id="topic" placeholder="Topic (e.g. a website that bypasses paywalls)" />
      <label class="muted">Background</label>
      <select id="bg">${(bgs||[]).map(b=>`<option value=\"${b.path}\">${b.category} / ${b.name}</option>`).join("")}</select>
      <label class="muted">Subtitle style</label>
      <select id="substyle">${["Default","TikTok","Cinema","Bold","Colorful","Cyberpunk","Soft","Cartoon","Haze"].map(s=>`<option>${s}</option>`).join("")}</select>
      <div class="canvas-wrap">
        <div class="canvas" id="canvas"></div>
        <div style="flex:1">
          <h2>Characters</h2>
          <p class="muted">Drag cutouts to place them. Speaker A = first, B = second.</p>
          <div id="charlist"></div>
          <button id="render">Render Video</button>
          <div class="steps" id="steps"></div>
        </div>
      </div></div>`;

    const canvas = document.getElementById("canvas");
    const placements = {};
    (chars || []).forEach((c, i) => {
      const tok = document.createElement("div");
      tok.className = "char-token";
      tok.style.left = (20 + i * 60) + "px"; tok.style.top = "300px"; tok.style.width = "90px";
      tok.innerHTML = c.image_path ? `<img src=\"${API}/assets/characters/${c.image_path.split(/[\\/]/).pop()}\"/>` : `<div class=\"tag\">${c.name}</div>`;
      canvas.appendChild(tok);
      placements[c.id] = { path: c.image_path, x: 20 + i * 60, y: 300, scale: 1 };
      makeDraggable(tok, canvas, (x, y) => { placements[c.id].x = x; placements[c.id].y = y; });
    });
    document.getElementById("charlist").innerHTML =
      (chars||[]).map(c=>`<div class=\"step\">${c.name} — voice ${c.voice_id||"(env)"}</div>`).join("") ||
      '<p class="muted">No characters yet. Add some on the Characters page.</p>';

    document.getElementById("render").onclick = async () => {
      const data = {
        topic: document.getElementById("topic").value,
        background_path: document.getElementById("bg").value,
        subtitle_style: document.getElementById("substyle").value,
        character_overlays: Object.values(placements),
      };
      const proj = await api("/api/projects", { method: "POST", headers: {"Content-Type":"application/json"},
        body: JSON.stringify({ name: data.topic || "Dialogue", type: "dialogue", data }) });
      const { job_id } = await api(`/api/projects/${proj.id}/render`, { method: "POST" });
      pollJob(job_id);
    };
  },

  characters: async () => {
    const chars = await api("/api/characters").catch(() => []);
    main.innerHTML = `<div class="card"><h1>Characters</h1>
      <div class="grid">${(chars||[]).map(c=>`<div class=\"card\"><h2>${c.name}</h2><p class=\"muted\">voice ${c.voice_id}</p></div>`).join("")}</div>
      <h2 style="margin-top:18px">Create Character</h2>
      <input id="cname" placeholder="Character name" />
      <input id="cvoice" placeholder="Fish Audio voice ID" />
      <input id="cimg" type="file" accept="image/*" />
      <button id="caddc">Add Character</button></div>`;
    document.getElementById("caddc").onclick = async () => {
      const fd = new FormData();
      fd.append("name", document.getElementById("cname").value);
      fd.append("voice_id", document.getElementById("cvoice").value);
      const f = document.getElementById("cimg").files[0];
      if (f) fd.append("image", f);
      await api("/api/characters", { method: "POST", body: fd });
      render("characters");
    };
  },

  voices: async () => {
    const voices = await api("/api/voices").catch(() => []);
    main.innerHTML = `<div class="card"><h1>Voices</h1>
      <div class="grid">${(voices||[]).map(v=>`<div class=\"card\"><h2>${v.name}</h2><p class=\"muted\">${v.voice_id}</p>
        <button onclick=\"tryVoice('${v.voice_id}')\">Try Out</button></div>`).join("")}</div>
      <h2 style="margin-top:18px">Add Voice</h2>
      <input id="vname" placeholder="Name" /><input id="vid" placeholder="Fish Audio voice ID" />
      <button id="vadd">Add</button></div>`;
    document.getElementById("vadd").onclick = async () => {
      await api("/api/voices", { method: "POST", headers: {"Content-Type":"application/json"},
        body: JSON.stringify({ name: document.getElementById("vname").value, voice_id: document.getElementById("vid").value }) });
      render("voices");
    };
  },

  backgrounds: async () => {
    const bgs = await api("/api/backgrounds").catch(() => []);
    const cats = ["Satisfying","Subway Surfer","Minecraft","Fortnite","Other Games","Abstract"];
    main.innerHTML = `<div class="card"><h1>Backgrounds</h1>
      <p class="muted">Upload your own .mp4 loops (Minecraft, satisfying, etc.). None are bundled.</p>
      <select id="bcat">${cats.map(c=>`<option>${c}</option>`).join("")}</select>
      <input id="bfile" type="file" accept="video/mp4" />
      <button id="bup">Upload</button>
      <div class="grid" style="margin-top:16px">${(bgs||[]).map(b=>`<div class=\"card\"><span class=\"tag\">${b.category}</span><h2>${b.name}</h2></div>`).join("")}</div></div>`;
    document.getElementById("bup").onclick = async () => {
      const fd = new FormData();
      fd.append("category", document.getElementById("bcat").value);
      fd.append("file", document.getElementById("bfile").files[0]);
      await api("/api/backgrounds", { method: "POST", body: fd });
      render("backgrounds");
    };
  },

  voiceover: async () => {
    const bgs = await api("/api/backgrounds").catch(() => []);
    main.innerHTML = `<div class="card"><h1>AI Voiceover</h1>
      <p class="muted">Write text → single AI voice narrates over a background, with centered captions.</p>
      <input id="vo_voice" placeholder="Fish Audio voice ID (blank = env default)" />
      <textarea id="vo_text" rows="6" placeholder="Narration text..."></textarea>
      ${bgSelect(bgs)} ${subSelect()}
      <button id="vo_go">Render Video</button><div class="steps" id="steps"></div></div>`;
    document.getElementById("vo_go").onclick = () => renderProject("voiceover", {
      voice_id: val("vo_voice"),
      segments: [{ text: val("vo_text") }],
      background_path: val("bg"), subtitle_style: val("substyle"),
    }, val("vo_text").slice(0, 40) || "Voiceover");
  },

  reddit: async () => {
    const bgs = await api("/api/backgrounds").catch(() => []);
    main.innerHTML = `<div class="card"><h1>Reddit Video</h1>
      <p class="muted">A Reddit-style post card is narrated over a background.</p>
      <input id="r_sub" placeholder="Subreddit (e.g. AskReddit)" />
      <input id="r_user" placeholder="Username" />
      <input id="r_title" placeholder="Post title" />
      <textarea id="r_body" rows="5" placeholder="Post body..."></textarea>
      <input id="r_voice" placeholder="Fish Audio voice ID (blank = env default)" />
      ${bgSelect(bgs)} ${subSelect()}
      <button id="r_go">Render Video</button><div class="steps" id="steps"></div></div>`;
    document.getElementById("r_go").onclick = async () => {
      const card = await api("/api/cards/reddit", post({
        subreddit: val("r_sub"), username: val("r_user"),
        title: val("r_title"), body: val("r_body"),
      }));
      const narration = `${val("r_title")}. ${val("r_body")}`;
      renderProject("reddit", {
        voice_id: val("r_voice"),
        segments: [{ text: narration, image_path: card.path }],
        background_path: val("bg"), subtitle_style: val("substyle"),
      }, val("r_title").slice(0, 40) || "Reddit");
    };
  },

  twitter: async () => {
    const bgs = await api("/api/backgrounds").catch(() => []);
    main.innerHTML = `<div class="card"><h1>Twitter Video</h1>
      <p class="muted">Add tweets; each is shown as a card and narrated in order.</p>
      <div id="tweets"></div>
      <button id="t_add">+ Add tweet</button>
      <input id="t_voice" placeholder="Fish Audio voice ID (blank = env default)" />
      ${bgSelect(bgs)} ${subSelect()}
      <button id="t_go">Render Video</button><div class="steps" id="steps"></div></div>`;
    const tweets = document.getElementById("tweets");
    const addTweet = () => {
      const row = document.createElement("div");
      row.className = "step"; row.style.display = "block"; row.style.marginBottom = "8px";
      row.innerHTML = `<input class=\"tw_name\" placeholder=\"Name\" />
        <input class=\"tw_handle\" placeholder=\"handle\" />
        <textarea class=\"tw_text\" rows=\"2\" placeholder=\"Tweet text...\"></textarea>`;
      tweets.appendChild(row);
    };
    addTweet();
    document.getElementById("t_add").onclick = addTweet;
    document.getElementById("t_go").onclick = async () => {
      const rows = [...tweets.children];
      const segments = [];
      for (const row of rows) {
        const name = row.querySelector(".tw_name").value;
        const handle = row.querySelector(".tw_handle").value;
        const text = row.querySelector(".tw_text").value;
        const card = await api("/api/cards/tweet", post({ name, handle, text }));
        segments.push({ text, image_path: card.path });
      }
      renderProject("twitter", {
        voice_id: val("t_voice"), segments,
        background_path: val("bg"), subtitle_style: val("substyle"),
      }, "Twitter");
    };
  },

  captions: async () => {
    main.innerHTML = `<div class="card"><h1>AI Captions</h1>
      <p class="muted">Upload a video → auto-transcribe → burn centered captions (scaled to 9:16).</p>
      <input id="cap_file" type="file" accept="video/*" />
      <button id="cap_up">Upload</button>
      <div id="cap_status" class="muted"></div>
      ${subSelect()}
      <button id="cap_go">Generate Captions</button><div class="steps" id="steps"></div></div>`;
    let videoPath = "";
    document.getElementById("cap_up").onclick = async () => {
      const fd = new FormData(); fd.append("file", document.getElementById("cap_file").files[0]);
      const r = await api("/api/media", { method: "POST", body: fd });
      videoPath = r.path; document.getElementById("cap_status").textContent = "Uploaded ✓";
    };
    document.getElementById("cap_go").onclick = () => {
      if (!videoPath) return alert("Upload a video first.");
      renderProject("captions", { video_path: videoPath, subtitle_style: val("substyle") }, "Captions");
    };
  },

  split: async () => {
    main.innerHTML = `<div class="card"><h1>Split Video</h1>
      <p class="muted">Brain-rot layout: main clip on top, background clip on bottom. Optional captions.</p>
      <label class="muted">Main clip (top)</label>
      <input id="sp_main" type="file" accept="video/*" /><button id="sp_main_up">Upload main</button>
      <label class="muted">Main speed</label><input id="sp_mspeed" type="number" value="1.0" step="0.25" />
      <label class="muted">Background clip (bottom)</label>
      <input id="sp_bg" type="file" accept="video/*" /><button id="sp_bg_up">Upload background</button>
      <label class="muted">BG speed</label><input id="sp_bspeed" type="number" value="1.0" step="0.25" />
      <label class="muted"><input id="sp_caps" type="checkbox" checked /> Auto captions</label>
      ${subSelect()}
      <div id="sp_status" class="muted"></div>
      <button id="sp_go">Render Video</button><div class="steps" id="steps"></div></div>`;
    let mainPath = "", bgPath = "";
    const up = async (inputId, set) => {
      const fd = new FormData(); fd.append("file", document.getElementById(inputId).files[0]);
      const r = await api("/api/media", { method: "POST", body: fd }); set(r.path);
      document.getElementById("sp_status").textContent = "Uploaded ✓";
    };
    document.getElementById("sp_main_up").onclick = () => up("sp_main", (p) => (mainPath = p));
    document.getElementById("sp_bg_up").onclick = () => up("sp_bg", (p) => (bgPath = p));
    document.getElementById("sp_go").onclick = () => {
      if (!mainPath || !bgPath) return alert("Upload both clips first.");
      renderProject("split", {
        main_path: mainPath, bg_path: bgPath,
        main_speed: parseFloat(val("sp_mspeed")) || 1.0,
        bg_speed: parseFloat(val("sp_bspeed")) || 1.0,
        captions: document.getElementById("sp_caps").checked,
        subtitle_style: val("substyle"),
      }, "Split");
    };
  },

  textstories: async () => {
    main.innerHTML = `<div class="card"><h1>Text Stories</h1>
      <p class="muted">Animated chat-bubble conversation. Sender bubbles on the right; others on the left.</p>
      <input id="ts_title" placeholder="Conversation title (header)" />
      <label class="muted">Color scheme</label>
      <select id="ts_scheme"><option value="dark">Dark</option><option value="light">Light</option></select>
      <label class="muted"><input id="ts_header" type="checkbox" checked /> Show header</label>
      <label class="muted"><input id="ts_narrate" type="checkbox" /> Narrate messages (Fish Audio)</label>
      <div id="ts_msgs"></div>
      <button id="ts_add">+ Add message</button>
      <button id="ts_go">Render Video</button><div class="steps" id="steps"></div></div>`;
    const wrap = document.getElementById("ts_msgs");
    const addMsg = () => {
      const row = document.createElement("div");
      row.className = "step"; row.style.display = "block"; row.style.marginBottom = "8px";
      row.innerHTML = `<label class=\"muted\"><input class=\"ts_sender\" type=\"checkbox\" /> Sender (right side)</label>
        <textarea class=\"ts_text\" rows=\"2\" placeholder=\"Message text...\"></textarea>
        <input class=\"ts_voice\" placeholder=\"Voice ID for narration (optional)\" />`;
      wrap.appendChild(row);
    };
    addMsg(); addMsg();
    document.getElementById("ts_add").onclick = addMsg;
    document.getElementById("ts_go").onclick = () => {
      const messages = [...wrap.children].map((row) => ({
        text: row.querySelector(".ts_text").value,
        sender: row.querySelector(".ts_sender").checked,
        voice_id: row.querySelector(".ts_voice").value || undefined,
      })).filter((m) => m.text.trim());
      if (!messages.length) return alert("Add at least one message.");
      renderProject("textstories", {
        messages,
        title: val("ts_title") || "Messages",
        scheme: val("ts_scheme"),
        show_header: document.getElementById("ts_header").checked,
        narrate: document.getElementById("ts_narrate").checked,
      }, val("ts_title") || "Text Story");
    };
  },

  isolation: async () => {
    main.innerHTML = `<div class="card"><h1>Voice Isolation</h1>
      <p class="muted">Upload audio or video → Demucs removes background music/noise → download clean vocals (.wav).</p>
      <input id="iso_file" type="file" accept="audio/*,video/*" />
      <button id="iso_up">Upload</button>
      <div id="iso_status" class="muted"></div>
      <button id="iso_go">Isolate Vocals</button><div class="steps" id="steps"></div></div>`;
    let inputPath = "";
    document.getElementById("iso_up").onclick = async () => {
      const fd = new FormData(); fd.append("file", document.getElementById("iso_file").files[0]);
      const r = await api("/api/media", { method: "POST", body: fd });
      inputPath = r.path; document.getElementById("iso_status").textContent = "Uploaded ✓";
    };
    document.getElementById("iso_go").onclick = () => {
      if (!inputPath) return alert("Upload a file first.");
      renderProject("isolation", { input_path: inputPath }, "Voice Isolation");
    };
  },

  account: async () => {
    main.innerHTML = `<div class="card"><h1>Account</h1>
      <input placeholder="Display name" />
      <input value="local@self-hosted" disabled />
      <button>Save Changes</button> <button>Sign Out</button></div>`;
  },
};

function makeDraggable(el, bounds, onMove) {
  let sx, sy, ox, oy, dragging = false;
  el.addEventListener("pointerdown", (e) => {
    dragging = true; el.setPointerCapture(e.pointerId);
    sx = e.clientX; sy = e.clientY; ox = el.offsetLeft; oy = el.offsetTop;
  });
  el.addEventListener("pointermove", (e) => {
    if (!dragging) return;
    let x = ox + (e.clientX - sx), y = oy + (e.clientY - sy);
    x = Math.max(0, Math.min(x, bounds.clientWidth - el.clientWidth));
    y = Math.max(0, Math.min(y, bounds.clientHeight - el.clientHeight));
    el.style.left = x + "px"; el.style.top = y + "px";
    // map canvas coords (270x480) to 1080x1920
    onMove(Math.round(x * 4), Math.round(y * 4));
  });
  el.addEventListener("pointerup", () => { dragging = false; });
}

async function pollJob(jobId) {
  const steps = document.getElementById("steps");
  const order = ["scripting","tts","broll","subtitles","assembling","ready"];
  const timer = setInterval(async () => {
    const j = await api(`/api/jobs/${jobId}`);
    steps.innerHTML = order.map(s => `<div class=\"step ${order.indexOf(s) <= order.indexOf(j.status) ? 'done' : ''}\">${s}</div>`).join("");
    if (j.status === "ready") {
      clearInterval(timer);
      steps.innerHTML += `<a class=\"btn\" href=\"${API}/api/jobs/${jobId}/download\">Download</a>`;
    } else if (j.status === "error") {
      clearInterval(timer);
      steps.innerHTML += `<div class=\"step\" style=\"background:rgba(255,120,120,0.3)\">error: ${j.error}</div>`;
    }
  }, 2000);
}

window.tryVoice = async (voiceId) => {
  const r = await fetch(API + "/api/voices/try", { method: "POST", headers: {"Content-Type":"application/json"},
    body: JSON.stringify({ voice_id: voiceId }) });
  const blob = await r.blob();
  new Audio(URL.createObjectURL(blob)).play();
};

render("home");
