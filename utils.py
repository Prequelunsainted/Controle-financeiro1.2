from datetime import datetime
import re


def formatar_moeda(valor: float) -> str:
    """Converte um float para a representação monetária brasileira (ex: 1350.5 -> R$ 1.350,50)."""
    if valor is None:
        valor = 0.0
    sinal = "-" if valor < 0 else ""
    valor_abs = abs(valor)
    partes = f"{valor_abs:.2f}".split(".")
    inteiro = partes[0]
    decimal = partes[1]

    # Formata milhares com ponto
    inteiro_formatado = re.sub(r"(\d)(?=(\d{3})+(?!\d))", r"\1.", inteiro)
    return f"{sinal}R$ {inteiro_formatado},{decimal}"


def converter_para_float(valor_str: str) -> float:
    """Converte uma string monetária brasileira ou padronizada para float.

    Aceita: "150.50", "150,50", "1.500,50", "R$ 1.500,50"
    """
    if not valor_str:
        raise ValueError("O valor não pode estar vazio.")

    # Remove R$, espaços e pontos de milhar
    limpo = (
        valor_str.replace("R$", "")
        .replace(" ", "")
        .replace(".", "")
        .strip()
    )
    # Substitui vírgula decimal por ponto
    limpo = limpo.replace(",", ".")

    val = float(limpo)
    if val <= 0:
        raise ValueError("O valor deve ser maior que zero.")
    return val


def validar_data(data_str: str) -> str:
    """Valida se a data está no formato DD/MM/AAAA e é uma data real.

    Retorna a string validada ou lança ValueError.
    """
    if not data_str or not data_str.strip():
        return datetime.now().strftime("%d/%m/%Y")

    data_str = data_str.strip()
    try:
        dt = datetime.strptime(data_str, "%d/%m/%Y")
        return dt.strftime("%d/%m/%Y")
    except ValueError:
        raise ValueError("Data inválida. Use o formato DD/MM/AAAA (ex: 26/08/2026).")