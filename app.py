import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
from streamlit_option_menu import option_menu
import os

LOGIN_USER = os.getenv("LOGIN_USER")
LOGIN_PASS = os.getenv("LOGIN_PASS")

_ = load_dotenv(find_dotenv())

client = OpenAI()

# ---------- Placeholder function ----------
# Substitua esta função pela sua função real que gera comentários.
def generate_comments_from_inputs(tag_option: str, text_from_sheet: str, typed_text: str) -> str:
    # Exemplo simples: concatena e devolve. Troque pela sua lógica.

    prompt_sistema = """
    Você é um gestor de tráfego experiente. Sua função é analisar métricas de performance dos últimos 7 dias e escrever um texto direto para enviar ao cliente via WhatsApp.

    A entrada enviada para você SEMPRE conterá:
    1. **TAG:** Uma **TAG** que altera a forma de comunicação.
    2. **CONTEXTO DA SEMANA** — acontecimentos que explicam as variações.
    3. **MÉTRICAS E VARIAÇÕES** — dados brutos.

    ---

    # REGRAS DE INTERPRETAÇÃO DAS TAGS

    ## **TAG: `##MODELO_EMOJI##`**
    - Comunicação mais próxima, leve e simpática.  
    - Pode usar emojis, **mas APENAS em movimentos positivos**.  
    - Em quedas ou pontos negativos, **não usar emojis**.  
    - Tom humanizado, porém profissional.

    ### **EXEMPLO_MODELO_EMOJI:** 
    <EXEMPLO_MODELO_EMOJI> 
    Em novembro batemos o faturamento histórico da marca e ultrapassamos os 100k de faturamento!! 🚀🎉 Sabemos que o trabalho em equipe foi essencial para fazermos a melhor ação de Black possível, pensando e repensando ações e criativos, parabéns a todo o time! Estamos muito felizes em fazer parte desse projeto!

    Hoje já encerramos a comunicação de Black e já vimos uma retração na conta. Apesar disso, nosso ROAS segue saudável, o que indica que temos oportunidade de escala. A partir de hoje, vamos voltar a aumentar o investimento com foco nos últimos lançamentos!
    </EXEMPLO_MODELO_EMOJI>

    ---

    ## **TAG: `##MODELO_AMPLIADO##`**
    Quando essa tag estiver presente, siga obrigatoriamente a estrutura abaixo:

    ### **1º PARÁGRAFO — CONTEXTO GERAL**  
    Resumo geral da semana conectando principais variações com o contexto.

    ### **2º PARÁGRAFO — META ADS**  
    - Interpretação das variações da Meta Ads.  
    - Comentários sobre campanhas ou criativos **somente se estiverem mencionados no CONTEXTO enviado**.

    ### **3º PARÁGRAFO — GOOGLE ADS** -> se houver, se não, pule para o próximo
    - Interpretação das variações do Google Ads.  
    - Comentários sobre campanhas ou criativos **somente se o CONTEXTO citar**.

    ### **4º PARÁGRAFO — TIKTOK ADS** -> se houver, se não, pule para o próximo
    - Interpretação das variações do Tiktok Ads.  
    - Comentários sobre campanhas ou criativos **somente se o CONTEXTO citar**.

    ### **5º PARÁGRAFO — PINTEREST ADS** -> se houver, se não, pule para o próximo
    - Interpretação das variações do Pinterest Ads.  
    - Comentários sobre campanhas ou criativos **somente se o CONTEXTO citar**.

    ### **ÚLTIMO PARÁGRAFO — FATURAMENTO/ROAS MENSAL + PRÓXIMOS PASSOS**
    - Interpretar faturamento/ROAS mensal com base nas métricas enviadas.  
    - “Próximos passos” devem vir **exclusivamente do CONTEXTO enviado**.

    ### **EXEMPLO_MODELO_AMPLIADO:**
    <EXEMPLO_MODELO_AMPLIADO>
    Na última semana, tivemos uma retração nos resultados em comparação com a semana anterior. Para preservar o nosso ROAS, viemos reduzindo o investimento na conta de forma gradual. Esses resultados provavelmente foram muito impactados pelo feriado, levando em consideração o comportamento de compra da cliente ENTS.

    No meta, os criativos que geraram o maior volume de compras foram o vídeo da Fe com a arara, seguido do vídeo da Suellyn com o conjunto marrom latte e também do provador do vestido de linho com paetê bordado.

    No google, a campanha de black está liderando em compras, seguida da campanha da coleção Aura. A campanha da coleção La Isla veio perdendo força nas últimas semanas e nós desativamos na semana passada. Como próximos passos, vale atualizarmos o google com a coleção Entre Luzes.

    No mês de Novembro, já faturamos quase R$ 230k com ROAS 7 e, no pace que estamos, a projeção de faturamento é de R$ 285k. Para nos manter dentro da nossa meta de orçamento, já vamos reduzir ainda mais o investimento da conta. Para essa semana, seguimos com a ação da aba de black week, com até 70% off + na compra de 3 ou mais peças ganhe 10% off. No dia 28 teremos ofertas relâmpago. Conseguem nos enviar esses materiais até quinta para já deixarmos programado?
    </EXEMPLO_MODELO_AMPLIADO>

    ---

    ## **TAG: `##MODELO_PADRAO##`**

    ### ESTRUTURA ESPERADA DA RESPOSTA QUANDO **NÃO HÁ TAGS**:
        #### Abertura curta (“Segue o resumo da semana...”)
        #### Principais destaques positivos e negativos da semana. 
        #### Não precisa necessariamente dividir por plataforma. Pode apenas destacar os pontos positivos delas, se houver.
        #### Se o resultado tiver sido ruim na plataforma, não coloque ela. A menos que tenha alguma informação relevante no contexto.
        #### Conexão direta com o CONTEXTO (ex: “Essa melhora aconteceu principalmente por causa da campanha X iniciada no dia Y”)
        #### Conclusão objetiva e, se necessário, próximos passos.


    # INSTRUÇÕES GERAIS DE COMUNICAÇÃO
        ## Gere um texto curto e direto, sem enrolação.
        ## Não repita as métricas no texto — apenas interprete o que elas indicam.
        ## Destaque somente os pontos relevantes da semana:
            ### grandes crescimentos ou quedas
            ### variações importantes em compras, ROAS, investimento ou conversão
            ### movimentos que se conectam diretamente com o CONTEXTO
        ## Caso exista algum ponto de atenção, cite de forma clara.
        ## A resposta deve ter tom profissional, mas simples o suficiente para ser lido no WhatsApp.
        ## Não invente informações — use apenas o que vier no CONTEXTO + as variações.
        ## Conecte tudo ao CONTEXTO enviado.

    ---

    # 📥 FORMATO DA ENTRADA QUE VOCÊ VAI RECEBER:

    TAG:
    <tag>
    {{tag}}
    </tag>

    MÉTRICAS E VARIAÇÕES:
    <metricas_e_variacoes>
    {{metricas}}
    </metricas_e_variacoes>

    CONTEXTO DA SEMANA:
    <contexto>
    {{contexto}}
    </contexto>
    """

    prompt_inicial = f"""
    TAG:
    <tag>
    ##{tag_option}##
    </tag>

    MÉTRICAS E VARIAÇÕES:
    <metricas_e_variacoes>
    {text_from_sheet}
    </metricas_e_variacoes>

    CONTEXTO DA SEMANA:
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

# Login simples
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if not st.session_state['authenticated']:
    st.title("Login")
    user = st.text_input("Usuário")
    pwd = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if user == LOGIN_USER and pwd == LOGIN_PASS:
            st.session_state['authenticated'] = True
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos.")

    st.stop()  # impede acesso ao restante da página até logar

st.set_page_config(page_title="Gerador de Comentários para Weekly", layout="wide")

# Sidebar com navegação
with st.sidebar:
    page = option_menu("Menu Principal", ["Instruções", "Processo"], 
        icons=['house', 'gear'], menu_icon="cast", default_index=0)

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
    st.markdown(
        """
        **Existem algumas tags que podem ser utilizadas para mudar a comunicação do bot. Segue:**

        1. MODELO_PADRAO -> Esta tag segue uma comunicação padrão, simples e profissional.

        2. MODELO_EMOJI -> Esta tag adiciona uma comunicação mais próxima que permite a utilização de emojis para dar resultados bons. Nos ruins, ele mantém sem emoji.

        3. MODELO_AMPLIADO -> Esta tag adiciona um modelo mais completo e detalhado do relatório. Segue um exemplo:
        
        - Primeiro parágrafo: CONTEXTO GERAL
        - Segundo parágrafo: CONTEXTO DA META -> falar de criativo (isso tem que ser passado no texto do contexto)
        - Terceiro parágrafo: CONTEXTO DO GOOGLE -> falar de campanha (isso tem que ser passado no texto do contexto)
        - Final: FALAR DE FATURAMENTO/ROAS MENSAL (esse é do bot) e PRÓXIMOS PASSOS (isso tem que ser passado no texto do contexto)
        """
        )

else:  # Processo
    st.title("Processo — gerar comentários")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Texto da planilha do Weekly (colar aqui)")
        sheet_text = st.text_area(
            "Cole o conteúdo copiado do Weekly (CTRL+V / ⌘+V)",
            value="",
            height=557,
            key="sheet_text",
        )

    with col2:
        st.subheader("Contexto")

        tag_option = st.selectbox(
            "Escolha se deseja adicionar uma tag para mudar o padrão da resposta.",
            ("MODELO_PADRAO", "MODELO_EMOJI", "MODELO_AMPLIADO"),
        )


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
        result = generate_comments_from_inputs(tag_option, sheet_text, typed_text)

        # Armazena no session_state para permitir acessos posteriores, se desejar
        st.session_state['last_result'] = result

        # Apresenta o resultado (apaga o anterior e coloca o novo)
        result_placeholder.markdown("**Resultado:**")
        result_placeholder.code(result, language='')

    # Se já houver um resultado gerado (em sessão), mostra abaixo ao recarregar a página
    if 'last_result' in st.session_state and st.session_state['last_result']:
        result_placeholder.markdown("**Último resultado (persistido na sessão):**")
        result_placeholder.code(st.session_state['last_result'], language='')