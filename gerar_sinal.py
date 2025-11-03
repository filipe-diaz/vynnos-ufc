#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
VYNNOS – gerar_sinal.py CORRIGIDO
Gera sinais de apostas com análise EV realista e recursos avançados
"""

import os
import json
import pickle
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path

# ======================================================================================
# CONFIGURAÇÕES
# ======================================================================================
BASE_DIR = Path(__file__).resolve().parent
DADOS_DIR = BASE_DIR / "dados"
MODELOS_DIR = BASE_DIR / "modelos"
SINAIS_DIR = BASE_DIR / "sinais"
SINAIS_DIR.mkdir(exist_ok=True, parents=True)

# Arquivos
ARQ_LUTAS = DADOS_DIR / "lutas_futuras.csv"
ARQ_ODDS = DADOS_DIR / "odds_lutas.csv"
ARQ_MODELO_WIN = MODELOS_DIR / "modelo_win.pkl"
ARQ_SINAIS_ATUAL = SINAIS_DIR / "sinais_atual.csv"
ARQ_HISTORICO = SINAIS_DIR / "historico_sinais.csv"
ARQ_MODEL_INFO = MODELOS_DIR / "model_info.json"

def log(msg: str, level: str = "INFO"):
    """Logging consistente"""
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{agora}] [{level}] {msg}")

# ======================================================================================
# FUNÇÕES AUXILIARES CORRIGIDAS
# ======================================================================================
def carregar_dados_avancado():
    """
    Carrega e combina dados de lutas e odds de forma robusta
    """
    # Carregar lutas
    if not ARQ_LUTAS.exists():
        log("Arquivo de lutas não encontrado", "ERRO")
        return pd.DataFrame()
    
    try:
        df_lutas = pd.read_csv(ARQ_LUTAS, delimiter=";")
        log(f"Carregadas {len(df_lutas)} lutas")
    except Exception as e:
        log(f"Erro ao carregar lutas: {e}", "ERRO")
        return pd.DataFrame()

    # Carregar odds
    if not ARQ_ODDS.exists():
        log("Arquivo de odds não encontrado - usando fallback", "WARN")
        df_odds = pd.DataFrame()
    else:
        try:
            df_odds = pd.read_csv(ARQ_ODDS, delimiter=";")
            log(f"Carregadas {len(df_odds)} linhas de odds")
        except Exception as e:
            log(f"Erro ao carregar odds: {e}", "ERRO")
            df_odds = pd.DataFrame()

    # Combinar dados
    if not df_odds.empty:
        # Merge por lutadores
        df_combinado = pd.merge(
            df_lutas, df_odds, 
            on=["evento", "lutador_a", "lutador_b"],
            how="left",
            suffixes=("", "_odds")
        )
    else:
        df_combinado = df_lutas.copy()
        # Adicionar colunas de odds vazias
        df_combinado[['casa', 'odd_a', 'odd_b', 'probabilidade_a']] = None

    return df_combinado

def carregar_modelo_avancado():
    """
    Carrega modelo com fallbacks inteligentes
    """
    if not ARQ_MODELO_WIN.exists():
        log("Modelo não encontrado - usando probabilidades base", "WARN")
        return None

    try:
        with open(ARQ_MODELO_WIN, "rb") as f:
            modelo_data = pickle.load(f)
        
        # Verificar estrutura do modelo
        if isinstance(modelo_data, dict):
            if "model" in modelo_data:
                modelo = modelo_data["model"]
                log("Modelo carregado do dict")
            elif "const_class" in modelo_data:
                log(f"Usando modelo constante: {modelo_data['const_class']}", "WARN")
                return modelo_data
            else:
                log("Estrutura do modelo desconhecida", "ERRO")
                return None
        else:
            modelo = modelo_data
            log("Modelo carregado diretamente")
        
        return modelo
        
    except Exception as e:
        log(f"Erro ao carregar modelo: {e}", "ERRO")
        return None

def calcular_probabilidades_avancadas(modelo, df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula probabilidades usando múltiplas estratégias
    """
    df_result = df.copy()
    
    # Estratégia 1: Usar modelo de ML se disponível
    if modelo and hasattr(modelo, 'predict_proba'):
        try:
            # Criar features básicas para predição
            features = pd.DataFrame()
            
            # Adicionar ratings se disponíveis
            if 'rating_a' in df.columns and 'rating_b' in df.columns:
                features['rating_diff'] = df['rating_a'].fillna(70) - df['rating_b'].fillna(70)
            else:
                # Fallback: usar diferença de tamanho do nome (simplificado)
                features['rating_diff'] = df['lutador_a'].str.len() - df['lutador_b'].str.len()
            
            # Preencher valores faltantes
            features = features.fillna(0)
            
            # Fazer predição
            probabilidades = modelo.predict_proba(features)
            if probabilidades.shape[1] == 2:
                df_result['prob_modelo_a'] = probabilidades[:, 1]
                df_result['prob_modelo_b'] = probabilidades[:, 0]
                log("Probabilidades calculadas com modelo ML")
            else:
                raise ValueError("Modelo não retornou 2 classes")
                
        except Exception as e:
            log(f"Erro na predição do modelo: {e}", "WARN")
            df_result['prob_modelo_a'] = 0.5
            df_result['prob_modelo_b'] = 0.5
    else:
        # Estratégia 2: Usar probabilidades das odds se disponíveis
        if 'probabilidade_a' in df.columns:
            df_result['prob_modelo_a'] = df['probabilidade_a'] / 100.0
            df_result['prob_modelo_b'] = 1 - df_result['prob_modelo_a']
            log("Usando probabilidades das odds")
        else:
            # Estratégia 3: Fallback baseado em ratings
            if 'rating_a' in df.columns and 'rating_b' in df.columns:
                total = df['rating_a'].fillna(70) + df['rating_b'].fillna(70)
                df_result['prob_modelo_a'] = df['rating_a'].fillna(70) / total
                df_result['prob_modelo_b'] = df['rating_b'].fillna(70) / total
                log("Usando probabilidades baseadas em ratings")
            else:
                # Estratégia 4: Fallback uniforme
                df_result['prob_modelo_a'] = 0.5
                df_result['prob_modelo_b'] = 0.5
                log("Usando probabilidades uniformes")

    return df_result

