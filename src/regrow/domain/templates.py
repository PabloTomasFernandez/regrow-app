from dataclasses import dataclass


@dataclass(frozen=True)
class TaskTemplate:
    name: str
    role: str
    week: int


@dataclass(frozen=True)
class CampaignTaskTemplate:
    name: str
    role: str
    week_offset: int


BASE_TASKS: list[TaskTemplate] = [
    TaskTemplate("Onboarding Pusher Coach", "pusher", 1),
    TaskTemplate("Envío de mensaje post onboarding (Pusher Coach)", "pusher", 1),
    TaskTemplate("Onboarding COO", "coo", 1),
    TaskTemplate("Envío de mensaje post onboarding (COO)", "coo", 1),
    TaskTemplate("Creación grupo Whatsapp/Slack", "account_manager", 1),
    TaskTemplate("Agendamiento de llamadas", "coo", 1),
    TaskTemplate("Alta SN", "coo", 2),
    TaskTemplate("Credenciales LinkedIn", "coo", 2),
    TaskTemplate("Alta Lemlist", "coo", 2),
    TaskTemplate("Credenciales Lemlist", "coo", 2),
    TaskTemplate("Entrevista de contenido", "copy", 2),
    TaskTemplate("Lista de ampliación de red", "automater", 2),
    TaskTemplate("Comienzo ampliación de red", "automater", 2),
    TaskTemplate("Propuesta de mejora de perfil", "copy", 3),
    TaskTemplate("Propuesta de ideas para posteos", "copy", 3),
    TaskTemplate("Reunión estrategia comercial", "account_manager", 3),
    TaskTemplate("Envío informe matriz de prospección", "account_manager", 3),
    TaskTemplate("Reunión de automatizaciones", "automater", 3),
    TaskTemplate("Lemlist pago", "automater", 3),
    TaskTemplate("Conexión email a Lemlist", "automater", 3),
    TaskTemplate("Armado búsqueda para FCA", "sdr", 3),
    TaskTemplate("Envío csv para FCA", "automater", 3),
    TaskTemplate("Limpieza csv para FCA", "automater", 3),
    TaskTemplate("Validación de mejora de perfil", "copy", 4),
    TaskTemplate("Implementación de mejora de perfil", "sdr", 4),
    TaskTemplate("Validación de ideas para posteos", "copy", 4),
    TaskTemplate("Propuesta de posteos", "copy", 4),
    TaskTemplate("Integración Lemlist-CRM", "automater", 4),
    TaskTemplate("Integración Lemlist-OpenAI", "automater", 4),
    TaskTemplate("Integración Lemlist-Looker", "automater", 4),
    TaskTemplate("Armado blacklist", "sdr", 4),
    TaskTemplate("Validación de posteos", "copy", 5),
    TaskTemplate("Lanzamiento posteo 1", "sdr", 5),
    TaskTemplate("Lanzamiento posteo 2", "sdr", 6),
    TaskTemplate("Lanzamiento posteo 3", "sdr", 7),
    TaskTemplate("Lanzamiento posteo 4", "sdr", 8),
    TaskTemplate("Envío de encuesta de satisfacción", "pusher", 7),
]

CAMPAIGN_NORMAL: list[CampaignTaskTemplate] = [
    CampaignTaskTemplate("Propuesta de prospecting canvas", "account_manager", 0),
    CampaignTaskTemplate("Validación de prospecting canvas", "account_manager", 1),
    CampaignTaskTemplate("Propuesta de prospección de cuentas", "sdr", 1),
    CampaignTaskTemplate("Validación de prospección de cuentas", "account_manager", 1),
    CampaignTaskTemplate("Propuesta de secuencia de mensajes", "copy", 1),
    CampaignTaskTemplate("Prospección de leads", "sdr", 2),
    CampaignTaskTemplate("Validación de secuencia de mensajes", "copy", 2),
    CampaignTaskTemplate("Automatización conexiones Lemlist", "automater", 2),
    CampaignTaskTemplate("Automatización mensajes Lemlist", "automater", 3),
    CampaignTaskTemplate("Informe de resultados", "account_manager", 4),
]

CAMPAIGN_SALES_PILOT: list[CampaignTaskTemplate] = [
    CampaignTaskTemplate("Prospección de cuentas SP", "sdr", 1),
    CampaignTaskTemplate("Cargar a Lemlist SP", "sdr", 2),
    CampaignTaskTemplate("Automatización Lemlist SP", "automater", 2),
    CampaignTaskTemplate("Informe de resultados SP", "account_manager", 4),
]

CAMPAIGN_EVENTO: list[CampaignTaskTemplate] = [
    CampaignTaskTemplate("Propuesta de prospección de cuentas", "sdr", 0),
    CampaignTaskTemplate("Validación de prospección de cuentas", "account_manager", 1),
    CampaignTaskTemplate("Prospección de leads", "sdr", 1),
    CampaignTaskTemplate("Propuesta de secuencia de mensajes", "copy", 1),
    CampaignTaskTemplate("Validación de secuencia de mensajes", "copy", 2),
    CampaignTaskTemplate("Automatización conexiones Lemlist", "automater", 2),
    CampaignTaskTemplate("Automatización mensajes Lemlist", "automater", 3),
    CampaignTaskTemplate("Informe de resultados", "account_manager", 4),
]

CAMPAIGN_START_WEEKS: list[int] = [3, 7, 11]

# Relación de campañas:
# - Al activar, se crean 3 campañas iniciales (semanas 3, 7, 11)
# - Se pueden agregar más campañas después bajo demanda
# - Cada campaña es "normal" o "evento"
# - Una campaña normal puede tener un Sales Pilot como sub-campaña
# - Nomenclatura SP: "{nombre tarea} - Campaña {numero_campana_padre}"