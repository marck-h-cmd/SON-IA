#!/usr/bin/env python3
"""
Entrenamiento del Modelo de Predicción de Pago
==============================================
Modelo: XGBoost Classifier
Objetivo: Predecir probabilidad de pago en los próximos 15 días
Dataset: Datos ficticios simulando comportamiento de pago
"""

import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, roc_auc_score, classification_report
import joblib
import structlog
from pathlib import Path
from datetime import datetime

logger = structlog.get_logger(__name__)

MODELS_DIR = Path(__file__).parent.parent / "models" / "trained"
MODELS_DIR.mkdir(parents=True, exist_ok=True)


def generate_payment_data(n_samples: int = 8000) -> pd.DataFrame:
    """
    Genera datos sintéticos de comportamiento de pago.
    
    Args:
        n_samples: Número de muestras
        
    Returns:
        DataFrame con features de pago
    """
    logger.info(f"Generando {n_samples} muestras de comportamiento de pago...")
    
    np.random.seed(42)
    
    data = pd.DataFrame({
        'dias_antes_vencimiento': np.random.randint(-15, 20, n_samples),
        'monto_factura': np.random.uniform(50, 15000, n_samples),
        'historial_pagos': np.random.poisson(15, n_samples),
        'num_recordatorios': np.random.randint(0, 5, n_samples),
        'score_confianza': np.random.uniform(0.2, 0.95, n_samples),
        'dias_desde_ultimo_pago': np.random.exponential(25, n_samples),
        'monto_acumulado_deuda': np.random.uniform(0, 50000, n_samples),
        'tiene_oferta_activa': np.random.choice([0, 1], n_samples, p=[0.7, 0.3]),
        'descuento_ofrecido': np.random.uniform(0, 20, n_samples),
        'mes_del_ano': np.random.randint(1, 13, n_samples),
        'dia_semana_vencimiento': np.random.randint(0, 7, n_samples),
        
        # Features categóricas
        'segmento': np.random.choice(['B2B', 'B2C', 'Gobierno'], n_samples, p=[0.3, 0.6, 0.1]),
        'canal_recordatorio': np.random.choice(['email', 'whatsapp', 'sms', 'ninguno'], n_samples),
    })
    
    # Crear variable objetivo: ¿pagó en los próximos 15 días?
    # Probabilidad base
    prob_base = (
        data['score_confianza'] * 0.40 +
        (data['dias_antes_vencimiento'] > 0).astype(float) * 0.20 +
        (data['historial_pagos'] > 10).astype(float) * 0.15 +
        (data['num_recordatorios'] > 0).astype(float) * 0.10 +
        (data['monto_acumulado_deuda'] < 10000).astype(float) * 0.10 +
        (data['tiene_oferta_activa'] == 1).astype(float) * 0.05
    )
    
    # Ajustar por segmento
    prob_base += (data['segmento'] == 'B2B').astype(float) * 0.05
    
    # Normalizar
    prob_base = prob_base / prob_base.max()
    
    # Crear target
    data['pago_realizado'] = (np.random.random(n_samples) < prob_base).astype(int)
    
    logger.info(f"Datos generados: {data['pago_realizado'].value_counts().to_dict()}")
    
    return data


def prepare_features(data: pd.DataFrame) -> tuple:
    """Prepara features para entrenamiento"""
    feature_cols = [
        'dias_antes_vencimiento', 'monto_factura', 'historial_pagos',
        'num_recordatorios', 'score_confianza', 'dias_desde_ultimo_pago',
        'monto_acumulado_deuda', 'tiene_oferta_activa', 'descuento_ofrecido',
        'mes_del_ano', 'dia_semana_vencimiento',
        'segmento', 'canal_recordatorio',
    ]
    
    X = pd.get_dummies(data[feature_cols], drop_first=True)
    y = data['pago_realizado']
    
    return train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)


def train_model(X_train, y_train) -> XGBClassifier:
    """Entrena el modelo XGBoost"""
    logger.info("Entrenando modelo de predicción de pago...")
    
    model = XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.08,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        use_label_encoder=False,
        eval_metric='logloss',
        early_stopping_rounds=15,
    )
    
    model.fit(X_train, y_train, eval_set=[(X_train, y_train)], verbose=False)
    
    return model


def evaluate_model(model, X_train, X_test, y_train, y_test, feature_names):
    """Evalúa el modelo y muestra métricas"""
    y_pred_test = model.predict(X_test)
    y_proba_test = model.predict_proba(X_test)[:, 1]
    
    accuracy = accuracy_score(y_test, y_pred_test)
    auc = roc_auc_score(y_test, y_proba_test)
    cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='roc_auc')
    
    logger.info("=" * 60)
    logger.info("📊 RESULTADOS DEL MODELO - Predicción de Pago")
    logger.info("=" * 60)
    logger.info(f"Accuracy:  {accuracy:.4f}")
    logger.info(f"AUC-ROC:   {auc:.4f}")
    logger.info(f"CV AUC:    {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
    logger.info("=" * 60)
    
    logger.info("\n📋 Reporte de Clasificación:")
    logger.info(classification_report(y_test, y_pred_test, target_names=['No Pagó', 'Pagó']))
    
    # Importancia de features
    importancia = pd.DataFrame({
        'feature': feature_names,
        'importance': model.feature_importances_,
    }).sort_values('importance', ascending=False)
    
    logger.info("\n📈 Top 10 Features más importantes:")
    for _, row in importancia.head(10).iterrows():
        logger.info(f"  {row['feature']}: {row['importance']:.4f}")
    
    return {
        'accuracy': accuracy,
        'auc_roc': auc,
        'cv_auc_mean': cv_scores.mean(),
        'cv_auc_std': cv_scores.std(),
    }


def save_model(model, metrics, feature_names):
    """Guarda el modelo entrenado"""
    model_path = MODELS_DIR / "prediccion_pago.pkl"
    metadata_path = MODELS_DIR / "prediccion_pago_metadata.json"
    
    joblib.dump(model, model_path)
    logger.info(f"✅ Modelo guardado en: {model_path}")
    
    import json
    metadata = {
        "modelo": "XGBoost Classifier",
        "fecha_entrenamiento": datetime.now().isoformat(),
        "features": list(feature_names),
        "metricas": metrics,
        "parametros": model.get_params(),
    }
    
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2, default=str)
    
    logger.info(f"✅ Metadatos guardados en: {metadata_path}")


def main():
    """Función principal"""
    logger.info("🚀 Iniciando entrenamiento del modelo de Predicción de Pago...")
    
    data = generate_payment_data(8000)
    X_train, X_test, y_train, y_test = prepare_features(data)
    feature_names = X_train.columns.tolist()
    
    logger.info(f"Features: {len(feature_names)} | Train: {len(X_train)} | Test: {len(X_test)}")
    
    model = train_model(X_train, y_train)
    metrics = evaluate_model(model, X_train, X_test, y_train, y_test, feature_names)
    save_model(model, metrics, feature_names)
    
    logger.info("🎉 Entrenamiento completado exitosamente!")
    
    return model, metrics


if __name__ == "__main__":
    main()