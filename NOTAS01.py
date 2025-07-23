import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Sistema de Gestão Escolar", page_icon="📚", layout="wide")

# Disciplinas e colunas base
disciplinas_base = [
    "Língua Portuguesa", "Matemática", "Inglês", "História", "Geografia",
    "Ciências", "Artes", "Educação Física", "Filosofia", "Educação Religiosa"
]

colunas_base = ["Número", "Aluno", "Ano", "Sala"]
colunas_notas = []
for disc in disciplinas_base:
    for semestre in ["S1", "S2", "S3", "S4"]:
        colunas_notas.append(f"{disc} {semestre}")
        colunas_notas.append(f"{disc} {semestre} Faltas")
    colunas_notas.append(f"{disc} Conceito Final")

colunas = colunas_base + colunas_notas

mapa_prefixos = {
    "Língua Portuguesa": "Lp",
    "Matemática": "Mat",
    "Inglês": "Ing",
    "História": "His",
    "Geografia": "Geo",
    "Ciências": "Cie",
    "Artes": "Arte",
    "Educação Física": "EdFi",
    "Filosofia": "Filo",
    "Educação Religiosa": "EdRe"
}

# Mapa invertido para reconhecer prefixos
prefixos_invertidos = {v: k for k, v in mapa_prefixos.items()}

def abreviado_para_completo(col):
    if col == "Num":
        return "Número"
    if col == "Alun":
        return "Aluno"
    if col == "Ano":
        return "Ano"
    if col == "Sala":
        return "Sala"
    for prefixo, nome_completo in prefixos_invertidos.items():
        if col.startswith(prefixo):
            sufixo = col[len(prefixo):]  # ex: "S1", "F1", "CF"
            if sufixo.startswith("S"):
                # Nota do semestre
                return f"{nome_completo} {sufixo}"
            elif sufixo.startswith("F") and len(sufixo) == 2 and sufixo[1].isdigit():
                # Faltas do semestre, ex: F1 -> " S1 Faltas"
                semestre_num = sufixo[1]
                return f"{nome_completo} S{semestre_num} Faltas"
            elif sufixo == "CF":
                # Conceito final
                return f"{nome_completo} Conceito Final"
    return col

def autenticar():
    senha_correta = "admin123"
    senha = st.sidebar.text_input("Digite a senha:", type="password")
    if senha == senha_correta:
        return True
    elif senha:
        st.sidebar.error("Senha incorreta!")
    return False

def pagina_upload_criacao():
    st.title("📂 Carregar ou Criar Tabela")
    uploaded_file = st.file_uploader("Selecione um arquivo CSV para carregar:", type="csv")
    if uploaded_file:
        try:
            dados = pd.read_csv(uploaded_file, encoding="utf-8-sig")
            dados.rename(columns=lambda c: abreviado_para_completo(c), inplace=True)
            faltantes = [c for c in colunas if c not in dados.columns]
            if faltantes:
                st.error(f"Colunas faltando no arquivo: {faltantes}")
                return None
            st.success("Arquivo carregado com sucesso!")
            return dados
        except Exception as e:
            st.error(f"Erro ao ler arquivo: {e}")
            return None
    else:
        if st.button("Criar tabela vazia do zero"):
            dados = pd.DataFrame(columns=colunas)
            st.success("Tabela criada com sucesso!")
            return dados
    st.info("Por favor, carregue um arquivo CSV ou crie uma tabela para continuar.")
    return None

