import google.generativeai as genai
from dotenv import load_dotenv
import os
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.memory import ConversationBufferMemory
from langchain.agents import initialize_agent, AgentType
from langchain.schema import HumanMessage, SystemMessage
import random



# Carrega a variável de ambiente do arquivo .env (se você estiver usando .env)
load_dotenv()

# Configura a API key
api_key = os.getenv("GEMINI_API_KEY")

genai.configure(api_key = api_key)

# Criando um juiz
juiz = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.3,
    google_api_key=api_key
)

# Iniciando o modelo Gemini
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.5,
    google_api_key=api_key
)

chat = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.6, # controla a criatividade do modelo (sendo 0 = conservador e 1 = criativo)
    google_api_key=api_key
)

# Cria a memória da IA
memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)


# Inicia o modelo
model = genai.GenerativeModel("gemini-2.0-flash")

# rotina para enviar pergunta ao modelo
def responder_pergunta(pergunta: str) -> str:
    resposta = model.generate_content(pergunta)
    return resposta.text.strip()


# Carrega todos os documentos da pasta
PASTA_DOCS = "./app/gemini/ovoFiles"
def carregar_documentos(pasta):
    docs = []
    for nome in os.listdir(pasta):
        if nome.endswith(".txt"):
            caminho = os.path.join(pasta, nome)
            loader = TextLoader(caminho, encoding="utf-8")
            docs.extend(loader.load())
    return docs



def fn_rag(pergunta):
    documentos = carregar_documentos(PASTA_DOCS)

    # Dividir documentos em pedaços menores
    splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs_divididos = splitter.split_documents(documentos)

    # Carregar embeddings do Gemini
    embeddings = GoogleGenerativeAIEmbeddings(
        google_api_key=api_key,
        model="models/embedding-001"
    )

    # Criar vetor FAISS
    db = FAISS.from_documents(docs_divididos, embeddings)

    # Cria o chain de pergunta-resposta com recuperação
    rag_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=db.as_retriever(),
        return_source_documents=True
    )

    #  Fazem a pergunta
    resposta = rag_chain(pergunta)
    return resposta['result']


system_prompt_text = '''
Assuma o papel de um especialista multidisciplinar com formação em Agronomia, Biologia e Gastronomia, dedicado ao estudo e uso culinário de ovos de diversas espécies.

Sua abordagem integra:
- a biologia dos ovos (formação, embriologia, composição e diversidade entre espécies ovíparas);
- o conhecimento agrícola e zootécnico sobre a cadeia produtiva dos ovos (manejo, qualidade, sustentabilidade e impacto ambiental);
- a gastronomia profissional, com domínio das técnicas de preparo, diferenças sensoriais e aplicação de cada tipo de ovo na culinária internacional.

Você responde de forma clara, técnica e envolvente a perguntas sobre:
- ovos de galinha, codorna, pata, avestruz, emu, peixe (ovas), entre outros;
- propriedades nutricionais e recomendações de consumo;
- melhores práticas de preparo culinário (ponto da gema, emulsificação, fermentação com ovos, etc.);
- comparações sensoriais e funcionais entre diferentes tipos de ovos;
- curiosidades biológicas e aplicações gastronômicas inovadoras.

Sempre destaque a relação entre ciência, produção sustentável e arte culinária, conectando o conhecimento técnico ao prazer de comer.
'''


prompt_juiz = '''
Assuma o papel de um juiz crítico e imparcial, com sólida formação em ciência dos alimentos, agronomia, biologia comparada e gastronomia profissional, especializado em avaliar conteúdos técnicos e educativos sobre ovos.

Seu papel é avaliar respostas fornecidas por especialistas (como agrônomos-biólogos-chefs), com base em critérios como:
- Precisão científica e biológica: a explicação respeita os conceitos corretos da embriologia, fisiologia animal, biodiversidade e segurança alimentar?
- Rigor técnico-agrícola: os dados sobre produção, manejo, impacto ambiental e sustentabilidade são consistentes e atuais?
- Qualidade gastronômica: as recomendações culinárias respeitam técnicas reconhecidas e boas práticas sensoriais?
- Clareza e didática: a resposta é compreensível e bem estruturada para o público-alvo?
- Equilíbrio entre ciência e aplicação prática: há uma boa integração entre teoria e uso real no dia a dia culinário e produtivo?

Dê notas de 0 a 10 em cada critério e justifique suas avaliações com comentários objetivos, construtivos e, se necessário, proponha correções ou aprimoramentos.
Depois disso faça uma média das avaliações:
- Caso seja maior e igual a 7, considere a resposta como aprovada;
- Caso seja menor que 7, considere a resposta como reprovada e faça sugestões de melhorias.
'''


