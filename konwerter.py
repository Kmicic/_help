import os
from bs4 import BeautifulSoup

# --- Konfiguracja ---
STARY_KATALOG = '.'
NOWY_KATALOG = 'nowa_strona'
PLIK_MENU = 'lc2009_content_static.html'

# --- Treść szablonu nowej strony HTML5 ---
SZABLON_HTML = """
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{tytul}</title>
    <link rel="stylesheet" href="styl.css">
</head>
<body>
    <div class="kontener">
        <nav class="menu-nawigacyjne">
            {menu}
        </nav>
        <main class="glowna-tresc">
            {tresc}
        </main>
    </div>
</body>
</html>
"""

# --- Podstawowe style CSS dla układu dwukolumnowego ---
STYLE_CSS = """
body {
    font-family: sans-serif;
    margin: 0;
    background-color: #f4f4f4;
}
.kontener { display: flex; }
.menu-nawigacyjne {
    width: 280px;
    min-width: 280px;
    background-color: #f0f0f0;
    padding: 20px;
    height: 100vh;
    overflow-y: auto;
    border-right: 1px solid #ddd;
    box-sizing: border-box;
}
.menu-nawigacyjne p { margin: 0 0 5px 0; line-height: 1.4; }
.menu-nawigacyjne a { color: #0000d0; text-decoration: none; }
.menu-nawigacyjne a:hover { text-decoration: underline; }
.glowna-tresc {
    flex-grow: 1;
    padding: 30px;
    background-color: #fff;
    max-width: calc(100% - 320px);
}
.glowna-tresc, .glowna-tresc p, .glowna-tresc font {
    font-family: "Times New Roman", serif;
    font-size: 12pt;
}
"""

def odczytaj_plik_z_autodetekcja_kodowania(sciezka):
    """Próbuje odczytać plik jako UTF-8, a jeśli się nie uda, jako ISO-8859-2."""
    try:
        with open(sciezka, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        print(f"  -> Błąd UTF-8 w pliku '{os.path.basename(sciezka)}'. Próbuję odczytu w ISO-8859-2.")
        with open(sciezka, 'r', encoding='iso-8859-2') as f:
            return f.read()

def konwertuj_strone():
    if not os.path.exists(NOWY_KATALOG):
        os.makedirs(NOWY_KATALOG)
        print(f"Utworzono katalog: '{NOWY_KATALOG}'")

    print(f"Wczytuję menu z pliku: '{PLIK_MENU}'")
    menu_raw_html = odczytaj_plik_z_autodetekcja_kodowania(os.path.join(STARY_KATALOG, PLIK_MENU))
    soup_menu = BeautifulSoup(menu_raw_html, 'html.parser')
    
    menu_container = soup_menu.find('body')
    if not menu_container:
        print("BŁĄD: Nie znaleziono tagu <body> w pliku spisu treści.")
        return

    linki_do_przetworzenia = menu_container.find_all('a')
    for a_tag in linki_do_przetworzenia:
        if a_tag.has_attr('target'):
            del a_tag['target']
    
    menu_html = ''.join(str(c) for c in menu_container.contents)
    print("Pomyślnie wyodrębniono menu.")
    print(f"Znaleziono {len(linki_do_przetworzenia)} linków do przetworzenia.")

    for a_tag in linki_do_przetworzenia:
        stary_plik_href = a_tag.get('href')
        
        if not stary_plik_href or stary_plik_href.startswith(('http', 'mailto')):
            continue
        
        sciezka_do_starego_pliku = os.path.join(STARY_KATALOG, stary_plik_href)
        
        if not os.path.exists(sciezka_do_starego_pliku):
            print(f"OSTRZEŻENIE: Pomijam, plik nie istnieje: '{sciezka_do_starego_pliku}'")
            continue

        print(f"Przetwarzam: '{stary_plik_href}'...")
        tresc_raw_html = odczytaj_plik_z_autodetekcja_kodowania(sciezka_do_starego_pliku)
        soup_tresc = BeautifulSoup(tresc_raw_html, 'html.parser')
        
        tresc_body = soup_tresc.find('body')
        tresc_html = ''.join(str(c) for c in tresc_body.contents) if tresc_body else ''
        
        tytul_strony = a_tag.get_text(strip=True) or "Dokumentacja"

        nowa_strona_html = SZABLON_HTML.format(tytul=tytul_strony, menu=menu_html, tresc=tresc_html)
        
        sciezka_do_nowego_pliku = os.path.join(NOWY_KATALOG, stary_plik_href)
        with open(sciezka_do_nowego_pliku, 'w', encoding='utf-8') as f:
            f.write(nowa_strona_html)

    sciezka_css = os.path.join(NOWY_KATALOG, 'styl.css')
    with open(sciezka_css, 'w', encoding='utf-8') as f: f.write(STYLE_CSS)
    print(f"Utworzono plik stylów: '{sciezka_css}'")

    if linki_do_przetworzenia:
        pierwszy_link = linki_do_przetworzenia[0].get('href')
        index_html_content = f'<!DOCTYPE html><html><head><title>Przekierowanie</title><meta http-equiv="refresh" content="0; url={pierwszy_link}"></head><body></body></html>'
        sciezka_index = os.path.join(NOWY_KATALOG, 'index.html')
        with open(sciezka_index, 'w', encoding='utf-8') as f: f.write(index_html_content)
        print(f"Utworzono plik startowy: '{sciezka_index}'")

    print("\n--- Zakończono! ---")
    print(f"Nowa strona została wygenerowana w katalogu '{NOWY_KATALOG}'.")

if __name__ == "__main__":
    konwertuj_strone()