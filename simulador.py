"""Simulador de rede de filas (G/G/c/K) orientado a eventos.
Uso: python simulador.py [config.json]
"""
import heapq, json, sys


class FimDaSimulacao(Exception):
    pass


class Gerador:
    """Congruencial linear; conta cada numero pseudoaleatorio usado."""
    def __init__(self, semente, limite, a=1664525, c=1013904223, m=2**32):
        self.x, self.a, self.c, self.m, self.usados = semente, a, c, m, 0
        self.limite = limite

    def proximo(self):
        if self.usados >= self.limite:
            raise FimDaSimulacao()  # o 100.000o ja foi usado: encerra
        self.x = (self.a * self.x + self.c) % self.m
        self.usados += 1
        return self.x / self.m

    def uniforme(self, lo, hi):
        return lo + (hi - lo) * self.proximo()


class Fila:
    def __init__(self, nome, cfg):
        self.nome = nome
        self.servidores = cfg["servidores"]
        self.capacidade = cfg["capacidade"]  # None = infinita
        self.atend_min, self.atend_max = cfg["atend_min"], cfg["atend_max"]
        self.clientes = 0
        self.perdas = 0
        self.tempos = [0.0]  # tempos[k] = tempo acumulado com k clientes

    def cheia(self):
        return self.capacidade is not None and self.clientes >= self.capacidade

    def acumula(self, delta):
        while len(self.tempos) <= self.clientes:
            self.tempos.append(0.0)
        self.tempos[self.clientes] += delta


def simular(cfg):
    rng = Gerador(cfg["semente"], cfg["total_aleatorios"])
    filas = {n: Fila(n, c) for n, c in cfg["filas"].items()}
    ext = cfg["chegada_externa"]
    agenda, seq = [], 0
    t = 0.0

    def agendar(tempo, tipo, fila):
        nonlocal seq
        heapq.heappush(agenda, (tempo, seq, tipo, fila)); seq += 1

    def chegada(f, agora):
        if f.cheia():
            f.perdas += 1
            return
        f.clientes += 1
        if f.clientes <= f.servidores:
            agendar(agora + rng.uniforme(f.atend_min, f.atend_max), "SAIDA", f.nome)

    def tratar(tipo, nome):
        f = filas[nome]
        if tipo == "CHEGADA":
            chegada(f, t)
            agendar(t + rng.uniforme(ext["min"], ext["max"]), "CHEGADA", ext["fila"])
        else:  # SAIDA
            f.clientes -= 1
            if f.clientes >= f.servidores:
                agendar(t + rng.uniforme(f.atend_min, f.atend_max), "SAIDA", nome)
            u, acum = rng.proximo(), 0.0
            for destino, p in cfg["rede"][nome]:
                acum += p
                if u < acum:
                    if destino:
                        chegada(filas[destino], t)
                    break

    agendar(cfg["primeira_chegada"], "CHEGADA", ext["fila"])  # nao usa aleatorio
    while agenda:
        tempo, _, tipo, nome = heapq.heappop(agenda)
        delta = tempo - t
        for f in filas.values():
            f.acumula(delta)  # acumula ANTES de mudar o estado
        t = tempo
        try:
            tratar(tipo, nome)
        except FimDaSimulacao:
            break
    return filas, t, rng.usados


def relatorio(filas, t, usados):
    print(f"Aleatorios usados: {usados}")
    print(f"Tempo global da simulacao: {t:.4f}\n")
    for f in filas.values():
        cap = "inf" if f.capacidade is None else f.capacidade
        print(f"=== {f.nome}: G/G/{f.servidores}/{cap} ===")
        print("Estado | Tempo acumulado | Probabilidade")
        for k, tk in enumerate(f.tempos):
            print(f"{k:>6} | {tk:>15.4f} | {tk / t * 100:>9.4f}%")
        print(f"Perdas de clientes: {f.perdas}\n")


if __name__ == "__main__":
    caminho = sys.argv[1] if len(sys.argv) > 1 else "config.json"
    with open(caminho) as arq:
        cfg = json.load(arq)
    relatorio(*simular(cfg))
