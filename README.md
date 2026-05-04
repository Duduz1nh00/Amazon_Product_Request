📌 Fine-Tuning com FLAN-T5 para Geração de Respostas sobre Produtos
🧩 Introdução

Neste projeto, utilizei o dataset AmazonTitles-1.3MM, composto por consultas de usuários, títulos de produtos da Amazon e suas descrições.

Realizei a limpeza dos dados, criei prompts de entrada e saída, e dividi o dataset em treino, validação e teste (train.json, val.json, test.json).

Optei pelo modelo google/flan-t5-base, uma versão do T5 voltada para tarefas de geração de texto. O modelo foi configurado utilizando a biblioteca Hugging Face Transformers, com tokenização via AutoTokenizer.

A função de pré-processamento foi responsável por tokenizar os prompts e respostas, preparando os dados para o treinamento. O modelo foi treinado com parâmetros definidos, como número de épocas e batch size, utilizando precisão mista para acelerar o processo.

Ao final, o modelo foi treinado, validado e salvo para uso posterior, completando o pipeline de fine-tuning.

📊 Preparação do Dataset

O dataset utilizado foi o AmazonTitles-1.3MM, contendo consultas reais de usuários e títulos de produtos relevantes, além de suas descrições.

🔧 Etapas realizadas:
1. Limpeza de Dados
Removi entradas duplicadas ou nulas
Normalizei o texto:
remoção de caracteres especiais
conversão para minúsculas
2. Criação dos Prompts

Formatei os dados no padrão prompt-response:

Entrada (prompt):
"Qual é a descrição do produto chamado 'Título do Produto'?"

Saída (resposta):
"Descrição detalhada do produto."
3. Divisão do Dataset
Treino: 80%
Validação: 10%
Teste: 10%
4. Armazenamento

Salvei os dados em arquivos:

train.json
val.json
test.json
⚙️ Parâmetros do Fine-Tuning

Escolhi o modelo google/flan-t5-base, baseado na arquitetura T5 (Text-to-Text Transfer Transformer).

Esse modelo utiliza instruction-tuning, permitindo resolver múltiplas tarefas de NLP com entrada textual simples, como:

tradução
resumo
perguntas e respostas
reescrita de texto

Utilizei o pipeline "text2text-generation" da Hugging Face para geração de respostas.

🔤 Tokenização

Utilizei:

AutoTokenizer.from_pretrained("google/flan-t5-base")
AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-base")
Função do tokenizer:
Converte texto → tokens numéricos
Permite que o modelo processe os dados
Reconverte tokens → texto legível
🧠 Pré-processamento e Treinamento

Implementei a função preprocess_data, responsável por:

Separar entradas (inputs) e saídas (targets)
Tokenizar os dados
Criar os labels usados no cálculo da perda
with tokenizer.as_target_tokenizer():

Essa etapa define que os targets são os valores esperados pelo modelo.

Utilizei:

dataset.map(preprocess_data, batched=True)

✔ Processamento em lote
✔ Melhor desempenho

🏋️ Treinamento do Modelo

Configurei:

Número de épocas (epochs)
Tamanho de batch (batch_size)

Utilizei o Trainer da Hugging Face para:

Treinar o modelo
Validar desempenho

Ao final, o modelo foi salvo em:

fine_tuned_model/
💬 Menu Interativo

Implementei um menu interativo para testar o modelo:

O usuário insere um prompt
O modelo gera a resposta correspondente
O sistema encerra ao digitar:
sair
✅ Conclusão

Neste trabalho, realizei o fine-tuning do modelo FLAN-T5-base utilizando o dataset AmazonTitles-1.3MM para geração de respostas sobre produtos.

O pipeline incluiu:

preparação e limpeza de dados
tokenização
pré-processamento
treinamento e validação

O modelo demonstrou capacidade de gerar respostas coerentes e relevantes para consultas textuais.

O uso da biblioteca Hugging Face Transformers facilitou significativamente a implementação.
