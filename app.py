import streamlit as st
import requests

# Dicionário de códigos da API por tipo de empréstimo
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
        taxa_anual = float(data[0]['valor'].replace(",", ".")) / 100
        taxa_mensal = (1 + taxa_anual) ** (1/12) - 1
        return taxa_mensal
    return None

# Cálculo de taxa de juros real (juros compostos) com método da taxa implícita
def calcular_taxa_juros_mensal(valor_presente, parcela, num_parcelas):
    taxa = 0.01
    precisao = 0.00001
    max_iter = 1000
    for _ in range(max_iter):
        valor_calculado = sum([parcela / (1 + taxa) ** i for i in range(1, num_parcelas + 1)])
        erro = valor_presente - valor_calculado
        if abs(erro) < precisao:
            return taxa
        taxa += erro / valor_presente / 10
    return taxa

# Cálculo da nova parcela se juros forem ajustados à média do Bacen
def calcular_parcela_com_taxa(valor_presente, taxa, num_parcelas):
    if taxa == 0:
        return valor_presente / num_parcelas
    return valor_presente * taxa / (1 - (1 + taxa) ** (-num_parcelas))

# Interface do App
st.title("🔎 Verificador de Juros Abusivos Bancários")
st.write("Compare os juros do seu contrato com as taxas médias praticadas segundo o Banco Central.")

tipo = st.selectbox("Tipo de empréstimo", ["pessoal", "veicular", "imobiliario", "reforma"])
valor_emprestado = st.number_input("Valor originalmente emprestado (R$)", min_value=100.0)
valor_parcela = st.number_input("Valor da parcela (R$)", min_value=10.0)
num_parcelas = st.number_input("Total de parcelas contratadas", min_value=1, step=1)
parcelas_pagas = st.number_input("Quantas parcelas já foram pagas?", min_value=0, max_value=int(num_parcelas), step=1)

if st.button("Verificar"):
    taxa_media = obter_taxa_bacen(tipo)
    if taxa_media:
        # Cálculo da taxa contratada
        juros_calc = calcular_taxa_juros_mensal(valor_emprestado, valor_parcela, int(num_parcelas))
        
        # Cálculo de parcela justa com base na taxa do Bacen
        parcela_justa = calcular_parcela_com_taxa(valor_emprestado, taxa_media, int(num_parcelas))

        # Cálculo da economia possível futura
        parcelas_restantes = int(num_parcelas - parcelas_pagas)
        economia = (valor_parcela - parcela_justa) * parcelas_restantes if parcela_justa < valor_parcela else 0

        # Resultado
        resultado = "🚨 POSSÍVEL ABUSO" if juros_calc > (taxa_media + 0.01) else "✅ Dentro da média"

        st.metric("Taxa média do mercado (BACEN)", f"{taxa_media*100:.2f}% ao mês")
        st.metric("Taxa do seu contrato", f"{juros_calc*100:.2f}% ao mês")
        st.metric("Resultado", resultado)

        st.markdown("---")
        st.subheader("📉 Simulação com taxa média do Bacen")
        st.write(f"Parcela original: **R${valor_parcela:.2f}**")
        st.write(f"Parcela ideal estimada (com taxa do Bacen): **R${parcela_justa:.2f}**")
        st.write(f"Parcelas restantes: **{parcelas_restantes}**")
        st.write(f"💰 Possível economia nas parcelas futuras: **R${economia:.2f}**")

    else:
        st.error("Erro ao obter taxa média para o tipo de empréstimo selecionado.")
