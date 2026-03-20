TEMPLATE_BASE = [
    # Semana 1 - Onboarding
    {"nombre": "Onboarding Pusher Coach", "rol": "pusher_coach", "semana": 1},
    {"nombre": "Envío de mensaje post onboarding (Pusher Coach)", "rol": "pusher_coach", "semana": 1},
    {"nombre": "Onboarding COO", "rol": "coo", "semana": 1},
    {"nombre": "Envío de mensaje post onboarding (COO)", "rol": "coo", "semana": 1},
    {"nombre": "Creación grupo Whatsapp/Slack", "rol": "account_manager", "semana": 1},
    {"nombre": "Agendamiento de llamadas", "rol": "coo", "semana": 1},
    # Semana 2 - Altas y credenciales
    {"nombre": "Alta SN", "rol": "coo", "semana": 2},
    {"nombre": "Credenciales LinkedIn", "rol": "coo", "semana": 2},
    {"nombre": "Alta Lemlist", "rol": "coo", "semana": 2},
    {"nombre": "Credenciales Lemlist", "rol": "coo", "semana": 2},
    {"nombre": "Entrevista de contenido", "rol": "copy", "semana": 2},
    {"nombre": "Lista de ampliación de red", "rol": "automater", "semana": 2},
    {"nombre": "Comienzo ampliación de red", "rol": "automater", "semana": 2},
    # Semana 3 - Propuestas y setup
    {"nombre": "Propuesta de mejora de perfil", "rol": "copy", "semana": 3},
    {"nombre": "Propuesta de ideas para posteos", "rol": "copy", "semana": 3},
    {"nombre": "Reunión estrategia comercial", "rol": "account_manager", "semana": 3},
    {"nombre": "Envío informe matriz de prospección", "rol": "account_manager", "semana": 3},
    {"nombre": "Reunión de automatizaciones", "rol": "automater", "semana": 3},
    {"nombre": "Lemlist pago", "rol": "automater", "semana": 3},
    {"nombre": "Conexión email a Lemlist", "rol": "automater", "semana": 3},
    {"nombre": "Armado búsqueda para FCA", "rol": "sdr", "semana": 3},
    {"nombre": "Envío csv para FCA", "rol": "automater", "semana": 3},
    {"nombre": "Limpieza csv para FCA", "rol": "automater", "semana": 3},
    # Semana 4 - Validaciones e implementación
    {"nombre": "Validación de mejora de perfil", "rol": "copy", "semana": 4},
    {"nombre": "Implementación de mejora de perfil", "rol": "sdr", "semana": 4},
    {"nombre": "Validación de ideas para posteos", "rol": "copy", "semana": 4},
    {"nombre": "Propuesta de posteos", "rol": "copy", "semana": 4},
    {"nombre": "Integración Lemlist-CRM", "rol": "automater", "semana": 4},
    {"nombre": "Integración Lemlist-OpenAI", "rol": "automater", "semana": 4},
    {"nombre": "Integración Lemlist-Looker", "rol": "automater", "semana": 4},
    {"nombre": "Armado blacklist", "rol": "sdr", "semana": 4},
    # Semana 5 - Posteos
    {"nombre": "Validación de posteos", "rol": "copy", "semana": 5},
    {"nombre": "Lanzamiento posteo 1", "rol": "sdr", "semana": 5},
    # Semana 6-8 - Posteos restantes
    {"nombre": "Lanzamiento posteo 2", "rol": "sdr", "semana": 6},
    {"nombre": "Lanzamiento posteo 3", "rol": "sdr", "semana": 7},
    {"nombre": "Lanzamiento posteo 4", "rol": "sdr", "semana": 8},
    # Semana 7 - Encuesta
    {"nombre": "Envío de encuesta de satisfacción", "rol": "pusher_coach", "semana": 7},
]

TEMPLATES_CAMPANA = {
    "campana_normal": [
        {"nombre": "Propuesta de prospecting canvas", "rol": "account_manager", "offset": 0},
        {"nombre": "Validación de prospecting canvas", "rol": "account_manager", "offset": 1},
        {"nombre": "Propuesta de prospección de cuentas", "rol": "sdr", "offset": 1},
        {"nombre": "Validación de prospección de cuentas", "rol": "account_manager", "offset": 1},
        {"nombre": "Propuesta de secuencia de mensajes", "rol": "copy", "offset": 1},
        {"nombre": "Prospección de leads", "rol": "sdr", "offset": 2},
        {"nombre": "Validación de secuencia de mensajes", "rol": "copy", "offset": 2},
        {"nombre": "Automatización conexiones Lemlist", "rol": "automater", "offset": 2},
        {"nombre": "Automatización mensajes Lemlist", "rol": "automater", "offset": 3},
        {"nombre": "Informe de resultados", "rol": "account_manager", "offset": 4},
    ],
    "sales_pilot": [
        {"nombre": "Prospección de cuentas SP", "rol": "sdr", "offset": 1},
        {"nombre": "Cargar a Lemlist SP", "rol": "sdr", "offset": 2},
        {"nombre": "Automatización Lemlist SP", "rol": "automater", "offset": 2},
        {"nombre": "Informe de resultados SP", "rol": "account_manager", "offset": 4},
    ],
    "evento": [
        {"nombre": "Propuesta de prospección de cuentas", "rol": "sdr", "offset": 0},
        {"nombre": "Validación de prospección de cuentas", "rol": "account_manager", "offset": 1},
        {"nombre": "Prospección de leads", "rol": "sdr", "offset": 1},
        {"nombre": "Propuesta de secuencia de mensajes", "rol": "copy", "offset": 1},
        {"nombre": "Validación de secuencia de mensajes", "rol": "copy", "offset": 2},
        {"nombre": "Automatización conexiones Lemlist", "rol": "automater", "offset": 2},
        {"nombre": "Automatización mensajes Lemlist", "rol": "automater", "offset": 3},
        {"nombre": "Informe de resultados", "rol": "account_manager", "offset": 4},
    ],
}

CAMPANAS_INICIALES = [3, 7, 11]

EQUIPO_REGROW = {
    "pusher_coach": [
        "clg@regrow.academy",
    ],
    "account_manager": [
        "mb@regrow.agency",
        "rg@regrow.agency",
        "mgr@regrow.academy",
    ],
    "copy": [
        "dm@regrow.academy",
    ],
    "sdr": [
        "ar@regrow.agency",
        "mg@regrow.agency",
        "ml@regrow.agency",
    ],
    "automater": [
        "tf@regrow.agency",
    ],
    "coo": [
        "fv@regrow.academy",
    ],
}