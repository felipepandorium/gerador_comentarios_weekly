import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())

client = OpenAI()

# ---------- Placeholder function ----------
# Substitua esta função pela sua função real que gera comentários.
def generate_comments_from_inputs(text_from_sheet: str, typed_text: str) -> str:
    # Exemplo simples: concatena e devolve. Troque pela sua lógica.

    prompt_sistema = """
    Você é um gestor de tráfego experiente. Sua função é analisar métricas de performance dos últimos 7 dias e escrever um texto direto e objetivo para enviar ao cliente via WhatsApp.

    Você receberá dois blocos de informação na entrada do modelo:

    1) CONTEXTO DA SEMANA — acontecimentos relevantes que justificam variações (ex: campanhas novas, mudanças no site, promoções, problemas técnicos etc.).
    <exemplo_contexto>
    Já ultrapassamos os 100k de faturamento e estamos a caminho de empatar o resultado YoY (189k). No entanto, queria muito chegar na casa dos 200k para entregar resultados melhores.
    O ponto de atenção é que ainda estamos atrás no ROAS. O que estou fazendo é segurar mais o Meta para conter o ROAS e manter o Google como está, porém meta está muito atras em LC esse mês.
    Finalmente, voltamos a ter compras via campanha de marca, mas ainda é muito pouco comparado ao que era antes. Além disso, o canal direto está indo muito mal e o tráfego dele está caro, por isso também fiz essa contenção.
    No mais, deixei escaladas as campanhas de sale para manter o volume de receita.
    </exemplo_contexto>

    2) MÉTRICAS E VARIAÇÕES — sempre no mesmo bloco, como no exemplo abaixo:
    <exemplo_metricas>
        "Boa tarde! Segue o resumo da performance da última semana.
        Período: *13/10/2025 a 19/10/2025*

        *- Global:*
        Sessões no site: 23393 (-24%)
        Carrinhos: 202 (-27%)
        Compras: 37 (-37%)
        Ticket médio: R$ 933,85 (+8%)
        Valor vendido: R$ 34.552,34 (-32%)
        Taxa de conversão: 0,16% (-18%)
        Valor investido: R$ 5.058,53 (-20%)
        ROAS: 6,83 (-15%)

        *- Meta Ads:*
        Valor vendido: R$ 6.153,00 (-68%)
        Valor investido: R$ 1.632,68 (-22%)
        ROAS: 3,77 (-59%)

        *- Google Ads:*
        Valor vendido: R$ 15.077,52 (-49%)
        Valor investido: R$ 3.425,85 (-20%)
        ROAS: 4,40110482877229 (-37%)

        Acumulado mensal: *01/10/2025 a 19/10/2025*
        Valor vendido: R$ 105.492,72 (0%)
        Valor investido: R$ 15.010,07 (0%)
        ROAS: 7,03 (0%)"
    </exemplo_metricas>
    
        # Instruções obrigatórias para sua resposta:

         ## Gere um texto curto e direto, sem enrolação.

         ## Não repita as métricas no texto — apenas interprete o que elas indicam.

         ## Destaque somente os pontos relevantes da semana:

            ### grandes crescimentos ou quedas

            ### variações importantes em compras, ROAS, investimento ou conversão

            ### movimentos que se conectam diretamente com o CONTEXTO

        ## Caso exista algum ponto de atenção, cite de forma clara.

        ## A resposta deve ter tom profissional, mas simples o suficiente para ser lido no WhatsApp.

        ## Não invente informações — use apenas o que vier no CONTEXTO + as variações.

        # Estrutura esperada da resposta:

         ## Abertura curta (“Segue o resumo da semana...”)

         ## Principais destaques positivos e negativos da semana

         ## Conexão direta com o CONTEXTO (ex: “Essa melhora aconteceu principalmente por causa da campanha X iniciada no dia Y”)

         ## Conclusão objetiva e, se necessário, próximos passos.
    """

    prompt_inicial = f"""
    Seguem as métricas e variações da semana:
    <metricas_e_variacoes>
    {text_from_sheet}
    </metricas_e_variacoes>

    Segue o contexto da semana:
    <contexto>
    {typed_text}
    </contexto>
    """

    completion = client.responses.create(
        model="gpt-5.1",
        input=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "input_text",
                        "text": prompt_sistema
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": prompt_inicial
                    }
                ]
            }
        ]
    )

    return completion.output_text

