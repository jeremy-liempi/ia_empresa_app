# logic/ai_utils.py

def sugerir_metodologia_y_equipo(descripcion, ubicacion, presupuesto, empleados):
    """
    Función dummy para simular sugerencias de metodología y equipo.
    Parámetros:
      - descripcion: str
      - ubicacion: str
      - presupuesto: int o float
      - empleados: list de dicts con datos de empleados
    
    Retorna:
      - str con sugerencia simulada
    """
    return (
        f"Sugerencia para proyecto en **{ubicacion}** con presupuesto **{presupuesto:,} CLP**:\n\n"
        "1. **Metodología Recomendada**: Ágil (Scrum con sprints de 2 semanas).\n"
        "2. **Equipo Mínimo**:\n"
        "   - Líder de proyecto (1)\n"
        "   - Desarrolladores Full-Stack (2)\n"
        "   - QA / Tester (1)\n"
        "   - Analista de datos (1)\n\n"
        "_Esta es una respuesta simulada mientras desarrollas la lógica real de IA._"
    )

