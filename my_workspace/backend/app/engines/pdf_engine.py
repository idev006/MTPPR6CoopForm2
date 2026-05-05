import io
import re
import base64
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

import pikepdf
from pikepdf import Pdf, Name, String, Dictionary, Array
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen.canvas import Canvas
from PIL import Image
from loguru import logger

# ─── Constants ──────────────────────────────────────────────────────────
FF_READONLY = 1
FF_RADIO = 0x8000
Q_LEFT, Q_CENTER, Q_RIGHT = 0, 1, 2
HIDDEN_FLAG = 2

class PdfEngine:
    """
    World-class PDF filling engine.
    Handles AcroForm filling, Thai font rendering (Appearance Streams),
    signature embedding, and document locking.
    """

    def __init__(self, font_path: Path, check_icon_path: Optional[Path] = None):
        self.font_path = font_path
        self.check_icon_path = check_icon_path
        self._font_registered = False
        self._register_font()

    def _register_font(self):
        if not self.font_path.exists():
            logger.error(f"Font file not found: {self.font_path}")
            return
        pdfmetrics.registerFont(TTFont("THSarabunNew", str(self.font_path)))
        self._font_registered = True
        logger.info(f"Registered font: {self.font_path.name}")

    def fill_form(self, input_pdf: Path, output_pdf: Path, data: Dict[str, Any]) -> bool:
        """
        Main entry point for filling a PDF form.
        """
        try:
            with Pdf.open(str(input_pdf)) as pdf:
                field_map = self._build_field_map(pdf)
                
                logger.info(f"Filling PDF: {input_pdf.name} with {len(data)} fields")
                
                for field_name, value in data.items():
                    if field_name not in field_map:
                        logger.warning(f"Field '{field_name}' not found in PDF template.")
                        continue
                        
                    self._process_field(pdf, field_map[field_name], field_name, value)

                # Set NeedAppearances to False since we generated custom /AP
                acroform = pdf.Root.get("/AcroForm")
                if acroform and "/NeedAppearances" in acroform:
                    del acroform["/NeedAppearances"]

                # Lock all fields
                self._lock_fields(field_map)
                
                pdf.save(str(output_pdf))
                logger.info(f"Successfully saved filled PDF to: {output_pdf}")
                return True
                
        except Exception as e:
            logger.exception(f"Failed to fill PDF: {e}")
            return False

    def _build_field_map(self, pdf: Pdf) -> Dict[str, pikepdf.Object]:
        """Recursively collect all fields from AcroForm."""
        acroform = pdf.Root.get("/AcroForm")
        if not acroform or "/Fields" not in acroform:
            return {}
            
        field_map = {}
        def _collect(fields_array, parent_path: str):
            for field_ref in fields_array:
                # pikepdf may return either an indirect reference or a direct object
                field = field_ref.resolve() if hasattr(field_ref, "resolve") else field_ref
                if field is None:
                    continue
                t = field.get("/T")
                if t is None: continue
                
                name = str(t)
                full_path = f"{parent_path}.{name}" if parent_path else name
                
                if "/FT" in field:
                    field_map[full_path] = field
                
                if "/Kids" in field:
                    _collect(field["/Kids"], full_path)
                    
        _collect(acroform["/Fields"], "")
        return field_map

    def _process_field(self, pdf: Pdf, field: pikepdf.Object, name: str, value: Any):
        """Process a single field based on its type and prefix."""
        prefix = name.split(".")[0]
        
        # 1. Handle Empty Value -> Hide Field
        if value is None or value == "":
            field["/V"] = String("")
            self._set_hidden(field)
            return

        # 2. Set Value /V
        field["/V"] = String(str(value))

        # 3. Handle Radio Buttons
        if prefix.startswith("rdo_"):
            ff = int(field.get("/Ff", 0))
            if ff & FF_RADIO:
                self._select_radio(field, str(value))
                return

        # 4. Generate Appearance Stream (/AP) for Text, Checkbox, and Signatures
        rect, widget = self._find_rect_and_widget(field)
        if not rect:
            logger.warning(f"Could not find /Rect for field: {name}")
            return

        ap_stream = None
        try:
            if prefix.startswith("chk_") and str(value).upper() == "Y":
                if self.check_icon_path:
                    ap_stream = self._make_image_appearance(pdf, rect, self.check_icon_path)
            
            elif prefix.startswith("sign_"):
                # Handle Base64 signature
                if isinstance(value, str) and value.startswith("data:image"):
                    ap_stream = self._make_signature_appearance(pdf, rect, value)
                else:
                    # Fallback to centered text (Signer Name)
                    ap_stream = self._make_text_appearance(pdf, value, rect, font_size=14, quadding=Q_CENTER)
            
            else:
                # Standard Text Field
                da = str(field.get("/DA", ""))
                font_size = self._extract_font_size(da)
                fill_color = self._extract_color(da)
                quadding = int(field.get("/Q", 0))
                ap_stream = self._make_text_appearance(pdf, str(value), rect, font_size, quadding, fill_color)

            if ap_stream:
                widget["/AP"] = Dictionary({"/N": ap_stream})
                
        except Exception as e:
            logger.error(f"Error generating appearance for {name}: {e}")

    def _make_text_appearance(self, dest_pdf: Pdf, value: str, rect: Array, 
                            font_size: float = 16, quadding: int = Q_LEFT, 
                            fill_color: Tuple[float, float, float] = (0, 0, 0)) -> pikepdf.Stream:
        """Create appearance stream for text using ReportLab."""
        x1, y1, x2, y2 = [float(v) for v in rect]
        w, h = x2 - x1, y2 - y1

        buf = io.BytesIO()
        c = Canvas(buf, pagesize=(w, h))
        c.setFont("THSarabunNew", font_size)
        c.setFillColorRGB(*fill_color)
        
        # Adjust vertical position for Thai font
        y_pos = (h - font_size) / 2 + (font_size * 0.05)

        if quadding == Q_CENTER:
            c.drawCentredString(w / 2, y_pos, value)
        elif quadding == Q_RIGHT:
            c.drawRightString(w - 5, y_pos, value)
        else:
            c.drawString(5, y_pos, value)
        c.save()

        return self._buffer_to_xobject(dest_pdf, buf, w, h)

    def _make_image_appearance(self, dest_pdf: Pdf, rect: Array, img_path: Path) -> pikepdf.Stream:
        """Create appearance stream with an image."""
        x1, y1, x2, y2 = [float(v) for v in rect]
        w, h = x2 - x1, y2 - y1

        buf = io.BytesIO()
        c = Canvas(buf, pagesize=(w, h))
        c.drawImage(str(img_path), 0, 0, width=w, height=h, mask="auto", preserveAspectRatio=True, anchor='c')
        c.save()

        return self._buffer_to_xobject(dest_pdf, buf, w, h)

    def _make_signature_appearance(self, dest_pdf: Pdf, rect: Array, sig_base64: str) -> pikepdf.Stream:
        """Process Base64 signature and create appearance stream."""
        # Decode base64
        try:
            header, encoded = sig_base64.split(",", 1)
            sig_data = base64.b64decode(encoded)
            img = Image.open(io.BytesIO(sig_data)).convert("RGBA")
            
            # Trim whitespace (optional but recommended for better fit)
            # bbox = img.getbbox()
            # if bbox: img = img.crop(bbox)
            
            x1, y1, x2, y2 = [float(v) for v in rect]
            w, h = x2 - x1, y2 - y1
            
            # Use ReportLab to draw the PIL image
            buf = io.BytesIO()
            c = Canvas(buf, pagesize=(w, h))
            c.drawInlineImage(img, 0, 0, width=w, height=h, preserveAspectRatio=True, anchor='c')
            c.save()
            
            return self._buffer_to_xobject(dest_pdf, buf, w, h)
        except Exception as e:
            logger.error(f"Failed to process signature: {e}")
            raise

    def _buffer_to_xobject(self, dest_pdf: Pdf, buf: io.BytesIO, w: float, h: float) -> pikepdf.Stream:
        """Helper to convert ReportLab buffer to pikepdf Form XObject."""
        buf.seek(0)
        with Pdf.open(buf) as mini:
            page = mini.pages[0]
            content_bytes = page["/Contents"].read_bytes()
            mini_res = page.get("/Resources", Dictionary())

            ap_stream = dest_pdf.make_stream(content_bytes)
            ap_stream["/Subtype"] = Name.Form
            ap_stream["/BBox"] = Array([0, 0, w, h])

            res_dict = Dictionary()
            if "/Font" in mini_res:
                font_dict = Dictionary()
                for fn, fref in mini_res["/Font"].items():
                    obj = fref.resolve() if hasattr(fref, "resolve") else fref
                    font_dict[fn] = dest_pdf.copy_foreign(obj)
                res_dict["/Font"] = font_dict

            if "/XObject" in mini_res:
                xobj_dict = Dictionary()
                for xn, xref in mini_res["/XObject"].items():
                    obj = xref.resolve() if hasattr(xref, "resolve") else xref
                    xobj_dict[xn] = dest_pdf.copy_foreign(obj)
                res_dict["/XObject"] = xobj_dict

            if res_dict:
                ap_stream["/Resources"] = res_dict
            
            return ap_stream

    def _set_hidden(self, field: pikepdf.Object):
        """Set field and kids to hidden."""
        def _hide(obj):
            current = int(obj.get("/F", 4)) # default 4 = Print
            obj["/F"] = pikepdf.Object.parse(str(current | HIDDEN_FLAG).encode())
            if "/AP" in obj: del obj["/AP"]

        _hide(field)
        if "/Kids" in field:
            for k in field["/Kids"]:
                _hide(k.resolve() if hasattr(k, "resolve") else k)

    def _select_radio(self, field: pikepdf.Object, value: str):
        """Handle Radio button selection."""
        field["/V"] = Name(f"/{value}")
        if "/Kids" not in field: return
        for k_ref in field["/Kids"]:
            k = k_ref.resolve() if hasattr(k_ref, "resolve") else k_ref
            ap = k.get("/AP")
            if not ap: continue
            n_ref = ap.get("/N")
            n = n_ref.resolve() if hasattr(n_ref, "resolve") else n_ref
            if isinstance(n, Dictionary) and f"/{value}" in n:
                k["/AS"] = Name(f"/{value}")
            else:
                k["/AS"] = Name("/Off")

    def _find_rect_and_widget(self, field: pikepdf.Object) -> Tuple[Optional[Array], pikepdf.Object]:
        """Find /Rect and the widget object (sometimes it's in /Kids)."""
        rect = field.get("/Rect")
        if rect: return rect, field
        
        if "/Kids" in field:
            # Find the largest kid (usually the visible widget)
            best_kid = None
            max_area = 0
            for k_ref in field["/Kids"]:
                k = k_ref.resolve() if hasattr(k_ref, "resolve") else k_ref
                r = k.get("/Rect")
                if not r: continue
                x1, y1, x2, y2 = [float(v) for v in r]
                area = abs((x2-x1) * (y2-y1))
                if area > max_area:
                    max_area = area
                    best_kid = k
                    rect = r
            return rect, best_kid
        return None, field

    def _extract_font_size(self, da: str) -> float:
        match = re.search(r'(\d+(\.\d+)?)\s+Tf', da)
        return float(match.group(1)) if match else 16.0

    def _extract_color(self, da: str) -> Tuple[float, float, float]:
        rgb_match = re.search(r'(\d+(\.\d+)?)\s+(\d+(\.\d+)?)\s+(\d+(\.\d+)?)\s+rg', da)
        if rgb_match:
            return (float(rgb_match.group(1)), float(rgb_match.group(3)), float(rgb_match.group(5)))
        gray_match = re.search(r'(\d+(\.\d+)?)\s+g', da)
        if gray_match:
            g = float(gray_match.group(1))
            return (g, g, g)
        return (0, 0, 0)

    def _lock_fields(self, field_map: Dict[str, pikepdf.Object]):
        """Set all fields to ReadOnly."""
        for field in field_map.values():
            ff = int(field.get("/Ff", 0))
            field["/Ff"] = pikepdf.Object.parse(str(ff | FF_READONLY).encode())
