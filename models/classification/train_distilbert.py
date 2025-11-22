import os
import argparse
import pandas as pd
import numpy as np
import tensorflow as tf
from transformers import TFDistilBertModel, DistilBertTokenizerFast
from sklearn.model_selection import train_test_split


def infer_columns(df: pd.DataFrame):
    text_cols = [
        'Body', 'Text', 'text', 'content', 'article', 'FullArticle', 'FullText'
    ]
    label_cols = ['Category', 'category', 'label', 'Label', 'category_name']

    text_col = next((c for c in text_cols if c in df.columns), None)
    label_col = next((c for c in label_cols if c in df.columns), None)
    if text_col is None or label_col is None:
        raise ValueError(
            f"Could not infer text/label columns. Available columns: {list(df.columns)}"
        )
    return text_col, label_col


def build_model(num_labels: int):
    base = TFDistilBertModel.from_pretrained('distilbert-base-uncased')

    input_ids = tf.keras.layers.Input(shape=(256,), dtype=tf.int32, name='input_ids')
    attn_mask = tf.keras.layers.Input(shape=(256,), dtype=tf.int32, name='attention_mask')

    outputs = base(input_ids, attention_mask=attn_mask)
    cls = outputs.last_hidden_state[:, 0, :]  # CLS token
    x = tf.keras.layers.Dropout(0.2)(cls)
    x = tf.keras.layers.Dense(256, activation='relu')(x)
    x = tf.keras.layers.Dropout(0.2)(x)
    logits = tf.keras.layers.Dense(num_labels, activation='softmax')(x)

    model = tf.keras.Model(inputs=[input_ids, attn_mask], outputs=logits)
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=3e-5),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    return model


def main():
    parser = argparse.ArgumentParser(description='Train DistilBERT and save distilbert_model.h5')
    parser.add_argument('--data', default=os.path.join('..', 'models', 'datasets', 'dataset.csv'))
    parser.add_argument('--output', default='distilbert_model.h5')
    parser.add_argument('--epochs', type=int, default=2)
    parser.add_argument('--batch', type=int, default=8)
    args = parser.parse_args()

    df = pd.read_csv(args.data)
    text_col, label_col = infer_columns(df)

    # Normalize labels to ids 0..N-1
    label_names = sorted(list({str(v) for v in df[label_col].dropna().unique()}))
    name_to_id = {name: idx for idx, name in enumerate(label_names)}
    y = df[label_col].map(lambda v: name_to_id.get(str(v), -1)).astype(int)
    df = df[(y >= 0)]
    y = y[y >= 0]
    texts = df[text_col].fillna('').astype(str).tolist()

    tok = DistilBertTokenizerFast.from_pretrained('distilbert-base-uncased')
    enc = tok(texts, truncation=True, padding='max_length', max_length=256, return_tensors='np')

    X_train_ids, X_val_ids, X_train_mask, X_val_mask, y_train, y_val = train_test_split(
        enc['input_ids'], enc['attention_mask'], y.values, test_size=0.1, random_state=42, stratify=y.values
    )

    model = build_model(num_labels=len(label_names))

    model.fit(
        x=[X_train_ids, X_train_mask], y=y_train,
        validation_data=([X_val_ids, X_val_mask], y_val),
        epochs=args.epochs, batch_size=args.batch
    )

    # Save in legacy H5 as expected by views.py
    model.save(args.output)
    # Also store the label mapping for reference
    with open('category_labels.txt', 'w', encoding='utf-8') as f:
        for i, name in enumerate(label_names):
            f.write(f"{i}\t{name}\n")

    print(f"Saved model to {args.output}. Labels: {label_names}")


if __name__ == '__main__':
    main()



