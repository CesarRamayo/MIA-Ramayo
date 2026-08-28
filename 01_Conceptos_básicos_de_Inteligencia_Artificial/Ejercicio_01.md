md_content = """# Ejercicio 01 — Aplicaciones de IA que uso o he usado

## Gemini IA
**Uso:** Esta IA la utilizo actualmente para todo tipo de ayuda, principalmente, para resolver cualquier tipo de pregunta, duda o investigación acerca de un tema en específico. Incluso llegando a usarla para dudas de tipo personal. 

**Áreas de aplicación:**
1. Universidad y proyectos de ingeniería.
2. Mi negocio (taller tipo cerrajería automotriz).
3. Mantenimiento y reparación de hardware.
4. Dudas y conversaciones de tipo general e incluso de tipo personal.

---

## Chat GPT
**Uso:** Antes de utilizar Gemini como IA principal, utilizaba Chat GPT, en su versión gratuita. Para exactamente lo mismo que uso a Gemini, es decir para ayuda general, desde código, reportes y tareas para la universidad, hasta dudas personales.
"""

file_path = '/mnt/data/ejercicio_01_aplicaciones_ia.md'
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(md_content)
    
print(f"File generated at: {file_path}")
