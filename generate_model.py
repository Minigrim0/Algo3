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

    # 1) Vérifier que les familles sont bien associées à un et un seul centre
    for i in range(I):
        only_1_list = []
        for j in range(J):
            only_1_list.append(model.l_i_j[(i, j)])
        only_1 = model.sum(only_1_list)
        model.add_constraint(only_1 == 1, f"Famille {i} associe a seulement un centre")

    # 2) Doses suffisantes dans les centres
    for j in range(J):
        list_vaccins_suffisants = []
        for i in range(I):
            list_vaccins_suffisants.append(
                (model.l_i_j[(i, j)] * d_i[i])
            )
        vaccins_suffisants = model.sum(list_vaccins_suffisants)
        model.add_constraint(vaccins_suffisants - (c_j[j] * list_e[j]) <= 0, f"Centre {j} possede assez de vaccins (et existe)")

    if p == "1":
        # 3) Création des variables contraintes si au moins 2 site sont trop proches
        apply_pen_list = model.binary_var_list(K, name="apply_pen")
        model.M = J+1
        for index, s_k in enumerate(list_S_k):  # Chaque groupe de centres considérés trop proches
            center_count_list = []
            for j in s_k:
                center_count_list.append(list_e[j])
            center_count = model.sum(center_count_list)
            model.add_constraint(center_count - model.M*apply_pen_list[index] <= 1)

    # COÛTS #

    # 1) Coûts des trajets
    list_resultat = []
    for index, value in model.l_i_j.items():  # index is (i, j)
        list_resultat.append(value * model.t_i_j[index[0]][index[1]])

    model.total_trajet = model.sum(list_resultat)

    # 2) Frais de construction
    frais_constru = [a * b for a, b in zip(list_e, f_j)]
    model.total_constru = model.sum(frais_constru)

    model.add_kpi(model.total_constru, "Total des couts de construction")
    model.add_kpi(model.total_trajet, "Total des couts des trajets des familles")

    if p == '1':
        # 3) Contrainte de proximité
        list_penalite = [a * b for a, b in zip(apply_pen_list, list_pen_costs)]
        model.total_penalite = model.sum(list_penalite)
        model.add_kpi(model.total_penalite, "Penalite due a des centres trop proches")
        model.minimize(model.total_constru + model.total_trajet + model.total_penalite)
    else:
        model.minimize(model.total_constru + model.total_trajet)

    model.export_as_lp(basename="foo", path=".")
