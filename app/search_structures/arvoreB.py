class ArvoreBNodo:
    # Estrutura do nó da Arvore B:
    # folha: Booleano indicando se é nó folha
    # chaves: Lista de chaves (CPFs, nomes)
    # valores: Lista de dados associados (Objeto Passageiro)
    # filhos: Lista de referências para nos filhos
    def __init__(self, folha=False):
        self.folha = folha
        self.chaves = []
        self.valores = []   
        self.filhos = []
        
class ArvoreB:
    def __init__(self, t=3):
        # t: Grau minimo da arvore (define tam min/max dos nós)
        self.raiz = ArvoreBNodo(True)
        self.t = t  
    
    # ---------------------------------------
    # Busca uma chave (k) e retorna o valor associado
    # ---------------------------------------
    def buscar(self, k, nodo_pai=None):
        if nodo_pai is None:
            nodo_pai = self.raiz
        
        # Encontra o índice da primeira chave maior ou igual a k
        i = 0
        while i < len(nodo_pai.chaves) and k > nodo_pai.chaves[i]:
            i += 1
            
        # Se encontrou a chave, retorna o val correspondente
        if i < len(nodo_pai.chaves) and k == nodo_pai.chaves[i]:
            return nodo_pai.valores[i] 
        
        # Se for folha e não achou, a chave não existe
        if nodo_pai.folha:
            return None
        
        # Se não é folha, desce recursivamente para o filho apropriado
        return self.buscar(k, nodo_pai.filhos[i])
    
    # ---------------------------------------
    # Retorna uma lista de valores cujas chaves começam com o prefixo
    # ---------------------------------------
    def buscar_parcial(self, prefixo, nodo=None, resultados=None):
        if resultados is None:
            resultados = []
        if nodo is None:
            nodo = self.raiz

        i = 0
        while i < len(nodo.chaves):
            chave_atual = nodo.chaves[i]
            # Verifica se não é None e se começa com o prefixo
            if chave_atual and str(chave_atual).startswith(prefixo):
                # Se o valor for uma lista (caso dos nomes), estende a lista de resultados
                val = nodo.valores[i]
                if isinstance(val, list):
                    resultados.extend(val)
                else:
                    resultados.append(val)
            if not nodo.folha:
                self.buscar_parcial(prefixo, nodo.filhos[i], resultados)
            
            i += 1
            
        if not nodo.folha:
            self.buscar_parcial(prefixo, nodo.filhos[i], resultados)
            
        return resultados
    
    # ---------------------------------------
    # Insere uma nova chave e valor na árvore
    # ---------------------------------------       
    def inserir(self, chave, valor):
        raiz = self.raiz
        
        # Se arvore ta cheia, divide e cresce em altura
        if len(raiz.chaves) == (2 * self.t) - 1:
            nova_raiz = ArvoreBNodo(False)
            self.raiz = nova_raiz
            nova_raiz.filhos.insert(0, raiz) 
            self._dividir_nodo_filho(nova_raiz, 0)
            self._inserir_nodo_nao_cheio(nova_raiz, chave, valor) 
        else:
            self._inserir_nodo_nao_cheio(raiz, chave, valor)     
    
    # ---------------------------------------
    # Divide um nó filho cheio em dois e sobe a mediana
    # ---------------------------------------    
    def _dividir_nodo_filho(self, nodo_pai, i):
        t = self.t                                          
        nodo_filho = nodo_pai.filhos[i]                
        z = ArvoreBNodo(nodo_filho.folha)
        
        # PEGA O MEIO (Chave e Valor)
        chave_meio = nodo_filho.chaves[t-1]
        valor_meio = nodo_filho.valores[t-1] 
        
        # MOVE METADE DIREITA PARA Z (Chaves e Valores)
        z.chaves = nodo_filho.chaves[t: (2 * t) - 1]
        z.valores = nodo_filho.valores[t: (2 * t) - 1] 
        
        if not nodo_filho.folha:
            z.filhos = nodo_filho.filhos[t: 2*t]

        # ATUALIZA NODO FILHO (Manteve metade esquerda)
        nodo_filho.chaves = nodo_filho.chaves[0: t-1]
        nodo_filho.valores = nodo_filho.valores[0: t-1] 
        
        if not nodo_filho.folha:
            nodo_filho.filhos = nodo_filho.filhos[0: t]        
        
        # CONECTA O NOVO NÓ Z AO PAI
        nodo_pai.filhos.insert(i + 1, z)
        
        # SUBIR A CHAVE E O VALOR PARA O PAI
        nodo_pai.chaves.insert(i, chave_meio)
        nodo_pai.valores.insert(i, valor_meio) 
    
    # ---------------------------------------
    # Insere em um nó que sabemos que não está cheio
    # ---------------------------------------    
    def _inserir_nodo_nao_cheio(self, nodo_pai, k, v):
        # k = chave (CPF)
        # v = valor 
        i = len(nodo_pai.chaves) - 1

        if nodo_pai.folha:
            # INSERÇÃO EM FOLHA (ORDENADA)
            nodo_pai.chaves.append(None)  
            nodo_pai.valores.append(None) 

            while i >= 0 and k < nodo_pai.chaves[i]:
                # Empurra chave e valor para frente
                nodo_pai.chaves[i + 1] = nodo_pai.chaves[i]
                nodo_pai.valores[i + 1] = nodo_pai.valores[i] 
                i -= 1
            
            # Insere na posição correta
            nodo_pai.chaves[i + 1] = k
            nodo_pai.valores[i + 1] = v 
            
        else:
            # NO INTERNO (Encontrar filho)
            while i >= 0 and k < nodo_pai.chaves[i]:
                i -= 1
            i += 1 
            
            if len(nodo_pai.filhos[i].chaves) == (2 * self.t) - 1:
                self._dividir_nodo_filho(nodo_pai, i)
                
                if k > nodo_pai.chaves[i]:
                    i += 1
            
            # Recursão passando o valor v
            self._inserir_nodo_nao_cheio(nodo_pai.filhos[i], k, v)