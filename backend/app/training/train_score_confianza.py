#!/usr/bin/env python3
"""
Entrenamiento del Modelo de Score de Confianza
==============================================
Modelo: XGBoost Classifier
Objetivo: Clasificar clientes según su probabilidad de pago oportuno
Dataset: Datos ficticios simulando comportamiento de clientes de telecomunicaciones
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

# Directorio de modelos
MODELS_DIR = Path(__file__).parent.parent / "models" / "trained"
MODELS_DIR.mkdir(parents=True, exist_ok=True)


def generate_synthetic_data(n_samples: int = 5000) -> pd.DataFrame:
    """
    Genera datos sintéticos para entrenamiento.
    Simula el comportamiento de clientes de telecomunicaciones.
    
    Args:
        n_samples: Número de muestras a generar
        
    Returns:
        DataFrame con features y variable objetivo
    """
    logger.info(f"Generando {n_samples} muestras sintéticas...")
    
    np.random.seed(42)
    
    data = pd.DataFrame({
        # Features numéricas
        'antiguedad_meses': np.random.exponential(24, n_samples).astype(int),
        'promedio_mora_dias': np.random.exponential(3, n_samples),
        'num_disputas_ultimo_anio': np.random.poisson(0.3, n_samples),
        'num_pagos_tarde': np.random.poisson(1.5, n_samples),
        'monto_promedio': np.random.uniform(50, 10000, n_samples),
        'num_servicios': np.random.poisson(2, n_samples),
        'cambios_plan': np.random.poisson(0.5, n_samples),
        
        # Features categóricas
        'segmento': np.random.choice(['B2B', 'B2C', 'Gobierno'], n_samples, p=[0.3, 0.6, 0.1]),
        'canal_preferido': np.random.choice(['email', 'whatsapp', 'app', 'llamada'], n_samples),
        'metodo_pago': np.random.choice(['Transferencia', 'Débito', 'Tarjeta', 'Efectivo'], n_samples),
    })
    
    # Crear variable objetivo: cliente confiable
    # Un cliente es confiable si:
    # - Antigüedad > 12 meses
    # - Promedio de mora < 5 días
    # - Pocas disputas
    # - Pocos pagos tarde
    
    score_base = (
        (data['antiguedad_meses'] > 12).astype(float) * 0.30 +
        (data['promedio_mora_dias'] < 5).astype(float) * 0.30 +
        (data['num_disputas_ultimo_anio'] < 2).astype(float) * 0.20 +
        (data['num_pagos_tarde'] < 3).astype(float) * 0.20
    )
    
    # B2B y Gobierno tienden a ser más confiables
    score_base += (data['segmento'].isin(['B2B', 'Gobierno'])).astype(float) * 0.05
    
    # Normalizar y crear target binario
    data['confiable'] = (score_base >= 0.60).astype(int)
    
    logger.info(f"Datos generados: {data['confiable'].value_counts().to_dict()}")
    
    return data


def prepare_features(data: pd.DataFrame) -> tuple:
    """
    Prepara features para entrenamiento.
    One-hot encoding para variables categóricas.
    
    Args:
        data: DataFrame completo
        
    Returns:
        Tuple[X_train, X_test, y_train, y_test]
    """
    # Features
    feature_cols = [
        'antiguedad_meses', 'promedio_mora_dias', 'num_disputas_ultimo_anio',
        'num_pagos_tarde', 'monto_promedio', 'num_servicios', 'cambios_plan',
        'segmento', 'canal_preferido', 'metodo_pago',
    ]
    
    X = pd.get_dummies(data[feature_cols], drop_first=True)
    y = data['confiable']
    
    return train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)


def train_model(X_train, y_train) -> XGBClassifier:
    """
    Entrena el modelo XGBoost.
    
    Args:
        X_train: Features de entrenamiento
        y_train: Target de entrenamiento
        
    Returns:
        Modelo entrenado
    """
    logger.info("Entrenando modelo XGBoost...")
    
    model = XGBClassifier(
        n_estimators=150,
        max_depth=5,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        use_label_encoder=False,
        eval_metric='logloss',
        early_stopping_rounds=10,
    )
    
    model.fit(
        X_train, y_train,
        eval_set=[(X_train, y_train)],
        verbose=False,
    )
    
    return model


def evaluate_model(model, X_train, X_test, y_train, y_test, feature_names):
    """
    Evalúa el modelo y muestra métricas.
    
    Args:
        model: Modelo entrenado
        X_train, X_test: Features
        y_train, y_test: Targets
        feature_names: Nombres de features
    """
    # Predicciones
    y_pred_train = model.predict(X_train)
    y_pred_test = model.predict(X_test)
    y_proba_test = model.predict_proba(X_test)[:, 1]
    
    # Métricas
    accuracy_train = accuracy_score(y_train, y_pred_train)
    accuracy_test = accuracy_score(y_test, y_pred_test)
    auc = roc_auc_score(y_test, y_proba_test)
    
    # Cross-validation
    cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='roc_auc')
    
    logger.info("=" * 60)
    logger.info("📊 RESULTADOS DEL MODELO - Score de Confianza")
    logger.info("=" * 60)
    logger.info(f"Accuracy (Train): {accuracy_train:.4f}")
    logger.info(f"Accuracy (Test):  {accuracy_test:.4f}")
    logger.info(f"AUC-ROC:          {auc:.4f}")
    logger.info(f"CV AUC (5-fold):  {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
    logger.info("=" * 60)
    
    # Reporte de clasificación
    logger.info("\n📋 Reporte de Clasificación:")
    logger.info(classification_report(y_test, y_pred_test, target_names=['No Confiable', 'Confiable']))
    
    # Importancia de features
    importancia = pd.DataFrame({
        'feature': feature_names,
        'importance': model.feature_importances_,
    }).sort_values('importance', ascending=False)
    
    logger.info("\n📈 Top 10 Features más importantes:")
    for _, row in importancia.head(10).iterrows():
        logger.info(f"  {row['feature']}: {row['importance']:.4f}")
    
    return {
        'accuracy_train': accuracy_train,
        'accuracy_test': accuracy_test,
        'auc_roc': auc,
        'cv_auc_mean': cv_scores.mean(),
        'cv_auc_std': cv_scores.std(),
    }


def save_model(model, metrics, feature_names):
    """
    Guarda el modelo entrenado y sus metadatos.
    
    Args:
        model: Modelo entrenado
        metrics: Métricas de evaluación
        feature_names: Nombres de features
    """
    model_path = MODELS_DIR / "score_confianza.pkl"
    metadata_path = MODELS_DIR / "score_confianza_metadata.json"
    
    # Guardar modelo
    joblib.dump(model, model_path)
    logger.info(f"✅ Modelo guardado en: {model_path}")
    
    # Guardar metadatos
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
    """Función principal de entrenamiento"""
    logger.info("🚀 Iniciando entrenamiento del modelo de Score de Confianza...")
    
    # 1. Generar datos
    data = generate_synthetic_data(5000)
    
    # 2. Preparar features
    X_train, X_test, y_train, y_test = prepare_features(data)
    feature_names = X_train.columns.tolist()
    
    logger.info(f"Features: {len(feature_names)} | Train: {len(X_train)} | Test: {len(X_test)}")
    
    # 3. Entrenar modelo
    model = train_model(X_train, y_train)
    
    # 4. Evaluar modelo
    metrics = evaluate_model(model, X_train, X_test, y_train, y_test, feature_names)
    
    # 5. Guardar modelo
    save_model(model, metrics, feature_names)
    
    logger.info("🎉 Entrenamiento completado exitosamente!")
    
    return model, metrics


if __name__ == "__main__":
    main()