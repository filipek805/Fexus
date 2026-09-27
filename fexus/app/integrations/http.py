from http.client import InvalidURL
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def probe_url(url: str, timeout: float = 4) -> dict:
    if not url.startswith(("http://", "https://")):
        url = "http://" + url
    request = Request(url, headers={"User-Agent": "Fexus/0.3"}, method="GET")
    try:
        with urlopen(request, timeout=timeout) as response:
            body = response.read(1024).decode("utf-8", errors="replace")
            return {
                "reachable": True,
                "status": response.status,
                "url": response.geturl(),
                "content_type": response.headers.get("content-type", ""),
                "preview": body[:240].replace("\n", " ").strip(),
            }
    except HTTPError as exc:
        return {
            "reachable": True,
            "status": exc.code,
            "url": url,
            "error": str(exc),
        }
    except (URLError, OSError, ValueError, InvalidURL) as exc:
        return {"reachable": False, "url": url, "error": str(exc)}
