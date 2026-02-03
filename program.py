import json
import os

from dotenv import load_dotenv

import contract_object
import send_email_tool

load_dotenv()

from langchain.agents import create_agent
from langchain_community.callbacks import get_openai_callback
from langchain_openai import ChatOpenAI
import pdf_reader_tool

openai_model = ChatOpenAI(model="gpt-5-nano", api_key=os.getenv("OPENAI_API_KEY"))
gemini_model = ChatOpenAI(base_url="https://generativelanguage.googleapis.com/v1beta/openai", model="gemini-2.5-flash", api_key=os.getenv("GEMINI_API_KEY"))

agent = create_agent(openai_model, tools=[pdf_reader_tool.read_pdf, send_email_tool.send_email])

schema_str = json.dumps(contract_object.FullExtractionSchema.model_json_schema(), indent=2)

prompt = f"""
    ### FERRAMENTAS DISPONÍVEIS
    1. 'pdf_reader': Faz uma busca semântica no PDF. Requer uma query em linguagem natural.
    2. 'send_email_tool': Envia o JSON final por e-mail.
    
    ### OBJETIVO
    Seu objetivo é extrair informações de um PDF para preencher um objeto JSON. 
    O esquema (estrutura) que você deve seguir é: {schema_str}
    
    ### DIRETRIZES DE EXECUÇÃO
    1. **DADOS, NÃO SCHEMA**: Não retorne as definições de tipo ($defs, properties, type). Retorne um JSON populado com os valores reais encontrados no documento.
    2. **BUSCA ATIVA**: Se um campo estiver vazio, use 'pdf_reader' para encontrá-lo.
    3. **FINALIZAÇÃO**: Quando coletar os dados ou atingir 15 tentativas, monte o JSON final preenchido e use a ferramenta 'send_email_tool'. 
    4. **COMPLETUDE**: Caso haja algum campo 'null' ou não preenchido, defina 'status_extracao' como 'INCOMPLETE', caso contrário defina como 'COMPLETE'.
    5. **FORMATO DO EMAIL**: O input da ferramenta 'send_email_tool' deve ser estritamente o objeto JSON com os dados extraídos, sem explicações adicionais.
    
    ### FORMATO DE RESPOSTA
    Pensamento: [Seu raciocínio sobre o que falta]
    Ação: [Qual ferramenta usar]
    Ação Input: [O que enviar para a ferramenta]
    Observação: [Resultado da ferramenta]
    ... (Repita até concluir)
"""

prompt_ = f"""
    Backstory: You are an elite legal analyst with a forensic eye for detail and a 
    specialization in corporate operations. Your precision is absolute. 
    You operate under a Mandatory Completeness Rule: if ANY field within 
    the schema (including any secondary fields like 'complemento' or 'observacoes') 
    is missing, null, or empty, you MUST mark the extraction_status as 'INCOMPLETE'. 
    In such cases, you do not just report the failure; you proactively 
    draft and manage professional outreach to the responsible parties 
    to ensure the final record reaches 100% data density.
    
    First task steps:
    1. Use the pdf_reader_tool.read_pdf to locate: 
     - Company registration data (CNPJ, Corporate Name, etc.).
     - Tables or clauses regarding positions (vagas), roles, and compensation.
     - Effective dates and the total contract value.
    2. Convert monetary values to cents (e.g., $ 1,000.00 -> 100000).
    3. Identify the PDF title and page count (if available in metadata or text).
    4. If at least one field was not found, set the extraction_status to 'INCOMPLETE'.
    5. You need to add a UUID to the pdf_title using the UUID generator tool.
    
    First task structured output:
    Structured JSON matching the {schema_str}.
    The pdf_title field must be 'banana'.
    
    Second task steps:
    1. Review the output from the Contract Data Analyst.
    2. If 'extraction_status' is 'COMPLETE', skip sending an email and set action_taken to 'SKIPPED'.
    3. If 'extraction_status' is 'INCOMPLETE', identify exactly which fields are missing (null).
    4. Compose a polite email to the representative.
    5. You must send the email to the representative's email address found in the Company Data.'
    5. Subject must include the Contract Title.
    6. Send the email using the send_email_tool.send_email and report the result.
    
    Second task structured output:
    A JSON object confirming if the email was sent and the tool's response.
"""

with get_openai_callback() as cb:
    response = agent.invoke({
        "messages": [{"role": "user", "content": prompt}]
    })
    print(f"Tokens Totais: {cb.total_tokens}")
    print(f"Tokens de Prompt: {cb.prompt_tokens}")
    print(f"Tokens de Resposta: {cb.completion_tokens}")
    print(f"Custo Total (USD): ${cb.total_cost}")

final_message = response["messages"][-1]
print(final_message.content)
