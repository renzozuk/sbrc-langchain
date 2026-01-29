import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
import pdf_reader

load_dotenv()

model = ChatOpenAI(model="gpt-5-nano", api_key=os.getenv("API_KEY"))
agent = create_agent(model, tools=[pdf_reader.read_pdf])

response = agent.invoke({
    "messages": [{"role": "user", "content": "Use a ferramenta até conseguir extrair as informações necessárias, você deve criar uma query apropriada a cada tentativa, a própria  ferramenta getPdfContent irá tentar conseguir informações do PDF para você, o nome é do arquivo que a tool vai tentar consultar é 'ContratoES.pdf'."}]
})
final_message = response["messages"][-1]
print(final_message.content)
