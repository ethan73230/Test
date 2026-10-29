#!/usr/bin/env python3
"""Génère le site statique du Ski Club Saint Alban Leysse.

Usage : python3 build.py   (depuis le dossier st-alban-ski)
Les articles sont dans data/posts.json ; modifiez-les puis relancez le script.
"""
import json, os, html
from datetime import date

ROOT = os.path.dirname(os.path.abspath(__file__))
U = "https://st-alban-ski.fr/wp-content/uploads/"
LOGO = U + "2015/10/logo-big-fondtransp.png"
FAVICON = U + "2015/10/cropped-picto-fondtransp-270x270.png"
FB = "https://www.facebook.com/skiclubSaintAlbanLeysse"
YT = "https://www.youtube.com/@skiclubsaint-alban-leysse926/playlists"
OLD_ARCHIVES = "https://st-alban-ski.fr/category/archives/page/2"

MOIS = ["janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.", "août", "sept.", "oct.", "nov.", "déc."]
MOIS_LONG = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]

# Chaque rubrique a sa couleur de piste, utilisée partout sur le site.
NAV = [
    ("index.html", "Accueil", "black", None),
    ("bourse-aux-skis-2026.html", "Bourse aux skis 2026", "red", None),
    ("les-sorties.html", "Les sorties", "blue", None),
    ("actualites.html", "Actualités", "green", None),
    ("membres.html", "Membres", "black", None),
    ("partenaires.html", "Partenaires", "orange", None),
    ("contact.html", "Contact", "orange", None),
]

SITE_URL = "https://ethan73230.github.io/Test/st-alban-ski/"
DEFAULT_IMG = U + "2026/04/154577-montagne_enneigee-neige-montagne_de_poudre-mont_blanc-ski-3840x2160-1-scaled.jpg"

def e(s): return html.escape(s, quote=True)

def thumb(src, w):
    """Photo redimensionnée et compressée (WebP) par le service d'images wsrv.nl.
    Si le service ne répond pas, site.js recharge la photo d'origine (data-orig)."""
    if not src.startswith("https://st-alban-ski.fr/"):
        return src
    return "https://wsrv.nl/?url=%s&w=%d&output=webp&q=78" % (src.replace("https://", ""), w)

def img(src, w, alt="", cls="", lazy=True, sizes=None, extra=""):
    srcset = ""
    if sizes:
        srcset = ' srcset="%s %dw, %s %dw" sizes="%s"' % (e(thumb(src, w)), w, e(thumb(src, w * 2)), w * 2, sizes)
    return '<img%s src="%s"%s alt="%s" data-orig="%s"%s decoding="async"%s>' % (
        ' class="%s"' % cls if cls else "", e(thumb(src, w)), srcset, e(alt), e(src),
        ' loading="lazy"' if lazy else ' fetchpriority="high"', extra)

def ICON(name):
    paths = {
        "fb": '<path fill="currentColor" d="M14 8h3V4h-3c-2.8 0-4 1.8-4 4.5V11H7v4h3v9h4v-9h3l1-4h-4V8.6c0-.4.3-.6.6-.6z"/>',
        "yt": '<path fill="currentColor" d="M23 7.2a3 3 0 0 0-2.1-2.1C19 4.6 12 4.6 12 4.6s-7 0-8.9.5A3 3 0 0 0 1 7.2 31 31 0 0 0 .5 12a31 31 0 0 0 .5 4.8 3 3 0 0 0 2.1 2.1c1.9.5 8.9.5 8.9.5s7 0 8.9-.5a3 3 0 0 0 2.1-2.1 31 31 0 0 0 .5-4.8 31 31 0 0 0-.5-4.8zM9.75 15.02V8.98L15.5 12z"/>',
        "doc": '<path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8zM14 2v6h6M9 15h6M9 18h6"/>',
        "cal": '<path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M3 6a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2zM16 2v4M8 2v4M3 10h18M12 14v4M10 16h4"/>',
        "print": '<path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M6 9V2h12v7M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2M6 14h12v8H6z"/>',
        "pin": '<path fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0z"/><circle cx="12" cy="10" r="3" fill="none" stroke="currentColor" stroke-width="2"/>',
    }
    return '<svg viewBox="0 0 24 24" aria-hidden="true">%s</svg>' % paths[name]

def dot(color):
    return '<span class="dot%s" aria-hidden="true"></span>' % (" black" if color == "black" else "")

def page(path, title, body, color="blue", desc="", current=None, prefix="", image=None):
    """prefix = '../' pour les pages dans un sous-dossier."""
    og_img = image or DEFAULT_IMG
    items = []
    for href, label, c, _ in NAV:
        cur = ' aria-current="page"' if href == current else ""
        items.append('<li><a class="c-%s" href="%s%s"%s>%s<span>%s</span></a></li>' % (c, prefix, href, cur, dot(c), label))
    items.append('<li><a href="%s" aria-label="Facebook du club">%s</a></li>' % (FB, ICON("fb").replace("<svg", '<svg style="width:20px;height:20px"')))
    doc = f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)} – Saint Alban ski club</title>
