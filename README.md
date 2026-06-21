<div align="center">

# 📄 PDF Translator v2

### Translate any PDF instantly using AI — free and fast

[![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat)](LICENSE)

[English](#english) • [Português](#português)

</div>

---

## English

### 📌 About

**PDF Translator v2** is a desktop application that translates PDF documents using AI. It extracts the original text, translates it while respecting paragraph structure and context, and generates a new formatted PDF — all through a simple and intuitive interface.

Built as a portfolio project to demonstrate integration between Python, AI APIs, PDF manipulation, and GUI development.

---

### ✨ Features

- 🌍 Translate to 10 languages: Portuguese, English, Spanish, French, German, Italian, Japanese, Chinese, Russian and Arabic
- 📝 Detects and preserves titles, bold text, lists and paragraph structure
- 🤖 Support for multiple AI providers: **Groq, Gemini, OpenRouter and Ollama (local)**
- 📷 **OCR support for scanned PDFs** — image-only pages are automatically detected and processed
- 🖥️ Clean and simple desktop interface with real-time progress and pipeline log
- 💡 Auto-suggests output file name and path
- 🔒 Supports API key via environment variable

---

### 🤖 AI Providers

| Provider | Quality | Speed | Cost | Status |
|---|---|---|---|---|
| **Groq** | ⭐⭐⭐⭐⭐ | ⚡ Very fast | Free (1,400 req/day) | ✅ Recommended |
| **Ollama** | ⭐⭐⭐⭐ | 🐢 Depends on hardware | Free forever | ✅ Works great |
| **OpenRouter** | ⭐⭐⭐⭐ | ⚡ Fast | Free (limited) | ⚠️ Unstable free tier |
| **Gemini** | ⭐⭐⭐⭐⭐ | ⚡ Fast | Free (limited) | ⚠️ Regional issues |

> **Recommendation:** Use **Groq** for best results online, or **Ollama** for complete privacy with no internet required.

---

### 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python 3.9+ | Core language |
| Tkinter | Desktop GUI |
| pdfplumber | PDF text extraction with formatting detection |
| ReportLab | Translated PDF generation |
| pytesseract + Pillow | OCR for scanned PDFs |
| Groq API | AI translation (Llama 3.3 70B) |
| Ollama | Local AI inference |

---

### 📦 Download

Download the latest Windows executable (`.exe`) from the [Releases](../../releases) page — no Python installation required.

> ⚠️ **For OCR support:** Tesseract must be installed separately. See the [Tesseract setup guide](#tesseract-ocr-for-scanned-pdfs) below.

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

### 🔍 Tesseract OCR (for scanned PDFs)

Tesseract is a free OCR engine that lets the app read scanned or image-only PDFs. It must be installed separately on your system.

**Windows**

1. Download the installer from **[github.com/UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki)**
   - Choose the `tesseract-ocr-w64-setup-x.x.x.exe` (64-bit) file
2. During installation:
   - Check **"Add to PATH"** when prompted
   - Under **Additional language data**, select **Portuguese** (and any other languages you need)
3. After installation, open a new terminal and verify:
```bash
tesseract --version
```
4. If the command is not recognized, add it manually to PATH:
   - Search for **"Environment Variables"** in Windows settings
   - Edit the **Path** variable under System variables
   - Add: `C:\Program Files\Tesseract-OCR`
   - Open a new terminal and try again

**Linux**
```bash
sudo apt install tesseract-ocr tesseract-ocr-por
```

**macOS**
```bash
brew install tesseract
```

> Once Tesseract is installed, OCR works automatically — scanned pages are detected and processed without any extra steps in the app.

---

### 🔑 How to get your free Groq API key

The app uses Groq's AI to translate your PDF. To use it, you need a free API key — think of it as a personal password that connects the app to the AI service. Here's how to get one:

1. Go to **[console.groq.com](https://console.groq.com)**
2. Click **"Sign Up"** and create a free account (you can use your Google account)
3. After logging in, look for **"API Keys"** in the left sidebar menu
4. Click **"Create API Key"**, give it any name you like (e.g. "pdf-translator") and confirm
5. A long code will appear — it starts with `gsk_...` — **copy it right away**, as it won't be shown again
6. Paste that code into the **"API Key"** field inside the app

> ⚠️ **Important:** keep your API key private. Don't share it with others or post it online.

---

### 🦙 How to use Ollama (local AI — no internet required)

Ollama lets you run AI translation entirely on your own computer — no API key, no internet, no data sent anywhere.

**Step 1 — Install Ollama**

Download and install from **[ollama.com](https://ollama.com)**. It's free and available for Windows, macOS and Linux.

**Step 2 — Download a model**

Open your terminal and run one of the following commands depending on your computer's RAM:

| Your RAM | Recommended model | Command |
|---|---|---|
| 4–8 GB | Gemma 4 E4B (best quality/size ratio) | `ollama pull gemma4:e4b` |
| 16 GB | Llama 3.3 8B (better quality) | `ollama pull llama3.3:8b` |
| 32 GB+ | Qwen 2.5 14B (best quality) | `ollama pull qwen2.5:14b` |

The download may take a few minutes depending on your internet speed.

**Step 3 — Use it in the app**

1. Open the app
2. Select **"Ollama (Local)"** in the AI Provider dropdown
3. Select the model you downloaded in the Model dropdown
4. No API key needed — just click **"Translate PDF"**

> 💡 The first translation may take longer while the model loads into memory. After that it speeds up.

---

### 🚀 How to use

1. Open the app and click **"Choose file"** to select your PDF
2. Choose where to save the translated file (if you skip this, it saves automatically next to the original)
3. Select the **target language** from the dropdown menu
4. Select your **AI Provider** and **Model**
5. Paste your **API key** (not needed for Ollama)
6. Click **"Translate PDF"** and wait — the progress bar and pipeline log show real-time status
7. When done, the app will ask if you want to open the translated file automatically

---

### ⚠️ Limitations

- Groq free tier: ~1,400 requests/day and 6,000 tokens/minute
- OpenRouter free models change frequently and may be unavailable at any time
- Gemini may not work in all regions
- OCR quality depends on scan resolution — 150 DPI or higher recommended

---

## Português

### 📌 Sobre

**PDF Translator v2** é uma aplicação desktop que traduz documentos PDF usando inteligência artificial. Ele extrai o texto original, traduz respeitando a estrutura de parágrafos e o contexto, e gera um novo PDF formatado — tudo por meio de uma interface simples e intuitiva.

Desenvolvido como projeto de portfólio para demonstrar integração entre Python, APIs de IA, manipulação de PDFs e desenvolvimento de interfaces gráficas.

---

### ✨ Funcionalidades

- 🌍 Traduz para 10 idiomas: Português, Inglês, Espanhol, Francês, Alemão, Italiano, Japonês, Chinês, Russo e Árabe
- 📝 Detecta e preserva títulos, negrito, listas e estrutura de parágrafos
- 🤖 Suporte a múltiplos provedores de IA: **Groq, Gemini, OpenRouter e Ollama (local)**
- 📷 **Suporte a OCR para PDFs escaneados** — páginas com imagem são detectadas e processadas automaticamente
- 🖥️ Interface desktop limpa com progresso em tempo real e log do pipeline
- 💡 Sugere automaticamente o nome e o caminho do arquivo de saída
- 🔒 Suporta chave de API via variável de ambiente

---

### 🤖 Provedores de IA

| Provedor | Qualidade | Velocidade | Custo | Status |
|---|---|---|---|---|
| **Groq** | ⭐⭐⭐⭐⭐ | ⚡ Muito rápido | Gratuito (1.400 req/dia) | ✅ Recomendado |
| **Ollama** | ⭐⭐⭐⭐ | 🐢 Depende do hardware | Gratuito para sempre | ✅ Funciona bem |
| **OpenRouter** | ⭐⭐⭐⭐ | ⚡ Rápido | Gratuito (limitado) | ⚠️ Tier gratuito instável |
| **Gemini** | ⭐⭐⭐⭐⭐ | ⚡ Rápido | Gratuito (limitado) | ⚠️ Problemas regionais |

> **Recomendação:** Use o **Groq** para melhores resultados online, ou o **Ollama** para privacidade total sem precisar de internet.

---

### 🛠️ Tecnologias

| Tecnologia | Uso |
|---|---|
| Python 3.9+ | Linguagem principal |
| Tkinter | Interface gráfica |
| pdfplumber | Extração de texto com detecção de formatação |
| ReportLab | Geração do PDF traduzido |
| pytesseract + Pillow | OCR para PDFs escaneados |
| Groq API | Tradução com IA (Llama 3.3 70B) |
| Ollama | Inferência local de IA |

---

### 📦 Download

Baixe o executável para Windows (`.exe`) na página de [Releases](../../releases) — sem precisar instalar nada.

> ⚠️ **Para suporte a OCR:** o Tesseract precisa ser instalado separadamente. Veja o [guia de instalação](#tesseract-ocr-para-pdfs-escaneados) abaixo.

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

### 🔍 Tesseract OCR (para PDFs escaneados)

O Tesseract é um motor de OCR gratuito que permite ao app ler PDFs escaneados ou com apenas imagens. Ele precisa ser instalado separadamente no seu sistema.

**Windows**

1. Baixe o instalador em **[github.com/UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki)**
   - Escolha o arquivo `tesseract-ocr-w64-setup-x.x.x.exe` (64-bit)
2. Durante a instalação:
   - Marque a opção **"Add to PATH"** quando aparecer
   - Em **Additional language data**, selecione **Portuguese** (e outros idiomas que precisar)
3. Após instalar, abra um terminal novo e verifique:
```bash
tesseract --version
```
4. Se o comando não for reconhecido, adicione manualmente ao PATH:
   - Pesquise **"Variáveis de Ambiente"** nas configurações do Windows
   - Edite a variável **Path** em variáveis do sistema
   - Adicione: `C:\Program Files\Tesseract-OCR`
   - Abra um terminal novo e tente novamente

**Linux**
```bash
sudo apt install tesseract-ocr tesseract-ocr-por
```

**macOS**
```bash
brew install tesseract
```

> Com o Tesseract instalado, o OCR funciona automaticamente — páginas escaneadas são detectadas e processadas sem nenhuma configuração extra no app.

---

### 🔑 Como obter sua chave de API gratuita do Groq

O aplicativo usa a IA do Groq para traduzir seu PDF. Para isso, você precisa de uma chave de API gratuita — pense nela como uma senha pessoal que conecta o programa ao serviço de inteligência artificial. Veja como obter a sua:

1. Acesse **[console.groq.com](https://console.groq.com)**
2. Clique em **"Sign Up"** e crie uma conta gratuita (pode usar sua conta do Google)
3. Após entrar, procure no menu do lado esquerdo a opção **"API Keys"**
4. Clique em **"Create API Key"**, dê qualquer nome para ela (ex: "pdf-translator") e confirme
5. Um código longo vai aparecer na tela — ele começa com `gsk_...` — **copie imediatamente**, pois ele não será exibido novamente
6. Cole esse código no campo **"API Key"** dentro do aplicativo

> ⚠️ **Importante:** mantenha sua chave em segredo. Não a compartilhe com outras pessoas nem publique na internet.

---

### 🦙 Como usar o Ollama (IA local — sem internet)

O Ollama permite rodar a tradução inteiramente no seu computador — sem chave de API, sem internet, sem enviar dados para nenhum lugar.

**Passo 1 — Instalar o Ollama**

Baixe e instale em **[ollama.com](https://ollama.com)**. É gratuito e disponível para Windows, macOS e Linux.

**Passo 2 — Baixar um modelo**

Abra o terminal e rode um dos comandos abaixo conforme a RAM do seu computador:

| Sua RAM | Modelo recomendado | Comando |
|---|---|---|
| 4–8 GB | Gemma 4 E4B (melhor relação qualidade/tamanho) | `ollama pull gemma4:e4b` |
| 16 GB | Llama 3.3 8B (melhor qualidade) | `ollama pull llama3.3:8b` |
| 32 GB+ | Qwen 2.5 14B (qualidade máxima) | `ollama pull qwen2.5:14b` |

O download pode demorar alguns minutos dependendo da sua internet.

**Passo 3 — Usar no aplicativo**

1. Abra o aplicativo
2. Selecione **"Ollama (Local)"** no dropdown de AI Provider
3. Selecione o modelo que você baixou no dropdown de Model
4. Não precisa de chave de API — clique em **"Translate PDF"** diretamente

> 💡 A primeira tradução pode demorar um pouco mais enquanto o modelo carrega na memória. Depois disso fica mais rápido.

---

### 🚀 Como usar

1. Abra o aplicativo e clique em **"Choose file"** para selecionar o PDF
2. Escolha onde salvar o arquivo traduzido (se pular essa etapa, ele é salvo automaticamente na mesma pasta do original)
3. Selecione o **idioma de destino** no menu
4. Selecione o **AI Provider** e o **Model**
5. Cole sua **chave de API** (não necessário para Ollama)
6. Clique em **"Translate PDF"** e aguarde — a barra de progresso e o log do pipeline mostram o status em tempo real
7. Ao finalizar, o aplicativo pergunta se você quer abrir o arquivo traduzido automaticamente

---

### ⚠️ Limitações

- Plano gratuito do Groq: ~1.400 requisições por dia e 6.000 tokens por minuto
- Modelos gratuitos do OpenRouter mudam frequentemente e podem estar indisponíveis
- Gemini pode não funcionar em todas as regiões
- Qualidade do OCR depende da resolução do scan — recomendado 150 DPI ou mais

---

### 📃 Licença / License

MIT License — free to use, modify and distribute. / Livre para usar, modificar e distribuir.

---

<div align="center">
Made by <a href="https://github.com/ArturBrazLopes">ArturBrazLopes</a>
</div>
