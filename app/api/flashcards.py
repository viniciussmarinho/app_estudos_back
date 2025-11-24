from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
import httpx
import json
from ..database import get_db
from ..models.user import User
from ..utils.dependencies import get_current_active_user
from ..config import settings

router = APIRouter()

# Schemas
class FlashcardRequest(BaseModel):
    subject: str
    topic: str = ""
    count: int = 20
    
    class Config:
        json_schema_extra = {
            "example": {
                "subject": "Cálculo I",
                "topic": "Limites e Derivadas",
                "count": 20
            }
        }

class Flashcard(BaseModel):
    question: str
    answer: str

class FlashcardResponse(BaseModel):
    subject: str
    flashcards: List[Flashcard]

async def generate_flashcards_with_llm(subject: str, topic: str = None, count: int = 20) -> List[dict]:
    """
    Gera flashcards usando a API da OpenAI (ou outro LLM)
    Você precisará configurar a API key no .env
    """
    
    print(f"Gerando flashcards para: {subject}, tópico: {topic}, quantidade: {count}")
    
    # Montar o prompt
    if topic:
        prompt = f"""Crie exatamente {count} flashcards educacionais sobre {subject}, focando especificamente em: {topic}.

Cada flashcard deve ter:
- Uma pergunta clara e direta
- Uma resposta concisa e precisa

Formate sua resposta como um JSON array com objetos contendo 'question' e 'answer'.

Exemplo de formato esperado:
[
  {{"question": "O que é...?", "answer": "É..."}},
  {{"question": "Como funciona...?", "answer": "Funciona através de..."}}
]

Agora crie os {count} flashcards:"""
    else:
        prompt = f"""Crie exatamente {count} flashcards educacionais sobre {subject}.

Cada flashcard deve ter:
- Uma pergunta clara e direta
- Uma resposta concisa e precisa

Formate sua resposta como um JSON array com objetos contendo 'question' e 'answer'.

Exemplo de formato esperado:
[
  {{"question": "O que é...?", "answer": "É..."}},
  {{"question": "Como funciona...?", "answer": "Funciona através de..."}}
]

Agora crie os {count} flashcards:"""

    try:        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.groq_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {"role": "system", "content": "Você é um professor especializado em criar flashcards educacionais."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 2000
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data['choices'][0]['message']['content']
                
                # Extrair JSON da resposta
                content = content.strip()
                if content.startswith('```json'):
                    content = content[7:]
                if content.startswith('```'):
                    content = content[3:]
                if content.endswith('```'):
                    content = content[:-3]
                
                flashcards = json.loads(content.strip())
                print(f"Flashcards gerados via Groq: {len(flashcards)}")
                return flashcards
        
        
        # Opção 2: Mock data para testes
        # Flashcards gerados localmente para testes
        """print(f"Gerando {count} flashcards mock...")
        flashcards = []
        
        topic_text = f" - {topic}" if topic else ""
        
        for i in range(min(count, 50)):
            flashcards.append({
                "question": f"Pergunta {i+1} sobre {subject}{topic_text}: Qual é um conceito importante?",
                "answer": f"Resposta {i+1}: Esta é uma explicação detalhada sobre um conceito fundamental de {subject}{topic_text}. É importante compreender este tópico para avançar nos estudos."
            })
        
        print(f"Flashcards gerados com sucesso: {len(flashcards)}")
        return flashcards"""
        
    except Exception as e:
        print(f"Erro ao gerar flashcards: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao gerar flashcards: {str(e)}"
        )

@router.post("/generate", response_model=FlashcardResponse)
async def generate_flashcards(
    request: FlashcardRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Gera flashcards usando IA"""
    
    if request.count < 1 or request.count > 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O número de flashcards deve estar entre 1 e 50"
        )
    
    # Converter string vazia para None
    topic = request.topic if request.topic else None
    
    flashcards = await generate_flashcards_with_llm(
        subject=request.subject,
        topic=topic,
        count=request.count
    )
    
    return {
        "subject": request.subject,
        "flashcards": flashcards
    }