<meta name="description" content="{e(desc)}">
<meta name="color-scheme" content="light dark">
<meta name="theme-color" content="#FFFFFF" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#121A21" media="(prefers-color-scheme: dark)">
<meta property="og:type" content="website">
<meta property="og:locale" content="fr_FR">
<meta property="og:site_name" content="Saint Alban ski club">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{SITE_URL}{path}">
<meta property="og:image" content="{e(og_img)}">
<meta name="twitter:card" content="summary_large_image">
<link rel="canonical" href="{SITE_URL}{path}">
<link rel="icon" href="{FAVICON}">
<link rel="preconnect" href="https://wsrv.nl">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Barlow:wght@400;500;600;700&family=Barlow+Semi+Condensed:wght@600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{prefix}assets/style.css">
</head>
<body class="p-{color}">
<a class="skip" href="#contenu">Aller au contenu</a>
<header class="top">
  <div class="wrap">
    <a class="brand" href="{prefix}index.html"><img src="{LOGO}" alt="" width="46" height="46">Saint Alban ski club</a>
    <button class="burger" aria-expanded="false" aria-controls="nav" aria-label="Ouvrir le menu"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 6h18M3 12h18M3 18h18" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/></svg></button>
    <nav class="nav" id="nav" aria-label="Navigation principale"><ul class="menu">{''.join(items)}</ul></nav>
  </div>
</header>
<aside class="nextup" id="next" data-prefix="{prefix}" aria-label="Prochain rendez-vous" hidden></aside>
<main id="contenu">
{body}
</main>
<footer class="foot">
  <div class="wrap">
    <div>
      <h2>Ski Club Saint Alban Leysse</h2>
      <p>Association loi 1901 pour les enfants de 5 à 18 ans, animée par des bénévoles.</p>
    </div>
    <div>
      <h2>Le club</h2>
      <ul>
        <li><a href="{prefix}les-sorties.html">Les sorties</a></li>
        <li><a href="{prefix}archives.html">Archives</a></li>
        <li><a href="{prefix}partenaires.html">Partenaires</a></li>
        <li><a href="{prefix}contact.html">Contact</a></li>
      </ul>
    </div>
    <div>
      <h2>Nous suivre</h2>
      <ul>
        <li><a href="{FB}">{ICON("fb")}Facebook</a></li>
        <li><a href="{YT}">{ICON("yt")}YouTube</a></li>
      </ul>
    </div>
    <p class="copy">Copyright {date.today().year} – Ski club Saint Alban Leysse</p>
  </div>
</footer>
<script src="{prefix}assets/site.js"></script>
</body>
</html>
"""
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(doc)

def d(s): return date.fromisoformat(s)
def fr_date(s):
    x = d(s); return "%d %s %d" % (x.day, MOIS_LONG[x.month - 1], x.year)
def season(s):
    x = d(s); y = x.year + 1 if x.month >= 8 else x.year
    return "Saison %d" % y

posts = json.load(open(os.path.join(ROOT, "data", "posts.json"), encoding="utf-8"))
posts.sort(key=lambda p: p["date"], reverse=True)
BY_SLUG = {p["slug"]: p for p in posts}

def row(p, prefix=""):
    x = d(p["date"])
    n = len(p["images"])
    sub = "%d photos" % n if n > 1 else (p["text"][0] if p["text"] else "")
    pics = []
    for src in ([p["cover"]] if p["cover"] else []) + p["images"]:
        if src not in pics: pics.append(src)
    if len(pics) >= 4:
        th = '<span class="sheet">%s</span>' % "".join(img(s, 220) for s in pics[:4])
    elif pics:
        th = img(pics[0], 400, cls="thumb")
    else:
        th = '<span class="thumb empty"></span>'
    return f"""<li class="row"><a href="{prefix}articles/{p['slug']}.html">
