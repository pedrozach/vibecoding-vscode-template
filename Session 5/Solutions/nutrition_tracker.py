import os
import json
import requests
import unicodedata
from dotenv import load_dotenv
from config import metas

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")


def dados_mock(alimento, gramas=100):
    amostras = {
        "frango": {"nome": "frango", "calorias": 165, "proteinas": 31, "carboidratos": 0, "gorduras": 3.6, "ferro": 1.0, "potassio": 300, "selenio": 30, "calcio": 15, "vitamina_d": 0.1, "vitamina_c": 0.0, "vitamina_b6": 0.4, "vitamina_b12": 0.3, "fibra": 0.0},
        "arroz": {"nome": "arroz", "calorias": 130, "proteinas": 2.7, "carboidratos": 28, "gorduras": 0.3, "ferro": 0.8, "potassio": 115, "selenio": 15, "calcio": 10, "vitamina_d": 0.0, "vitamina_c": 0.0, "vitamina_b6": 0.1, "vitamina_b12": 0.0, "fibra": 1.3},
        "salmão": {"nome": "salmão", "calorias": 208, "proteinas": 22, "carboidratos": 0, "gorduras": 13, "ferro": 0.8, "potassio": 363, "selenio": 36, "calcio": 12, "vitamina_d": 13.0, "vitamina_c": 0.0, "vitamina_b6": 0.4, "vitamina_b12": 3.2, "fibra": 0.0},
        "banana": {"nome": "banana", "calorias": 89, "proteinas": 1.1, "carboidratos": 22.8, "gorduras": 0.3, "ferro": 0.3, "potassio": 358, "selenio": 1.0, "calcio": 5, "vitamina_d": 0.0, "vitamina_c": 8.7, "vitamina_b6": 0.4, "vitamina_b12": 0.0, "fibra": 2.6},
        "ovo": {"nome": "ovo", "calorias": 155, "proteinas": 13, "carboidratos": 1.1, "gorduras": 11, "ferro": 1.8, "potassio": 126, "selenio": 30, "calcio": 56, "vitamina_d": 1.1, "vitamina_c": 0.0, "vitamina_b6": 0.1, "vitamina_b12": 1.1, "fibra": 0.0},
        "feijão": {"nome": "feijão", "calorias": 132, "proteinas": 8.7, "carboidratos": 24, "gorduras": 0.5, "ferro": 2.1, "potassio": 364, "selenio": 2.0, "calcio": 40, "vitamina_d": 0.0, "vitamina_c": 0.0, "vitamina_b6": 0.2, "vitamina_b12": 0.0, "fibra": 6.4},
        "iogurte": {"nome": "iogurte", "calorias": 61, "proteinas": 3.5, "carboidratos": 4.7, "gorduras": 3.3, "ferro": 0.1, "potassio": 155, "selenio": 3.0, "calcio": 121, "vitamina_d": 0.1, "vitamina_c": 0.0, "vitamina_b6": 0.1, "vitamina_b12": 0.5, "fibra": 0.0},
    }

    def normalizar_chave(valor):
        valor = unicodedata.normalize("NFKD", valor.lower().strip())
        return "".join(ch for ch in valor if not unicodedata.combining(ch))

    chave = normalizar_chave(alimento)
    dado = None
    for nome, dados in amostras.items():
        if normalizar_chave(nome) == chave:
            dado = dados
            break
    if not dado:
        return {
            "nome": alimento,
            "calorias": 100,
            "proteinas": 5,
            "carboidratos": 10,
            "gorduras": 3,
            "ferro": 1,
            "potassio": 150,
            "selenio": 5,
            "calcio": 50,
            "vitamina_d": 0.5,
            "vitamina_c": 5,
            "vitamina_b6": 0.2,
            "vitamina_b12": 0.3,
            "fibra": 2,
        }

    fator = gramas / 100
    resultado = {
        "nome": dado["nome"],
        "calorias": round(dado["calorias"] * fator, 1),
        "proteinas": round(dado["proteinas"] * fator, 1),
        "carboidratos": round(dado["carboidratos"] * fator, 1),
        "gorduras": round(dado["gorduras"] * fator, 1),
    }

    for chave_nutriente in ["ferro", "potassio", "selenio", "calcio", "vitamina_d", "vitamina_c", "vitamina_b6", "vitamina_b12", "fibra"]:
        resultado[chave_nutriente] = round(dado.get(chave_nutriente, 0) * fator, 2)

    return resultado


