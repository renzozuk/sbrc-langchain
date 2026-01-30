import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

import email_writer
import pdf_reader

load_dotenv()

model = ChatOpenAI(model="gpt-5-nano", api_key=os.getenv("API_KEY"))
agent = create_agent(model, tools=[pdf_reader.read_pdf, email_writer.send_email])

response = agent.invoke({
    "messages": [{"role": "user", "content": "Use a ferramenta até conseguir extrair as informações necessárias, "
                                             "você deve criar uma query apropriada a cada tentativa, a própria  "
                                             "ferramenta getPdfContent irá tentar conseguir informações do PDF para "
                                             "você, o nome é do arquivo que a tool vai tentar consultar é "
                                             "'ContratoES.pdf'. Gere um JSON com base nos atributos identificados no "
                                             "PDF. Após extrair as informações do PDF e gerar o JSON, envie um email "
                                             "com os seguintes argumentos: \" "+ os.getenv("ORIGIN_ADDRESS") + ", " + os.getenv("ORIGIN_PASSWORD")
                                             + ", " + os.getenv("DESTINY_ADDRESS") + ", um assunto apropriado e o "
                                                                                     "JSON gerado como"
                                                                      "conteúdo."}]
})
final_message = response["messages"][-1]
print(final_message.content)