<time datetime="{p['date']}"><b>{x.day}</b><span>{MOIS[x.month-1]} {x.year}</span></time>
<div><h3>{e(p['title'])}</h3><p>{e(sub)}</p></div>{th}</a></li>"""

def rows_by_season(lst, prefix=""):
    out, cur = [], None
    for p in lst:
        s = season(p["date"])
        if s != cur:
            if cur: out.append("</ul>")
            out.append('<h2 class="season-title">%s</h2><ul class="rows">' % s)
            cur = s
        out.append(row(p, prefix))
    if cur: out.append("</ul>")
    return "\n".join(out)

# ---------------------------------------------------------------- Accueil
actus = [p for p in posts if p["cat"] == "actus"]
SORTIES_2026 = sorted([p for p in actus if p["slug"].startswith("sortie-") and p["slug"].endswith("2026")
                       and not p["slug"].startswith("sortie-00")], key=lambda p: p["slug"][7:9])

# Sorties 2027 : (date ISO, libellé court, station, note)
SORTIES_2027 = [
    ("2027-01-09", "9 janv.", "Saint-François-Longchamp", ""),
    ("2027-01-16", "16 janv.", "Saint-François-Longchamp", ""),
    ("2027-01-23", "23 janv.", "Saint-François-Longchamp", ""),
    ("2027-01-30", "30 janv.", "Saint-François-Longchamp", ""),
    ("2027-02-06", "6 févr.", "Saint-François-Longchamp", ""),
    ("2027-02-27", "27 févr.", "Les Karellis", ""),
    ("2027-03-06", "6 mars", "Les Karellis", ""),
    ("2027-03-13", "13 mars", "Les Karellis", ""),
    ("2027-03-20", "20 mars", "Les Karellis", "tests"),
    ("2027-03-27", "27 mars", "Les Karellis", ""),
]

def board(title_id, title, prefix=""):
    out = ['<section class="board" aria-labelledby="%s"><div class="wrap">' % title_id,
           '<h2 id="%s">%s</h2>' % (title_id, title)]
    for st in ("Saint-François-Longchamp", "Les Karellis"):
        lis = "".join('<li%s><time datetime="%s">%s</time>%s</li>' % (
            ' class="special"' if note else "", iso, lab, " : " + note if note else "")
            for iso, lab, s, note in SORTIES_2027 if s == st)
        out.append('<div class="station"><h3><span class="dot ice" aria-hidden="true"></span>%s</h3><ul class="dates">%s</ul></div>' % (st, lis))
    out.append('<p class="board-actions"><a class="btn inv" href="%scalendrier-sorties-2027.ics" download>%sAjouter les 10 sorties à mon agenda</a>' % (prefix, ICON("cal")))
    out.append('<a class="btn inv" href="%sles-sorties.html">Horaires, matériel et consignes</a></p>' % prefix if title_id != "h-cal" else "</p>")
    out.append("</div></section>")
    return "\n".join(out)

wall = "".join(
    '<a href="articles/%s.html">%s<span>%s</span></a>' % (s["slug"], img(s["cover"], 420, alt=s["title"], sizes="(max-width: 700px) 50vw, 20vw"), "Sortie #%s" % s["slug"][7:9])
    for s in SORTIES_2026)

home = f"""
<section class="hero" aria-labelledby="h1" style="padding:0">
  {img(DEFAULT_IMG, 1600, lazy=False, sizes="100vw")}
  <div class="wrap">
    <div>
      <h1 id="h1">Ski Club Saint Alban Leysse</h1>
      <p class="season">Saison 2027</p>
    </div>
    <nav class="post" aria-label="Accès rapides">
      <a class="sign r" href="bourse-aux-skis-2026.html">Bourse aux skis<small>30, 31 oct. et 1er nov. 2026</small></a>
      <a class="sign b" href="les-sorties.html">Les sorties 2027<small>Le samedi, de janvier à mars</small></a>
      <a class="sign g" href="actualites.html">Actualités<small>Photos de chaque sortie</small></a>
      <a class="sign k" href="membres.html">L'encadrement</a>
    </nav>
  </div>
</section>

<section class="bg-paper">
  <div class="wrap split">
    <div class="narrow">
      <h2>Le ski pour les enfants de 5 à 18 ans</h2>
      <p class="lead">Le Ski Club est une association loi 1901. Il fait découvrir et progresser les enfants dans le ski sous toutes ses formes, dans un esprit convivial et à un prix modéré.</p>
      <p>Toute l'organisation, des sorties à leur déroulement, repose sur des bénévoles. Le club fait aussi appel à des moniteurs de l'ESF pour que les enfants acquièrent des bases solides.</p>
      <p>Les sorties ont lieu le samedi, de 11h00 à 18h45, de janvier à mars, à Saint-François-Longchamp et aux Karellis. Les groupes sont encadrés soit par des moniteurs ESF, soit par des bénévoles accompagnés de serre-files. En fin de saison, les enfants peuvent passer les tests ESF.</p>
      <div class="doclinks">
        <a class="btn" href="{U}2025/08/statuts-2021.pdf">{ICON("doc")}Statuts (PDF)</a>
        <a class="btn" href="{U}2025/08/reglement-interieur-2021.pdf">{ICON("doc")}Règlement intérieur (PDF)</a>
      </div>
    </div>
    <figure>
      {img(U + "2026/03/IMG_20260307_153602-scaled.jpg", 700, alt="Enfants du club sur les pistes", sizes="(max-width: 860px) 100vw, 45vw")}
      <figcaption>Sortie du 7 mars 2026</figcaption>
    </figure>
  </div>
</section>

{board("h-sorties", "Les sorties 2027")}

<section aria-labelledby="h-actus" style="--page:var(--green)">
  <div class="wrap">
    <h2 id="h-actus">Dernières nouvelles</h2>
    <ul class="rows" style="border-top:2px solid var(--slate)">{''.join(row(p) for p in actus[:4])}</ul>
    <p style="margin-top:24px"><a class="btn" href="actualites.html">Toutes les actualités</a></p>
  </div>
</section>

<section class="bg-paper" aria-labelledby="h-wall">
  <div class="wrap">
    <h2 id="h-wall">La saison 2026 en photos</h2>
    <p class="lead">Une sortie par photo : touchez-en une pour voir toute la galerie.</p>
    <div class="wall">{wall}</div>
  </div>
