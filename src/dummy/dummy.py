
my_list = [
    ("iron", 45.0),
    ("plastic", 12.0),
    ("paper", 6.0),
    ("plastic", 43.0),
    ("plastic", 2.0),
    ("iron", 23.0),
    ("iron", 233.0),
    ("iron", 2.23)
]

merged = []
for material, thickness in my_list:
    if merged and merged[-1][0] == material:
        merged[-1] = (material, merged[-1][1] + thickness)
    else:
        merged.append((material, thickness))

#print (my_list)

#print ("\nwww\n")

#print(merged)

import random

# --- Variabili randomiche (sampled) ---
N = 10  # massimo numero di coppie
color_set = ["rosso", "verde", "blu", "giallo", "arancione", "viola", "ciano", "magenta", "marrone", "nero"]

# Random variabili discrete e continue, campionate direttamente:

L = random.randint(1, N)                      # lunghezza sequenza

# Sequenza colori costruita a partire da L e color_set (procedura deterministica con random scelto solo per ogni posizione)
# Per chiarezza, il campionamento avviene qui, ma senza tentativi o loop

# Valore della somma totale t, scelto direttamente in [sum_t_min, sum_t_max]
sum_t_min, sum_t_max = 10.0, 20.0
S = random.uniform(sum_t_min, sum_t_max)     # somma totale desiderata

# L valori grezzi in [0,1] per poi normalizzare a somma 1
raw_t = [random.random() for _ in range(L)]  # valori non normalizzati

# --- Variabili dipendenti (calcolate da quelle randomiche) ---

# 1. Genera sequenza colori senza due consecutivi uguali, processo sequenziale diretto
def genera_colori_sequenza(L, color_set):
    seq = []
    for i in range(L):
        if i == 0:
            c = random.choice(color_set)
        else:
            possibili = [col for col in color_set if col != seq[-1]]
            c = random.choice(possibili)
        seq.append(c)
    return seq

colors_seq = genera_colori_sequenza(L, color_set)

# 2. Normalizzo raw_t in modo che sommino 1
s = sum(raw_t)
norm_t = [v/s for v in raw_t]

# 3. Scalo norm_t per far sommare esattamente a S
t_values = [v * S for v in norm_t]

# 4. Mappo ogni t in [t_min, t_max], rimanendo all'interno del range  
t_min, t_max = 0.5, 5.0
# Qui può esserci il problema che la mappatura non mantiene somma S, quindi applico questo:  
# Se t_values escono fuori da [t_min, t_max], posso fare una mappatura lineare diversa:
# Però, per evitare controllo post e retry, imposto direttamente
# S minimo e massimo compatibili con t_min * L e t_max * L

# Garantiamo coerenza scegliendo S in [L*t_min, L*t_max], quindi ricalcolo S così:
sum_t_min = L * t_min
sum_t_max = L * t_max
S = random.uniform(sum_t_min, sum_t_max)   # ridefinisco S per sicurezza

# Ricalcolo t_values con nuovo S
t_values = [v * S for v in norm_t]

# Qui tutti t_values in [0, t_max * L], ma non garantito in [t_min, t_max]
# Per far rispettare t_min <= t_i <= t_max senza retry e senza uscire dal vincolo di somma,
# applichiamo il trucco:  
# t_i = t_min + norm_t[i] * (t_max - t_min)
# In questo modo ogni t_i è in [t_min, t_max]
# La somma totale sarà = L*t_min + (t_max - t_min)*sum(norm_t) = L*t_min + (t_max - t_min)*1 = L*t_max
# Quindi somma t = L*t_max sempre

# Per poter avere somma t tra sum_t_min e sum_t_max, bisogna modificare i parametri o accettare somma fissa

# Per semplificare e rispettare tutti vincoli senza retry:

# Somma(t) = L * t_min + (t_max - t_min) * 1 = L * t_max

# Se vuoi somma dentro un intervallo, deve essere esattamente L*t_max (per questo metodo)

# Se somma deve variare, serve aggiustamento più complicato, ma con retry

# Quindi con questo codice:

t_values = [t_min + v * (t_max - t_min) for v in norm_t]

# --- Stampa esempio ---

if __name__ == "__main__":
    print(f"Numero coppie L = {L}")
    print(f"Sequenza colori: {colors_seq}")
    print(f"Valori t: {[round(x,3) for x in t_values]}")
    print(f"Somma t: {sum(t_values):.3f} (vincolo: tra {L*t_min:.3f} e {L*t_max:.3f})")