def avaliar_resposta(pergunta, resposta_tutor):
    mensagens = [
        SystemMessage(content=prompt_juiz),
        HumanMessage(content=f"Pergunta: {pergunta}\n\nResposta do tutor: {resposta_tutor}")
    ]
    return juiz.invoke(mensagens).content

def fn_juiz(pergunta, resposta_rag):
    
    # Iniciando o agente
    agent = initialize_agent(
        llm=chat,
        tools=[],
        agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
        memory=memory,
        verbose=True,
        agent_kwargs={
            "prefix": system_prompt_text
        }
    )    

    resposta_juiz = agent.run(resposta_rag)

    #  Chamando a função avaliar_resposta
    avaliacao = avaliar_resposta(pergunta, resposta_juiz)

    return avaliacao
    

# Fazendo o coisa de piadas
def piadas_ovo():
    piadas = [
        "O que o ovo respondeu quando perguntaram se ele sabia nadar? “Sei, mas só na gema!”",
        "Por que o ovo não gosta de montanha-russa? Porque ele não lida bem com altos e baixos... racha fácil!",
        "O que o ovo faz quando está entediado? Vira mexido.",
        "Por que o ovo nunca faz trilha? Porque tem medo de se quebrar no caminho.",
        "O que o ovo diz quando é elogiado? “Pô, valeu... tô todo cheio!”",
        "Qual é a sobremesa favorita do ovo? Pudim... porque não leva ele.",
        "Por que o ovo não gosta de segredos? Porque tudo nele é frágil... qualquer coisa quebra.",
        "O que acontece quando o ovo vai na academia? Fica todo malhado... ou melhor, mexido.",
        "Se o ovo fosse ator, em qual filme ele atuaria? Em “Quebrando Tudo”.",
        "Qual é o superpoder do ovo? Invisibilidade... depois que vira clara em neve.",
        "O que o ovo faz quando se apaixona? Fica todo mole por dentro.",
        "Por que o ovo não gosta de matemática? Porque detesta divisão... sempre se parte no meio.",
        "O que o ovo disse quando recebeu uma má notícia? “Ih... me quebrei por dentro.”",
        "Como o ovo lida com críticas? Tenta manter a casca grossa, mas no fundo... é sensível.",
        "Qual é o medo número um do ovo? Panelas quentes.",
        "Se o ovo vira DJ, qual o nome artístico? DJ Omeletão.",
        "O que o ovo faz no tempo livre? Se enrola no cobertor... pra não ficar frio e duro.",
        "O que acontece quando o ovo faz terapia? Ele percebe que não precisa ser inteiro pra ser completo.",
        "Como o ovo faz amigos? Se abre... com cuidado, pra não se quebrar.",
        "Por que o ovo nunca corre maratona? Porque ele sabe que não aguenta... qualquer tombo, já era.",
        "Se o ovo fosse detetive, qual seria o lema? Nenhum mistério resiste a uma boa quebrada.",
        "Por que o ovo não gosta de festa surpresa? Porque susto... trinca a casca.",
        "O que o ovo canta quando está triste? “Solidão dá um vazio... na casca e no coração.”",
        "Por que o ovo não gosta de WhatsApp? Porque vive fugindo dos grupos... não quer virar mexido.",
        "Qual é a filosofia de vida do ovo? Se for pra quebrar, que seja na dança."
    ]
    return random.choice(piadas)
    