</section>
"""
page("index.html", "Accueil", home, "black", "Ski Club de Saint-Alban-Leysse : sorties ski le samedi pour les enfants de 5 à 18 ans.", "index.html")

# ---------------------------------------------------------------- Bourse
B = U + "2026/10/"
bourse = f"""
<section class="bhero" style="padding:48px 0 0">
  <div class="wrap">
    <div>
      <h1>Bourse aux skis 2026</h1>
      <p class="when">30, 31 octobre et 1er novembre</p>
      <p class="where"><a href="https://www.google.com/maps/search/?api=1&amp;query=Gymnase+Vivet+impasse+du+Repos+Saint-Alban-Leysse">Gymnase Vivet, impasse du Repos, Saint-Alban-Leysse</a></p>
      <p class="status"><span class="dot" aria-hidden="true"></span><span id="bourse-status" aria-live="polite">Dépôt ouvert vendredi à 9h00</span></p>
      <p class="bactions"><a class="btn inv" href="bourse-aux-skis-2026.ics" download>{ICON("cal")}Ajouter à mon agenda</a><a class="btn inv" href="https://www.google.com/maps/dir/?api=1&amp;destination=Gymnase+Vivet+impasse+du+Repos+Saint-Alban-Leysse">{ICON("pin")}Itinéraire</a></p>
    </div>
    <figure class="gallery solo"><a href="{B}Capture-decran-2026-10-07-164002.png" data-big="{thumb(B+'Capture-decran-2026-10-07-164002.png',1600)}">{img(B+"Capture-decran-2026-10-07-164002.png", 760, alt="Affiche de la bourse aux skis 2026", lazy=False)}</a></figure>
  </div>
</section>

<section class="bg-paper" aria-labelledby="h-prog" style="padding-top:72px">
  <div class="wrap">
    <h2 id="h-prog">Programme</h2>
    <div class="days">
      <div class="day"><h3>Vendredi <span>30 oct.</span></h3>
        <div class="slot k-depot">{dot('')}<b>9h00 – 20h00</b><span style="color:var(--slate)">Dépôt</span></div></div>
      <div class="day"><h3>Samedi <span>31 oct.</span></h3>
        <div class="slot k-depot">{dot('')}<b>8h00 – 11h30</b><span style="color:var(--slate)">Dépôt</span></div>
        <div class="slot k-forfait">{dot('')}<b>9h30 – 17h30</b><span style="color:var(--slate)">Forfaits Savoie Grand Revard</span></div>
        <div class="slot k-vente">{dot('')}<b>14h00 – 19h30</b><span style="color:var(--slate)">Vente</span></div></div>
      <div class="day"><h3>Dimanche <span>1er nov.</span></h3>
        <div class="slot k-vente">{dot('')}<b>9h00 – 16h30</b><span style="color:var(--slate)">Vente</span></div>
        <div class="slot k-resti">{dot('')}<b>18h30 – 19h15</b><span style="color:var(--slate)">Restitution</span></div></div>
    </div>
    <p style="margin-top:24px">Pendant toute la bourse, stand de fartage avec Réseau Ski Partenaire.</p>
  </div>
</section>

<section aria-labelledby="h-how">
  <div class="wrap cols3">
    <div>
      <h3 class="k-depot">{dot('')}<span style="color:var(--slate)">Déposer</span></h3>
      <p>Matériel de ski propre et en bon état, et vêtements de ski « techniques », proposés par les particuliers. 30 articles maximum par déposant.</p>
      <p>Vous fixez le prix de vente, en accord avec le Ski Club. Des frais de dépôt sont payés pour chaque article.</p>
      <p>Une <strong>pièce d'identité</strong> est obligatoire (passeport, carte d'identité, permis de conduire ou carte de séjour). La loi impose son enregistrement par le club, qui la tient à disposition de l'Administration.</p>
      <p><a href="{B}fiche-prepa-depot-bourse.pdf">Préparez votre dépôt avec la fiche à télécharger</a></p>
    </div>
    <div>
      <h3 class="k-vente">{dot('')}<span style="color:var(--slate)">Acheter</span></h3>
      <p>Les articles sont vendus au prix étiqueté. Ils ne sont ni garantis, ni repris.</p>
      <p>Paiement en espèces ou par carte bancaire.</p>
      {img(U+"2021/10/logoCB.jpg", 144, alt="Carte bancaire acceptée", extra=' width="72"')}
    </div>
    <div>
      <h3 class="k-resti">{dot('')}<span style="color:var(--slate)">Récupérer</span></h3>
      <p>Sur présentation <strong>obligatoire du reçu de dépôt</strong>, vous récupérez le paiement de vos articles vendus et vos invendus.</p>
      <p>Le paiement se fait uniquement par chèque à l'ordre du déposant, avec la liste du matériel vendu ou non.</p>
    </div>
  </div>
  <div class="wrap" style="margin-top:40px">
    <div class="net">
      <p><strong>Gardez votre reçu de dépôt.</strong> Lui seul permet de récupérer votre chèque et vos invendus.</p>
      <p>Les articles non récupérés après 19h15 seront déposés au tri sélectif de Saint-Alban-Leysse le lundi matin. Les chèques non récupérés seront déposés en mairie.</p>
    </div>
  </div>
</section>

