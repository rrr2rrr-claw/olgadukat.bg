#!/usr/bin/env python3
from __future__ import annotations

import pathlib
import re
import sys

import yaml

from build_homepage import esc, image_src, text

ROOT = pathlib.Path(__file__).resolve().parents[1]


def load_yaml(path: str) -> dict:
    with (ROOT / path).open(encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def replace_main(filename: str, html_block: str) -> None:
    path = ROOT / filename
    source = path.read_text(encoding="utf-8")
    result, count = re.subn(
        r"(</nav>\n).*?(\n<footer class=\"footer\">)",
        rf"\1{html_block}\2",
        source,
        count=1,
        flags=re.S,
    )
    if count != 1:
        raise RuntimeError(f"Could not replace main content in {filename}")
    path.write_text(result, encoding="utf-8")


def paragraphs(items: list[str], *, css: str = "margin-bottom:20px;line-height:1.7;", raw: bool = False) -> str:
    lines = []
    for index, item in enumerate(items):
        style = css if index < len(items) - 1 else re.sub(r"margin-bottom:\s*\d+px;", "margin-bottom:0;", css)
        body = text(item) if raw else esc(item)
        lines.append(f'        <p style="{style}">{body}</p>')
    return "\n".join(lines)


def hero_paragraphs(items: list[str]) -> str:
    return "\n".join(f'        <p class="hero__text">{text(item)}</p>' for item in items)


def team_cards(team: dict) -> str:
    members = []
    for index, member in enumerate(team.get("members", [])):
        margin = "margin-bottom: 32px; " if index < len(team.get("members", [])) - 1 else ""
        members.append(f"""      <div class="testimonial-card" data-animate="fade-up" style="{margin}color: #151521;">
        <h3 style="font-family: 'Lora', serif; font-size: 1.2rem; margin-bottom: 12px; color: #151521;">{esc(member.get("name"))}</h3>
        <p style="color: #666; margin-bottom: 12px; font-size: 0.9rem;">{esc(member.get("role"))}</p>
        <p style="line-height: 1.7; color: #151521;">{esc(member.get("bio"))}</p>
      </div>""")
    return f"""<!-- ЕКИП -->
<section class="about" id="team" style="padding: 80px 0;">
  <div class="container">
    <div class="text-center">
      <span class="badge" data-animate="fade-up">{esc(team.get("badge"))}</span>
      <h2 class="section-title" data-animate="fade-up">{esc(team.get("title"))}</h2>
      <p class="section-subtitle" data-animate="fade-up" style="margin-bottom: 32px;">{esc(team.get("subtitle"))}</p>
      <img src="{esc(image_src(team.get("image")))}" alt="{esc(team.get("title"))}" data-animate="fade-up" style="width: 100%; max-width: 780px; border-radius: 16px; margin: 0 auto 48px; display: block;">
    </div>

    <div style="max-width: 780px; margin: 0 auto;">
{chr(10).join(members)}
    </div>
  </div>
</section>"""


def render_books_page(data: dict) -> str:
    hero = data["hero"]
    chunks = [f"""<main class="books-page books-page--sections">
  <section class="books-page__hero">
    <div class="container text-center">
      <span class="badge" data-animate="fade-up">{esc(hero.get("badge"))}</span>
      <h1 class="section-title" data-animate="fade-up">{esc(hero.get("title"))}</h1>
      <p class="page-intro" data-animate="fade-up">{esc(hero.get("intro"))}</p>
    </div>
  </section>"""]
    for index, book in enumerate(data.get("books", [])):
        dark = book.get("theme") == "dark"
        feature_class = "book-feature book-feature--dark" if dark else "book-feature book-feature--yellow"
        inside_class = "book-inside-block book-inside-block--dark" if dark else "book-inside-block book-inside-block--yellow"
        badge_class = "badge badge--light" if dark else "badge"
        btn_class = "btn btn--white" if dark else "btn btn--primary"
        grid_class = "book-feature__grid book-feature__grid--reverse" if dark else "book-feature__grid"
        content_animate = "fade-left" if dark else "fade-right"
        image_animate = "fade-right" if dark else "fade-left"
        text_bits = []
        if book.get("quote"):
            text_bits.append(f'          <blockquote>„{esc(book.get("quote"))}”</blockquote>')
        if book.get("lead"):
            text_bits.append(f'          <p class="book-feature__lead">{esc(book.get("lead"))}</p>')
        text_bits.append(f'          <p>{esc(book.get("text"))}</p>')
        content = f"""        <div class="book-feature__content" data-animate="{content_animate}">
          <span class="{badge_class}">{esc(book.get("badge"))}</span>
          <h2>{esc(book.get("title"))}</h2>
          <p class="book-feature__meta">{esc(book.get("meta"))}</p>
{chr(10).join(text_bits)}
          <div class="book-feature__price">{esc(book.get("price"))}</div>
          <a href="{esc(book.get("purchase_url"))}" class="{btn_class}" target="_blank">{esc(book.get("button"))}</a>
        </div>"""
        image = f'        <div class="book-feature__image" data-animate="{image_animate}"><img src="{esc(image_src(book.get("image")))}" alt="{esc(book.get("image_alt"))}"></div>'
        left, right = (content, image) if dark else (image, content)
        chunks.append(f"""
  <section class="{feature_class}" id="{esc(book.get("id"))}">
    <div class="container">
      <div class="{grid_class}">
{left}
{right}
      </div>
    </div>
  </section>""")
        items = "\n".join(f'        <li data-animate="fade-up"><span>✅</span> {esc(item)}</li>' for item in book.get("inside_items", []))
        chunks.append(f"""
  <section class="{inside_class}">
    <div class="container text-center">
      <span class="{badge_class}" data-animate="fade-up">СЪДЪРЖАНИЕ</span>
      <h2 class="section-title" data-animate="fade-up">{esc(book.get("inside_title"))}</h2>
      <ul class="book-inside-list{' book-inside-list--dark' if dark else ''}" data-stagger>
{items}
      </ul>
    </div>
  </section>""")
    author = data["author"]
    tags = "\n".join(f"            <span>{esc(tag)}</span>" for tag in author.get("tags", []))
    chunks.append(f"""
  <section class="books-author books-author--white" id="about">
    <div class="container">
      <div class="books-author__card" data-animate="fade-up">
        <img src="{esc(image_src(author.get("image")))}" alt="{esc(author.get("title"))}" class="books-author__photo">
        <div class="books-author__content">
          <span class="badge">{esc(author.get("badge"))}</span>
          <h2>{esc(author.get("title"))}</h2>
          <p>{esc(author.get("text"))}</p>
          <blockquote class="books-author__quote">„{esc(author.get("quote"))}”</blockquote>
          <div class="books-author__tags">
{tags}
          </div>
        </div>
      </div>
    </div>
  </section>""")
    buttons = "\n".join(
        f'        <a href="{esc(book.get("purchase_url"))}" class="btn btn--white" target="_blank">{esc(book.get("title"))} · {esc(book.get("price"))}</a>'
        for book in data.get("books", [])
    )
    cta = data["cta"]
    chunks.append(f"""
  <section class="books-buy-cta" data-animate="zoom-in">
    <div class="container text-center">
      <h2 class="section-title">{esc(cta.get("title"))}</h2>
      <p class="section-subtitle">{esc(cta.get("subtitle"))}</p>
      <div class="books-buy-cta__buttons">
{buttons}
      </div>
    </div>
  </section>
</main>""")
    return "\n".join(chunks)


def render_consultations_page(data: dict, pricing: dict) -> str:
    hero = data["hero"]
    intro = "".join(f"<p>{esc(item)}</p>" for item in hero.get("intro", []))
    package_items = "".join(f"<li>{esc(item)}</li>" for item in data["package"].get("items", []))
    services = "".join(
        f"<li><span>{esc(item.get('title'))}</span><strong>{esc(item.get('price_eur'))} €</strong></li>"
        for item in pricing["consultations"].get("services", [])
    )
    cta = data["cta"]
    return f"""<section class="book-hero"><div class="container text-center"><span class="badge" data-animate="fade-up">{esc(hero.get("badge"))}</span><h1 class="section-title" data-animate="fade-up">{esc(hero.get("title"))}</h1><div class="page-intro" style="max-width: 820px; text-align: left;" data-animate="fade-up">{intro}</div><img src="{esc(image_src(hero.get("image")))}" alt="{esc(hero.get("image_alt"))}" class="consultations-hero-photo" data-animate="fade-up"><p class="page-intro" style="margin-top:24px;" data-animate="fade-up">{esc(hero.get("package_line"))} · <strong>{esc(hero.get("package_price"))}</strong><br>{esc(hero.get("location"))}</p><a href="#" class="btn btn--primary" data-animate="fade-up" onclick="openContactModal();return false;">{esc(hero.get("button"))}</a></div></section>
<section class="section-light" style="padding:80px 0;"><div class="container"><div style="max-width:820px;margin:0 auto;">
<div class="testimonial-card" data-animate="fade-up" style="margin-bottom:32px;"><h2 class="section-title" style="font-size:1.6rem;">{esc(data["package"].get("title"))}</h2><ul style="padding-left:20px;line-height:1.8;color:var(--text);">{package_items}</ul></div>
<div class="testimonial-card" data-animate="fade-up"><h2 class="section-title" style="font-size:1.6rem;">{esc(data["services"].get("title"))}</h2><ul class="service-list">{services}</ul></div>
</div></div></section>
{team_cards(data["team"])}
<section class="final-cta" data-animate="zoom-in"><div class="container"><h2 class="section-title">{esc(cta.get("title"))}</h2><p class="section-subtitle">{esc(cta.get("subtitle"))}</p><a href="#" class="btn btn--white" onclick="openContactModal();return false;">{esc(cta.get("button"))}</a></div></section>"""


def price_rows(items: list[dict], pad: int = 12) -> str:
    rows = []
    for index, item in enumerate(items):
        border = " border-bottom: 1px solid rgba(0,0,0,0.08);" if index < len(items) - 1 else ""
        rows.append(f'<li style="display: flex; justify-content: space-between; padding: {pad}px 0;{border}"><span>{esc(item.get("title"))}</span><strong>{esc(item.get("price"))}</strong></li>')
    return "".join(rows)


def render_birth_page(data: dict) -> str:
    hero = data["hero"]
    care = data["care"]
    pricing = data["pricing"]
    conditions = data["conditions"]
    cta = data["cta"]
    include_items = "\n".join(f"          <li>{esc(item)}</li>" for item in pricing.get("includes", []))
    return f"""<section class="book-hero">
  <div class="container">
    <div class="book-hero__grid">
      <div class="book-hero__cover" style="animation: heroSlideLeft 1s cubic-bezier(0.22,1,0.36,1) 0.2s both;"><img src="{esc(image_src(hero.get("image")))}" alt="{esc(hero.get("image_alt"))}" class="book-hero__img" style="border-radius:16px;aspect-ratio:3/4;object-fit:cover;"></div>
      <div class="book-hero__content" style="animation: heroSlideRight 1s cubic-bezier(0.22,1,0.36,1) 0.4s both;">
        <span class="badge">{esc(hero.get("badge"))}</span><h1 class="section-title">{esc(hero.get("title"))}</h1>
{hero_paragraphs(hero.get("paragraphs", []))}
        <a href="#" class="btn btn--primary" onclick="openContactModal();return false;">{esc(hero.get("button"))}</a>
      </div>
    </div>
  </div>
</section>
<section class="section-light" style="padding:80px 0;">
  <div class="container">
    <div class="text-center"><span class="badge" data-animate="fade-up">{esc(care.get("badge"))}</span><h2 class="section-title" data-animate="fade-up">{esc(care.get("title"))}</h2></div>
    <div class="content-grid-right">
      <div data-animate="fade-up">
{paragraphs(care.get("paragraphs", []))}
      </div>
      <div class="content-grid-right__image" data-animate="fade-up"><img src="{esc(image_src(care.get("image")))}" alt="{esc(care.get("image_alt"))}"></div>
    </div>
  </div>
</section>
<!-- ЦЕНИ РАЖДАНЕ -->
<section class="book-teaser" id="pricing">
  <div class="container text-center">
    <span class="badge badge--light" data-animate="fade-up">{esc(pricing.get("badge"))}</span>
    <h2 class="section-title" style="color: var(--white); margin-bottom: 16px;" data-animate="fade-up">{esc(pricing.get("title"))}</h2>
    <p style="color: var(--accent-light, #C2B6C1); margin-bottom: 48px; font-style: italic;" data-animate="fade-up">{esc(pricing.get("subtitle"))}</p>

    <div style="max-width: 700px; margin: 0 auto;">
      <div class="testimonial-card" data-animate="fade-up" style="margin-bottom: 32px; color: var(--text, #151521);">
        <h3 style="font-family: 'Lora', serif; font-size: 1.3rem; margin-bottom: 20px; color: var(--text, #151521);">{esc(pricing.get("packages_title"))}</h3>
        <ul style="list-style: none; padding: 0; margin: 0;">{price_rows(pricing.get("packages", []), 12)}</ul>
      </div>

      <div class="testimonial-card" data-animate="fade-up" style="margin-bottom: 32px; color: var(--text, #151521);">
        <h3 style="font-family: 'Lora', serif; font-size: 1.1rem; margin-bottom: 16px; color: var(--text, #151521);">{esc(pricing.get("includes_title"))}</h3>
        <ul style="padding-left: 20px; line-height: 1.8; color: var(--text, #151521);">
{include_items}
        </ul>
      </div>

      <div class="testimonial-card" data-animate="fade-up" style="color: var(--text, #151521);">
        <h3 style="font-family: 'Lora', serif; font-size: 1.1rem; margin-bottom: 16px; color: var(--text, #151521);">{esc(pricing.get("extra_title"))}</h3>
        <ul style="list-style: none; padding: 0; margin: 0;">{price_rows(pricing.get("extras", []), 10)}</ul>
      </div>
    </div>
  </div>
</section>

<section class="section-light" style="padding:80px 0;">
  <div class="container">
    <div class="content-grid-right">
      <div data-animate="fade-up" class="conditions-text">
        <span class="badge">{esc(conditions.get("badge"))}</span><h2 class="section-title">{esc(conditions.get("title"))}</h2>
{paragraphs(conditions.get("paragraphs", []), css="margin-bottom:18px;line-height:1.7;", raw=True)}
      </div>
      <div class="content-grid-right__image" data-animate="fade-up"><img src="{esc(image_src(conditions.get("image")))}" alt="{esc(conditions.get("image_alt"))}"></div>
    </div>
  </div>
</section>
{team_cards(data["team"])}

<section class="final-cta" data-animate="zoom-in"><div class="container"><h2 class="section-title">{esc(cta.get("title"))}</h2><p class="section-subtitle">{esc(cta.get("subtitle"))}</p><a href="#" class="btn btn--white" onclick="openContactModal();return false;">{esc(cta.get("button"))}</a></div></section>"""


def main() -> int:
    pricing = load_yaml("data/pricing.yml")
    replace_main("knigi.html", render_books_page(load_yaml("data/books.yml")))
    replace_main("konsultatsii.html", render_consultations_page(load_yaml("data/consultations.yml"), pricing))
    replace_main("razhdane-s-nas.html", render_birth_page(load_yaml("data/birth.yml")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