def cadastrar_aluno():
    st.header("Cadastro de Alunos")
    with st.form("form_cadastro"):
        numero = st.text_input("Número do aluno")
        nome = st.text_input("Nome do aluno")
        ano = st.selectbox("Ano", options=[str(i) for i in range(1, 13)])
        sala = st.text_input("Sala")
        submitted = st.form_submit_button("Adicionar aluno")
        if submitted:
            if not (numero and nome and ano and sala):
                st.error("Preencha todos os campos!")
                return
            try:
                numero_int = int(numero)
            except:
                st.error("Número deve ser inteiro!")
                return
            dados = st.session_state["dados"]
            if numero_int in dados["Número"].values:
                st.warning("Número já cadastrado!")
                return
            nova_linha = {col: "" for col in colunas}
            nova_linha["Número"] = numero_int
            nova_linha["Aluno"] = nome
            nova_linha["Ano"] = ano
            nova_linha["Sala"] = sala
            st.session_state["dados"] = pd.concat([dados, pd.DataFrame([nova_linha])], ignore_index=True)
            st.success(f"Aluno {nome} adicionado!")

def lancar_notas():
    st.header("Lançamento de Notas")
    dados = st.session_state["dados"]
    if dados.empty:
        st.warning("Nenhum aluno cadastrado.")
        return
    
    anos = sorted(dados["Ano"].dropna().unique())
    ano_sel = st.selectbox("Ano", options=anos)
    salas = sorted(dados.loc[dados["Ano"] == ano_sel, "Sala"].dropna().unique())
    sala_sel = st.selectbox("Sala", options=salas)
    disc_sel = st.selectbox("Disciplina", options=disciplinas_base)

    alunos_filtrados = dados[(dados["Ano"] == ano_sel) & (dados["Sala"] == sala_sel)]
    if alunos_filtrados.empty:
        st.warning("Nenhum aluno encontrado para este filtro.")
        return

    semestre_sel = st.selectbox("Semestre", options=["S1", "S2", "S3", "S4"])

    edit_cols = ["Número", "Aluno", f"{disc_sel} {semestre_sel}", f"{disc_sel} {semestre_sel} Faltas", f"{disc_sel} Conceito Final"]
    df_edit = alunos_filtrados[edit_cols].copy()

    edited_df = st.data_editor(df_edit, num_rows="dynamic")

    if st.button("Salvar notas e faltas"):
        for idx, row in edited_df.iterrows():
            numero = row["Número"]
            idx_df = st.session_state["dados"][st.session_state["dados"]["Número"] == numero].index[0]
            st.session_state["dados"].at[idx_df, f"{disc_sel} {semestre_sel}"] = row[f"{disc_sel} {semestre_sel}"]
            st.session_state["dados"].at[idx_df, f"{disc_sel} {semestre_sel} Faltas"] = row[f"{disc_sel} {semestre_sel} Faltas"]
            st.session_state["dados"].at[idx_df, f"{disc_sel} Conceito Final"] = row[f"{disc_sel} Conceito Final"]
        st.success("Notas, faltas e conceito final atualizados!")

def visualizar_dados():
    st.header("Visualizar Dados")
    st.dataframe(st.session_state["dados"])

