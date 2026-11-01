from ..components.forms import (
    _label,
    _input_style,
    _select_style,
    _input_s,
    _select_s,
    _field,
    _field_with_check,
    _section_header,
    _section,
)
import reflex as rx
from ...state import State
from ..theme import (
    _ldc_reg, ORANGE, ORANGE_LIGHT, ORANGE_BORDER, NAVY, NAVY_DARK, BLUE_ACC,
    RED_ERR, GREEN_OK, VIOLET, PAGE_BG, CARD_BG, CARD_BDR, TEXT_MAIN, TEXT_SUB,
    TEXT_LABEL, INPUT_BG, INPUT_BDR, INPUT_FOC, SECT_BG, DIVIDER,
)
from ..components.common import brand_footer
from ..components.navigation import navbar, utility_bar
from ..components.footer import footer
from ..components.attachments import (
    ui_boton_descargar_adjunto,
    ui_enlace_archivo,
    ui_tarjeta_adjunto,
    ui_tarjeta_adjunto_historial,
)

def solicitudes_page() -> rx.Component:
    # navbar() ya está definida en este módulo, no requiere importar desde pqrs
 
    acceso_denegado = rx.center(
        rx.vstack(
            rx.icon("lock", size=48, color=RED_ERR),
            rx.heading("Acceso Denegado", size="7", color=RED_ERR),
            rx.text("Necesitas iniciar sesión para crear una solicitud.", color=TEXT_SUB),
            rx.link(rx.button("Ir al Login", color_scheme="blue", border_radius="10px"), href="/login"),
            spacing="4", align_items="center",
        ),
        min_height="80vh",
    )
 
    contenido = rx.box(
        navbar(),
        rx.center(
            rx.box(
                rx.vstack(
 
                    # �??�?? Encabezado �??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??
                    rx.vstack(
                        rx.hstack(
                            rx.box(
                                rx.icon("file-plus", size=22, color="white"),
                                bg=f"linear-gradient(135deg, {NAVY_DARK}, {NAVY})",
                                border_radius="14px",
                                width="50px", height="50px",
                                display="flex", align_items="center", justify_content="center",
                                box_shadow=f"0 6px 20px {NAVY}44",
                                flex_shrink="0",
                            ),
                            rx.vstack(
                                rx.heading(
                                    "Nueva Solicitud PQRS",
                                    size="6", color=TEXT_MAIN,
                                    font_weight="800", letter_spacing="-0.02em",
                                ),
                                rx.text(
                                    "Completa el formulario para radicar tu Petición, Queja, Reclamo o Sugerencia.",
                                    font_size="13px", color=TEXT_SUB,
                                ),
                                spacing="0", align_items="start",
                            ),
                            spacing="3", align_items="center",
                        ),
                        border_bottom=f"2px solid {_ldc_reg('#e2e8f0','#1e3a5f')}",
                        padding_bottom="16px",
                        margin_bottom="4px",
                        width="100%",
                    ),

                    # �??�?? Datos de contacto (Solo para no registrados) �??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??
                    rx.cond(
                        ~State.es_autenticada,
                        _section("mail", "Datos de contacto",
                            rx.vstack(
                                _label("Correo electrónico para respuesta", required=True),
                                rx.input(
                                    placeholder="ejemplo@correo.com",
                                    value=State.pqrs_contacto_email,
                                    on_change=State.set_pqrs_contacto_email,
                                    type="email",
                                    **_input_s(),
                                ),
                                rx.text(
                                    "Te enviaremos las actualizaciones y respuesta de tu solicitud a este correo.",
                                    font_size="12px", color=TEXT_SUB,
                                ),
                                spacing="2", align_items="start", width="100%",
                            ),
                        ),
                    ),
 
                    # �??�?? Sección 1: Tipo + Área �??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??
                    _section("tag", "Clasificación de la solicitud",
                        rx.grid(
                            rx.vstack(
                                _label("Tipo de Solicitud"),
                                rx.select(
                                    ["Petición", "Queja", "Reclamo", "Sugerencia"],
                                    placeholder="Selecciona el tipo",
                                    value=State.tipo_solicitud,
                                    on_change=State.set_tipo_solicitud,
                                    **_select_s(),
                                ),
                                spacing="0", align_items="start", width="100%",
                            ),
                            rx.vstack(
                                _label("Área Responsable"),
                                rx.select(
                                    ["Secretaría","Contabilidad","Bienestar","Tesorería","Atención al Ciudadano","Otros"],
                                    placeholder="Selecciona el área",
                                    value=State.area_responsable,
                                    on_change=State.set_area_responsable,
                                    **_select_s(),
                                ),
                                spacing="0", align_items="start", width="100%",
                            ),
                            template_columns={"base": "1fr", "md": "1fr 1fr"},
                            gap="4", width="100%",
                        ),
                    ),
 
                    # Campo "otro área"
                    rx.cond(
                        State.area_responsable == "Otros",
                        rx.box(
                            rx.vstack(
                                _label("Especifica el área"),
                                rx.input(
                                    placeholder="Nombre del área responsable",
                                    value=State.area_otro,
                                    on_change=State.set_area_otro,
                                    **_input_s(),
                                ),
                                spacing="0", align_items="start", width="100%",
                            ),
                            bg=CARD_BG, border=f"1px solid {CARD_BDR}",
                            border_radius="14px", padding="18px 20px", width="100%",
                        ),
                    ),
 
                    # �??�?? Sección 2: Asunto + Descripción �??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??
                    _section("file-text", "Detalle de la solicitud",
                        rx.vstack(
                            rx.vstack(
                                _label("Asunto"),
                                rx.text_area(
                                    placeholder="Escribe el asunto de tu solicitud...",
                                    value=State.asunto,
                                    on_change=State.set_asunto,
                                    rows="3",
                                    resize="vertical",
                                    min_height="90px",
                                    **_input_s(),
                                ),
                                spacing="0", align_items="start", width="100%",
                            ),
                            rx.vstack(
                                _label("Descripción detallada"),
                                rx.text_area(
                                    placeholder="Escribe aquí todos los detalles de tu solicitud...",
                                    value=State.descripcion,
                                    on_change=State.set_descripcion,
                                    rows="5",
                                    max_length=1000,
                                    resize="vertical",
                                    min_height="130px",
                                    **_input_s(),
                                ),
                                rx.hstack(
                                    rx.spacer(),
                                    rx.text(
                                        State.descripcion_len,
                                        font_size="12px",
                                        color=rx.cond(State.descripcion_len > 900, ORANGE, TEXT_SUB),
                                        font_weight="500",
                                    ),
                                    rx.text(" / 1000 caracteres", font_size="12px", color=TEXT_SUB),
                                    spacing="0", width="100%",
                                ),
                                spacing="1", align_items="start", width="100%",
                            ),
                            spacing="4", width="100%",
                        ),
                    ),
 
                    # �??�?? Sección 3: Adjuntos �??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??
                    _section("paperclip", "Documento adjunto (opcional)",
                        rx.vstack(
                            rx.text(
                                "Puedes adjuntar hasta 3 archivos PDF, PNG o JPG (máx. 10 MB en total).",
                                font_size="12px", color=TEXT_SUB, line_height="1.6",
                            ),
 
                            # �??�?? Zona de carga: widget JS autocontenido �??�??�??�??�??�??
                            rx.script("""
window.__pqrsUpload = window.__pqrsUpload || (function(){
    function init(root){
        if(root.__pqrsInit) return;
        root.__pqrsInit = true;
 
        const MAX  = 10*1024*1024, MAX_N = 3;
        const OK   = ['pdf','png','jpg','jpeg'];
        let   list = [];
 
        const zone  = root.querySelector('[data-zone]');
        const inp   = root.querySelector('[data-inp]') || root.querySelector('input[type="file"]');
        const lbl   = root.querySelector('[data-lbl]');
        const meta  = root.querySelector('[data-meta]');
        const barW  = root.querySelector('[data-barw]');
        const bar   = root.querySelector('[data-bar]');
        const usedL = root.querySelector('[data-used]');
        const freeL = root.querySelector('[data-free]');
        const rows  = root.querySelector('[data-rows]');
        const errEl = root.querySelector('[data-err]');
 
        function fmt(b){ return (b/1048576).toFixed(2)+' MB'; }
        function ext(n){ return n.split('.').pop().toLowerCase(); }
        function total(){ return list.reduce((a,f)=>a+f.size,0); }
 
        function showErr(msg){
            errEl.textContent=msg; errEl.style.display='block';
        }

        function clearErr(){
            errEl.textContent=''; errEl.style.display='none';
        }
 
        function render(){
            const used=total(), free=Math.max(0,MAX-used);
            const pct=Math.min(100,(used/MAX)*100);
 
            // barra
            barW.style.display = list.length?'block':'none';
            bar.style.width    = pct+'%';
            const col = pct>=95?'#ef4444':pct>=75?'#f59e0b':'#10b981';
            bar.style.background=col;
            usedL.textContent = fmt(used)+' usado';
            freeL.textContent = fmt(free)+' libres';
            freeL.style.color = col;
 
            // zona label
            if(list.length){
                lbl.textContent = list.map(f=>f.name).join(', ');
                lbl.style.color = '#f0f6ff';
                meta.textContent= list.length+' archivo(s)';
            } else {
                lbl.textContent = 'Arrastra y suelta archivos aquí o haz clic para explorar';
                lbl.style.color = '#94a3b8';
                meta.textContent= 'PDF, PNG, JPG · máx. 10 MB · hasta 3 archivos';
            }
 
            // filas
            rows.innerHTML='';
            list.forEach(function(f,i){
                const d=document.createElement('div');
                d.style.cssText='display:flex;align-items:center;gap:8px;'+
                    'padding:7px 0;border-bottom:1px solid #1e3a5f;';
                d.innerHTML=
                    '<svg width="13" height="13" viewBox="0 0 24 24" fill="none"'+
                    ' stroke="#3b82f6" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16'+
                    'a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/>'+
                    '</svg>'+
                    '<span style="flex:1;font-size:12px;color:#f0f6ff;">'+
                        f.name+' <em style="color:#64748b;font-style:normal;">('+fmt(f.size)+')</em>'+
                    '</span>'+
                    '<button type="button" style="background:none;border:none;cursor:pointer;'+
                    'color:#ef4444;font-size:14px;padding:2px 6px;" data-i="'+i+'">✖</button>';
                rows.appendChild(d);
            });
            rows.querySelectorAll('[data-i]').forEach(function(btn){
                btn.onclick=function(e){ e.preventDefault(); list.splice(+btn.dataset.i,1); render(); };
            });
            if(list.length){
                const clearAll=document.createElement('button');
                clearAll.type='button';
                clearAll.textContent='Quitar todos los adjuntos';
                clearAll.style.cssText='margin-top:8px;width:100%;padding:6px 10px;border:1px solid #991b1b;'+
                    'border-radius:8px;background:#450a0a;color:#fca5a5;font-size:12px;cursor:pointer;';
                clearAll.onclick=function(e){
                    e.preventDefault();
                    list=[];
                    clearErr();
                    inp.value='';
                    render();
                };
                rows.appendChild(clearAll);
            }
        }
 
        inp.addEventListener('change',function(){
            const inc=Array.from(this.files);
            clearErr();
            for(const f of inc){
                if(!OK.includes(ext(f.name))){
                    showErr('�? Formato ".' + ext(f.name) + '" no permitido. Solo se aceptan PDF, PNG o JPG.');
                    this.value=''; return;
                }
                if(f.size>MAX){
                    showErr('�? "'+f.name+'" supera el límite de 10 MB.');
                    this.value=''; return;
                }
                if(list.some(function(e){return e.name===f.name&&e.size===f.size;})) continue;
                if(list.length>=MAX_N){
                    showErr('�? Solo puedes adjuntar hasta '+MAX_N+' archivos.');
                    this.value=''; return;
                }
                if(total()+f.size>MAX){
                    showErr('�? Agregar "'+f.name+'" superaría el límite. Libre: '+fmt(MAX-total()));
                    this.value=''; return;
                }
                list.push({name:f.name,size:f.size});
            }
            this.value='';
            render();
        });
 
        // drag & drop
        zone.addEventListener('dragover',function(e){
            e.preventDefault();
            zone.style.borderColor='#2563eb';
            zone.style.background='#0f2744';
        });
        zone.addEventListener('dragleave',function(){
            zone.style.borderColor='#334155';
            zone.style.background='#0a1628';
        });
        zone.addEventListener('drop',function(e){
            e.preventDefault();
            zone.style.borderColor='#334155';
            zone.style.background='#0a1628';
            // simular change con los archivos soltados
            const dt=new DataTransfer();
            Array.from(e.dataTransfer.files).forEach(function(f){ dt.items.add(f); });
            inp.files=dt.files;
            inp.dispatchEvent(new Event('change'));
        });
    }
 
    window.__pqrsClear = function() {
        document.querySelectorAll('[data-pqrs-upload]').forEach(function(root) {
            const inp = root.querySelector('[data-inp]') || root.querySelector('input[type="file"]');
            if (inp) {
                inp.value = '';
                inp.dispatchEvent(new Event('change'));
            }
        });
    };

    // observar DOM para inicializar cuando el widget aparezca
    const obs=new MutationObserver(function(){
        document.querySelectorAll('[data-pqrs-upload]').forEach(init);
    });
    obs.observe(document.body,{childList:true,subtree:true});
    document.querySelectorAll('[data-pqrs-upload]').forEach(init);
    return {init:init};
})();
"""),
                            rx.el.div(
                                # Zona de carga
                                rx.el.div(
                                    rx.el.div(
                                        rx.el.svg(
                                            rx.el.path(d="M16 16 L12 12 L8 16"),
                                            rx.el.path(d="M20.39 18.39A5 5 0 0 0 18 9h-1.26A8 8 0 1 0 3 16.3"),
                                            width="22", height="22", viewBox="0 0 24 24",
                                            fill="none", stroke="#3b82f6",
                                            stroke_width="2", stroke_linecap="round",
                                            style={"flexShrink":"0"},
                                        ),
                                        rx.el.div(
                                            rx.el.div(
                                                "Arrastra y suelta archivos aquí o haz clic para explorar",
                                                data_lbl=True,
                                                style={"fontSize":"13px","color":"#94a3b8","fontWeight":"500"},
                                            ),
                                            rx.el.div(
                                                "PDF, PNG, JPG · máx. 10 MB · hasta 3 archivos",
                                                data_meta=True,
                                                style={"fontSize":"11px","color":"#64748b","marginTop":"3px"},
                                            ),
                                        ),
                                        style={"display":"flex","alignItems":"center","gap":"12px"},
                                    ),
                                    rx.upload(
                                        id="upload_solicitud",
                                        multiple=True,
                                        accept={
                                            "application/pdf": [".pdf"],
                                            "image/png": [".png"],
                                            "image/jpeg": [".jpg", ".jpeg"]
                                        },
                                        style={
                                            "position":"absolute","inset":"0",
                                            "width":"100%","height":"100%",
                                            "opacity":"0","cursor":"pointer",
                                        },
                                    ),
                                    data_zone=True,
                                    style={
                                        "position":"relative","border":"2px dashed #334155",
                                        "borderRadius":"12px","padding":"16px 20px",
                                        "background":"#0a1628","cursor":"pointer",
                                        "transition":"border-color .15s,background .15s",
                                        "width":"100%",
                                    },
                                    onmouseenter="this.style.borderColor='#2563eb';this.style.background='#0f2744'",
                                    onmouseleave="this.style.borderColor='#334155';this.style.background='#0a1628'",
                                ),
                                # Barra de almacenamiento
                                rx.el.div(
                                    rx.el.div(
                                        rx.el.span("0.00 MB usado", data_used=True,
                                                   style={"fontSize":"11px","color":"#94a3b8"}),
                                        rx.el.span("10.00 MB libres", data_free=True,
                                                   style={"fontSize":"11px","fontWeight":"700","color":"#10b981"}),
                                        style={"display":"flex","justifyContent":"space-between","marginBottom":"4px"},
                                    ),
                                    rx.el.div(
                                        rx.el.div(
                                            data_bar=True,
                                            style={
                                                "height":"100%","width":"0%","borderRadius":"6px",
                                                "background":"#10b981",
                                                "transition":"width .35s ease,background .35s ease",
                                            },
                                        ),
                                        style={
                                            "background":"#1e3a5f","borderRadius":"6px",
                                            "height":"7px","overflow":"hidden",
                                        },
                                    ),
                                    data_barw=True,
                                    style={"display":"none","marginTop":"10px"},
                                ),
                                # Lista de archivos
                                rx.el.div(data_rows=True, style={"marginTop":"6px"}),
                                # Error
                                rx.el.div(
                                    data_err=True,
                                    style={
                                        "display":"none","marginTop":"8px",
                                        "padding":"8px 14px",
                                        "background":"#2d0000","border":"1px solid #991b1b",
                                        "borderRadius":"8px","fontSize":"12px","color":"#ef4444",
                                    },
                                ),
                                data_pqrs_upload=True,
                                style={"width":"100%"},
                            ),
 
                            # Error desde State (validaciones servidor)
                            rx.cond(
                                State.archivo_error_mensaje != "",
                                rx.hstack(
                                    rx.icon("alert-circle", size=14, color=RED_ERR),
                                    rx.text(State.archivo_error_mensaje, font_size="12px", color=RED_ERR),
                                    spacing="2", align_items="center",
                                ),
                            ),
                            spacing="3", width="100%",
                        ),
                    ),
 
                    # �??�?? Autorización �??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??
                    rx.hstack(
                        rx.checkbox(
                            is_checked=State.acepta_politica_solicitud,
                            on_change=State.set_acepta_politica_solicitud,
                            color_scheme="blue",
                            size="2",
                        ),
                        rx.hstack(
                            rx.text("He leído y acepto la ", font_size="13px", color=TEXT_SUB),
                            rx.link(
                                "Política de Tratamiento de Datos Personales",
                                href="/politica-privacidad",
                                color=BLUE_ACC,
                                font_size="13px",
                                font_weight="600",
                                text_decoration="none",
                                _hover={"text_decoration": "underline"},
                            ),
                            spacing="0", flex_wrap="wrap",
                        ),
                        spacing="3", align_items="center",
                        bg=_ldc_reg("#eff6ff","#0a1628"),
                        border=f"1px solid {_ldc_reg('#bfdbfe','#1e3a5f')}",
                        border_radius="10px",
                        padding="12px 16px",
                        width="100%",
                    ),
 
                    # �??�?? Botón enviar �??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??
                    rx.button(
                        rx.hstack(
                            rx.icon("send", size=16),
                            rx.text("Enviar Solicitud", font_size="15px", font_weight="600"),
                            spacing="2",
                        ),
                        on_click=State.crear_solicitud(rx.upload_files(upload_id="upload_solicitud")),
                        width="100%",
                        height="48px",
                        bg=rx.cond(
                            State.acepta_politica_solicitud,
                            f"linear-gradient(135deg, {NAVY_DARK}, {NAVY})",
                            _ldc_reg("#e2e8f0","#1e293b"),
                        ),
                        color=rx.cond(State.acepta_politica_solicitud, "white", TEXT_SUB),
                        border_radius="12px",
                        cursor=rx.cond(State.acepta_politica_solicitud, "pointer", "not-allowed"),
                        box_shadow=rx.cond(
                            State.acepta_politica_solicitud,
                            f"0 4px 16px {NAVY}44",
                            "none",
                        ),
                        _hover=rx.cond(
                            State.acepta_politica_solicitud,
                            {"opacity": "0.92", "transform": "translateY(-1px)"},
                            {},
                        ),
                        transition="all 0.15s ease",
                        is_disabled=~State.acepta_politica_solicitud,
                    ),

                    # �??�?? Mensaje resultado �??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??�??
                    rx.cond(
                        State.solicitud_mensaje != "",
                        rx.hstack(
                            rx.icon(
                                rx.cond(State.solicitud_mensaje.contains("éxito"), "circle-check", "circle-x"),
                                size=16,
                                color=rx.cond(State.solicitud_mensaje.contains("éxito"), GREEN_OK, RED_ERR),
                            ),
                            rx.text(
                                State.solicitud_mensaje, font_size="13px", font_weight="500",
                                color=rx.cond(State.solicitud_mensaje.contains("éxito"), GREEN_OK, RED_ERR),
                            ),
                            spacing="2", align_items="center",
                            bg=rx.cond(State.solicitud_mensaje.contains("éxito"),
                                       _ldc_reg("#f0fdf4","#002818"), _ldc_reg("#fef2f2","#2d0000")),
                            border=rx.cond(State.solicitud_mensaje.contains("éxito"),
                                           "1px solid #bbf7d0", "1px solid #fecaca"),
                            border_radius="10px", padding="12px 16px", width="100%",
                        ),
                    ),
 
                    spacing="4",
                    align_items="stretch",
                    width="100%",
                ),
                width="100%",
                max_width="720px",
                padding={"base": "20px 16px", "md": "36px 40px"},
            ),
            width="100%",
        ),
        bg=PAGE_BG, min_height="100vh", width="100%",
    )
 
    return contenido

