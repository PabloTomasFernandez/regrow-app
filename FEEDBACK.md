# FEEDBACK.md — Regrow App

Archivo vivo para capturar feedback real de uso de la app.
Cada item se cierra cuando se resuelve o se descarta.

## Cómo usar este archivo

- Cada vez que encontrés algo raro, confuso, o que falta → anotalo acá
- Cuando el equipo te diga algo sobre la app → anotalo acá
- Priorizá por impacto (cuántas personas lo sufren, cuánto tiempo pierden)
- Cuando migremos a Reflex, este archivo define el diseño de la V2

## Formato

```
### [CATEGORIA] Título corto
- **Fecha**: 2026-04-16
- **Reportado por**: Pablo (uso personal) / Rodrigo / Loli / etc
- **Severidad**: 🔴 Crítico / 🟠 Alto / 🟡 Medio / 🟢 Bajo
- **Contexto**: qué estabas haciendo cuando encontraste esto
- **Problema**: descripción concreta
- **Solución propuesta**: (opcional) cómo se resolvería
- **Estado**: 🆕 nuevo / 🛠️ en progreso / ✅ resuelto / ❌ descartado
```

---

## Feedback abierto

### [UX] Al elegir SDR en crear proyecto, mostraba todos los miembros
- **Fecha**: 2026-04-16
- **Reportado por**: Pablo
- **Severidad**: 🟠 Alto
- **Contexto**: Crear un nuevo proyecto y asignar el SDR del equipo
- **Problema**: El selectbox traía todos los miembros, no solo los con rol=SDR
- **Solución propuesta**: Filtrar por rol específico con checkbox "mostrar todos" opcional
- **Estado**: 🛠️ en progreso (branch fix/team-reassignment)

### [FEATURE] Gestión de alta/baja de equipo
- **Fecha**: 2026-04-16
- **Reportado por**: Pablo
- **Severidad**: 🟠 Alto
- **Contexto**: Entra alguien nuevo al equipo o se va
- **Problema**: No había forma de agregar miembros sin tocar el seed
- **Solución propuesta**: Página Equipo con CRUD + bulk replace al desactivar
- **Estado**: ✅ resuelto

### [BUG] Tareas de campañas no se muestran
- **Fecha**: 2026-04-16
- **Reportado por**: Pablo
- **Severidad**: 🔴 Crítico
- **Contexto**: Abro el panel de tareas de un proyecto
- **Problema**: Solo aparecen las tareas base, las de las 3 campañas no
- **Solución propuesta**: Al activar, auto-crear 3 campañas y generar sus tareas
- **Estado**: 🆕 nuevo

### [FEATURE] Eliminar/editar empresas, clientes, proyectos
- **Fecha**: 2026-04-16
- **Reportado por**: Pablo
- **Severidad**: 🟡 Medio
- **Contexto**: Creé algo por error y no puedo modificarlo
- **Problema**: Las páginas son solo "crear + ver", falta editar/eliminar
- **Estado**: 🆕 nuevo

### [FEATURE] Comentarios en tareas
- **Fecha**: 2026-04-16
- **Reportado por**: Pablo
- **Severidad**: 🟡 Medio
- **Contexto**: Quiero dejar contexto sobre una tarea específica
- **Problema**: La tabla CommentDB existe en el diseño pero no está implementada
- **Solución propuesta**: Click en tarea → panel lateral con comentarios
- **Estado**: 🆕 nuevo

---

## Ideas del equipo (cuando las compartan)

_Acá van ideas/sugerencias que surgen en conversaciones con el equipo._

---

## Preguntas para investigar

_Cosas que no está claro cómo resolver y hay que pensar._

- ¿Cómo deberían validar los clientes los copys? ¿Siguen en Google Docs o meter algo en la app?
- ¿Notificaciones en Slack al cambiar estados de campaña? ¿Cuáles disparan alerta?
- ¿Quién cambia el status de un BP: copy, cliente, o ambos?
- ¿Tenemos que guardar los mensajes de Lemlist en la app o solo el lemlist_campaign_id?

---

## Métricas a trackear (cuando haya uso real)

- [ ] ¿Cuántos proyectos tiene cada miembro asignado?
- [ ] ¿Cuánto tarda un proyecto en pasar de activo a completado?
- [ ] ¿Cuántas tareas se completan a tiempo vs vencidas?
- [ ] ¿Cuál es el tiempo promedio de validación por BP?