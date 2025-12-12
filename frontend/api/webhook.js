export default async function handler(req, res) {
  await fetch("http://127.0.0.1:8000:5000/agent/kestra", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action: req.body.event }),
  });

  res.json({ ok: true });
}
