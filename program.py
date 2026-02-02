import os
import json
import agentops
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate

import contract_object
import send_email_tool

load_dotenv()

# agentops.init(api_key=os.getenv("AGENTOPS_API_KEY"))

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
import pdf_reader

model = ChatOpenAI(model="gpt-5-nano", api_key=os.getenv("OPENAI_API_KEY"))

agent = create_agent(model, tools=[pdf_reader.read_pdf, send_email_tool.send_email])

# agentops.start_trace()

schema_str = json.dumps(contract_object.FullExtractionSchema.model_json_schema(), indent=2)

prompt = f"""
    Você é um agente de extração. Sua prioridade máxima é ENVIAR O E-MAIL.

    FLUXO OBRIGATÓRIO:
    1. Realize no máximo 5 ou 6 buscas usando 'read_pdf' para capturar o essencial (Empresa, CNPJ, Valor), comece com a query 'contrato'.
    2. Mesmo que não encontre TODOS os dados do schema, você DEVE consolidar o que conseguiu e chamar 'send_email' IMEDIATAMENTE.
    3. É melhor enviar um JSON incompleto do que entrar em um loop infinito de busca.

    DADOS PARA ENVIO:
    - Destinatário: exemplo@mail.com
    - Assunto: Extração de Contrato
    - Schema: {schema_str}
"""

response = agent.invoke({
    "messages": [{"role": "user", "content": prompt}]
})

# agentops.end_trace()

final_message = response["messages"][-1]
print(final_message.content)