<section class="bg-paper" aria-labelledby="h-frais">
  <div class="wrap cols2">
    <div>
      <h2 id="h-frais">Frais de dépôt</h2>
      <table>
        <thead><tr><th scope="col">Prix de l'article</th><th scope="col" class="fee">Frais</th></tr></thead>
        <tbody>
          <tr><td>Jusqu'à 30 €</td><td class="fee">1 €</td></tr>
          <tr><td>De 30 € à 100 €</td><td class="fee">2 €</td></tr>
          <tr><td>Plus de 100 €</td><td class="fee">3 €</td></tr>
        </tbody>
      </table>
      <p style="margin-top:24px"><span class="bigfig">12 %</span><br>de commission sur le montant des ventes, au profit du Ski Club.</p>
    </div>
    <div>
      <h2>Non acceptés</h2>
      <ul class="nope">
        <li>Skis droits</li>
        <li>Chaussures de ski à entrée arrière</li>
        <li>Pulls, doudounes, sous-couches</li>
        <li>Bottes de pluie</li>
        <li>Petits textiles : gants, bonnets, casques…</li>
        <li>Textiles de braderie : vestes de mode, etc.</li>
      </ul>
    </div>
  </div>
</section>

<section aria-labelledby="h-sgr">
  <div class="wrap cols2">
    <div>
      <h2 id="h-sgr">Forfaits Savoie Grand Revard</h2>
      <p>Samedi 31 octobre, de 9h30 à 17h30, Savoie Grand Revard vend sur place ses forfaits :</p>
      <ul>
        <li><strong>Nordique</strong> : Savoie Grand Revard, 73 et National</li>
        <li><strong>Alpin</strong></li>
        <li><strong>Mixte</strong> : alpin et nordique</li>
      </ul>
      <p>Les bénévoles du club sont mobilisés pour vous accueillir dans les meilleures conditions, avec conseils et logistique.</p>
    </div>
    <div>
      <h2>Documents</h2>
      <ul class="docs">
        <li><a class="btn" href="{B}Reglement-bourse-aux-skis-2026.pdf">{ICON("doc")}Règlement de la bourse 2026 (PDF)</a></li>
        <li><a class="btn" href="{B}fiche-prepa-depot-bourse.pdf">{ICON("doc")}Fiche de préparation du dépôt (PDF)</a></li>
        <li><a class="btn" href="{B}FicheDeDepot-1.xlsx">{ICON("doc")}Fiche de dépôt (Excel)</a></li>
      </ul>
    </div>
  </div>
</section>

<section class="bg-paper" aria-labelledby="h-aff">
  <div class="wrap">
    <h2 id="h-aff">Affiches et informations</h2>
    <div class="gallery" style="columns:2 300px">
      <a href="{B}Capture-decran-2026-10-18-103844.png" data-big="{thumb(B+'Capture-decran-2026-10-18-103844.png',1600)}">{img(B+"Capture-decran-2026-10-18-103844.png", 700, alt="Informations sur la bourse aux skis 2026", extra=' width="707" height="1024"')}</a>
      <a href="{B}Capture-decran-2026-10-18-114804.png" data-big="{thumb(B+'Capture-decran-2026-10-18-114804.png',1600)}">{img(B+"Capture-decran-2026-10-18-114804.png", 700, alt="Informations complémentaires sur la bourse aux skis 2026", extra=' width="1024" height="335"')}</a>
    </div>
  </div>
</section>
"""
page("bourse-aux-skis-2026.html", "Bourse aux skis 2026", bourse, "red",
     "30, 31 octobre et 1er novembre au gymnase Vivet de Saint-Alban-Leysse : dépôt, vente, restitution, frais et règlement.",
     "bourse-aux-skis-2026.html", image=B + "Capture-decran-2026-10-07-164002.png")

# ---------------------------------------------------------------- Sorties
sorties = f"""
<div class="phead"><div class="wrap"><h1>Les sorties 2027</h1><p>Dix samedis de ski, de janvier à mars, à Saint-François-Longchamp puis aux Karellis.</p></div></div>

{board("h-cal", "Calendrier")}
<div class="wrap"><p style="margin:16px 0 0">Le 20 mars est réservé au passage des tests. La dernière sortie, le 27 mars, tombe le week-end de Pâques.</p></div>

<section class="bg-paper" aria-labelledby="h-jour">
  <div class="wrap cols2">
    <div>
      <h2 id="h-jour">Le jour de la sortie</h2>
      <div class="days" style="grid-template-columns:1fr">
        <div class="slot k-vente">{dot('')}<b>11h00</b><span style="color:var(--slate)">Rendez-vous au parking du collège</span></div>
        <div class="slot k-vente">{dot('')}<b>11h30</b><span style="color:var(--slate)">Départ du bus</span></div>
        <div class="slot k-vente">{dot('')}<b>vers 13h00</b><span style="color:var(--slate)">Arrivée en station</span></div>
        <div class="slot k-vente">{dot('')}<b>18h45</b><span style="color:var(--slate)">Retour</span></div>
      </div>
      <p style="margin-top:14px">L'horaire de départ peut être avancé les samedis de fort trafic. Le pique-nique est fourni par la famille, dans le sac de l'enfant.</p>
    </div>
    <div>
      <h2>Annulations</h2>
      <div class="net">
        <p>Le club peut annuler une sortie en cas de mauvais temps ou de routes impraticables. <strong>Vous êtes prévenus par SMS au plus tard le vendredi à 18h00.</strong></p>
        <p>Une sortie annulée par le club est remboursée en fin de saison. Une absence de l'enfant n'est pas remboursée, quel qu'en soit le motif.</p>
      </div>
    </div>
  </div>
</section>