def calcular_ev_detalhado(probabilidade: float, odd: float) -> dict:
    """
    Calcula métricas EV detalhadas
    """
    if pd.isna(odd) or odd <= 1.0:
        return {
            'ev': -1.0,
            'valor_esperado': -1.0,
            'roi_esperado': -1.0,
            'kelley_criterion': 0.0
        }
    
    ev = (probabilidade * odd) - 1
    valor_esperado = ev  # Por unidade apostada
    roi_esperado = ev * 100  # Em percentual
    
    # Kelley Criterion simplificado
    kelley = max(0, (probabilidade * odd - 1) / (odd - 1)) if odd > 1 else 0
    
    return {
        'ev': round(ev, 4),
        'valor_esperado': round(valor_esperado, 4),
        'roi_esperado': round(roi_esperado, 2),
        'kelley_criterion': round(kelley, 3)
    }

def classificar_sinal_avancado(ev: float, prob: float, odd: float) -> dict:
    """
    Classificação avançada de sinais
    """
    if pd.isna(ev) or ev < 0:
        return {
            'classificacao': 'NÃO ENTRAR',
            'confianca': 'baixa',
            'risco': 'alto',
            'stake_recomendado': '0%'
        }
    
    # Classificação por EV
    if ev >= 0.15:
        classificacao = 'FORTE'
        confianca = 'alta'
        risco = 'baixo'
        stake = '3-5%'
    elif ev >= 0.08:
        classificacao = 'MODERADO'
        confianca = 'media'
        risco = 'medio' 
        stake = '2-3%'
    elif ev >= 0.03:
        classificacao = 'LEVE'
        confianca = 'baixa'
        risco = 'alto'
        stake = '1-2%'
    else:
        classificacao = 'NÃO ENTRAR'
        confianca = 'baixa'
        risco = 'alto'
        stake = '0%'
    
    # Ajustar por probabilidade
    if prob > 0.7 and classificacao != 'NÃO ENTRAR':
        confianca = 'alta'
        risco = 'baixo'
    
    return {
        'classificacao': classificacao,
        'confianca': confianca,
        'risco': risco,
        'stake_recomendado': stake
    }

