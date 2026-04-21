import asyncio
import os
from datetime import datetime
import pytz
import logging
import openai
from llama_searcher.utils.logger import log_print


class AnalysisAgent:
    def __init__(self, model_name="gemini-1.5-flash-8b", maxmuim_concurent=4):
        self.model_name = model_name
        log_print("INFO", f"Initialized AnalysisAgent with model: {model_name}")
        self.client = openai.AsyncOpenAI(
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            api_key=os.getenv("Gemini_API_KEY", "dummy_key"),
        )
        self.client_2 = openai.AsyncOpenAI(
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            api_key=os.getenv("Gemini_API_KEY_2", "dummy_key"),
        )
        self.maxmuim_concurent = maxmuim_concurent
        self.max_client_1 = 0
        self.max_client_2 = 0

    def call(self, search_query, top_results):
        log_print("INFO", f"Call invoked for: {search_query}")
        try:
            return asyncio.run(self.summarize_all(search_query, top_results))
        except RuntimeError as e:
            log_print("ERROR", f"Event loop already running. Fallback: {e}")
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(
                self.summarize_all(search_query, top_results)
            )

    async def summarize(self, user_query, text_to_summarize, index, max_queue):
        day, date = self.get_time("Rome")
        log_print("INFO", f"Summarizing Starting for index {index}")
        try:
            if max_queue[0] < self.maxmuim_concurent:
                max_queue[0] += 1
                messages = [
                    {
                        "role": "system",
                        "content": "You are a highly capable AI assistant doing extraction and summarization of search scraping data for the user request.",
                    },
                    {
                        "role": "user",
                        "content": f"Date context: {date},{day}\nUser Query: {user_query}\nPlease summarize the below data efficiently:\n\n{text_to_summarize}",
                    },
                ]

                if self.max_client_1 < self.maxmuim_concurent // 2:
                    client = self.client
                    self.max_client_1 += 1
                else:
                    client = self.client_2
                    self.max_client_2 += 1

                async def get_completion():
                    response = await client.chat.completions.create(
                        model=self.model_name,
                        messages=messages,
                        temperature=0.5,
                        max_tokens=300,
                    )
                    return response.choices[0].message.content.strip()

                output = await asyncio.wait_for(get_completion(), timeout=5)
                log_print("INFO", f"Summarizing Ending for index {index}")
                return output
            else:
                return ""
        except asyncio.TimeoutError:
            log_print("WARNING", "Summarization timed out after 5 seconds.")
            return ""

        except Exception as e:
            log_print("ERROR", f"OpenAI API error: {e}")
            return f"Error summarizing: {e}"

    async def summarize_all(self, search_query, top_results):
        log_print("INFO", f"Summarizing {len(top_results)} items...")
        tasks = []
        for index, item in enumerate(top_results):
            content = (
                str(item.get("snippet", "")) if isinstance(item, dict) else str(item)
            )
            if content.strip() and item not in ["", " ", None]:
                tasks.append(self.summarize(search_query, content, index, [0]))
            else:
                tasks.append(asyncio.sleep(0, result="Skipped: Empty content"))

        results = await asyncio.gather(*tasks, return_exceptions=True)
        return [str(r) if isinstance(r, Exception) else r for r in results]

    def get_time(self, location="Rome"):
        try:
            tz_match = [
                tz for tz in pytz.all_timezones if location.lower() in tz.lower()
            ]
            tz = pytz.timezone(tz_match[0] if tz_match else "Europe/Rome")
            now = datetime.now(tz)
            return now.strftime("%A"), now.strftime("%Y-%m-%d")
        except Exception as e:
            logging.warning(f"Timezone error: {e}")
            now = datetime.now(pytz.utc)
            return now.strftime("%A"), now.strftime("%Y-%m-%d")


# Instantiate a default agent
summarize_agent = AnalysisAgent()
