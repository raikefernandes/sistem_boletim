import streamlit as st
import pandas as pd
import io
import os

st.set_page_config(page_title="Sistema de Gestão Escolar", page_icon="📚", layout="centered")

def autenticar():
    senha_correta = "admin123"
    senha = st.text_input("Digite a senha:", type="password")
    if senha == senha_correta:
        return True
    elif senha:
        st.error("Senha incorreta!")
    return False

# Disciplinas e colunas
disciplinas_base = [
    "Língua Portuguesa", "Matemática", "Inglês", "História", "Geografia",
    "Ciências", "Artes", "Educação Física", "filosofia", "Educação Religiosa"
]

colunas = ["Número", "Aluno", "Ano", "Sala"]
for disc in disciplinas_base:
    for semestre in ["S1", "S2", "S3", "S4"]:
        colunas.append(f"{disc} {semestre}")
        colunas.append(f"{disc} {semestre} Faltas")
    colunas.append(f"{disc} Conceito Final")

mapa_prefixos = {
    "Língua Portuguesa": "Lp",
    "Matemática": "Mat",
    "Inglês": "Ing",
    "História": "His",
    "Geografia": "Geo",
    "Ciências": "Cie",
    "Artes": "Arte",
    "Educação Física": "EdFi",
    "filosofia": "Filo",
    "Educação Religiosa": "EdRe"
}

def baixar_csv(dados):
    csv_buffer = io.StringIO()
    dados.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)
    st.download_button(
        label="💾 Baixar arquivo CSV",
        data=csv_buffer,
        file_name="notas.csv",
        mime="text/csv"
    )

def exportar_boletim_xml(dados):
    st.markdown("### 📤 Exportar para XML")

    if st.button("Gerar XML Completo"):
        try:
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

            xml_bytes = xml_str.encode('utf-8')

            st.download_button(
                label="📥 Baixar XML Completo",
                data=xml_bytes,
                file_name="Boletim_Completo.xml",
                mime="application/xml"
            )
        except Exception as e:
            st.error(f"Erro ao exportar XML: {e}")

    if st.button("Gerar XMLs Individuais"):
        try:
            st.markdown("### ⬇️ Downloads dos XMLs Individuais")
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

                xml_bytes = xml_str.encode('utf-8')
                nome_arquivo = f"{aluno['Aluno'].replace(' ', '_')}_boletim.xml"

                st.download_button(
                    label=f"📥 Baixar XML de {aluno['Aluno']}",
                    data=xml_bytes,
                    file_name=nome_arquivo,
                    mime="application/xml"
                )
        except Exception as e:
            st.error(f"Erro ao gerar XMLs individuais: {e}")

st.title("📚 Sistema de Gestão Escolar")

if autenticar():
    st.success("Acesso concedido ✅")

    uploaded_file = st.file_uploader("📂 Selecione o arquivo de notas (CSV):", type="csv")

    if uploaded_file:
        dados = pd.read_csv(uploaded_file)
        if not all(col in dados.columns for col in colunas):
            st.error("❌ As colunas do arquivo estão incompatíveis.")
            st.stop()
    else:
        st.warning("⚠️ Nenhum arquivo CSV carregado.")
        if st.button("📋 Criar nova tabela do zero"):
            dados = pd.DataFrame(columns=colunas)
            st.success("Tabela criada com sucesso!")
        else:
            st.stop()

    pagina = st.sidebar.selectbox("Escolha uma página:", [
        "Visualizar Dados",
        "Exportar Boletins em XML",
        "Salvar Arquivo CSV",
        "Lançar Notas"
    ])

    if pagina == "Visualizar Dados":
        st.markdown("### 🔍 Filtros de Visualização")
        anos_disponiveis = dados["Ano"].dropna().unique()
        salas_disponiveis = dados["Sala"].dropna().unique()
        ano_selecionado = st.selectbox("Selecione o Ano:", sorted(anos_disponiveis))
        sala_selecionada = st.selectbox("Selecione a Sala:", sorted(salas_disponiveis))
        dados_filtrados = dados[(dados["Ano"] == ano_selecionado) & (dados["Sala"] == sala_selecionada)]
        st.markdown(f"### 📋 Alunos do Ano {ano_selecionado}, Sala {sala_selecionada}")
        st.dataframe(dados_filtrados)

    elif pagina == "Exportar Boletins em XML":
        exportar_boletim_xml(dados)

    elif pagina == "Salvar Arquivo CSV":
        baixar_csv(dados)

    elif pagina == "Lançar Notas":
        st.header("📝 Lançamento de Notas por Ano e Sala")
        anos_disponiveis = dados["Ano"].dropna().unique()
        salas_disponiveis = dados["Sala"].dropna().unique()
        ano_escolhido = st.selectbox("Selecione o Ano:", sorted(anos_disponiveis))
        sala_escolhida = st.selectbox("Selecione a Sala:", sorted(salas_disponiveis))
        dados_filtrados = dados[(dados["Ano"] == ano_escolhido) & (dados["Sala"] == sala_escolhida)]

        if dados_filtrados.empty:
            st.warning("Nenhum aluno encontrado para o Ano e Sala selecionados.")
        else:
            aluno_selecionado = st.selectbox("Selecione o Aluno:", dados_filtrados["Aluno"])
            aluno_idx = dados[(dados["Ano"] == ano_escolhido) & (dados["Sala"] == sala_escolhida) & (dados["Aluno"] == aluno_selecionado)].index[0]

            for disc in disciplinas_base:
                st.subheader(f"📘 {disc}")
                for semestre in ["S1", "S2", "S3", "S4"]:
                    nota = st.text_input(f"Nota {semestre} - {disc}", value=str(dados.at[aluno_idx, f"{disc} {semestre}"]))
                    faltas = st.text_input(f"Faltas {semestre} - {disc}", value=str(dados.at[aluno_idx, f"{disc} {semestre} Faltas"]))
                    dados.at[aluno_idx, f"{disc} {semestre}"] = nota
                    dados.at[aluno_idx, f"{disc} {semestre} Faltas"] = faltas

                conceito = st.text_input(f"Conceito Final - {disc}", value=str(dados.at[aluno_idx, f"{disc} Conceito Final"]))
                dados.at[aluno_idx, f"{disc} Conceito Final"] = conceito

            if st.button("💾 Salvar Lançamento"):
                st.success(f"Notas salvas para {aluno_selecionado} - {ano_escolhido} {sala_escolhida}")

