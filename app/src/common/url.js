export function opParseUrl(url) {
  const res = {};
  const attrs = ["protocol", "hostname", "port", "pathname", "search", "hash", "host"];
  const a = document.createElement("a");
  a.href = url;

  for (let i = 0; i < attrs.length; ++i) {
    const attr = attrs[i];
    res[attr] = a[attr];
  }
  return res;
}
