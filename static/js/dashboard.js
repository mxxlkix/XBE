async function loadStats() {
  const res = await fetch("/api/live-stats");
  const data = await res.json();

  document.getElementById("liveUsers").innerText = data.users;
}

loadStats();
