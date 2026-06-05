from app.services.ai_service import AIService

text = "Сегодня в Алматы прошёл технологический форум."

result = AIService.process_news(
    title=text,
    content=text,
    source_lang='ru'
)

print(result)