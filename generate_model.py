import sys
from docplex.mp.model import Model


if len(sys.argv) < 3:
    print("usage : python3 generate_models.py path_to_file.txt p")
    exit(1)


def parse_line(file):
    temp = file.readline()
    parsed_line = temp.split()
    for index in range(len(parsed_line)):
        parsed_line[index] = int(parsed_line[index])
    return parsed_line


filepath, p = sys.argv[1:]
model = Model("VaccinationOptimization")

with open(filepath) as f:
    # La première ligne du fichier contient I, J et K, respectivements
    # Le nombre de familles, le nombre de centres et le nombres de lignes
    # dans lesquelles il faut compter un cout suppplementaire si 2 centres sont ouverts
    I, J, K = (int(val) for val in f.readline().split())
    model.I, model.J, model.K = I, J, K

    f_j = parse_line(f)  # Coûts de contruction des sites 1, ..., J
    d_i = parse_line(f)  # Demandes de doses des familles 1, ..., I
    c_j = parse_line(f)  # Capacité max de vacc des sites 1, ..., J

    list_t_ij = []
    for i in range(I):
        temp = f.readline()
        list_t_ij.append([int(val) for val in temp.split()])

    list_S_k = []  # dernier indice de chaque sous liste = p_k  [[S_k_1_1 ... S_k_1_k, p_k], ... , [S_k_K_1 ... S_k_K_k, p_k]]
    list_pen_costs = []
    for k in range(K):
        temp = f.readline()
        *s_k, cost = [int(val) for val in temp.split()]
        list_S_k.append(s_k)
        list_pen_costs.append(cost)

    model.t_i_j = list_t_ij
    model.l_i_j = model.binary_var_matrix(I, J, name="l")

    # Présence ou non d'un site à un emplacement
    list_e = model.binary_var_list(J, name="e")

    # CONTRAINTES #

    # Vérifier que les familles sont bien associées à un et un seul centre
    for i in range(I):
        only_1_list = []
        for j in range(J):
            only_1_list.append(model.l_i_j[(i, j)])
        only_1 = model.sum(only_1_list)
        model.add_constraint(only_1 == 1, f"Famille {i} associe a seulement un centre")

    # Doses suffisantes dans les centres
    for j in range(J):
        list_vaccins_suffisants = []
        for i in range(I):
            list_vaccins_suffisants.append(
                (model.l_i_j[(i, j)] * d_i[i])
            )
        vaccins_suffisants = model.sum(list_vaccins_suffisants)
        model.add_constraint(vaccins_suffisants - (c_j[j] * list_e[j]) <= 0, f"Centre {j} possede assez de vaccins (et existe)")


    # COÛTS #

    # Coûts des trajets
    list_resultat = []
    for index, value in model.l_i_j.items():  # index is (i, j)
        list_resultat.append(value * model.t_i_j[index[0]][index[1]])

    model.total_trajet = model.sum(list_resultat)

    # Frais de construction
    frais_constru = [a * b for a, b in zip(list_e, f_j)]
    model.total_constru = model.sum(frais_constru)

    model.add_kpi(model.total_constru, "Total des couts de construction")
    model.add_kpi(model.total_trajet, "Total des couts des trajets des familles")

    model.minimize(model.total_constru + model.total_trajet)

    model.export_as_lp(basename="foo", path=".")
    # print(model.export_as_lp_string())


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

pour 0 < j < len(J)
    Binary exist_j # {0,1} vu que binaire
    Binary i_j

    total += exist_j * (f_j) + i_j * (t_ij)

    capacite_total >= tout les d_i
    capacite_site >= toute les familles qui lui sont lie => donc pas lier des famille si capacite trop petite
"""
