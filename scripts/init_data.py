# scripts/init_data.py
"""Script para inicializar dados padrão no banco de dados"""

import sys
import os

# Adicionar o diretório do app ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database import SessionLocal
from app.models.user import EventType

def init_event_types():
    """Inicializa os tipos de eventos padrão"""
    db = SessionLocal()
    try:
        # Verificar se os tipos já existem
        existing_types = db.query(EventType).count()
        if existing_types > 0:
            print("Tipos de eventos já existem no banco de dados.")
            return

        # Criar tipos de eventos padrão
        event_types = [
            EventType(name="Prova", default_reminder_days=7, color="#EF4444"),
            EventType(name="Entrega", default_reminder_days=3, color="#F59E0B"),
            EventType(name="Renovação", default_reminder_days=2, color="#10B981"),
            EventType(name="Compromisso", default_reminder_days=1, color="#8B5CF6"),
            EventType(name="Outro", default_reminder_days=1, color="#6B7280")
        ]

        for event_type in event_types:
            db.add(event_type)
        
        db.commit()
        print("Tipos de eventos criados com sucesso!")

    except Exception as e:
        print(f"Erro ao criar tipos de eventos: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Inicializando dados padrão...")
    init_event_types()
    print("Concluído!")