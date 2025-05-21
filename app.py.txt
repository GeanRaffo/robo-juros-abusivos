import streamlit as st
import requests

CODIGOS_BACEN = {
    'pessoal': 25401,
    'veicular': 25402,
    'imobiliario': 25404,
    'reforma': 25403  # Supondo que exista
}

def obter_taxa_bacen(tipo_emprestimo):
    codigo = CODIGOS_BACEN.get(tipo_emprestimo)
    if not codigo:
        return None
    url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados/ultimos/1?formato=json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return float(data[0]['valor'].replace(",", ".")) / 100
    return None

def calcular_juros_aproximado(valor, parcela, num_parcelas):
    total_pago = parcela * num_parcelas
    juros_total = total_pago - valor
    return (juros_total / valor) / num_parcelas

st.title("🔎 Verificador de Juros Abusivos")
st.write("Verifique se os juros do seu empréstimo são abusivos com base nos dados do Banco Central.")

tipo = st.selectbox("Tipo de empréstimo", ["pessoal", "veicular", "imobiliario", "reforma"])
valor_emprestado = st.number_input("Valor emprestado (R$)", min_value=100.0)
valor_parcela = st.number_input("Valor da parcela (R$)", min_value=10.0)
num_parcelas = st.number_input("Número de parcelas", min_value=1, step=1)

if st.button("Verificar"):
    taxa_media = obter_taxa_bacen(tipo)
    if taxa_media:
        juros_calc = calcular_juros_aproximado(valor_emprestado, valor_parcela, num_parcelas)
        resultado = "🚨 POSSÍVEL ABUSO" if juros_calc > (taxa_media + 0.01) else "✅ Dentro da média"

        st.metric("Taxa média do mercado (BACEN)", f"{taxa_media*100:.2f}% ao mês")
        st.metric("Taxa do seu contrato", f"{juros_calc*100:.2f}% ao mês")
        st.success(f"Resultado: {resultado}")
    else:
        st.error("Erro ao obter taxa média para o tipo de empréstimo selecionado.")
