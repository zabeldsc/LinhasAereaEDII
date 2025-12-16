import heapq

class Grafo:
    def __init__(self):
        # Estrutura do grafo:
        # adj[origem] = [(destino, dados_voo), ...]
        self.adj = {}

    # ---------------------------------------
    # Adiciona aresta ao grafo
    # ---------------------------------------
    def adicionar_aresta(self, origem, destino, dados_voo):
        if origem not in self.adj:
            self.adj[origem] = []
        self.adj[origem].append((destino, dados_voo))

    # ---------------------------------------
    # Obtém vizinhos de um nó
    # ---------------------------------------
    def vizinhos(self, origem):
        return self.adj.get(origem, [])

    # ---------------------------------------
    # Algoritmo de Dijkstra (menor custo)
    # ---------------------------------------
    def dijkstra(self, origem, destino):
        if origem not in self.adj:
            return None
        
        #Contador de desempate
        cont = 0
        
        # heap: (custo_acumulado, contador, cidade_atual, caminho_de_voos)
        heap = [(0, cont, origem, [])]
        visitado = set()

        while heap:
            #_ ignora o contador
            custo, _, atual, caminho = heapq.heappop(heap)

            if atual in visitado:
                continue
            visitado.add(atual)

            # Se chegou ao destino, monta resposta
            if atual == destino:
                return self._montar_resposta(caminho)

            # Explora vizinhos
            for prox, voo in self.vizinhos(atual):
                if prox not in visitado:
                    novo_custo = custo + float(voo.get("preco_passagem", 0))
                    cont += 1
                    heapq.heappush(heap, (novo_custo, cont, prox, caminho + [voo]))

        return None  # Sem rota

    # ---------------------------------------
    # Monta o dicionário final esperado pelo HTML
    # ---------------------------------------
    def _montar_resposta(self, lista_de_voos):
        if not lista_de_voos:
            return None

        total_milhas = sum(int(voo.get("milhas", 0)) for voo in lista_de_voos)
        total_preco = sum(float(voo.get("preco_passagem", 0)) for voo in lista_de_voos)

        return {
            "conexoes": max(0, len(lista_de_voos) - 1),
            "milhas_totais": total_milhas,
            "preco_total": total_preco,
            "trechos": [
                {
                    "codigo": voo.get("codigo"),
                    "origem": voo.get("origem"),
                    "destino": voo.get("destino"),
                    "milhas": voo.get("milhas"),
                    "preco": voo.get("preco_passagem"),
                    "aeronave": voo.get("tipo_aeronave"),
                }
                for voo in lista_de_voos
            ]
        }


# ----------------------------------------------------
# Função utilitária para construir o grafo dos voos
# ----------------------------------------------------
def construir_grafo_voos(voos_dict):
    """
    voos_dict é o app.config['VOOS'], no formato:
    {
        "1": {"codigo": "...", "origem": "...", "destino": "...", ...},
        "2": {...}
    }
    """
    g = Grafo()

    for _, voo in voos_dict.items():
        # cada voo representa uma aresta orientada origem -> destino
        origem = voo.get("origem")
        destino = voo.get("destino")

        if origem and destino:
            g.adicionar_aresta(origem, destino, voo)

    return g
