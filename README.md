# Simulador de Rede de Filas (G/G/c/K)

Simulador orientado a eventos, em Python 3 (sem bibliotecas externas).

## Como executar
    python simulador.py            # usa config.json
    python simulador.py outro.json # usa outro modelo

## Arquivos
- `simulador.py`: codigo-fonte.
- `config.json`: modelo (filas, servidores, capacidades, tempos, roteamento, semente, total de aleatorios).
- `resultado.txt`: saida da simulacao do modelo da atividade.

## Como alterar o modelo
Edite `config.json`:
- `filas`: servidores, capacidade (`null` = infinita), atend_min/atend_max (uniforme).
- `chegada_externa`: fila de entrada e intervalo entre chegadas.
- `rede`: para cada fila, lista [destino, probabilidade]; destino `null` = saida do sistema.
- `semente` e `total_aleatorios` (criterio de parada).

## Regras
- Primeira chegada em t = 2,0 (nao consome aleatorio).
- Cada sorteio (chegada, atendimento, roteamento) consome 1 numero do gerador congruencial linear.
- A simulacao encerra ao usar 100.000 aleatorios.
- Cliente que chega em fila cheia e perdido (contado em "perdas").
