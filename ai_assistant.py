"""
AI Assistant Module - Google Gemini Integration
"""

import os
import asyncio
from typing import List

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')

FALLBACK_RESPONSES = {
    'shipping': "Доставката се извършва до 3-5 работни дни. Таксата за доставка е 5.99 лв., а за поръчки над 80 лв. е безплатна!",
    'return': "Имате право да върнете продукт в 14-дневен срок от получаване, при условие че е неизползван и в оригиналната опаковка.",
    'ingredients': "Нашите продукти се правят само с естествени съставки - без парабени, без сулфати и без изкуствени аромати!",
    'vegan': "Да, всички наши продукти са 100% веган и не са тествани върху животни!",
    'gift': "Предлагаме луксозни комплекти и опция за персонален поздрав. Посетете нашите 'Сетове' в магазина.",
    'organic': "Повечето ни съставки са сертифицирани био. За конкретен продукт проверете описанието му.",
    'contact': "Можете да се свържете с нас на: hello@beigebeauty.com или на телефон: 0888 123 456",
    'order_status': "За да проверите статуса на поръчката си, влезте в профила и отидете на 'Поръчки'.",
    'discount': "Следете нашия сайт за промоции! Записалите се за бюлетин получават 10% отстъпка за първата поръчка.",
    'default': "Благодаря за въпроса! Моля, уточнете повече или се свържете с поддръжката на hello@beigebeauty.com"
}

class AIAssistant:
    def __init__(self):
        self.has_gemini = False
        self.model = None
        self._init_gemini()

    def _init_gemini(self):
        if GEMINI_API_KEY:
            try:
                import google.generativeai as genai
                genai.configure(api_key=GEMINI_API_KEY)
                self.model = genai.GenerativeModel('gemini-pro')
                self.has_gemini = True
                print("Google Gemini AI е активиран!")
            except Exception as e:
                print(f"Грешка при инициализация на Gemini: {e}")
                self.has_gemini = False
        else:
            print("Няма GEMINI_API_KEY - използва се fallback режим")

    def get_keywords(self, text: str) -> List[str]:
        text_lower = text.lower()
        keywords = []

        keyword_map = {
            'shipping': ['доставк', 'shipping', 'delivery', 'пратка', 'куриер'],
            'return': ['връщан', 'return', 'refund', 'гаранци'],
            'ingredients': ['съставк', 'ingredients', 'съдържа'],
            'vegan': ['vegan', 'веган', 'животн', 'animal'],
            'gift': ['комплект', 'gift', 'set', 'подарък'],
            'organic': ['organic', 'био', 'natural', 'естеств'],
            'contact': ['контакт', 'contact', 'телефон', 'email'],
            'order_status': ['статус', 'поръчк', 'order'],
            'discount': ['отстъпк', 'discount', 'промоция', 'намален']
        }

        for key, words in keyword_map.items():
            for word in words:
                if word in text_lower:
                    keywords.append(key)
                    break
        return keywords if keywords else ['default']

    def get_fallback_response(self, question: str) -> str:
        keywords = self.get_keywords(question)
        response_key = keywords[0] if keywords else 'default'
        return FALLBACK_RESPONSES.get(response_key, FALLBACK_RESPONSES['default'])

    async def ask_gemini(self, question: str) -> str:
        if not self.has_gemini or not self.model:
            return self.get_fallback_response(question)

        try:
            system_prompt = """Ти си приятелски AI асистент за онлайн магазин за козметика "Beige Beauty".
            Отговаряй на български език, кратко и полезно (максимум 3-4 изречения).
            Бъди топъл и професионален."""

            full_prompt = f"{system_prompt}\n\nКлиент пита: {question}\n\nОтговор:"
            response = self.model.generate_content(full_prompt)
            return response.text[:500]
        except Exception as e:
            print(f"Грешка от Gemini: {e}")
            return self.get_fallback_response(question)

    def get_response_sync(self, question: str) -> str:
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            response = loop.run_until_complete(self.ask_gemini(question))
            loop.close()
            return response
        except Exception as e:
            print(f"Грешка: {e}")
            return self.get_fallback_response(question)

assistant = AIAssistant()