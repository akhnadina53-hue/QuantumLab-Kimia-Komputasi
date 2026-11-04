import streamlit as st
import sympy as sp
from sympy.parsing.sympy_parser import (
    parse_expr, standard_transformations, implicit_multiplication_application,
    convert_xor
)
from PIL import Image
import io
import math

# ----------------------------- Page setup -----------------------------
st.set_page_config(
    page_title="QuantumLab | Komputasi Kuantum",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Inter:wght@400;500;600;700;800&display=swap');
:root { --navy:#101a2d; --panel:#17243a; --line:#2b3b55; --cyan:#56d6e8; --muted:#9fb0c8; }
html, body, [class*="css"] { font-family: Inter, sans-serif; }
.stApp { background: radial-gradient(circle at 10% 0%, #1a3150 0, #0b1424 44%, #080f1c 100%); color:#edf4ff; }
section[data-testid="stSidebar"] { background:#0d1728; border-right:1px solid #263650; }
.block-container { padding-top:1.6rem; padding-bottom:3rem; max-width:1450px; }
.hero { background:linear-gradient(120deg,#172943,#1a3b50); border:1px solid #34516c;
        border-radius:18px; padding:24px 28px; margin-bottom:20px; }
.hero h1 { margin:0; font-size:30px; color:#f5fbff; font-weight:800; }
.hero p { color:#b8c8dc; margin:7px 0 0 0; }
.kicker { color:#63d9e9; font-size:11px; letter-spacing:2px; font-weight:800; text-transform:uppercase; }
.panel { background:rgba(21,34,54,.92); border:1px solid #2b3e59; border-radius:15px; padding:18px 20px; }
.metric { background:#101e32; border:1px solid #2c4562; border-radius:12px; padding:14px; }
.metric-label { color:#9fb0c8; font-size:12px; }
.metric-value { color:#70e1ed; font-size:22px; font-weight:800; font-family:'DM Mono',monospace; }
.small-muted { color:#9fb0c8; font-size:12px; }
div[data-testid="stTextArea"] textarea, div[data-testid="stTextInput"] input {
    background:#0b1627 !important; color:#eaf4ff !important; border:1px solid #38506e !important;
    border-radius:10px !important; font-family:'DM Mono',monospace !important;
}
div[data-testid="stNumberInput"] input { background:#0b1627 !important; color:#eaf4ff !important; }
.stButton>button { border-radius:9px; border:1px solid #3b7185; background:#16465b; color:#f3fdff; font-weight:700; }
.stButton>button:hover { border-color:#65ddec; color:white; background:#1b5c70; }
div[data-testid="stAlert"] { border-radius:10px; }
h2,h3 { color:#f0f7ff; }
code { color:#75e1ed !important; }
hr { border-color:#2b3d56; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <div class="kicker">DESKTOP SCIENTIFIC WORKSPACE · PYTHON</div>
  <h1>⚛️ QuantumLab</h1>
  <p>Laboratorium mini untuk persamaan matematika dan perhitungan mekanika kuantum.</p>
</div>
""", unsafe_allow_html=True)

# ----------------------------- Helpers -----------------------------
if "ocr_to_input" in st.session_state:
    st.session_state["general_equation"] = st.session_state.pop("ocr_to_input")

TRANSFORMS = standard_transformations + (
    implicit_multiplication_application, convert_xor
)
SYMBOLS = {
    "pi": sp.pi, "π": sp.pi, "e": sp.E, "E": sp.E,
    "sqrt": sp.sqrt, "sin": sp.sin, "cos": sp.cos, "tan": sp.tan,
    "exp": sp.exp, "log": sp.log, "ln": sp.log, "abs": sp.Abs,
    "I": sp.I
}

def parse_math(text):
    """Parse common mathematical notation into a SymPy expression."""
    clean = (text or "").strip()
    if not clean:
        raise ValueError("Masukkan persamaan atau ekspresi terlebih dahulu.")
    clean = clean.replace("−", "-").replace("×", "*").replace("·", "*")
    clean = clean.replace("÷", "/").replace("π", "pi").replace("²", "**2").replace("³", "**3")
    clean = clean.replace("√", "sqrt")
    if clean.startswith("$") and clean.endswith("$"):
        clean = clean[1:-1]
    return parse_expr(clean, local_dict=SYMBOLS, transformations=TRANSFORMS, evaluate=True)

def fmt(expr):
    return sp.sstr(sp.simplify(expr))

def solve_input(text):
    if "=" in text:
        left, right = text.split("=", 1)
        lhs, rhs = parse_math(left), parse_math(right)
        equation = sp.Eq(lhs, rhs)
        variables = sorted(equation.free_symbols, key=lambda x: x.name)
        if not variables:
            return equation, ["Pernyataan numerik: " + str(bool(sp.simplify(lhs-rhs) == 0))]
        answers = sp.solve(equation, variables[0])
        return equation, [f"{variables[0]} = {fmt(a)}" for a in answers] or ["Tidak ditemukan solusi simbolik."]
    expr = parse_math(text)
    simplified = sp.simplify(expr)
    return expr, [f"Bentuk sederhana: {fmt(simplified)}",
                  f"Nilai desimal: {sp.N(simplified, 12)}" if not simplified.free_symbols else "Ekspresi masih memuat variabel."]

def perturbation_element(k, n, V1):
    # Matrix element from the uploaded lecture notes:
    # H'kn = -8*k*n*V1 / (pi^2*(k^2-n^2)^2) for opposite parity;
    # zero for equal parity.
    if k == n:
        return sp.Rational(1, 2) * V1
    if (k - n) % 2 == 0:
        return sp.Integer(0)
    return -8 * k * n * V1 / (sp.pi**2 * (k**2 - n**2)**2)

# ----------------------------- Sidebar -----------------------------
with st.sidebar:
    st.markdown("### ⚛️ QuantumLab")
    st.caption("Aplikasi pembelajaran kimia komputasi")
    st.markdown("---")
    st.markdown("**Modul tersedia**")
    st.markdown("• Kalkulator persamaan")
    st.markdown("• Teori perturbasi orde pertama")
    st.markdown("• Input soal dari gambar")
    st.markdown("---")
    st.markdown("**Petunjuk input**")
    st.caption("Gunakan `^` atau `**` untuk pangkat, `sqrt(x)` untuk akar, `pi` untuk π, serta `sin(x)`, `cos(x)`, dan fungsi SymPy lainnya.")
    st.caption("Contoh: `h^2/(8*m*a^2)` atau `x^2 - 4 = 0`")
    st.markdown("---")
    st.caption("Versi 1.0 · Python + Streamlit + SymPy")

tab1, tab2, tab3 = st.tabs(["⌨️  Input & Output", "⚛️  Teori Perturbasi", "🖼️  Baca Soal Gambar"])

# ----------------------------- Tab 1 -----------------------------
with tab1:
    st.markdown("## Kalkulator persamaan")
    st.write("Ketik persamaan, fungsi, atau ekspresi matematika. Simbol Yunani dan notasi umum dapat digunakan.")
    col_in, col_out = st.columns([1.05, 0.95], gap="large")
    with col_in:
        st.markdown('<div class="kicker">01 · RUANG INPUT</div>', unsafe_allow_html=True)
        equation = st.text_area(
            "Persamaan / fungsi",
            value="x^2 - 5*x + 6 = 0",
            height=155,
            placeholder="Contoh: x^2 - 5*x + 6 = 0",
            key="general_equation"
        )
        st.caption("Contoh simbol: π, √, ², ³, ×, ÷. Untuk fungsi, gunakan sintaks seperti `sin(pi/2)`.")
        if st.button("Hitung persamaan  →", key="solve_general", use_container_width=True):
            try:
                result_expr, result_lines = solve_input(equation)
                st.session_state["general_result"] = (fmt(result_expr), result_lines)
                st.session_state["general_error"] = None
            except Exception as exc:
                st.session_state["general_error"] = str(exc)
                st.session_state["general_result"] = None
    with col_out:
        st.markdown('<div class="kicker">02 · RUANG OUTPUT</div>', unsafe_allow_html=True)
        if st.session_state.get("general_error"):
            st.error(st.session_state["general_error"])
        elif st.session_state.get("general_result"):
            source, lines = st.session_state["general_result"]
            st.markdown('<div class="panel">', unsafe_allow_html=True)
            st.markdown("**Hasil pembacaan**")
            st.code(source, language="text")
            st.markdown("**Jawaban**")
            for line in lines:
                st.success(line)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="panel"><span class="small-muted">Hasil perhitungan akan muncul di area ini setelah tombol Hitung ditekan.</span></div>', unsafe_allow_html=True)
        st.markdown("")
        st.info("Kalkulator umum menyelesaikan persamaan satu variabel dan menyederhanakan ekspresi simbolik. Untuk model perturbasi pada materi kuliah, gunakan tab Teori Perturbasi.")

# ----------------------------- Tab 2 -----------------------------
with tab2:
    st.markdown("## Teori perturbasi tak-degenerat orde pertama")
    st.write("Modul ini mengikuti contoh partikel dalam sumur potensial dengan perturbasi linear pada materi PDF yang dilampirkan.")
    st.latex(r"\hat{H}'(x)=\frac{V_1}{a}x,\qquad \psi_n(x)=\sqrt{\frac{2}{a}}\sin\left(\frac{n\pi x}{a}\right)")
    left, right = st.columns([0.9, 1.1], gap="large")
    with left:
        st.markdown('<div class="kicker">PARAMETER PERHITUNGAN</div>', unsafe_allow_html=True)
        V1_val = st.number_input("Ketinggian potensial V₁", value=1.0, step=0.1, format="%.6f")
        n_val = st.number_input("Bilangan kuantum keadaan awal n", min_value=1, max_value=30, value=1, step=1)
        max_state = st.number_input("Keadaan akhir maksimum k", min_value=2, max_value=30, value=6, step=1)
        E1_val = st.number_input("Energi dasar skala E₁ (opsional, satuan energi)", min_value=0.000001, value=1.0, step=0.1, format="%.6f")
        run_pert = st.button("Jalankan perhitungan perturbasi  →", use_container_width=True)
    with right:
        st.markdown('<div class="kicker">HASIL DAN LANGKAH</div>', unsafe_allow_html=True)
        if run_pert:
            V1s = sp.Float(V1_val)
            E1s = sp.Float(E1_val)
            energy_correction = V1s / 2
            energy_total = n_val**2 * E1s + energy_correction
            st.markdown('<div class="metric"><div class="metric-label">KOREKSI ENERGI ORDE PERTAMA</div><div class="metric-value">', unsafe_allow_html=True)
            st.latex(r"E_n^{(1)}=\frac{V_1}{2}")
            st.markdown(f'<div class="metric-value">{float(energy_correction):.10g}</div></div>', unsafe_allow_html=True)
            st.markdown("**Energi setelah koreksi**")
            st.latex(r"E_n\approx E_n^{(0)}+E_n^{(1)}=n^2E_1+\frac{V_1}{2}")
            st.success(f"E({n_val}) ≈ {float(energy_total):.10g}")
            rows = []
            psi_terms = []
            for k in range(1, int(max_state)+1):
                if k == n_val:
                    continue
                Hkn = sp.simplify(perturbation_element(k, int(n_val), V1s))
                denom = (n_val**2 - k**2) * E1s
                coeff = sp.simplify(Hkn / denom)
                rows.append({"k": k, "H′kn": fmt(Hkn), "E⁽⁰⁾n − E⁽⁰⁾k": fmt(denom), "cₖₙ": fmt(coeff), "desimal cₖₙ": f"{float(sp.N(coeff)):.8g}"})
                if coeff != 0:
                    psi_terms.append((k, coeff))
            st.markdown("**Koefisien koreksi fungsi gelombang**")
            st.dataframe(rows, use_container_width=True, hide_index=True)
            st.latex(r"|\psi_n\rangle^{(1)}=\sum_{k\ne n}\frac{H'_{kn}}{E_n^{(0)}-E_k^{(0)}}|\psi_k\rangle")
            if psi_terms:
                expr_parts = [f"({sp.sstr(sp.simplify(c))}) ψ{idx}" for idx, c in psi_terms]
                st.code(f"ψ({n_val}) terkoreksi ≈ ψ{n_val} + " + " + ".join(expr_parts), language="text")
            else:
                st.caption("Tidak ada suku koreksi non-nol pada rentang keadaan yang dipilih.")
            st.caption("Catatan: koefisien dihitung langsung dari elemen matriks dan selisih energi; hasil bergantung pada nilai V₁ dan E₁ yang dimasukkan.")
        else:
            st.markdown('<div class="panel"><span class="small-muted">Atur parameter di kiri, lalu jalankan perhitungan untuk melihat koreksi energi, elemen matriks, dan koefisien fungsi gelombang.</span></div>', unsafe_allow_html=True)
    with st.expander("Rumus yang digunakan dan catatan terhadap materi PDF"):
        st.latex(r"E_n^{(1)}=\langle\psi_n|\hat H'|\psi_n\rangle=\frac{V_1}{2}")
        st.latex(r"H'_{kn}=\begin{cases}-\frac{8knV_1}{\pi^2(k^2-n^2)^2}, & k-n\text{ ganjil}\\0, & k-n\text{ genap},\ k\ne n\end{cases}")
        st.latex(r"c_{kn}=\frac{H'_{kn}}{(n^2-k^2)E_1}")
        st.warning("Pada halaman 5 PDF, angka koefisien untuk suku ψ₄ tampak tertulis 0,0096(V₁/E₁). Namun, jika memakai H′₄₁ = −32V₁/(225π²) dan penyebut −15E₁ seperti yang tercantum pada halaman yang sama, hasil pembagian langsung adalah sekitar 0,00096(V₁/E₁). Aplikasi menghitung dari rumus, bukan menyalin angka yang tampak tidak konsisten tersebut.")

# ----------------------------- Tab 3 -----------------------------
with tab3:
    st.markdown("## Unggah soal dalam bentuk gambar")
    st.write("Unggah foto atau tangkapan layar soal. Teks akan dibaca menggunakan OCR, lalu dapat dikirim ke kalkulator.")
    upload = st.file_uploader("Pilih gambar soal", type=["png", "jpg", "jpeg", "webp", "bmp"])
    if upload:
        image = Image.open(upload).convert("RGB")
        preview_col, ocr_col = st.columns([0.9, 1.1], gap="large")
        with preview_col:
            st.image(image, caption="Pratinjau gambar yang diunggah", use_container_width=True)
        with ocr_col:
            st.markdown('<div class="kicker">HASIL EKSTRAKSI TEKS (OCR)</div>', unsafe_allow_html=True)
            if st.button("Baca teks pada gambar", use_container_width=True):
                try:
                    import pytesseract
                    extracted = pytesseract.image_to_string(image, lang="eng")
                    st.session_state["ocr_text"] = extracted.strip()
                    st.session_state["ocr_error"] = None
                except ImportError:
                    st.session_state["ocr_error"] = "Pustaka pytesseract belum terpasang. Jalankan: pip install pytesseract"
                except Exception as exc:
                    st.session_state["ocr_error"] = "OCR belum dapat dijalankan. Pastikan Tesseract OCR sudah terpasang di komputer. Detail: " + str(exc)
            if st.session_state.get("ocr_error"):
                st.warning(st.session_state["ocr_error"])
                st.caption("Selain memasang pytesseract, instal juga aplikasi Tesseract OCR pada Windows dan pastikan lokasinya terdaftar di PATH.")
            if st.session_state.get("ocr_text") is not None:
                ocr_text = st.text_area("Teks hasil OCR (boleh diperbaiki sebelum dihitung)", value=st.session_state["ocr_text"], height=180, key="ocr_edit")
                if st.button("Kirim teks ke ruang input", use_container_width=True):
                    st.session_state["ocr_to_input"] = ocr_text
                    st.success("Teks OCR siap dimasukkan. Aplikasi akan mengisinya pada ruang input setelah halaman dimuat ulang; periksa simbol dan angka sebelum menghitung.")
    else:
        st.markdown('<div class="panel"><span class="small-muted">Format yang didukung: PNG, JPG, JPEG, WEBP, BMP. Untuk akurasi terbaik, gunakan gambar yang terang, fokus, dan tidak miring.</span></div>', unsafe_allow_html=True)

st.markdown("---")
st.markdown('<div class="small-muted">QuantumLab adalah alat bantu pembelajaran. Periksa kembali hasil OCR dan asumsi matematis sebelum menggunakan jawaban untuk laporan atau tugas.</div>', unsafe_allow_html=True)
