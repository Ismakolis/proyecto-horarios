"""
ia_service.py
Servicio de integracion con Groq (LLaMA 3) para sugerencia inteligente de horarios.
Groq es gratuito y ultrarapido. Requiere GROQ_API_KEY en el archivo .env
Obtener API key gratis en: console.groq.com
"""

import os
import json
import httpx
from fastapi import HTTPException


GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL   = "llama-3.3-70b-versatile"


def _get_api_key() -> str:
    key = os.getenv("GROQ_API_KEY", "")
    if not key:
        raise HTTPException(
            status_code=503,
            detail="API de IA no configurada. Agrega GROQ_API_KEY en el archivo .env — obtén tu clave gratis en console.groq.com"
        )
    return key


def _construir_prompt(contexto: dict) -> str:
    """
    Construye el prompt con todo el contexto del instituto para enviarlo a Groq.
    """
    carrera    = contexto["carrera"]
    modulo_num = contexto["modulo_numero"]
    asignaturas = contexto["asignaturas"]
    docentes    = contexto["docentes"]
    dias        = ["lunes", "martes", "miercoles", "jueves", "viernes"]

    asig_txt = "\n".join([
        f"  - ID: {a['id']} | Nombre: {a['nombre']} | Nivel: {a['nivel_numero']} | "
        f"Paralelo: {a['paralelo']} | Horas modulo: {a['horas_modulo']}h"
        for a in asignaturas
    ])

    doc_txt = "\n".join([
        f"  - ID: {d['id']} | Nombre: {d['nombre']} | Tipo: {d['tipo']} | "
        f"Asignaturas ya asignadas este modulo: {d['asignaturas_actuales']}/3 | "
        f"Disponibilidad: {', '.join(d['disponibilidad']) if d['disponibilidad'] else 'todos los dias'}"
        for d in docentes
    ])

    return f"""Eres un asistente especializado en planificacion academica para institutos tecnologicos.

Debes generar una distribucion optima de horarios para el siguiente contexto:

CARRERA: {carrera}
MODULO: {modulo_num}
DIAS DISPONIBLES: {', '.join(dias)}

ASIGNATURAS A DISTRIBUIR (cada una necesita un docente, dia y hora):
{asig_txt}

DOCENTES DISPONIBLES:
{doc_txt}

REGLAS OBLIGATORIAS — DEBES CUMPLIRLAS TODAS SIN EXCEPCION:
1. Cada docente puede tener MAXIMO 3 asignaturas en este modulo en total.
2. CHOQUE DE DOCENTE: Un mismo docente NO puede tener DOS asignaturas con el mismo dia Y la misma hora_inicio. Si el docente ya tiene una asignacion en "lunes 08:00", la siguiente debe ir en otro dia O en otra hora.
3. CHOQUE DE PARALELO: Un mismo paralelo de un nivel NO puede tener DOS asignaturas con el mismo dia Y la misma hora_inicio. Cada paralelo debe tener sus clases en dias u horas distintas.
4. Jornada MATUTINA — combinaciones validas unicamente:
   - hora_inicio "08:00" con hora_fin "10:00"
   - hora_inicio "10:00" con hora_fin "12:00"
5. Jornada NOCTURNA — combinaciones validas unicamente:
   - hora_inicio "18:30" con hora_fin "20:00"
   - hora_inicio "20:00" con hora_fin "21:30"
6. Distribuye dias de forma variada — usa lunes, martes, miercoles, jueves y viernes, no pongas todo el mismo dia.
7. Distribuye docentes de forma equitativa — no asignes todas las materias al mismo docente.
8. Alterna las horas — no pongas todas las asignaturas a las 08:00, usa tambien 10:00, 18:30 y 20:00.

PROCESO QUE DEBES SEGUIR:
- Para cada asignatura, antes de asignarla verifica que el docente elegido NO tenga ya una asignacion en ese mismo dia y hora.
- Para cada asignatura, verifica que el paralelo NO tenga ya una asignacion en ese mismo dia y hora.
- Si hay choque, cambia el dia o la hora hasta encontrar un slot libre.

Devuelve UNICAMENTE un JSON valido con esta estructura exacta, sin texto adicional, sin markdown, sin explicaciones:

{{
  "asignaciones": [
    {{
      "asignatura_id": "uuid-de-la-asignatura",
      "docente_id": "uuid-del-docente",
      "dia": "lunes",
      "jornada": "matutina",
      "hora_inicio": "08:00",
      "hora_fin": "10:00"
    }}
  ],
  "resumen": "Breve descripcion de la estrategia de distribucion usada"
}}

Genera una asignacion para CADA asignatura listada. Solo JSON, nada mas."""


async def solicitar_sugerencia_ia(contexto: dict) -> dict:
    """
    Llama a la API de Groq con el contexto del modulo y retorna el plan de horarios sugerido.
    """
    api_key = _get_api_key()
    prompt  = _construir_prompt(contexto)

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {
                "role": "system",
                "content": "Eres un experto en planificacion academica. Respondes UNICAMENTE con JSON valido, sin markdown ni explicaciones."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.2,
        "max_tokens": 4096,
    }

    headers = {
        "Content-Type":  "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(GROQ_API_URL, json=payload, headers=headers)

        if response.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail=f"Error en la API de IA: {response.status_code} - {response.text[:200]}"
            )

        data  = response.json()
        texto = data["choices"][0]["message"]["content"].strip()

        # Limpiar markdown por si acaso
        if texto.startswith("```"):
            lines = texto.split("\n")
            texto = "\n".join(lines[1:-1])

        plan = json.loads(texto)

        if "asignaciones" not in plan:
            raise ValueError("Respuesta de IA sin campo 'asignaciones'")

        return plan

    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=502,
            detail=f"La IA devolvio una respuesta no valida (JSON invalido): {str(e)}"
        )
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="Tiempo de espera agotado al contactar la API de IA. Intenta de nuevo."
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error inesperado al contactar la IA: {str(e)}"
        )