def exportar_boletim_xml():
    st.header("Exportar Boletins em XML")
    dados = st.session_state["dados"]
    caminho_xml = st.text_input("Caminho para salvar XML (ex: boletins_xml/Boletim_Completo.xml)", value="boletins_xml/Boletim_Completo.xml")

    if st.button("Gerar XML Completo"):
        try:
            os.makedirs(os.path.dirname(caminho_xml), exist_ok=True)
            dados_xml = pd.DataFrame()
            dados_xml["Num"] = dados["Número"]
            dados_xml["Alun"] = dados["Aluno"]
            dados_xml["Ano"] = dados["Ano"]
            dados_xml["Sala"] = dados["Sala"]

            for disc, prefixo in mapa_prefixos.items():
                for i, semestre in enumerate(["S1", "S2", "S3", "S4"], start=1):
                    dados_xml[f"{prefixo}S{i}"] = dados[f"{disc} {semestre}"]
                    dados_xml[f"{prefixo}F{i}"] = dados[f"{disc} {semestre} Faltas"]
                dados_xml[f"{prefixo}CF"] = dados[f"{disc} Conceito Final"]

            xml_str = '<?xml version="1.0" encoding="UTF-8"?>\n<Boletins>\n'
            for _, row in dados_xml.iterrows():
                xml_str += "  <Aluno>\n"
                for col in dados_xml.columns:
                    xml_str += f"    <{col}>{str(row[col]).strip()}</{col}>\n"
                xml_str += "  </Aluno>\n"
            xml_str += "</Boletins>"

            with open(caminho_xml, "w", encoding="utf-8") as f:
                f.write(xml_str)

            st.success(f"✅ XML exportado com sucesso para: {caminho_xml}")

            with open(caminho_xml, "rb") as f:
                st.download_button("📥 Baixar XML Completo", f, file_name=os.path.basename(caminho_xml), mime="application/xml")
        except Exception as e:
            st.error(f"Erro ao exportar XML: {e}")

    if st.button("Gerar XML por Aluno"):
        try:
            output_dir = os.path.join(os.path.dirname(caminho_xml), "boletins_individuais")
            os.makedirs(output_dir, exist_ok=True)
            for _, aluno in dados.iterrows():
                dados_xml = pd.DataFrame()
                dados_xml["Num"] = [aluno["Número"]]
                dados_xml["Alun"] = [aluno["Aluno"]]
                dados_xml["Ano"] = [aluno["Ano"]]
                dados_xml["Sala"] = [aluno["Sala"]]
                for disc, prefixo in mapa_prefixos.items():
                    for i, semestre in enumerate(["S1", "S2", "S3", "S4"], start=1):
                        dados_xml[f"{prefixo}S{i}"] = [aluno[f"{disc} {semestre}"]]
                        dados_xml[f"{prefixo}F{i}"] = [aluno[f"{disc} {semestre} Faltas"]]
                    dados_xml[f"{prefixo}CF"] = [aluno[f"{disc} Conceito Final"]]
                xml_str = '<?xml version="1.0" encoding="UTF-8"?>\n<Boletins>\n  <Aluno>\n'
                for col in dados_xml.columns:
                    xml_str += f"    <{col}>{str(dados_xml[col][0]).strip()}</{col}>\n"
                xml_str += "  </Aluno>\n</Boletins>"
                nome_arquivo = f"{aluno['Aluno'].replace(' ', '_')}_boletim.xml"
                caminho_final = os.path.join(output_dir, nome_arquivo)
                with open(caminho_final, "w", encoding="utf-8") as f:
                    f.write(xml_str)
            st.success(f"✅ XMLs individuais gerados em: {output_dir}")
        except Exception as e:
            st.error(f"Erro ao gerar XMLs individuais: {e}")

def salvar_csv():
    st.header("Salvar Arquivo CSV")
    caminho_csv = st.text_input("Caminho para salvar o CSV:", value="notas.csv")
    if st.button("Salvar CSV"):
        try:
            st.session_state["dados"].to_csv(caminho_csv, index=False, encoding="utf-8-sig")
            st.success(f"Arquivo salvo em {caminho_csv}")
        except Exception as e:
            st.error(f"Erro ao salvar: {e}")

st.title("📚 Sistema de Gestão Escolar")

if autenticar():
    if "dados" not in st.session_state or st.session_state["dados"] is None:
        dados = pagina_upload_criacao()
        if dados is not None:
            st.session_state["dados"] = dados
        else:
            st.stop()

    pagina = st.sidebar.selectbox("Navegação", [
        "Cadastro de Alunos",
        "Lançamento de Notas",
        "Visualizar Dados",
        "Exportar Boletins em XML",
        "Salvar CSV"
    ])

    if pagina == "Cadastro de Alunos":
        cadastrar_aluno()
    elif pagina == "Lançamento de Notas":
        lancar_notas()
    elif pagina == "Visualizar Dados":
        visualizar_dados()
    elif pagina == "Exportar Boletins em XML":
        exportar_boletim_xml()
    elif pagina == "Salvar CSV":
        salvar_csv()
else:
    st.warning("Por favor, digite a senha para continuar.")
