import { mkdirSync, writeFileSync } from "node:fs";

const html = `<!doctype html>
<html lang="zh-Hant">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta http-equiv="refresh" content="0; url=/#/admin" />
    <title>前往管理後台</title>
  </head>
  <body>
    <script>location.replace("/#/admin");</script>
    <p>正在前往管理後台...</p>
  </body>
</html>
`;

mkdirSync("dist/admin", { recursive: true });
writeFileSync("dist/admin/index.html", html, "utf8");
