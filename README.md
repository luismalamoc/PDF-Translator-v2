# PDF-Translator-v2
A PDF Translator using AI 
<div align="center">

# 📄 PDF Translator v2

### Translate any PDF instantly using AI — free and fast

[![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Groq](https://img.shields.io/badge/Powered%20by-Groq%20%2B%20Llama-orange?style=flat)](https://console.groq.com/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat)](LICENSE)

[English](#english) • [Português](#português)

</div>

---

## English

### 📌 About

**PDF Translator v2** is a desktop application that translates PDF documents using AI. It extracts the original text, translates it while respecting the paragraph structure and context, and generates a new formatted PDF — all through a simple and intuitive interface.

Built as a portfolio project to demonstrate integration between Python, AI APIs, PDF manipulation, and GUI development.

---

### ✨ Features

- 🌍 Translate to 10 languages: Portuguese, English, Spanish, French, German, Italian, Japanese, Chinese, Russian and Arabic
- 📝 Preserves paragraph structure and document context
- 🚀 Fast translation powered by **Groq + Llama 3.3 70B**
- 🖥️ Clean and simple desktop interface
- 📊 Real-time progress bar per page
- 💡 Auto-suggests output file name and path
- 🔑 Supports API key via environment variable

---

### 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python 3.9+ | Core language |
| Tkinter | Desktop GUI |
| pdfplumber | PDF text extraction |
| ReportLab | Translated PDF generation |
| Groq API | AI translation (Llama 3.3 70B) |

---

### 📦 Download

Download the latest Windows executable (`.exe`) from the [Releases](../../releases) page — no Python installation required.

---

### ⚙️ Installation (for developers)

**1. Clone the repository**
```bash
git clone https://github.com/ArturBrazLopes/PDF-Translator-v2.git
cd PDF-Translator-v2
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Run the app**
```bash
python interface.py
```

---

### 🔑 How to get your free Groq API key

The app uses Groq's AI to translate your PDF. To use it, you need a free API key — think of it as a personal password that connects the app to the AI service. Here's how to get one:

1. Go to **[console.groq.com](https://console.groq.com)**
2. Click **"Sign Up"** and create a free account (you can use your Google account)
3. After logging in, look for **"API Keys"** in the left sidebar menu
4. Click **"Create API Key"**, give it any name you like (e.g. "pdf-translator") and confirm
5. A long code will appear — it starts with `gsk_...` — **copy it right away**, as it won't be shown again
6. Paste that code into the **"Groq API Key"** field inside the app

> ⚠️ **Important:** keep your API key private. Don't share it with others or post it online.

---

### 🚀 How to use

1. Open the app and click **"Choose file"** to select your PDF
2. Choose where to save the translated file (if you skip this, it saves automatically next to the original)
3. Select the **target language** from the dropdown menu
4. Paste your **Groq API key** into the key field
5. Click **"Translate PDF"** and wait — the progress bar shows each page being translated
6. When done, the app will ask if you want to open the translated file automatically

---

### ⚠️ Limitations

- Works with text-based PDFs only — scanned documents (photos of pages) are not supported
- Groq free tier: 14,400 requests/day and 6,000 tokens/minute
- Very large PDFs may take longer since they are processed page by page

---

## Português

### 📌 Sobre

**PDF Translator v2** é uma aplicação desktop que traduz documentos PDF usando inteligência artificial. Ele extrai o texto original, traduz respeitando a estrutura de parágrafos e o contexto, e gera um novo PDF formatado — tudo por meio de uma interface simples e intuitiva.

Desenvolvido como projeto de portfólio para demonstrar integração entre Python, APIs de IA, manipulação de PDFs e desenvolvimento de interfaces gráficas.

---

### ✨ Funcionalidades

- 🌍 Traduz para 10 idiomas: Português, Inglês, Espanhol, Francês, Alemão, Italiano, Japonês, Chinês, Russo e Árabe
- 📝 Preserva a estrutura de parágrafos e o contexto do documento
- 🚀 Tradução rápida com **Groq + Llama 3.3 70B**
- 🖥️ Interface desktop limpa e simples
- 📊 Barra de progresso em tempo real por página
- 💡 Sugere automaticamente o nome e o caminho do arquivo de saída
- 🔑 Suporta chave de API via variável de ambiente

---

### 🛠️ Tecnologias

| Tecnologia | Uso |
|---|---|
| Python 3.9+ | Linguagem principal |
| Tkinter | Interface gráfica |
| pdfplumber | Extração de texto do PDF |
| ReportLab | Geração do PDF traduzido |
| Groq API | Tradução com IA (Llama 3.3 70B) |

---

### 📦 Download

Baixe o executável para Windows (`.exe`) na página de [Releases](../../releases) — sem precisar instalar nada.

---

### ⚙️ Instalação (para desenvolvedores)

**1. Clone o repositório**
```bash
git clone https://github.com/ArturBrazLopes/PDF-Translator-v2.git
cd PDF-Translator-v2
```

**2. Instale as dependências**
```bash
pip install -r requirements.txt
```

**3. Execute o programa**
```bash
python interface.py
```

---

### 🔑 Como obter sua chave de API gratuita do Groq

O aplicativo usa a IA do Groq para traduzir seu PDF. Para isso, você precisa de uma chave de API gratuita — pense nela como uma senha pessoal que conecta o programa ao serviço de inteligência artificial. Veja como obter a sua:

1. Acesse **[console.groq.com](https://console.groq.com)**
2. Clique em **"Sign Up"** e crie uma conta gratuita (pode usar sua conta do Google)
3. Após entrar, procure no menu do lado esquerdo a opção **"API Keys"**
4. Clique em **"Create API Key"**, dê qualquer nome para ela (ex: "pdf-translator") e confirme
5. Um código longo vai aparecer na tela — ele começa com `gsk_...` — **copie imediatamente**, pois ele não será exibido novamente
6. Cole esse código no campo **"Groq API Key"** dentro do aplicativo

> ⚠️ **Importante:** mantenha sua chave em segredo. Não a compartilhe com outras pessoas nem publique na internet.

---

### 🚀 Como usar

1. Abra o aplicativo e clique em **"Choose file"** para selecionar o PDF
2. Escolha onde salvar o arquivo traduzido (se pular essa etapa, ele é salvo automaticamente na mesma pasta do original)
3. Selecione o **idioma de destino** no menu
4. Cole sua **chave de API do Groq** no campo indicado
5. Clique em **"Translate PDF"** e aguarde — a barra de progresso mostra cada página sendo traduzida
6. Ao finalizar, o aplicativo pergunta se você quer abrir o arquivo traduzido automaticamente

---

### ⚠️ Limitações

- Funciona apenas com PDFs de texto — documentos escaneados (fotos de páginas) não são suportados
- Plano gratuito do Groq: 14.400 requisições por dia e 6.000 tokens por minuto
- PDFs muito grandes podem demorar mais, pois são processados página por página

---

### 📃 Licença / License

MIT License — free to use, modify and distribute. / Livre para usar, modificar e distribuir.

---

<div align="center">
Made by <a href="https://github.com/ArturBrazLopes">ArturBrazLopes</a>
</div>