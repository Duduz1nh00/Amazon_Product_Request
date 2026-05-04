import os
import pandas as pd
import json
import torch
from sklearn.model_selection import train_test_split
from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
    Seq2SeqTrainingArguments,
    Seq2SeqTrainer,
    pipeline
)
from datasets import load_dataset

# Configuração para evitar problemas com MPS
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

# Verificar dispositivo disponível
device = torch.device("mps" if torch.has_mps else "cuda" if torch.cuda.is_available() else "cpu")

# 1. Carregar o dataset
with open("/Users/daniel.gomes/Documents/Projetos/Python/data/part_old.json", "r") as file:
    data = json.load(file)

# Criar um DataFrame com as colunas relevantes
df = pd.DataFrame(data)
df = df[["title", "content"]].dropna()

# Formatar prompts e respostas
df["prompt"] = "Qual é a descrição do produto chamado '" + df["title"] + "'?"
df["response"] = df["content"]

# Divisão do dataset
train, test = train_test_split(df, test_size=0.2, random_state=42)
val, test = train_test_split(test, test_size=0.5, random_state=42)

# Salvar os conjuntos preparados
train.to_json("train.json", orient="records", lines=True)
val.to_json("val.json", orient="records", lines=True)
test.to_json("test.json", orient="records", lines=True)

# 2. Testando o modelo pré-treinado
# Usar pipeline corretamente
model_name = "google/flan-t5-base"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name).to(device)

generator = pipeline(
    "text2text-generation",
    model=model,
    tokenizer=tokenizer,
    device=0 if device.type in ["cuda", "mps"] else -1
)

# Exemplo de teste com o modelo base
prompt = "Qual é a descrição do produto chamado 'Smartphone X'?"
print(generator(prompt))

# 3. Fine-Tuning do modelo

# Carregar o dataset para Hugging Face
dataset = load_dataset(
    "json",
    data_files={"train": "train.json", "validation": "val.json"}
)

# Pré-processamento dos dados
def preprocess_data(examples):
    # Obter inputs (prompts) e targets (respostas)
    model_inputs = tokenizer(
        examples["prompt"], max_length=512, truncation=True, padding="max_length"
    )
    labels = tokenizer(
        examples["response"], max_length=512, truncation=True, padding="max_length"
    )["input_ids"]
    model_inputs["labels"] = labels
    return model_inputs

# Aplicar o pré-processamento ao dataset
tokenized_datasets = dataset.map(
    preprocess_data,
    batched=True,
    remove_columns=dataset["train"].column_names
)

# Configuração de treinamento com melhorias
training_args = Seq2SeqTrainingArguments(
    output_dir="./results",
    evaluation_strategy="epoch",
    learning_rate=5e-5,
    per_device_train_batch_size=2,  # Reduzido para evitar problemas de memória
    per_device_eval_batch_size=2,
    gradient_accumulation_steps=1,  # Compensar o batch size menor
    num_train_epochs=2,
    weight_decay=0.01,
    save_total_limit=1,
    predict_with_generate=True,
    logging_steps=50,
    fp16=False,
)

# Criar o Trainer
trainer = Seq2SeqTrainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_datasets["train"],
    eval_dataset=tokenized_datasets["validation"],
    tokenizer=tokenizer,
)

# Executar o treinamento
trainer.train()

# Salvar o modelo treinado e o tokenizer
trainer.save_model("fine_tuned_model")
tokenizer.save_pretrained("fine_tuned_model")

# 4. Input e Output Interativo
print("\n=== Chat com o Modelo Fine-Tuned ===")
print("Digite 'sair' para encerrar a conversa.\n")

# Carregar o modelo fine-tuned e criar pipeline de geração
tokenizer = AutoTokenizer.from_pretrained("fine_tuned_model")
model = AutoModelForSeq2SeqLM.from_pretrained("fine_tuned_model").to(device)
generator = pipeline(
    "text2text-generation",
    model=model,
    tokenizer=tokenizer,
    device=0 if device.type in ["cuda", "mps"] else -1
)

while True:
    pergunta = input("Pergunta: ")
    if pergunta.lower() == "sair":
        print("Encerrando a conversa. Até logo!")
        break
    
    # Gera a resposta do modelo
    resposta = generator(pergunta, max_length=128, num_return_sequences=1)[0]['generated_text']
    print(f"Resposta: {resposta}\n")