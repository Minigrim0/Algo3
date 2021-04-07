import sys

if len(sys.argv) < 3:
    print("usage : python3 ")


filepath, p = sys.argv[1:]
with open(filepath) as f:
    a = f.readline()
    I, J, K = a.split()
    I, J, K = int(I), int(J), int(K)

    temp = f.readline()
    f_j = temp.split()

    temp = f.readline()
    d_i = temp.split()

    temp = f.readline()
    c_j = temp.split()

    list_t_ij = []
    for j in range(J):
        temp = f.readline()
        list_t_ij.append(temp.split(" "))

    list_S_k = []  # dernier indice de chaque sous liste = p_k  [[S_k_1_1 ... S_k_1_k, p_k], ... , [S_k_K_1 ... S_k_K_k, p_k]]
    for k in range(K):
        temp = f.readline()
        list_S_k.append(temp.split(" "))


"""
centre = un site construit
j = un site
J = ensemble de sites possibles
f_j = cout de construction du site j
c_j = capacite maximal de doses du centre j (0 si site mais pas centre)

i = une famille
I = L'ensemble des familles
t_ij =  cout trajet de la famille i vers le centre j
d_i = la demande de dose de la famille i


S_k = liste de centre trop proche qui ont donc une penalite
p_k = penalite si trop proche
(faut relire les penalites j'ai pas tout compris)

But minimise le cout total 

famille pas d'office affecte au centre le plus proches car c_j est plus important
"""