def consultar_nutricao(alimento, gramas=100):
    print("⚠️  Usando dados mockados.")
    return dados_mock(alimento, gramas)

    if not api_key:
        print("⚠️  GEMINI_API_KEY não configurada; usando dados mockados.")
        return dados_mock(alimento, gramas)

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"

    prompt = f"""
    Retorne os dados nutricionais de {gramas}g de {alimento}.
    Responda APENAS com um JSON válido, sem texto adicional, neste formato:
    {{
        "nome": "nome do alimento",
        "calorias": 0,
        "proteinas": 0,
        "carboidratos": 0,
        "gorduras": 0
    }}
    """

    body = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    try:
        resposta = requests.post(url, json=body, timeout=30)
        resposta.raise_for_status()
        dados = resposta.json()
        texto = dados["candidates"][0]["content"]["parts"][0]["text"]
        texto_limpo = texto.strip().replace("```json", "").replace("```", "").strip()
        return json.loads(texto_limpo)
    except Exception as erro:
        print(f"⚠️  Erro ao consultar a API: {erro}; usando dados mockados.")
        return dados_mock(alimento, gramas)

def mostrar_relatorio(alimento, gramas=100):
    resultado = consultar_nutricao(alimento, gramas)
    
    if not resultado:
        print(f"❌ Não encontrei '{alimento}'.")
        return

    calorias = round(resultado["calorias"])
    proteinas = round(resultado["proteinas"], 1)
    carboidratos = round(resultado["carboidratos"], 1)
    gorduras = round(resultado["gorduras"], 1)

    print(f"\n🍽️  {gramas}g de {resultado['nome']}")
    print("━" * 40)
    print(f"Calorias:      {calorias} kcal  ({round(calorias/metas['calorias']*100)}% da meta diária)")
    print(f"Proteínas:     {proteinas}g  ({round(proteinas/metas['proteinas']*100)}% da meta diária)")
    print(f"Carboidratos:  {carboidratos}g  ({round(carboidratos/metas['carboidratos']*100)}% da meta diária)")
    print(f"Gorduras:      {gorduras}g  ({round(gorduras/metas['gorduras']*100)}% da meta diária)")

    micronutrientes = [
        ("Ferro", "ferro", "mg"),
        ("Potássio", "potassio", "mg"),
        ("Selênio", "selenio", "mcg"),
        ("Cálcio", "calcio", "mg"),
        ("Vitamina D", "vitamina_d", "mcg"),
        ("Vitamina C", "vitamina_c", "mg"),
        ("Vitamina B6", "vitamina_b6", "mg"),
        ("Vitamina B12", "vitamina_b12", "mcg"),
        ("Fibra", "fibra", "g"),
    ]

    print("Micronutrientes:")
    for nome, chave, unidade in micronutrientes:
        valor = resultado.get(chave)
        if valor is None:
            continue
        meta = metas.get(nome)
        percentual = f" ({round(valor/meta*100)}% da meta diária)" if meta else ""
        print(f"- {nome:<12}: {valor:.2f}{unidade}{percentual}")
    print("━" * 40)

if __name__ == "__main__":
    print("🥗 Bem-vinda ao NutriTracker!")
    print("━" * 40)
    alimento = input("Qual alimento quer consultar? ")
    gramas = input("Quantas gramas? ")
    mostrar_relatorio(alimento, gramas=int(gramas))

    while True:
        print("\nQuer consultar outro alimento?")
        continuar = input("Digite 's' para sim ou 'n' para sair: ").strip().lower()
        if continuar != "s":
            break
        alimento = input("Qual alimento? ")
        gramas = input("Quantas gramas? ")
        mostrar_relatorio(alimento, gramas=int(gramas))

    print("\n✅ Até a próxima, cuida da alimentação!")