# ======================================================================================
# PIPELINE PRINCIPAL CORRIGIDO
# ======================================================================================
def gerar_sinais_avancados():
    """
    Pipeline principal para gerar sinais avançados
    """
    log("=== VYNNOS – GERADOR DE SINAIS AVANÇADO ===")
    
    # 1. Carregar dados
    df = carregar_dados_avancado()
    if df.empty:
        log("Nenhum dado para processar", "ERRO")
        return
    
    # 2. Carregar modelo
    modelo = carregar_modelo_avancado()
    
    # 3. Calcular probabilidades
    df = calcular_probabilidades_avancadas(modelo, df)
    
    # 4. Gerar sinais para cada luta
    sinais = []
    timestamp = datetime.now().isoformat(timespec="seconds")
    
    for _, luta in df.iterrows():
        # Dados básicos
        evento = luta.get('evento', 'Evento Desconhecido')
        lutador_a = luta.get('lutador_a', '')
        lutador_b = luta.get('lutador_b', '')
        
        # Probabilidades
        prob_a = luta.get('prob_modelo_a', 0.5)
        prob_b = luta.get('prob_modelo_b', 0.5)
        
        # Odds
        odd_a = luta.get('odd_a')
        odd_b = luta.get('odd_b')
        casa = luta.get('casa', 'SEM_ODD')
        
        # Calcular EV para ambos os lados
        ev_info_a = calcular_ev_detalhado(prob_a, odd_a)
        ev_info_b = calcular_ev_detalhado(prob_b, odd_b)
        
        # Determinar melhor lado
        if ev_info_a['ev'] >= ev_info_b['ev']:
            lado_escolhido = 'A'
            prob_escolhida = prob_a
            odd_escolhida = odd_a
            ev_escolhido = ev_info_a
        else:
            lado_escolhido = 'B'
            prob_escolhida = prob_b
            odd_escolhida = odd_b
            ev_escolhido = ev_info_b
        
        # Classificar sinal
        classificacao = classificar_sinal_avancado(
            ev_escolhido['ev'], prob_escolhida, odd_escolhida
        )
        
        # Montar sinal
        sinal = {
            'timestamp': timestamp,
            'evento': evento,
            'data_evento': luta.get('data_evento', ''),
            'lutador_a': lutador_a,
            'lutador_b': lutador_b,
            'lado_escolhido': lado_escolhido,
            'probabilidade': round(prob_escolhida * 100, 1),
            'odd_escolhida': odd_escolhida,
            'ev': ev_escolhido['ev'],
            'valor_esperado': ev_escolhido['valor_esperado'],
            'roi_esperado': ev_escolhido['roi_esperado'],
            'kelley_criterion': ev_escolhido['kelley_criterion'],
            'casa': casa,
            'classificacao': classificacao['classificacao'],
            'confianca': classificacao['confianca'],
            'risco': classificacao['risco'],
            'stake_recomendado': classificacao['stake_recomendado'],
            'odd_a': odd_a,
            'odd_b': odd_b,
            'probabilidade_a': round(prob_a * 100, 1),
            'probabilidade_b': round(prob_b * 100, 1)
        }
        
        sinais.append(sinal)
    
    # 5. Salvar resultados
    df_sinais = pd.DataFrame(sinais)
    
    # Salvar sinal atual
    df_sinais.to_csv(ARQ_SINAIS_ATUAL, index=False, encoding='utf-8-sig')
    log(f"Sinais atuais salvos: {ARQ_SINAIS_ATUAL}")
    
    # Atualizar histórico
    if ARQ_HISTORICO.exists():
        df_hist = pd.read_csv(ARQ_HISTORICO)
        df_final = pd.concat([df_hist, df_sinais], ignore_index=True)
    else:
        df_final = df_sinais
    
    df_final.to_csv(ARQ_HISTORICO, index=False, encoding='utf-8-sig')
    log(f"Histórico atualizado: {ARQ_HISTORICO}")
    
    # 6. Salvar informações do processamento
    info = {
        'last_run': timestamp,
        'total_lutas': len(df),
        'total_sinais': len(sinais),
        'sinais_ev_positivo': len([s for s in sinais if s['ev'] > 0]),
        'sinais_fortes': len([s for s in sinais if s['classificacao'] == 'FORTE']),
        'modelo_utilizado': bool(modelo and hasattr(modelo, 'predict_proba')),
        'versao': '2.0_avancado'
    }
    
    with open(ARQ_MODEL_INFO, 'w', encoding='utf-8') as f:
        json.dump(info, f, ensure_ascii=False, indent=2)
    
    log(f"Informações salvas: {ARQ_MODEL_INFO}")
    
    # 7. Resumo estatístico
    if not df_sinais.empty:
        sinais_ev_positivo = df_sinais[df_sinais['ev'] > 0]
        log(f"=== RESUMO ESTATÍSTICO ===")
        log(f"Total de lutas analisadas: {len(df_sinais)}")
        log(f"Sinais com EV positivo: {len(sinais_ev_positivo)}")
        log(f"Sinais FORTES: {len(df_sinais[df_sinais['classificacao'] == 'FORTE'])}")
        log(f"Melhor EV: {df_sinais['ev'].max():.3f}")
        log(f"EV médio: {df_sinais['ev'].mean():.3f}")
    
    log("=== PROCESSAMENTO CONCLUÍDO ===")

if __name__ == "__main__":
    gerar_sinais_avancados()