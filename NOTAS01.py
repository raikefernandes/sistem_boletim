import streamlit as st
import pandas as pd
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

def exportar_csv_estilo_xml(dados):
    try:
        dados_export = pd.DataFrame()
        dados_export["Num"] = dados["Número"]
        dados_export["Alun"] = dados["Aluno"]
        dados_export["Ano"] = dados["Ano"]
        dados_export["Sala"] = dados["Sala"]
        for disc, prefixo in mapa_prefixos.items():
            for i, semestre in enumerate(["S1", "S2", "S3", "S4"], start=1):
                dados_export[f"{prefixo}S{i}"] = dados[f"{disc} {semestre}"]
                dados_export[f"{prefixo}F{i}"] = dados[f"{disc} {semestre} Faltas"]
            dados_export[f"{prefixo}CF"] = dados[f"{disc} Conceito Final"]
        csv_str = dados_export.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Baixar CSV no Esquema XML",
            data=csv_str,
            file_name="notas_esquema_xml.csv",
            mime="text/csv"
        )
    except Exception as e:
        st.error(f"Erro ao exportar CSV: {e}")

def exportar_boletim_xml(dados):
    st.markdown("### 📤 Exportar para XML")

    if st.button("Gerar XML Completo"):
        try:
            xml_str = '<?xml version="1.0" encoding="UTF-8"?>\n<Boletins>\n'

            for _, row in dados.iterrows():
                xml_str += "  <Aluno>\n"
                xml_str += f"    <Num>{row['Número']}</Num>\n"
                xml_str += f"    <Alun>{row['Aluno']}</Alun>\n"
                xml_str += f"    <Ano>{row['Ano']}</Ano>\n"
                xml_str += f"    <Sala>{row['Sala']}</Sala>\n"

                for disc, prefixo in mapa_prefixos.items():
                    for i, semestre in enumerate(["S1", "S2", "S3", "S4"], start=1):
                        nota = row.get(f"{disc} {semestre}", "nan")
                        faltas = row.get(f"{disc} {semestre} Faltas", "nan")
                        xml_str += f"    <{prefixo}S{i}>{nota}</{prefixo}S{i}>\n"
                        xml_str += f"    <{prefixo}F{i}>{faltas}</{prefixo}F{i}>\n"
                    conceito = row.get(f"{disc} Conceito Final", "nan")
                    xml_str += f"    <{prefixo}CF>{conceito}</{prefixo}CF>\n"

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
            for _, row in dados.iterrows():
                xml_str = '<?xml version="1.0" encoding="UTF-8"?>\n<Boletins>\n'
                xml_str += "  <Aluno>\n"
                xml_str += f"    <Num>{row['Número']}</Num>\n"
                xml_str += f"    <Alun>{row['Aluno']}</Alun>\n"
                xml_str += f"    <Ano>{row['Ano']}</Ano>\n"
                xml_str += f"    <Sala>{row['Sala']}</Sala>\n"

                for disc, prefixo in mapa_prefixos.items():
                    for i, semestre in enumerate(["S1", "S2", "S3", "S4"], start=1):
                        nota = row.get(f"{disc} {semestre}", "nan")
                        faltas = row.get(f"{disc} {semestre} Faltas", "nan")
                        xml_str += f"    <{prefixo}S{i}>{nota}</{prefixo}S{i}>\n"
                        xml_str += f"    <{prefixo}F{i}>{faltas}</{prefixo}F{i}>\n"
                    conceito = row.get(f"{disc} Conceito Final", "nan")
                    xml_str += f"    <{prefixo}CF>{conceito}</{prefixo}CF>\n"

                xml_str += "  </Aluno>\n</Boletins>"

                xml_bytes = xml_str.encode('utf-8')
                nome_arquivo = f"{row['Aluno'].replace(' ', '_')}_boletim.xml"
                st.download_button(
                    label=f"📥 Baixar XML de {row['Aluno']}",
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
        exportar_csv_estilo_xml(dados)

    elif pagina == "Lançar Notas":
        st.header("📝 Lançamento de Notas por Disciplina e Semestre")

        anos_disponiveis = dados["Ano"].dropna().unique()
        salas_disponiveis = dados["Sala"].dropna().unique()
        ano_escolhido = st.selectbox("Selecione o Ano:", sorted(anos_disponiveis))
        sala_escolhida = st.selectbox("Selecione a Sala:", sorted(salas_disponiveis))
        disciplina_escolhida = st.selectbox("Selecione a Disciplina:", disciplinas_base)
        semestre_escolhido = st.selectbox("Selecione o Semestre:", ["S1", "S2", "S3", "S4"])

        dados_filtrados = dados[(dados["Ano"] == ano_escolhido) & (dados["Sala"] == sala_escolhida)]

        if dados_filtrados.empty:
            st.warning("Nenhum aluno encontrado para o Ano e Sala selecionados.")
        else:
            st.markdown(f"### Alunos da turma - {disciplina_escolhida} - {semestre_escolhido}")
            for idx, aluno in dados_filtrados.iterrows():
                st.subheader(f"👤 {aluno['Aluno']}")

                nota_key = f"{disciplina_escolhida} {semestre_escolhido}"
                falta_key = f"{disciplina_escolhida} {semestre_escolhido} Faltas"

                nota = st.text_input(f"{aluno['Aluno']} - Nota {semestre_escolhido}", value=str(dados.at[idx, nota_key]), key=f"nota_{idx}")
                faltas = st.text_input(f"{aluno['Aluno']} - Faltas {semestre_escolhido}", value=str(dados.at[idx, falta_key]), key=f"falta_{idx}")

                dados.at[idx, nota_key] = nota
                dados.at[idx, falta_key] = faltas

            if st.button("💾 Salvar Notas do Semestre"):
                try:
                    csv_str = dados.to_csv(index=False).encode('utf-8')
                    st.success("Notas e faltas salvas com sucesso!")
                    st.download_button(
                        label="📥 Baixar CSV Atualizado",
                        data=csv_str,
                        file_name="notas_atualizado.csv",
                        mime="text/csv"
                    )
                except Exception as e:
                    st.error(f"Erro ao gerar o arquivo: {e}")
