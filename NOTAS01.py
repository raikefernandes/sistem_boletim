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

# Mapeamento dos prefixos curtos
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

def salvar_dados_em_caminho(dados):
    caminho_csv = st.text_input("💾 Caminho para salvar o CSV (ex: C:/meus_dados/notas.csv):", value="notas.csv")
    if st.button("Salvar Arquivo CSV"):
        try:
            dados.to_csv(caminho_csv, index=False)
            st.success(f"Arquivo salvo com sucesso em: {caminho_csv}")
        except Exception as e:
            st.error(f"Erro ao salvar o arquivo: {e}")

def exportar_boletim_xml(dados):
    st.markdown("### 📤 Exportar para XML")
    caminho_xml = st.text_input("Digite o caminho de destino do XML (ex: C:/meus_dados/Boletim_Completo.xml):", value="boletins_xml/Boletim_Completo.xml")

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

    # 🔧 FILTRO POR ANO E SALA (inserido exatamente aqui)
    anos_disponiveis = sorted(dados["Ano"].dropna().unique())
    salas_disponiveis = sorted(dados["Sala"].dropna().unique())

    ano_filtrado = st.selectbox("📅 Selecione o ano:", anos_disponiveis)
    sala_filtrada = st.selectbox("🏫 Selecione a sala:", salas_disponiveis)

    dados_filtrados = dados[(dados["Ano"] == ano_filtrado) & (dados["Sala"] == sala_filtrada)]

    pagina = st.sidebar.selectbox("Escolha uma página:", [
        "Visualizar Dados",
        "Exportar Boletins em XML",
        "Salvar Arquivo CSV"
    ])

    if pagina == "Visualizar Dados":
        st.dataframe(dados_filtrados)

    elif pagina == "Exportar Boletins em XML":
        exportar_boletim_xml(dados_filtrados)

    elif pagina == "Salvar Arquivo CSV":
        salvar_dados_em_caminho(dados_filtrados)

