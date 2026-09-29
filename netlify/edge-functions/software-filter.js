// Serves /software/TitleName1,TitleName2 by filtering the static /software.json.
export default async (request) => {
  const url = new URL(request.url);
  const titles = decodeURIComponent(url.pathname.replace(/^\/software\//, ""))
    .split(",")
    .filter(Boolean);

  const json = (body, status) =>
    new Response(JSON.stringify(body), {
      status,
      headers: { "Content-Type": "application/json" },
    });

  if (titles.length === 0) {
    return json({ error: `Bad Request: ${url.pathname}` }, 400);
  }

  const resp = await fetch(new URL("/software.json", url));
  if (!resp.ok) {
    return json({ error: "Internal Server Error: Unable to load titles" }, 500);
  }

  const software = await resp.json();
  const missing = titles.find((t) => !software.some((s) => s.id === t));
  if (missing) {
    return json({ error: `Title Not Found: ${missing}` }, 404);
  }

  return json(software.filter((s) => titles.includes(s.id)), 200);
};

export const config = { path: "/software/*" };