<section aria-labelledby="h-mat">
  <div class="wrap cols2">
    <div>
      <h2 id="h-mat">À vérifier avant de partir</h2>
      <p class="noprint"><button class="btn" type="button" data-print>{ICON("print")}Imprimer la liste</button></p>
      <ul class="check">
        <li>Fixations réglées</li><li>Bâtons</li><li>Casque</li><li>Masque</li><li>Gants</li><li>Crème solaire</li>
        <li>Pique-nique</li><li>Goûter</li><li>Boisson chaude</li><li>Mouchoirs</li><li>Barres de céréales</li>
        <li>Veste du club, carte d'adhérent dans la manche gauche</li>
      </ul>
    </div>
    <div>
      <h2>Sacs et housses</h2>
      <p>La <strong>veste de ski</strong> est prêtée par le club et obligatoire. Le casque est marqué par le club ; marquez vous-même le masque, les skis et les petits vêtements.</p>
      <p>Une <strong>housse à skis</strong>, une <strong>housse à chaussures</strong> et un sac pour le goûter et le pique-nique sont obligatoires. Le club fournit une étiquette par sac ou housse : il y a environ 180 sacs noirs dans la soute !</p>
      <p>Attachez ensemble le sac et les housses de votre enfant pour qu'il les retrouve facilement en station.</p>
      {img(U+"2022/01/sac-225x300.png", 450, alt="Exemple de sac et de housses attachés ensemble", extra=' width="225" height="300"')}
    </div>
  </div>
</section>

<section class="bg-paper" aria-labelledby="h-sante">
  <div class="wrap cols2">
    <div>
      <h2 id="h-sante">Vêtements</h2>
      <p>Habillez votre enfant selon la météo, surtout les plus petits : ils ont vite froid en attendant au télésiège. Les bénévoles peuvent retirer une couche de vêtements, mais pas en ajouter.</p>
    </div>
    <div>
      <h2>Santé</h2>
      <p>Une bonne nuit la veille et des sucres lents au petit-déjeuner aident à tenir toute la journée.</p>
      <p>Enfant asthmatique : prévoyez la Ventoline. Les bénévoles ne peuvent administrer aucun médicament.</p>
      <p>Mal des transports : signalez-le au bénévole à la montée dans le bus. Les places à l'avant sont peu nombreuses, un médicament peut être nécessaire. Le téléphone dans le bus favorise les nausées.</p>
      <p>Le téléphone n'est pas utile pendant la sortie. Le club n'est pas responsable en cas de perte ou de vol.</p>
    </div>
  </div>
</section>
"""
page("les-sorties.html", "Les sorties 2027", sorties, "blue",
     "Calendrier, horaires, matériel et consignes des sorties ski du samedi.", "les-sorties.html")

# ---------------------------------------------------------------- Actualités
act = f"""
<div class="phead"><div class="wrap"><h1>Actualités</h1><p>Les nouvelles du club et les photos de chaque sortie.</p></div></div>
<section style="padding-top:24px"><div class="wrap">{rows_by_season(actus)}
<p style="margin-top:36px"><a class="btn" href="archives.html">Saisons précédentes</a></p></div></section>
"""
page("actualites.html", "Actualités", act, "green", "Actualités et photos du Ski Club Saint Alban Leysse.", "actualites.html")

arch_posts = [p for p in posts if p["cat"] == "archives"]
arch = f"""
<div class="phead"><div class="wrap"><h1>Archives</h1><p>Les sorties et événements des saisons passées.</p></div></div>
<section style="padding-top:24px"><div class="wrap">{rows_by_season(arch_posts)}
<p style="margin-top:36px">Les saisons plus anciennes sont encore sur l'ancien site : <a href="{OLD_ARCHIVES}">voir les archives d'avant 2025</a>.</p></div></section>
"""
page("archives.html", "Archives", arch, "green", "Archives du Ski Club Saint Alban Leysse.")

# ---------------------------------------------------------------- Articles
SORTIE_SLUGS = [p for p in actus if p["slug"].startswith("sortie-") and p["slug"].endswith("2026") and not p["slug"].startswith("sortie-00")]
for p in posts:
    lst = actus if p["cat"] == "actus" else arch_posts
    idx = lst.index(p)
    newer = lst[idx - 1] if idx > 0 else None
    older = lst[idx + 1] if idx + 1 < len(lst) else None
    back = ("../actualites.html", "Actualités") if p["cat"] == "actus" else ("../archives.html", "Archives")
    imgs = p["images"]
    cover = ""
    if p["cover"]:
        cover = '<figure class="cover">%s</figure>' % img(p["cover"], 1400, alt=p["title"], lazy=False, sizes="100vw")
    gal = ""
    if len(imgs) > 1 or (imgs and imgs[0] != p["cover"]):
        tiles = "".join(
            '<a href="%s" data-big="%s">%s</a>' % (e(src), e(thumb(src, 1600)),
                img(src, 360, alt="%s, photo %d" % (p["title"], k + 1), sizes="(max-width: 560px) 50vw, (max-width: 1000px) 33vw, 25vw"))
            for k, src in enumerate(imgs))
        gal = ('<section style="padding-top:8px" aria-labelledby="h-gal"><div class="wrap"><h2 id="h-gal">%d photos</h2>'
               '<p class="hint">Touchez une photo pour l’agrandir, puis glissez pour passer à la suivante.</p>'
               '<div class="gallery">%s</div></div></section>') % (len(imgs), tiles)
    track = ""
    if p in SORTIES_2026:
        balises = "".join(
            '<li><a href="%s.html"%s><span class="bal">%d</span><span class="lab">%s</span></a></li>' % (
                s["slug"], ' aria-current="page"' if s is p else "", k + 1, "%d %s" % (int(s["slug"][10:12]), MOIS[int(s["slug"][13:15]) - 1]))
            for k, s in enumerate(SORTIES_2026))
        track = '<nav class="track" aria-label="Les dix sorties de la saison 2026"><div class="wrap"><ol>%s</ol></div></nav>' % balises
    extra = ""
    if p["slug"] == "recap-2026":
        recap_wall = "".join(
            '<a href="%s.html">%s<span>%s, %d photos</span></a>' % (s["slug"], img(s["cover"], 420, alt=s["title"], sizes="(max-width: 700px) 50vw, 20vw"), "Sortie #" + s["slug"][7:9], len(s["images"]))
            for s in SORTIES_2026)
        extra = '<section style="padding-top:8px"><div class="wrap"><h2>Les dix sorties</h2><div class="wall">%s</div></div></section>' % recap_wall
    if p["slug"] == "rendez-vous-a-la-bourse-aux-skis-2025":
        extra = '<div class="wrap narrow"><p><a href="../bourse-aux-skis-2026.html">Voir la bourse aux skis 2026</a></p></div>'
    if p["slug"] == "les-inscriptions-2026":
        extra = '<div class="wrap narrow"><p><a class="btn solid" href="../bourse-aux-skis-2026.html">Bourse aux skis 2026</a></p></div>'
    pager = '<nav class="pager" aria-label="Articles voisins">'
    pager += (f'<a class="sign left g" href="{older["slug"]}.html">Article précédent<small>{e(older["title"])}</small></a>' if older else "<span></span>")
    pager += (f'<a class="sign g" href="{newer["slug"]}.html">Article suivant<small>{e(newer["title"])}</small></a>' if newer else "<span></span>")
    pager += "</nav>"
    text = "".join("<p>%s</p>" % e(t) for t in p["text"])
    body = f"""