NAVY      = "#1e3a8a"
NAVY_DARK = "#172554"
BLUE_ACC  = "#2563eb"
GREEN_OK  = "#16a34a"
ORANGE    = "#f59e0b"
RED_ERR   = "#ef4444"
VIOLET    = "#8b5cf6"
 
def consultar_estado_page() -> rx.Component:
    text_color = rx.color_mode_cond(light="#0f172a", dark="#f8fafc")
    subtext_color = rx.color_mode_cond(light="#64748b", dark="#94a3b8")
    card_bg = rx.color_mode_cond(light="rgba(255, 255, 255, 0.94)", dark="rgba(15, 23, 42, 0.82)")
    card_border = rx.color_mode_cond(light="1px solid rgba(226, 232, 240, 0.9)", dark="1px solid rgba(51, 65, 85, 0.6)")
    inner_card_bg = rx.color_mode_cond(light="#f8fafc", dark="rgba(30, 41, 59, 0.4)")
    inner_border = rx.color_mode_cond(light="1px solid #e2e8f0", dark="1px solid #334155")

    def estado_badge(estado: str) -> rx.Component:
        return rx.badge(
            estado,
            color_scheme=rx.match(
                estado,
                ("Radicada", "orange"),
                ("Asignada a Area", "blue"),
                ("En Gestion de Area", "purple"),
                ("Solucionada", "teal"),
                ("Reabierta", "yellow"),
                ("Cerrada", "green"),
                "gray"
            ),
            size="2",
            radius="full",
            variant="surface",
        )

    def timeline_step(title: str, is_active: bool, icon_name: str) -> rx.Component:
        color = rx.cond(is_active, "#2563eb", rx.color_mode_cond(light="#94a3b8", dark="#475569"))
        bg_color = rx.cond(is_active, rx.color_mode_cond(light="#eff6ff", dark="rgba(37,99,235,0.2)"), rx.color_mode_cond(light="#f1f5f9", dark="rgba(15,23,42,0.5)"))
        border_color = rx.cond(is_active, "#2563eb", rx.color_mode_cond(light="#cbd5e1", dark="#334155"))
        return rx.vstack(
            rx.box(
                rx.icon(icon_name, size=18, color=color),
                bg=bg_color,
                border=f"2px solid",
                border_color=border_color,
                border_radius="full",
                width="42px", height="42px",
                display="flex", align_items="center", justify_content="center",
                box_shadow=rx.cond(is_active, "0 6px 16px -2px rgba(37,99,235,0.45)", "none"),
                transition="all 0.25s ease",
            ),
            rx.text(
                title, 
                font_size="12px", 
                font_weight=rx.cond(is_active, "700", "500"), 
                color=rx.cond(is_active, text_color, subtext_color)
            ),
            spacing="1",
            align_items="center"
        )

    def timeline_connector(is_active: bool) -> rx.Component:
        color = rx.cond(is_active, "#2563eb", rx.color_mode_cond(light="#cbd5e1", dark="#334155"))
        return rx.box(
            height="3px",
            flex="1",
            bg=color,
            margin_bottom="22px",
            border_radius="full",
            transition="all 0.25s ease",
        )

    return rx.box(
        navbar(),
        rx.center(
            rx.box(
                rx.vstack(
                    # ── Header Minimalista & Botón Cerrar ──
                    rx.hstack(
                        rx.hstack(
                            rx.box(
                                rx.icon("search", size=22, color="#2563eb"),
                                width="46px", height="46px", border_radius="14px",
                                bg=rx.color_mode_cond(light="#eff6ff", dark="rgba(37,99,235,0.18)"),
                                border=rx.color_mode_cond(light="1px solid #bfdbfe", dark="1px solid rgba(59,130,246,0.3)"),
                                display="flex", align_items="center", justify_content="center",
                                box_shadow="0 4px 12px -2px rgba(37,99,235,0.25)",
                            ),
                            rx.vstack(
                                rx.heading("Consulta de Solicitud", size="6", color=text_color, font_weight="800", letter_spacing="-0.02em"),
                                rx.text("Rastrea en tiempo real el avance y trazabilidad de tu radicado.", color=subtext_color, font_size="13px"),
                                align_items="start", spacing="0"
                            ),
                            spacing="3", align_items="center"
                        ),
                        rx.spacer(),
                        rx.icon_button(
                            "x",
                            variant="soft",
                            color_scheme="gray",
                            radius="full",
                            size="3",
                            on_click=State.cerrar_consulta,
                            cursor="pointer",
                        ),
                        width="100%",
                        align_items="center",
                        padding_bottom="5",
                        border_bottom=rx.color_mode_cond(light="1px solid #e2e8f0", dark="1px solid #334155")
                    ),
                    
                    # ── Barra de Búsqueda Flotante tipo Pill ──
                    rx.box(
                        rx.vstack(
                            rx.text("Número de Radicado Oficial", font_weight="700", font_size="13px", color=text_color),
                            rx.hstack(
                                rx.hstack(
                                    rx.icon("hash", size=17, color="#2563eb"),
                                    rx.input(
                                        placeholder="Ej: PQRS-2024-abc12345",
                                        value=State.consulta_radicado,
                                        on_change=State.set_consulta_radicado,
                                        border="none",
                                        outline="none",
                                        size="3",
                                        variant="soft",
                                        width="100%",
                                        bg="transparent",
                                        font_size="14px",
                                    ),
                                    spacing="2",
                                    align_items="center",
                                    flex="1",
                                    px="3",
                                ),
                                rx.button(
                                    rx.hstack(
                                        rx.icon("search", size=15),
                                        rx.text("Buscar Radicado", font_weight="700", font_size="13px"),
                                        spacing="2",
                                        align_items="center"
                                    ),
                                    on_click=State.consultar_estado_solicitud,
                                    size="3",
                                    radius="full",
                                    style={
                                        "background": "linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)",
                                        "color": "white",
                                        "padding": "0 22px",
                                        "boxShadow": "0 6px 18px -4px rgba(37,99,235,0.6)",
                                        "cursor": "pointer"
                                    },
                                    _hover={"transform": "translateY(-1px)", "boxShadow": "0 8px 24px -4px rgba(37,99,235,0.8)"},
                                    transition="all 0.2s ease",
                                ),
                                width="100%",
                                p="1.5",
                                border_radius="full",
                                bg=rx.color_mode_cond(light="#ffffff", dark="#0f172a"),
                                border=rx.color_mode_cond(light="1px solid #cbd5e1", dark="1px solid #334155"),
                                box_shadow=rx.color_mode_cond(
                                    light="0 4px 14px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.02)",
                                    dark="0 4px 14px rgba(0,0,0,0.4)"
                                ),
                                align_items="center",
                            ),
                            spacing="2",
                            width="100%",
                            align_items="start",
                        ),
                        width="100%",
                        margin_y="5"
                    ),
                    
                    # ── Mensaje de Resultado ──
                    rx.cond(
                        State.consulta_mensaje,
                        rx.box(
                            rx.hstack(
                                rx.icon(
                                    rx.cond(
                                        State.consulta_mensaje.contains("encontrada") & ~State.consulta_mensaje.contains("No se encontró"),
                                        "circle-check",
                                        "circle-alert"
                                    ),
                                    size=17,
                                    color=rx.cond(
                                        State.consulta_mensaje.contains("encontrada") & ~State.consulta_mensaje.contains("No se encontró"),
                                        "#16a34a",
                                        "#ef4444"
                                    ),
                                ),
                                rx.text(
                                    State.consulta_mensaje,
                                    color=rx.cond(
                                        State.consulta_mensaje.contains("encontrada") & ~State.consulta_mensaje.contains("No se encontró"),
                                        rx.color_mode_cond(light="#15803d", dark="#4ade80"),
                                        rx.color_mode_cond(light="#b91c1c", dark="#f87171")
                                    ),
                                    font_weight="600",
                                    font_size="13px"
                                ),
                                spacing="2",
                                align_items="center"
                            ),
                            p="3.5",
                            border_radius="14px",
                            border=rx.cond(
                                State.consulta_mensaje.contains("encontrada") & ~State.consulta_mensaje.contains("No se encontró"),
                                "1px solid rgba(34, 197, 94, 0.35)",
                                "1px solid rgba(239, 68, 68, 0.35)"
                            ),
                            bg=rx.cond(
                                State.consulta_mensaje.contains("encontrada") & ~State.consulta_mensaje.contains("No se encontró"),
                                rx.color_mode_cond(light="#f0fdf4", dark="rgba(22,163,74,0.12)"),
                                rx.color_mode_cond(light="#fef2f2", dark="rgba(239,68,68,0.12)")
                            ),
                            width="100%",
                            margin_bottom="4"
                        )
                    ),
                    
                    # ── Tarjeta de Detalles de la Solicitud ──
                    rx.cond(
                        State.solicitud_consultada,
                        rx.box(
                            rx.vstack(
                                # Cabecera de Radicado
                                rx.hstack(
                                    rx.hstack(
                                        rx.box(
                                            rx.icon("file-check", size=20, color="#2563eb"),
                                            bg=rx.color_mode_cond(light="#eff6ff", dark="rgba(37,99,235,0.15)"),
                                            border_radius="12px",
                                            width="40px", height="40px",
                                            display="flex", align_items="center", justify_content="center",
                                            border=rx.color_mode_cond(light="1px solid #bfdbfe", dark="1px solid rgba(37,99,235,0.3)"),
                                        ),
                                        rx.vstack(
                                            rx.text("Expediente de Radicación", font_weight="700", font_size="14px", color=text_color),
                                            rx.text(State.solicitud_consultada.get("radicado", ""), font_family="monospace", font_size="14px", color="#2563eb", font_weight="800"),
                                            spacing="0", align_items="start"
                                        ),
                                        spacing="3", align_items="center"
                                    ),
                                    rx.spacer(),
                                    estado_badge(State.solicitud_consultada.get("estado", "")),
                                    width="100%", align_items="center", padding_bottom="4",
                                    border_bottom=rx.color_mode_cond(light="1px solid #e2e8f0", dark="1px solid #334155")
                                ),
                                
                                # Timeline de Estados en Vivo
                                rx.box(
                                    rx.hstack(
                                        timeline_step("Radicada", True, "file-text"),
                                        timeline_connector(State.solicitud_consultada.get("estado") != "Radicada"),
                                        timeline_step(
                                            "En Trámite",
                                            State.solicitud_consultada.get("estado") != "Radicada",
                                            "activity"
                                        ),
                                        timeline_connector(
                                            (State.solicitud_consultada.get("estado") == "Solucionada") |
                                            (State.solicitud_consultada.get("estado") == "Cerrada")
                                        ),
                                        timeline_step(
                                            "Solucionada",
                                            (State.solicitud_consultada.get("estado") == "Solucionada") |
                                            (State.solicitud_consultada.get("estado") == "Cerrada"),
                                            "circle-check"
                                        ),
                                        timeline_connector(State.solicitud_consultada.get("estado") == "Cerrada"),
                                        timeline_step(
                                            "Cerrada",
                                            State.solicitud_consultada.get("estado") == "Cerrada",
                                            "archive"
                                        ),
                                        spacing="0", align_items="center", width="100%"
                                    ),
                                    padding_y="4",
                                    width="100%"
                                ),
                                
                                # Grilla Bento de Atributos
                                rx.grid(
                                    rx.box(
                                        rx.text("Tipo de Solicitud", font_size="11px", color=subtext_color, text_transform="uppercase", font_weight="700", letter_spacing="0.05em"),
                                        rx.text(State.solicitud_consultada.get("tipo_solicitud", ""), font_size="14px", color=text_color, font_weight="600", margin_top="1")
                                    ),
                                    rx.box(
                                        rx.text("Área Responsable", font_size="11px", color=subtext_color, text_transform="uppercase", font_weight="700", letter_spacing="0.05em"),
                                        rx.text(State.solicitud_consultada.get("area_responsable", "Por asignar"), font_size="14px", color=text_color, font_weight="600", margin_top="1")
                                    ),
                                    rx.box(
                                        rx.text("Fecha de Registro", font_size="11px", color=subtext_color, text_transform="uppercase", font_weight="700", letter_spacing="0.05em"),
                                        rx.text(State.solicitud_consultada.get("fecha", ""), font_size="14px", color=text_color, font_weight="500", margin_top="1")
                                    ),
                                    rx.box(
                                        rx.text("Asunto Principal", font_size="11px", color=subtext_color, text_transform="uppercase", font_weight="700", letter_spacing="0.05em"),
                                        rx.text(State.solicitud_consultada.get("asunto", ""), font_size="14px", color=text_color, font_weight="600", margin_top="1")
                                    ),
                                    template_columns={"base": "repeat(1, 1fr)", "sm": "repeat(2, 1fr)"},
                                    gap="4",
                                    width="100%",
                                    bg=inner_card_bg,
                                    p="4",
                                    border_radius="16px",
                                    border=inner_border,
                                ),
                                
                                # Descripción
                                rx.cond(
                                    State.solicitud_consultada.get("descripcion") != "",
                                    rx.vstack(
                                        rx.text("Descripción Detallada", font_weight="700", font_size="12px", color=subtext_color, text_transform="uppercase", letter_spacing="0.05em"),
                                        rx.box(
                                            rx.text(State.solicitud_consultada.get("descripcion", ""), font_size="13px", color=text_color, line_height="1.6"),
                                            bg=inner_card_bg,
                                            border=inner_border,
                                            border_radius="16px",
                                            p="4",
                                            width="100%"
                                        ),
                                        spacing="1", width="100%", align_items="start", margin_top="2"
                                    )
                                ),
                                
                                # Respuesta Oficial del Funcionario
                                rx.cond(
                                    State.solicitud_consultada.get("respuesta") != "",
                                    rx.vstack(
                                        rx.hstack(
                                            rx.icon("message-circle", size=15, color="#10b981"),
                                            rx.text("Respuesta Oficial de la Entidad", font_weight="700", font_size="12px", color="#10b981", text_transform="uppercase", letter_spacing="0.04em"),
                                            spacing="2", align_items="center"
                                        ),
                                        rx.box(
                                            rx.text(State.solicitud_consultada.get("respuesta", ""), font_size="13px", color=text_color, line_height="1.6"),
                                            bg=rx.color_mode_cond(light="#ecfdf5", dark="rgba(16,185,129,0.08)"),
                                            border="1px solid #a7f3d0",
                                            border_left="4px solid #10b981",
                                            border_radius="16px",
                                            p="4",
                                            width="100%",
                                            box_shadow="0 4px 12px -2px rgba(16,185,129,0.12)"
                                        ),
                                        spacing="2", width="100%", align_items="start", margin_top="4"
                                    )
                                ),
                                rx.cond(
                                    State.solicitud_consultada_tiene_adjunto_respuesta,
                                    rx.vstack(
                                        rx.hstack(
                                            rx.icon("paperclip", size=14, color="#10b981"),
                                            rx.text("Anexos de Respuesta del Servidor", font_weight="700", font_size="11px", color="#10b981", text_transform="uppercase"),
                                            spacing="2", align_items="center",
                                        ),
                                        rx.cond(
                                            State.solicitud_consultada_respuesta_adjuntos.length() > 0,
                                            rx.vstack(
                                                rx.foreach(
                                                    State.solicitud_consultada_respuesta_adjuntos,
                                                    lambda doc: rx.vstack(
                                                        rx.cond(
                                                            doc.documento_preview_src != "",
                                                            rx.image(
                                                                src=doc.documento_preview_src,
                                                                alt="Adjunto de respuesta",
                                                                width="100%",
                                                                max_height="120px",
                                                                object_fit="contain",
                                                                border_radius="lg",
                                                                border="1px solid #a7f3d0",
                                                            ),
                                                            rx.box(),
                                                        ),
                                                        ui_boton_descargar_adjunto(
                                                            doc.documento_href,
                                                            doc.documento_adjunto,
                                                            color_scheme="green",
                                                        ),
                                                        spacing="2",
                                                        width="100%",
                                                        align_items="start",
                                                        margin_bottom="2",
                                                    )
                                                ),
                                                spacing="2",
                                                width="100%",
                                            ),
                                            rx.text(
                                                "El archivo ya no está disponible en el servidor",
                                                font_size="xs",
                                                color="#ef4444",
                                            ),
                                        ),
                                        spacing="2", width="100%", align_items="start", margin_top="2",
                                    ),
                                ),
                                # Adjuntos
                                rx.cond(
                                    State.solicitud_consultada.get("documento_adjuntos"),
                                    rx.vstack(
                                        rx.hstack(
                                            rx.icon("paperclip", size=14, color="#3b82f6"),
                                            rx.text("Documentos Radicados", font_weight="700", font_size="11px", color=subtext_color, text_transform="uppercase"),
                                            spacing="2", align_items="center"
                                        ),
                                        rx.vstack(
                                            rx.foreach(
                                                State.solicitud_consultada_adjuntos,
                                                lambda doc: ui_tarjeta_adjunto(doc),
                                            ),
                                            spacing="2", width="100%"
                                        ),
                                        spacing="2", width="100%", align_items="start", margin_top="4"
                                    )
                                ),
                                
                                # Calificación Obligatoria para HU11
                                rx.cond(
                                    (State.solicitud_consultada.get("estado") == "Solucionada") | (State.solicitud_consultada.get("estado") == "Cerrada"),
                                    rx.box(
                                        rx.vstack(
                                            rx.hstack(
                                                rx.icon("star", color="#10b981", size=22),
                                                rx.heading("¡Califica la Atención Recibida!", size="4", color="#10b981", font_weight="700"),
                                                align_items="center", spacing="2"
                                            ),
                                            rx.text("Tu opinión nos ayuda a perfeccionar los tiempos y calidad institucional.", font_size="13px", color=text_color),
                                            rx.text("Nota: Si no calificas en 5 días hábiles, se cerrará con 5 estrellas automáticamente.", font_size="11px", color=subtext_color),
                                            
                                            rx.cond(
                                                State.solicitud_consultada.get("calificacion_servicio") == None,
                                                rx.vstack(
                                                    rx.text_area(
                                                        placeholder="Deja un comentario constructivo sobre la atención (opcional)...",
                                                        value=State.comentario_calificacion,
                                                        on_change=State.set_comentario_calificacion,
                                                        width="100%", size="2", margin_top="2",
                                                        border_radius="12px"
                                                    ),
                                                    rx.vstack(
                                                        rx.select(
                                                            ["5 - Excelente", "4 - Muy Bueno", "3 - Bueno", "2 - Regular", "1 - Malo"],
                                                            placeholder="Selecciona una calificación",
                                                            on_change=State.set_calificacion_opcion,
                                                            size="3", radius="large", width="100%"
                                                        ),
                                                        rx.button(
                                                            "Enviar Calificación",
                                                            on_click=State.enviar_calificacion,
                                                            color_scheme="green", size="3", radius="full", width="100%",
                                                            style={"cursor": "pointer", "fontWeight": "700"}
                                                        ),
                                                        width="100%", margin_top="2", spacing="3"
                                                    ),
                                                    width="100%"
                                                ),
                                                rx.text(f"Ya calificaste este servicio con {State.solicitud_consultada.get('calificacion_servicio')} estrella(s). ¡Gracias por tu tiempo!", color="green.600", font_weight="bold", margin_top="2")
                                            ),
                                            rx.cond(
                                                State.calificacion_mensaje,
                                                rx.text(State.calificacion_mensaje, color="blue.500", font_size="sm", font_weight="medium", margin_top="2")
                                            ),
                                            align_items="start",
                                            spacing="2",
                                            width="100%"
                                        ),
                                        p="5",
                                        border="1px solid #6ee7b7",
                                        bg=rx.color_mode_cond(light="#ecfdf5", dark="rgba(16,185,129,0.08)"),
                                        border_radius="18px",
                                        width="100%",
                                        margin_y="5",
                                        box_shadow="0 6px 18px -4px rgba(16, 185, 129, 0.15)"
                                    )
                                ),

                                # Bitácora de Trazabilidad
                                rx.box(
                                    rx.vstack(
                                        rx.hstack(
                                            rx.icon("git-commit-horizontal", size=15, color="#8b5cf6"),
                                            rx.text("Bitácora Oficial de Seguimiento", font_size="13px", font_weight="700", color=text_color),
                                            rx.badge("Auditoría", color_scheme="purple", variant="soft", size="1"),
                                            spacing="2",
                                            align_items="center",
                                            width="100%",
                                        ),
                                        rx.cond(
                                            State.historial_solicitud.length() > 0,
                                            rx.vstack(
                                                rx.foreach(
                                                    State.historial_solicitud,
                                                    lambda h: rx.box(
                                                        rx.vstack(
                                                            rx.hstack(
                                                                rx.badge(h["estado_anterior"], color_scheme="gray", variant="surface", size="1"),
                                                                rx.icon("arrow-right", size=10, color=subtext_color),
                                                                rx.badge(h["estado_nuevo"], color_scheme="purple", variant="surface", size="1"),
                                                                rx.spacer(),
                                                                rx.text(h["fecha_cambio"], font_size="2xs", color=subtext_color, font_weight="500"),
                                                                width="100%",
                                                                align_items="center",
                                                            ),
                                                            rx.cond(
                                                                h["area_asignada"] != "",
                                                                rx.text(h["area_asignada"], font_size="2xs", color="#f59e0b", font_weight="700"),
                                                                rx.box(),
                                                            ),
                                                            rx.cond(
                                                                h["observaciones"] != "",
                                                                rx.text(
                                                                    h["observaciones"],
                                                                    font_size="xs",
                                                                    color=text_color,
                                                                    white_space="pre-wrap",
                                                                    line_height="1.5",
                                                                ),
                                                                rx.box(),
                                                            ),
                                                            rx.cond(
                                                                h["documento_adjunto"] != "",
                                                                ui_tarjeta_adjunto_historial(h),
                                                                rx.box(),
                                                            ),
                                                            spacing="1",
                                                            width="100%",
                                                            align_items="start",
                                                        ),
                                                        p="3.5",
                                                        border=inner_border,
                                                        border_left="3px solid #8b5cf6",
                                                        border_radius="12px",
                                                        bg=inner_card_bg,
                                                        width="100%",
                                                    ),
                                                ),
                                                spacing="3",
                                                width="100%",
                                                max_height="240px",
                                                overflow_y="auto",
                                            ),
                                            rx.center(
                                                rx.text("No hay eventos registrados en bitácora aún.", font_size="xs", color=subtext_color),
                                                p="4",
                                                width="100%",
                                            ),
                                        ),
                                        spacing="3",
                                        width="100%",
                                        align_items="start",
                                    ),
                                    p="4",
                                    border=inner_border,
                                    border_radius="16px",
                                    margin_top="3",
                                    width="100%",
                                ),

                                spacing="4",
                                align_items="start",
                                width="100%"
                            ),
                            width="100%",
                            margin_top="3",
                            animation="fadeIn 0.4s cubic-bezier(0.16, 1, 0.3, 1)"
                        )
                    ),
                    
                    spacing="0",
                    align_items="start",
                    width="100%"
                ),
                bg=card_bg,
                backdrop_filter="blur(24px)",
                border=card_border,
                border_radius="28px",
                box_shadow=rx.color_mode_cond(
                    light="0 25px 60px -15px rgba(15, 23, 42, 0.08), 0 0 1px 1px rgba(255,255,255,0.7) inset",
                    dark="0 25px 60px -15px rgba(0, 0, 0, 0.7)"
                ),
                width="100%",
                max_width="780px",
                p={"base": "6", "md": "8"},
                margin_y="10",
                style={
                    "@keyframes fadeIn": {
                        "from": {"opacity": "0", "transform": "translateY(12px)"},
                        "to": {"opacity": "1", "transform": "translateY(0)"}
                    }
                }
            ),
            size="3",
            width="100%",
            padding_x="4"
        ),
        bg=rx.color_mode_cond(
            light="linear-gradient(180deg, #f1f5f9 0%, #e2e8f0 100%)", 
            dark="linear-gradient(180deg, #0b1120 0%, #020617 100%)"
        ),
        min_height="100vh",
        width="100%"
    )