# ---------- App Streamlit ----------

# Antes de criar widgets: aplicar pendência (se existir)
if 'typed_text_pending' in st.session_state:
    # transfere a pendência para o estado usa pelo widget
    st.session_state['typed_text'] = st.session_state.pop('typed_text_pending')

# Login simples (admin/admin)
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if not st.session_state['authenticated']:
    st.title("Login")
    user = st.text_input("Usuário")
    pwd = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if user == "admin" and pwd == "admin":
            st.session_state['authenticated'] = True
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos.")

    st.stop()  # impede acesso ao restante da página até logar

st.set_page_config(page_title="Gerador de Comentários para Weekly", layout="wide")

# Sidebar com navegação
page = st.sidebar.radio("Navegação", ["Instruções", "Processo"])

if page == "Instruções":
    st.title("Instruções")
    st.markdown(
        """
        **Como usar este app**

        1. Vá para a aba "Processo" na barra lateral.
        2. Cole o texto copiado da planilha do Weekly na primeira caixa.
        3. No campo abaixo, digite o texto complementar diretamente no app.
        4. Clique em "Gerar comentários" para rodar a função que gera os comentários.
        5. O resultado aparecerá logo abaixo das caixas. Você pode clicar novamente para gerar um novo resultado até encontrar um bom resultado — o anterior será substituído.
        """
    )

    st.markdown("---")
    st.markdown("Ainda está sendo validado.")

else:  # Processo
    st.title("Processo — gerar comentários")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Texto da planilha do Weekly (colar aqui)")
        sheet_text = st.text_area(
            "Cole o conteúdo copiado do Weekly (CTRL+V / ⌘+V)",
            value="",
            height=473,
            key="sheet_text",
        )

    with col2:
        st.subheader("Contexto")
        typed_text = st.text_area(
            "Digite aqui o contexto para complementar o relatório.",
            value="",
            height=300,
            key="typed_text",
        )

        # st.write("🎤 Gravar áudio para transcrever.")
        audio_file = st.audio_input("Clique para gravar", key="audio_input")

        if st.button("Transcrever", key='transcrever'):

            st.info("Transcrevendo...")

            try:

                # Enviando para o GPT
                transcription = client.audio.transcriptions.create(
                    model="gpt-4o-mini-transcribe", 
                    file=audio_file
                )

                text_transcribed = transcription.text

                # Inserindo o texto transcrito na caixa

                st.session_state["typed_text_pending"] = text_transcribed
            except:
                st.error("Erro ao transcrever.\n\nRecarregue a página e tente novamente.")

            st.rerun()


    st.markdown("---")

    # Espaço para resultado que será substituído a cada geração
    result_placeholder = st.empty()

    # Botão para gerar comentários — permanece ativo para repetir a operação
    if st.button("Gerar comentários", key='gerar_comentarios'):

        # Informando que está gerando o comentário
        st.info("Gerando o comentário...")

        # Chame aqui a função real que você vai implementar
        result = generate_comments_from_inputs(sheet_text, typed_text)

        # Armazena no session_state para permitir acessos posteriores, se desejar
        st.session_state['last_result'] = result

        # Apresenta o resultado (apaga o anterior e coloca o novo)
        result_placeholder.markdown("**Resultado:**")
        result_placeholder.code(result, language='')

    # Se já houver um resultado gerado (em sessão), mostra abaixo ao recarregar a página
    if 'last_result' in st.session_state and st.session_state['last_result']:
        result_placeholder.markdown("**Último resultado (persistido na sessão):**")
        result_placeholder.code(st.session_state['last_result'], language='')