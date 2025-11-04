#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make_copyright_pdf.py
Genera un único PDF con el código fuente (backend + frontend) listo para depósito en Copyright Office.

Características:
- Portada con título / autor / asunto / fecha.
- Tabla de contenido con página de inicio por archivo.
- Contenido con números de línea, wrapping de líneas y encabezado por archivo.
- Metadatos PDF: Title, Author, Subject.
- Excluye rutas ruidosas y archivos binarios por default.
- Solo depende de reportlab.

Uso:
  python make_copyright_pdf.py --output out.pdf --roots ctrctsapp crewsapp apptransactions appschedule appinventory src
  python make_copyright_pdf.py --output copyright-deposit.pdf --roots ctrctsapp crewsapp auditapp apptransactions appschedule appinventory src --title "Chalan-Pro Source Code Deposit" --author "Division16 LLC / Mister Oliver" --subject "Copyright Office Deposit - Chalan-Pro"

"""
import argparse
import os
import sys
import datetime
from pathlib import Path

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib import utils

# -----------------------------
# Config por defecto
# -----------------------------
DEFAULT_INCLUDE_EXTS = {
    ".py", ".vue", ".js", ".ts", ".tsx", ".jsx",
    ".css", ".scss", ".sass",
    ".html", ".htm",
    ".md", ".rst", ".txt",
    ".json", ".yml", ".yaml", ".ini", ".env", ".toml",
    ".sql",
}

DEFAULT_EXCLUDE_DIRS = {
    "__pycache__", ".git", ".hg", ".svn", ".idea", ".vscode",
    "node_modules", "dist", "build", "venv", ".venv", ".mypy_cache",
    ".pytest_cache", ".DS_Store", ".cache", ".parcel-cache",
    ".next", "coverage", ".nuxt", ".output",
    "media", "staticfiles", "static_root"
}

DEFAULT_MAX_FILE_BYTES = 2 * 1024 * 1024  # 2 MB por archivo para evitar mamotretos

PAGE_SIZE = LETTER
MARGIN_L = 0.75 * inch
MARGIN_R = 0.75 * inch
MARGIN_T = 0.75 * inch
MARGIN_B = 0.75 * inch

# Tipografía monoespaciada base del PDF (sin fuentes externas)
FONT = "Courier"
FONT_BOLD = "Courier-Bold"

TITLE_FONT_SIZE = 20
SUBTITLE_FONT_SIZE = 12
HEADER_FONT_SIZE = 10
BODY_FONT_SIZE = 9
FOOTER_FONT_SIZE = 9

LINE_SPACING = 11  # leading (pts) para BODY_FONT_SIZE=9 es cómodo
TOC_FONT_SIZE = 10
TOC_LINE_SPACING = 13


def is_textlike(path: Path, include_exts):
    # Si no hay extensión (ej. Makefile), lo incluimos si es razonable leerlo como texto
    if path.suffix:
        return path.suffix.lower() in include_exts
    # Heurística: archivos sin extensión pero pequeños -> incluir
    return path.is_file() and path.stat().st_size <= DEFAULT_MAX_FILE_BYTES


def should_skip_dir(dirname: str, exclude_dirs):
    # Coincidencia simple por nombre
    return dirname in exclude_dirs


def collect_files(roots, include_exts, exclude_dirs, max_bytes):
    files = []
    for root in roots:
        root_path = Path(root)
        if not root_path.exists():
            continue
        if root_path.is_file():
            if is_textlike(root_path, include_exts) and root_path.stat().st_size <= max_bytes:
                files.append(root_path)
            continue

        for dirpath, dirnames, filenames in os.walk(root_path):
            # Filtra in-place dirnames para evitar descender
            dirnames[:] = [d for d in dirnames if not should_skip_dir(d, exclude_dirs)]
            for fname in filenames:
                fpath = Path(dirpath) / fname
                # Filtra binarios obvios por extensión
                ext = fpath.suffix.lower()
                if ext in {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".pdf", ".zip", ".7z", ".rar", ".exe", ".dll", ".so"}:
                    continue
                # Texto por extensión o heurística de tamaño
                if is_textlike(fpath, include_exts) and fpath.stat().st_size <= max_bytes:
                    files.append(fpath)

    # Orden determinístico (alfabético por ruta relativa)
    files = sorted(files, key=lambda p: str(p).lower())
    return files


def read_file_safely(path: Path):
    try:
        # Intentar UTF-8 primero; fallback latin-1 para robustez
        data = path.read_text(encoding="utf-8", errors="strict")
    except Exception:
        data = path.read_text(encoding="latin-1", errors="replace")
    return data


def wrap_line_to_width(line, max_width_pts, font_name, font_size):
    """Divide una línea en fragmentos que quepan en max_width_pts medidos en puntos."""
    chunks = []
    if not line:
        return [""]

    start = 0
    n = len(line)
    while start < n:
        # Buscamos el mayor segmento que quepa
        lo, hi = start + 1, n
        best = start + 1
        while lo <= hi:
            mid = (lo + hi) // 2
            seg = line[start:mid]
            w = stringWidth(seg, font_name, font_size)
            if w <= max_width_pts:
                best = mid
                lo = mid + 1
            else:
                hi = mid - 1
        segment = line[start:best]
        # Evitar bucles infinitos con un solo carácter muy ancho (no aplica con Courier)
        if best == start:
            best = start + 1
            segment = line[start:best]
        chunks.append(segment)
        start = best
    return chunks


def paginate_estimate(files, available_width, available_height, font_name, font_size, line_spacing):
    """
    Precalcula cuántas páginas consumirá cada archivo para construir TOC con páginas de inicio.
    Devuelve:
      - file_page_starts: dict[path] = page_number_start (1-based incluyendo portada y TOC)
      - total_pages: número total de páginas estimado (con portada y TOC placeholders)
    """
    # Páginas iniciales reservadas:
    #  1 página de portada
    #  n páginas de TOC (se calcula al final con base en el número de entradas)
    # Primero estimamos contenido -> luego estimamos TOC -> sumamos.
    cover_pages = 1

    lines_per_page = int(available_height // line_spacing)
    # Header por archivo consume algunas líneas: 3 líneas de cabecera de sección
    header_lines = 3

    per_file_pages = []
    for path in files:
        text = read_file_safely(path)
        # Normalizar tabs a 4 espacios
        text = text.replace("\t", "    ").splitlines()
        # restar header lines de la primera página
        remaining_lines_first_page = max(0, lines_per_page - header_lines)
        total_lines_consumed = 0

        # Calcula wrap por línea
        wrapped_lines = []
        for idx, line in enumerate(text, start=1):
            # Line numbers ocupan margen izquierdo en texto, pero aquí medimos solo el contenido
            # Dejamos ~6 caracteres para numeración y espacio "00000: "
            line_for_wrap = f"{idx:05d}: {line}".rstrip("\n\r")
            wrapped = wrap_line_to_width(line_for_wrap, available_width, font_name, font_size)
            wrapped_lines.extend(wrapped if wrapped else [""])

        if not wrapped_lines:
            wrapped_lines = [""]

        # Primera página
        count = 0
        if wrapped_lines:
            first_page_lines = min(remaining_lines_first_page, len(wrapped_lines))
            count += 1  # primera página
            left = len(wrapped_lines) - first_page_lines
            if left > 0:
                # Páginas completas siguientes
                full_pages, rem = divmod(left, lines_per_page)
                count += full_pages
                if rem > 0:
                    count += 1

        per_file_pages.append((path, count))

    # Calcular páginas del TOC: ~1 línea por archivo + títulos
    toc_header_lines = 3  # título + subtítulo + espacio
    toc_lines = toc_header_lines + len(files)
    toc_pages = (toc_lines + (int(available_height // TOC_LINE_SPACING) - 1)) // int(available_height // TOC_LINE_SPACING)
    toc_pages = max(1, toc_pages)  # al menos 1

    # Construir mapa de páginas de inicio
    file_page_starts = {}
    current_page = 1  # portada empieza en 1
    current_page += cover_pages
    current_page += toc_pages
    for path, pages in per_file_pages:
        file_page_starts[path] = current_page
        current_page += max(1, pages)

    total_pages = current_page - 1
    return file_page_starts, total_pages, cover_pages, toc_pages


def draw_footer(c, page_num, total_pages):
    c.setFont(FONT, FOOTER_FONT_SIZE)
    footer = f"Page {page_num} of {total_pages}"
    c.drawRightString(c._pagesize[0] - MARGIN_R, MARGIN_B / 2.0, footer)


def draw_header_filename(c, relpath):
    c.setFont(FONT_BOLD, HEADER_FONT_SIZE)
    c.drawString(MARGIN_L, c._pagesize[1] - MARGIN_T + 6, relpath)


def render_pdf(output_path, files, title, author, subject, roots_base):
    c = canvas.Canvas(output_path, pagesize=PAGE_SIZE)
    width, height = PAGE_SIZE

    available_width = width - (MARGIN_L + MARGIN_R)
    available_height = height - (MARGIN_T + MARGIN_B)

    # Estimar paginación para TOC
    file_page_starts, total_pages, cover_pages, toc_pages = paginate_estimate(
        files, available_width, available_height, FONT, BODY_FONT_SIZE, LINE_SPACING
    )

    # Metadatos
    c.setTitle(title or "Source Code Deposit")
    if author:
        c.setAuthor(author)
    if subject:
        c.setSubject(subject)

    # ---- Portada
    today = datetime.datetime.now().strftime("%B %d, %Y")
    c.setFont(FONT_BOLD, TITLE_FONT_SIZE)
    c.drawString(MARGIN_L, height - 2 * inch, title or "Source Code Deposit")
    c.setFont(FONT, SUBTITLE_FONT_SIZE)
    c.drawString(MARGIN_L, height - 2 * inch - 24, f"Author: {author or '—'}")
    c.drawString(MARGIN_L, height - 2 * inch - 24 - 16, f"Subject: {subject or '—'}")
    c.drawString(MARGIN_L, height - 2 * inch - 24 - 16 - 16, f"Date: {today}")

    # Nota sobre el alcance
    c.setFont(FONT, 10)
    c.drawString(MARGIN_L, height - 2 * inch - 24 - 16 - 16 - 28,
                 "This PDF aggregates selected source files for copyright deposit.")
    draw_footer(c, 1, total_pages)
    c.showPage()

    # ---- TOC
    lines_per_toc_page = int(available_height // TOC_LINE_SPACING)
    c.setFont(FONT_BOLD, 16)
    c.drawString(MARGIN_L, height - MARGIN_T, "Table of Contents")
    c.setFont(FONT, 10)
    c.drawString(MARGIN_L, height - MARGIN_T - 18, "File path → starting page")
    y = height - MARGIN_T - 18 - 18

    count_on_page = 0
    for path in files:
        rel = str(Path(path).relative_to(roots_base) if roots_base and Path(path).is_relative_to(roots_base) else path)
        start_page = file_page_starts[path]
        c.setFont(FONT, TOC_FONT_SIZE)
        # Ajuste de truncado si muy largo
        left_text = rel
        right_text = str(start_page)
        # Separadores: dibujamos "...."
        dots_area_width = (width - MARGIN_R) - (MARGIN_L + 60)
        max_left_pts = dots_area_width - 40  # heurística para no chocar con el número
        # Recortar si excede
        while stringWidth(left_text, FONT, TOC_FONT_SIZE) > max_left_pts and len(left_text) > 8:
            left_text = left_text[:len(left_text)-4] + "…"

        c.drawString(MARGIN_L, y, left_text)
        c.drawRightString(width - MARGIN_R, y, right_text)

        y -= TOC_LINE_SPACING
        count_on_page += 1
        if count_on_page >= lines_per_toc_page:
            # footer de TOC: calculamos la página actual
            current_page_number = c.getPageNumber()
            draw_footer(c, current_page_number, total_pages)
            c.showPage()
            # nuevo encabezado de página TOC
            c.setFont(FONT_BOLD, 16)
            c.drawString(MARGIN_L, height - MARGIN_T, "Table of Contents (cont.)")
            y = height - MARGIN_T - 24
            count_on_page = 0

    # Footer de la última página de TOC
    current_page_number = c.getPageNumber()
    draw_footer(c, current_page_number, total_pages)
    c.showPage()

    # ---- Contenido de archivos
    for path in files:
        # Relativo respecto al primer root común si aplica
        try:
            rel = str(Path(path).relative_to(roots_base))
        except Exception:
            rel = str(path)

        # Leer y normalizar
        raw = read_file_safely(path)
        raw = raw.replace("\t", "    ")
        lines = raw.splitlines() or [""]

        # Preparar medidas para wrapping
        c.setFont(FONT, BODY_FONT_SIZE)
        max_text_width = width - (MARGIN_L + MARGIN_R)

        # Comenzar página nueva con encabezado de archivo
        def new_page_with_header():
            c.setFont(FONT_BOLD, HEADER_FONT_SIZE)
            c.drawString(MARGIN_L, height - MARGIN_T + 6, rel)
            c.setFont(FONT, BODY_FONT_SIZE)
            # Línea base donde empezamos a pintar texto
            return height - MARGIN_T - 14

        y = new_page_with_header()
        lines_per_page = int((y - MARGIN_B) // LINE_SPACING)
        used_lines = 0

        # Espacio para contenido tras header
        # Vamos línea por línea con numeración + wrapping
        for idx, line in enumerate(lines, start=1):
            numbered = f"{idx:05d}: {line.rstrip()}"
            wrapped = wrap_line_to_width(numbered, max_text_width, FONT, BODY_FONT_SIZE)
            if not wrapped:
                wrapped = [""]

            for segment in wrapped:
                if used_lines >= lines_per_page:
                    # Footer de página saliente
                    current_page_number = c.getPageNumber()
                    draw_footer(c, current_page_number, total_pages)
                    c.showPage()
                    y = new_page_with_header()
                    used_lines = 0
                    lines_per_page = int((y - MARGIN_B) // LINE_SPACING)

                c.setFont(FONT, BODY_FONT_SIZE)
                c.drawString(MARGIN_L, y, segment)
                y -= LINE_SPACING
                used_lines += 1

        # Footer de la última página del archivo (o página única)
        current_page_number = c.getPageNumber()
        draw_footer(c, current_page_number, total_pages)
        c.showPage()

    # Cerrar
    c.save()


def find_common_root(roots):
    """Devuelve un path base común si es posible (para TOC bonito)."""
    abs_roots = [str(Path(r).resolve()) for r in roots if Path(r).exists()]
    if not abs_roots:
        return None
    common = os.path.commonpath(abs_roots)
    try:
        return Path(common)
    except Exception:
        return None


def main():
    parser = argparse.ArgumentParser(description="Genera un PDF único con el código fuente para depósito de Copyright.")
    parser.add_argument("--output", "-o", default="copyright-deposit.pdf", help="Nombre del PDF de salida.")
    parser.add_argument("--roots", nargs="+", required=True,
                        help="Raíces a incluir (carpetas o archivos). Ej: ctrctsapp crewsapp apptransactions appschedule appinventory src")
    parser.add_argument("--title", default="Chalan-Pro Source Code Deposit", help="Título del documento PDF.")
    parser.add_argument("--author", default="Division16 LLC / Mister Oliver", help="Autor del documento PDF.")
    parser.add_argument("--subject", default="Copyright Office Deposit - Chalan-Pro", help="Asunto/Subject del PDF.")
    parser.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_FILE_BYTES,
                        help=f"Tamaño máximo por archivo en bytes (default {DEFAULT_MAX_FILE_BYTES}).")
    parser.add_argument("--include-exts", nargs="*", default=None,
                        help="Extensiones a incluir (override). Ej: .py .vue .js .css .html .md")
    parser.add_argument("--exclude-dirs", nargs="*", default=None,
                        help="Directorios a excluir (override).")
    args = parser.parse_args()

    include_exts = set(args.include_exts) if args.include_exts else DEFAULT_INCLUDE_EXTS
    exclude_dirs = set(args.exclude_dirs) if args.exclude_dirs else DEFAULT_EXCLUDE_DIRS

    files = collect_files(args.roots, include_exts, exclude_dirs, args.max_bytes)
    if not files:
        print("No se encontraron archivos de código para incluir. Revisa --roots / --include-exts / --exclude-dirs.", file=sys.stderr)
        sys.exit(1)

    common_base = find_common_root(args.roots)
    render_pdf(args.output, files, args.title, args.author, args.subject, common_base)

    print(f"✅ PDF generado: {args.output}")
    print(f"Archivos incluidos: {len(files)}")
    print("Pro tip: conserva un ZIP de los fuentes tal cual para tu resguardo interno.")


if __name__ == "__main__":
    main()