<div class="phead"><div class="wrap">
  <p class="crumb"><a href="{back[0]}">{back[1]}</a></p>
  <h1>{e(p['title'])}</h1>
  <p><time datetime="{p['date']}">Publié le {fr_date(p['date'])}</time></p>
</div></div>
{track}
{cover}
<section style="padding-bottom:24px"><div class="wrap narrow lead">{text}</div></section>
{extra}
{gal}
<div class="wrap" style="padding-bottom:64px">{pager}</div>
"""
    page(f"articles/{p['slug']}.html", p["title"], body, "green",
         p["text"][0] if p["text"] else p["title"], None, prefix="../", image=p["cover"] or (imgs[0] if imgs else None))

# ---------------------------------------------------------------- Membres
membres = f"""
<div class="phead"><div class="wrap"><h1>L'encadrement</h1><p>Des bénévoles et des moniteurs ESF accompagnent les enfants à chaque sortie.</p></div></div>
<section class="bg-paper"><div class="wrap split">
  <div class="narrow">
    <h2>Un club tenu par des bénévoles</h2>
    <p class="lead">De l'organisation des sorties à leur déroulement, tout le club fonctionne grâce à ses bénévoles.</p>
    <p>Sur les pistes, les groupes d'enfants sont encadrés soit par des moniteurs de l'ESF, soit par des bénévoles encadrants accompagnés de serre-files.</p>
    <p>Chaque saison commence par une sortie réservée aux encadrants, pour préparer l'année.</p>
    <p><a class="btn" href="articles/sortie-00-04-01-2026.html">Voir la sortie des encadrants 2026</a></p>
  </div>
  <figure>{img(U+"2026/01/20260103_140045-scaled.jpg", 700, alt="Les encadrants du club en station", sizes="(max-width: 860px) 100vw, 45vw")}<figcaption>Sortie des encadrants, janvier 2026</figcaption></figure>
</div></section>
<section><div class="wrap narrow">
  <h2>Vous voulez aider ?</h2>
  <p>Le club a toujours besoin de bras, pour les sorties comme pour la bourse aux skis.</p>
  <p><a class="btn solid" style="--page:var(--black)" href="contact.html">Contacter le club</a></p>
