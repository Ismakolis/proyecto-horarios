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
    Prompt simplificado: la IA solo decide qué docente va con qué asignatura.
    El sistema se encarga de asignar días y horas sin choques.
    """
    carrera     = contexto["carrera"]
    modulo_num  = contexto["modulo_numero"]
    asignaturas = contexto["asignaturas"]
    docentes    = contexto["docentes"]

    asig_txt = "\n".join([
        f"  - ID: {a['id']} | {a['nombre']} | Nivel {a['nivel_numero']} | Paralelo {a['paralelo']} | Jornada: {a['jornada']}"
        for a in asignaturas
    ])

    def fmt_doc(d):
        ocupados = d.get("horarios_ya_asignados", [])
        cupo = 3 - d["asignaturas_actuales"]
        return (
            f"  - ID: {d['id']} | {d['nombre']} | {d['tipo']} | "
            f"Cupo disponible: {cupo}/3"
        )
    doc_txt = "\n".join([fmt_doc(d) for d in docentes if d["asignaturas_actuales"] < 3])

    return f"""Eres un coordinador academico. Tu unica tarea es asignar un docente a cada asignatura.

CARRERA: {carrera} | MODULO: {modulo_num}

ASIGNATURAS (necesitan un docente):
{asig_txt}

DOCENTES DISPONIBLES (con cupo):
{doc_txt}

REGLAS:
1. Cada docente puede recibir MAXIMO {3} asignaturas en total.
2. Distribuye equitativamente — no asignes todo al mismo docente.
3. Usa solo IDs exactos de las listas anteriores.

Devuelve SOLO este JSON, sin texto adicional:

{{
  "asignaciones": [
    {{
      "asignatura_id": "id-exacto-de-la-lista",
      "docente_id": "id-exacto-del-docente"
    }}
  ],
  "resumen": "breve descripcion de la distribucion"
}}

Una entrada por cada asignatura. Total esperado: {len(asignaturas)} asignaciones."""


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