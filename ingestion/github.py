"""Crawl léger de la doc Nuxt 3 et Symfony 7 (cache disque, fallback offline)."""

import hashlib
import logging
import time
from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from config import DATA_DIR

logger = logging.getLogger(__name__)

RAW_HTML_DIR = DATA_DIR / "raw_html"
USER_AGENT = "bb-assistant-technique-poc/0.1 (+contact charles@agence-bb.ch)"
CRAWL_DELAY_SECONDS = 0.5
REQUEST_TIMEOUT_SECONDS = 15

NUXT_URLS: list[str] = [
    "https://nuxt.com/docs/getting-started/introduction",
    "https://nuxt.com/docs/getting-started/installation",
    "https://nuxt.com/docs/getting-started/configuration",
    "https://nuxt.com/docs/getting-started/views",
    "https://nuxt.com/docs/getting-started/routing",
    "https://nuxt.com/docs/getting-started/data-fetching",
    "https://nuxt.com/docs/getting-started/deployment",
    "https://nuxt.com/docs/guide/concepts/auto-imports",
    "https://nuxt.com/docs/guide/concepts/rendering",
    "https://nuxt.com/docs/guide/concepts/server-engine",
    "https://nuxt.com/docs/guide/directory-structure/app",
    "https://nuxt.com/docs/guide/directory-structure/components",
    "https://nuxt.com/docs/guide/directory-structure/composables",
    "https://nuxt.com/docs/guide/directory-structure/pages",
    "https://nuxt.com/docs/guide/directory-structure/plugins",
    "https://nuxt.com/docs/guide/directory-structure/server",
    "https://nuxt.com/docs/guide/going-further/nitro",
]

SYMFONY_URLS: list[str] = [
    "https://symfony.com/doc/current/setup.html",
    "https://symfony.com/doc/current/configuration.html",
    "https://symfony.com/doc/current/routing.html",
    "https://symfony.com/doc/current/controller.html",
    "https://symfony.com/doc/current/best_practices.html",
    "https://symfony.com/doc/current/templates.html",
    "https://symfony.com/doc/current/forms.html",
    "https://symfony.com/doc/current/doctrine.html",
    "https://symfony.com/doc/current/security.html",
    "https://symfony.com/doc/current/service_container.html",
    "https://symfony.com/doc/current/deployment.html",
    "https://symfony.com/doc/current/cache.html",
    "https://symfony.com/doc/current/testing.html",
]


def _chemin_cache(url: str) -> Path:
    """Chemin local stable pour l'HTML d'une URL donnée."""
    parsed = urlparse(url)
    slug = parsed.path.strip("/").replace("/", "_") or "index"
    digest = hashlib.md5(url.encode()).hexdigest()[:6]
    return RAW_HTML_DIR / parsed.netloc / f"{slug}__{digest}.html"


def _telecharger(url: str) -> str | None:
    """Télécharge l'URL, met en cache, retourne le HTML ou None si échec."""
    cache = _chemin_cache(url)
    if cache.exists():
        return cache.read_text(encoding="utf-8")

    cache.parent.mkdir(parents=True, exist_ok=True)
    try:
        response = requests.get(
            url,
            headers={"User-Agent": USER_AGENT},
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        logger.warning("crawl échoué pour %s : %s", url, exc)
        return None

    html = response.text
    cache.write_text(html, encoding="utf-8")
    time.sleep(CRAWL_DELAY_SECONDS)
    return html


def _extraire_texte(html: str) -> tuple[str, str]:
    """Retourne (titre, texte nettoyé) à partir du HTML brut."""
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form"]):
        tag.decompose()

    titre = soup.title.string.strip() if soup.title and soup.title.string else ""

    main = soup.find("main") or soup.find("article") or soup.body or soup
    lignes: list[str] = []
    for elem in main.descendants:
        if elem.name in ("h1", "h2", "h3"):
            niveau = int(elem.name[1])
            texte = elem.get_text(" ", strip=True)
            if texte:
                lignes.append(f"\n{'#' * niveau} {texte}\n")
        elif elem.name in ("p", "li", "pre", "code"):
            texte = elem.get_text(" ", strip=True)
            if texte:
                lignes.append(texte)

    texte = "\n\n".join(lignes)
    return titre, texte


def crawler_urls(urls: list[str], source_type: str) -> list[dict]:
    """Crawle la liste d'URLs, retourne les documents chargeables par le chunker."""
    documents: list[dict] = []
    for url in urls:
        html = _telecharger(url)
        if html is None:
            continue
        titre, texte = _extraire_texte(html)
        if not texte.strip():
            continue
        contenu = f"# {titre}\n\n{texte}" if titre else texte
        documents.append(
            {
                "content": contenu,
                "metadata": {
                    "source_type": source_type,
                    "source_path": urlparse(url).path,
                    "section": titre,
                    "url": url,
                },
            }
        )
    return documents


def crawler_nuxt() -> list[dict]:
    """Crawle la doc Nuxt 3 ciblée."""
    return crawler_urls(NUXT_URLS, source_type="nuxt_official")


def crawler_symfony() -> list[dict]:
    """Crawle la doc Symfony 7 ciblée."""
    return crawler_urls(SYMFONY_URLS, source_type="symfony_official")
