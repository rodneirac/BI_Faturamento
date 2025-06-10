# Dashboard Kit Faturamento

Este projeto exibe um dashboard interativo para análise de faturamento por Divisão e Mês.

## 📊 Funcionalidades
- KPIs: total de Notas Fiscais, Contratos, Clientes e Obras
- Filtros laterais: Divisão e Mês
- Gráficos interativos com evolução mensal por categoria
- Visualização automática com dados hospedados no GitHub

## 🚀 Como executar localmente

```bash
# Clone o repositório
git clone https://github.com/rodneic/relatorio_faturamento.git
cd relatorio_faturamento

# (Opcional) Crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Instale as dependências
pip install -r requirements.txt

# Execute o app
streamlit run relatorio_faturamento.py
```

## ☁️ Deploy com Streamlit Cloud
1. Acesse: [https://streamlit.io/cloud](https://streamlit.io/cloud)
2. Clique em **"New app"**
3. Conecte sua conta GitHub e selecione este repositório
4. Escolha o arquivo `relatorio_faturamento.py`
5. Clique em **Deploy**

## 🗂 Estrutura esperada
```
├── relatorio_faturamento.py   # Código principal do dashboard
├── DADOSZSD065.XLSX           # Planilha de dados hospedada no GitHub
├── logo.png                   # Logo exibido no topo do app
├── requirements.txt           # Dependências do projeto
└── README.md                  # Este arquivo
```

## 🖼 Exemplo de visualização
(Adicione aqui um print da tela do app depois de deployado)

---

Mantenha os arquivos `DADOSZSD065.XLSX` e `logo.png` no repositório para garantir o funcionamento automático do app.

Para sugestões, melhorias ou contribuições, fique à vontade para abrir uma *issue* ou *pull request*.
