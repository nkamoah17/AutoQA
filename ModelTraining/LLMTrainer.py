
from transformers import AutoModelForMaskedLM, AutoTokenizer, Trainer, TrainingArguments

def fine_tune_LLM(dataset_path, model_name="facebook/bart-large"):
    # Load the model and tokenizer
    model = AutoModelForMaskedLM.from_pretrained(model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    # Load and preprocess the dataset
    dataset = load_dataset(dataset_path)
    dataset = dataset.map(lambda e: tokenizer(e['text'], truncation=True, padding='max_length'), batched=True)

    # Define the training arguments
    training_args = TrainingArguments(
        output_dir="./results",
        num_train_epochs=3,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=64,
        warmup_steps=500,
        weight_decay=0.01,
    )

    # Initialize the Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
    )

    # Train the model
    trainer.train()

    # Save the fine-tuned model
    model.save_pretrained("./results")

    # Return the fine-tuned model
    return model