</div></section>
"""
page("membres.html", "Membres", membres, "black", "L'encadrement du Ski Club Saint Alban Leysse.", "membres.html")

# ---------------------------------------------------------------- Partenaires
partners = [
    (U + "2022/11/image-3.png", U + "2022/11/image-3.png", "Logo d'un partenaire du club"),
    (U + "2022/11/image-2.png", U + "2022/11/image-2.png", "Logo d'un partenaire du club"),
    (U + "2022/11/image-1.png", U + "2022/11/image-1.png", "Logo d'un partenaire du club"),
    (U + "2021/09/logo_foirfouille.png", "https://magasins.lafoirfouille.fr/fr_FR/decoration/st-alban-leysse-chambery/0338", "La Foir'Fouille Saint-Alban-Leysse"),
    (U + "2019/11/logo_stac.png", None, "STAC"),
    (U + "2025/08/Capture-decran-2025-08-31-222123.png", U + "2025/08/Capture-decran-2025-08-31-222123.png", "Logo d'un partenaire du club"),
    (U + "2019/11/saint-francois-longchamp.jpg", None, "Saint-François-Longchamp"),
    (U + "2020/01/logo-credit-mutuel-2.png", None, "Crédit Mutuel"),
]
tiles = ""
for src, href, alt in partners:
    im = img(src, 480, alt=alt)
    tiles += f'<a href="{href}">{im}</a>' if href else f"<div>{im}</div>"
part = f"""
<div class="phead"><div class="wrap"><h1>Partenaires</h1><p>Merci aux entreprises et institutions qui soutiennent le club.</p></div></div>
<section><div class="wrap"><div class="logos">{tiles}</div></div></section>
"""
page("partenaires.html", "Partenaires", part, "orange", "Les partenaires du Ski Club Saint Alban Leysse.", "partenaires.html")

# ---------------------------------------------------------------- Contact
contact = f"""
<div class="phead"><div class="wrap"><h1>Nous contacter</h1><p>Une question sur les sorties, les inscriptions ou la bourse aux skis ?</p></div></div>
<section class="bg-paper"><div class="wrap cols2">
  <div>
    <h2>Écrivez-nous sur Facebook</h2>
    <p>Le plus rapide est de nous envoyer un message sur la page Facebook du club.</p>
    <p><a class="btn solid" style="--page:var(--blue)" href="{FB}">{ICON("fb")}Page Facebook du club</a></p>
  </div>
  <div>
    <h2>Nous rencontrer</h2>
    <p>Le club tient un stand au forum des associations de Saint-Alban-Leysse chaque début septembre, et organise la bourse aux skis fin octobre.</p>
    <p><a class="btn" href="bourse-aux-skis-2026.html">Bourse aux skis 2026</a></p>
  </div>
</div></section>
"""
page("contact.html", "Contact", contact, "orange", "Contacter le Ski Club Saint Alban Leysse.", "contact.html")

# ---------------------------------------------------------------- Agenda (.ics) et plan du site
def ics(path, events):
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Ski Club Saint Alban Leysse//FR", "CALSCALE:GREGORIAN",
             "X-WR-CALNAME:Ski Club Saint Alban", "X-WR-TIMEZONE:Europe/Paris"]
    for uid, start, end, summary, loc, descr in events:
        lines += ["BEGIN:VEVENT", "UID:%s@st-alban-ski" % uid, "DTSTAMP:20261029T120000Z",
                  "DTSTART;TZID=Europe/Paris:%s" % start, "DTEND;TZID=Europe/Paris:%s" % end,
                  "SUMMARY:%s" % summary, "LOCATION:%s" % loc.replace(",", "\\,"), "DESCRIPTION:%s" % descr.replace(",", "\\,"),
                  "END:VEVENT"]
    lines.append("END:VCALENDAR")
    with open(os.path.join(ROOT, path), "w", encoding="utf-8", newline="") as f:
        f.write("\r\n".join(lines) + "\r\n")

ics("calendrier-sorties-2027.ics", [
    ("sortie-2027-%02d" % (k + 1), iso.replace("-", "") + "T110000", iso.replace("-", "") + "T184500",
     "Ski club : sortie %d%s (%s)" % (k + 1, ", tests" if note else "", st), "Parking du collège, Saint-Alban-Leysse",
     "Rendez-vous 11h00, départ 11h30, retour vers 18h45. Pique-nique dans le sac. Veste du club obligatoire.")
    for k, (iso, lab, st, note) in enumerate(SORTIES_2027)])
ics("bourse-aux-skis-2026.ics", [
    ("bourse-2026-depot1", "20261030T090000", "20261030T200000", "Bourse aux skis : dépôt", "Gymnase Vivet, impasse du Repos, Saint-Alban-Leysse", "Pièce d'identité obligatoire."),
    ("bourse-2026-depot2", "20261031T080000", "20261031T113000", "Bourse aux skis : dépôt", "Gymnase Vivet, impasse du Repos, Saint-Alban-Leysse", "Pièce d'identité obligatoire."),
    ("bourse-2026-vente1", "20261031T140000", "20261031T193000", "Bourse aux skis : vente", "Gymnase Vivet, impasse du Repos, Saint-Alban-Leysse", "Espèces ou carte bancaire."),
    ("bourse-2026-vente2", "20261101T090000", "20261101T163000", "Bourse aux skis : vente", "Gymnase Vivet, impasse du Repos, Saint-Alban-Leysse", "Espèces ou carte bancaire."),
    ("bourse-2026-resti", "20261101T183000", "20261101T191500", "Bourse aux skis : restitution", "Gymnase Vivet, impasse du Repos, Saint-Alban-Leysse", "Reçu de dépôt obligatoire."),
])

urls = ["index.html", "bourse-aux-skis-2026.html", "les-sorties.html", "actualites.html", "archives.html",
        "membres.html", "partenaires.html", "contact.html"] + ["articles/%s.html" % p["slug"] for p in posts]
with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
    f.write("".join("  <url><loc>%s%s</loc></url>\n" % (SITE_URL, u) for u in urls))
    f.write("</urlset>\n")

print("Pages générées :", len(urls))
