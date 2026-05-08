async function loadStats(){

  const response = await fetch("/api/stats");

  const data = await response.json();

  document.getElementById("users").innerText =
  data.users;

  document.getElementById("servers").innerText =
  data.servers;
}

loadStats();
