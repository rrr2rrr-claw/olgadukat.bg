#!/usr/bin/env python3
from __future__ import annotations

import html
import pathlib
import re
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]


def load_yaml(path: str) -> dict:
    with (ROOT / path).open(encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def esc(value: object) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def text(value: object) -> str:
    return "" if value is None else str(value)


def image_src(value: object) -> str:
    value = text(value)
    return value[1:] if value.startswith("/") else value


def replace_between(source: str, start: str, end: str, replacement: str) -> str:
    pattern = rf"({re.escape(start)}\n).*?(\n{re.escape(end)})"
    result, count = re.subn(pattern, rf"\1{replacement}\2", source, count=1, flags=re.S)
    if count != 1:
        raise RuntimeError(f"Could not replace section between {start!r} and {end!r}")
    return result


def render_hero(data: dict, pricing: dict) -> str:
    hero = data["hero"]
    full_course = next((item for item in pricing["course"] if item.get("featured")), pricing["course"][0])
    return f"""<section class="hero">
  <div class="container">
    <div class="hero__grid">
      <div class="hero__content">
        <span class="hero__badge">{esc(hero.get("badge"))}</span>
        <h1>{esc(hero.get("title"))}</h1>
        <p class="hero__sub">{esc(hero.get("subtitle"))}</p>
        <p class="hero__text">{esc(hero.get("text"))}</p>
        <div class="hero__buttons">
          <a href="{esc(full_course.get("purchase_url"))}" class="btn btn--primary" target="_blank">{esc(hero.get("primary_button"))}</a>
          <a href="#program" class="btn btn--outline">{esc(hero.get("secondary_button"))}</a>
        </div>
      </div>
      <div class="hero__image">
        <div class="hero__dot hero__dot--1"></div>
        <div class="hero__dot hero__dot--2"></div>
        <div class="hero__arch">
          <img src="{esc(image_src(hero.get("image")))}" alt="Олга Дукат — акушерка" class="hero__photo">
        </div>
      </div>
    </div>
  </div>
</section>"""


ICONS = [
    '<svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a4 4 0 0 1 4 4c0 1.95-1.4 3.57-3.25 3.92"/><path d="M8.5 9.5c-.83 1.5-1.5 3.5-1.5 5.5 0 4 2.5 7 5 7s5-3 5-7c0-1.5-.37-2.84-.87-4"/><circle cx="12" cy="14" r="1.5"/></svg>',
    '<svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10z"/><path d="M8 15s1.5 2 4 2 4-2 4-2"/><line x1="9" y1="9" x2="9.01" y2="9"/><line x1="15" y1="9" x2="15.01" y2="9"/></svg>',
    '<svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22c-4-2.5-8-6-8-11a8 8 0 0 1 16 0c0 5-4 8.5-8 11z"/><path d="M12 8v4"/><path d="M10 12h4"/></svg>',
    '<svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
    '<svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21.5 2v6h-6"/><path d="M2.5 22v-6h6"/><path d="M2.5 16A10 10 0 0 1 7 4.5"/><path d="M21.5 8a10 10 0 0 1-4.5 11.5"/></svg>',
    '<svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg>',
]


def render_for_whom(data: dict) -> str:
    title = data["for_whom_title"]
    cards = []
    for index, item in enumerate(data["for_whom"]):
        cards.append(f"""      <div class="for-whom__card" data-animate="fade-up">
        <div class="for-whom__card-icon">
          {ICONS[index] if index < len(ICONS) else ICONS[-1]}
        </div>
        <h3>{esc(item.get("title"))}</h3>
        <p>{esc(item.get("text"))}</p>
      </div>""")
    return f"""<section class="for-whom" id="for-whom">
  <div class="container text-center">
    <span class="badge" data-animate="fade-up">{esc(title.get("badge"))}</span>
    <h2 class="section-title" data-animate="fade-up">{esc(title.get("title"))}</h2>
    <div class="for-whom__cards" data-stagger>
{chr(10).join(cards)}
    </div>
  </div>
</section>"""


def render_about(data: dict) -> str:
    about = data["about"]
    quals = "\n".join(
        f'          <span class="about__qual">{esc(item)}</span>' for item in about.get("qualifications", [])
    )
    return f"""<section class="about" id="about">
  <div class="container">
    <div class="about__grid">
      <div class="about__image" data-animate="fade-left">
        <img src="{esc(image_src(about.get("image")))}" alt="Олга Дукат" class="about__photo">
      </div>
      <div class="about__content" data-animate="fade-right">
        <span class="badge badge--light">{esc(about.get("badge"))}</span>
        <h2 class="section-title">{esc(about.get("title"))}</h2>
        <p class="about__text"><strong>{esc(about.get("name"))}</strong> {esc(about.get("text"))}</p>
        <div class="about__quals">
{quals}
        </div>
        <a href="#program" class="btn btn--white">{esc(about.get("button"))}</a>
      </div>
    </div>
  </div>
</section>"""


def render_program(data: dict) -> str:
    program = data["program"]
    modules = []
    for module in program.get("modules", []):
        episodes = "\n".join(f"            <li>{esc(item)}</li>" for item in module.get("episodes", []))
        modules.append(f"""      <div class="program__module" data-animate="fade-up">
        <button class="program__module-header">
          <div class="program__module-info">
            <span class="program__module-num">{esc(module.get("number"))}</span>
            <h3>{esc(module.get("title"))}</h3>
            <span class="program__module-count">{esc(module.get("count"))}</span>
          </div>
          <span class="program__module-toggle">+</span>
        </button>
        <div class="program__module-body">
          <ol class="program__episodes">
{episodes}
          </ol>
        </div>
      </div>""")
    bonuses = "\n".join(f"        <span>{esc(item)}</span>" for item in program.get("bonus_items", []))
    return f"""<section class="program" id="program">
  <div class="container text-center">
    <span class="badge" data-animate="fade-up">{esc(program.get("badge"))}</span>
    <h2 class="section-title" data-animate="fade-up">{esc(program.get("title"))}</h2>
    <p class="section-subtitle" data-animate="fade-up">{esc(program.get("subtitle"))}</p>
    <p class="section-desc" data-animate="fade-up">{esc(program.get("description"))}</p>

    <div class="program__modules" data-stagger>
{chr(10).join(modules)}
    </div>

    <div class="program__bonus">
      <h4>{esc(program.get("bonus_title"))}</h4>
      <div class="program__bonus-items">
{bonuses}
      </div>
    </div>
  </div>
</section>"""


def render_quote(data: dict) -> str:
    quote = data["quote"]
    return f"""<section class="quote-section" data-animate="fade-in">
  <div class="container">
    <blockquote>„{esc(quote.get("text"))}”</blockquote>
    <p class="quote-author">— {esc(quote.get("author"))}</p>
  </div>
</section>"""


def render_pricing(homepage: dict, pricing: dict) -> str:
    section = homepage["pricing"]
    cards = []
    for item in pricing.get("course", []):
        featured = bool(item.get("featured"))
        card_class = "pricing__card pricing__card--featured" if featured else "pricing__card"
        animate = "scale-in" if featured else "fade-up"
        label = f'        <span class="pricing__card-label">{esc(item.get("label"))}</span>\n' if item.get("label") else ""
        btn_class = "btn btn--white" if featured else "btn btn--outline"
        features = "\n".join(f"          <li>{esc(feature)}</li>" for feature in item.get("features", []))
        cards.append(f"""      <div class="{card_class}" data-animate="{animate}">
{label}        <h3 class="pricing__card-title">{esc(item.get("title"))}</h3>
        <div class="pricing__card-price">{esc(item.get("price_eur"))} € / {esc(item.get("price_bgn"))} лв</div>
        <div class="pricing__card-note">{esc(item.get("note"))}</div>
        <ul class="pricing__card-features">
{features}
        </ul>
        <a href="{esc(item.get("purchase_url"))}" class="{btn_class}" target="_blank">{esc(item.get("button"))}</a>
      </div>""")
    return f"""<section class="pricing" id="pricing">
  <div class="container text-center">
    <span class="badge" data-animate="fade-up">{esc(section.get("badge"))}</span>
    <h2 class="section-title" data-animate="fade-up">{esc(section.get("title"))}</h2>
    <div class="pricing__cards">
{chr(10).join(cards)}
    </div>
    <div class="pricing__special">
      <p>{text(section.get("special"))}</p>
    </div>
  </div>
</section>"""


def render_books(data: dict) -> str:
    section = data["book_teaser"]
    cards = []
    for index, item in enumerate(section.get("books", [])):
        subtitle = ""
        if item.get("subtitle"):
            subtitle = f'        <p class="book-teaser__subtitle" style="font-style: italic; color: var(--accent-light, #C2B6C1); margin-bottom: 12px;">{esc(item.get("subtitle"))}</p>\n'
        margin = ' style="margin-top: 48px;"' if index else ""
        cards.append(f"""    <div class="book-teaser__grid"{margin}>
      <div class="book-teaser__cover" data-animate="fade-left">
        <a href="{esc(item.get("detail_url"))}"><img src="{esc(image_src(item.get("image")))}" alt="{esc(item.get("title"))}" class="book-teaser__img"></a>
      </div>
      <div class="book-teaser__content" data-animate="fade-right">
        <a href="{esc(item.get("detail_url"))}" style="text-decoration: none; color: inherit;"><h3 class="section-title" style="font-size: 1.8rem;">{esc(item.get("title"))}</h3></a>
{subtitle}        <p class="book-teaser__text">{esc(item.get("text"))}</p>
        <p class="book-teaser__price">{esc(item.get("price"))}</p>
        <a href="{esc(item.get("purchase_url"))}" class="btn btn--primary" target="_blank">{esc(item.get("buy_button"))}</a>
        <a href="{esc(item.get("detail_url"))}" class="btn btn--white" style="margin-left: 12px;">{esc(item.get("detail_button"))}</a>
      </div>
    </div>""")
    return f"""<section class="book-teaser" id="book">
  <div class="container">
    <span class="badge badge--light">{esc(section.get("badge"))}</span>
    <h2 class="section-title" style="color: var(--white); margin-bottom: 48px;">{esc(section.get("title"))}</h2>
{chr(10).join(cards)}
  </div>
</section>"""


def render_testimonials(data: dict) -> str:
    title = data["testimonials_title"]
    cards = []
    for item in data.get("testimonials", []):
        cards.append(f"""      <div class="testimonial-card" data-animate="fade-up">
        <div class="testimonial-card__stars">{esc(item.get("stars", "★★★★★"))}</div>
        <p class="testimonial-card__text">„{esc(item.get("text"))}”</p>
        <p class="testimonial-card__author">— {esc(item.get("name"))}</p>
      </div>""")
    return f"""<section class="testimonials" id="testimonials">
  <div class="container">
    <div class="text-center">
      <span class="badge" data-animate="fade-up">{esc(title.get("badge"))}</span>
      <h2 class="section-title" data-animate="fade-up">{esc(title.get("title"))}</h2>
    </div>
    <div class="testimonials__stack">
{chr(10).join(cards)}
    </div>
  </div>
</section>"""


def render_faq(data: dict) -> str:
    title = data["faq_title"]
    items = []
    for item in data.get("faq", []):
        items.append(f"""      <div class="faq__item" data-animate="fade-up">
        <button class="faq__question">{esc(item.get("question"))}</button>
        <div class="faq__answer"><p>{esc(item.get("answer"))}</p></div>
      </div>""")
    return f"""<section class="faq" id="faq">
  <div class="container text-center">
    <span class="badge" data-animate="fade-up">{esc(title.get("badge"))}</span>
    <h2 class="section-title" data-animate="fade-up">{esc(title.get("title"))}</h2>
  </div>
  <div class="container">
    <div class="faq__list">
{chr(10).join(items)}
    </div>
  </div>
</section>"""


def render_final_cta(data: dict, pricing: dict) -> str:
    cta = data["final_cta"]
    full_course = next((item for item in pricing["course"] if item.get("featured")), pricing["course"][0])
    return f"""<section class="final-cta" data-animate="zoom-in">
  <div class="container">
    <h2 class="section-title">{esc(cta.get("title"))}</h2>
    <p class="section-subtitle">{esc(cta.get("subtitle"))}</p>
    <a href="{esc(full_course.get("purchase_url"))}" class="btn btn--white" target="_blank">{esc(cta.get("button"))}</a>
  </div>
</section>"""


def main() -> int:
    homepage = load_yaml("data/homepage.yml")
    pricing = load_yaml("data/pricing.yml")
    path = ROOT / "index.html"
    source = path.read_text(encoding="utf-8")

    replacements = [
        ("<!-- HERO -->", "<!-- FOR WHOM -->", render_hero(homepage, pricing)),
        ("<!-- FOR WHOM -->", "<!-- ABOUT -->", render_for_whom(homepage)),
        ("<!-- ABOUT -->", "<!-- PROGRAM -->", render_about(homepage)),
        ("<!-- PROGRAM -->", "<!-- QUOTE -->", render_program(homepage)),
        ("<!-- QUOTE -->", "<!-- PRICING -->", render_quote(homepage)),
        ("<!-- PRICING -->", "<!-- BOOK TEASER -->", render_pricing(homepage, pricing)),
        ("<!-- BOOK TEASER -->", "<!-- TESTIMONIALS -->", render_books(homepage)),
        ("<!-- TESTIMONIALS -->", "<!-- FAQ -->", render_testimonials(homepage)),
        ("<!-- FAQ -->", "<!-- FINAL CTA -->", render_faq(homepage)),
        ("<!-- FINAL CTA -->", "<!-- FOOTER -->", render_final_cta(homepage, pricing)),
    ]
    for start, end, html_block in replacements:
        source = replace_between(source, start, end, html_block)

    path.write_text(source, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
