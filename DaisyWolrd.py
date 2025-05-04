import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import random

st.set_page_config(layout="wide")

if "sim_data" not in st.session_state:
    st.session_state.sim_data = None

st.title("Daisyworld Simulation")
st.markdown("""
Daisyworld ist ein Gedankenexperiment, welches 1983 vom englischen Klimaforscher James Lovelock entwickelt wurde. Es ist ein vereinfachtes Modell eines Planeten ähnlich der Erde, welcher um einen Sonnenähnlichen Stern kreist. Es zeigt, wie Leben das Klima eines Planeten stabil halten kann, ohne Planung oder Absicht. 

Auf dem Planeten wachsen nur zwei Arten von Blumen:

•  Weisse Gänseblümchen, welche viel Sonnenlicht reflektieren, eine hohe Albedo haben und dadurch ihre Umgebung abkühlen
	
•  Schwarze Gänseblümchen, welche viel Sonnenlicht absorbieren, eine tiefe Albedo haben und somit ihre Umgebung erwärmen

Die Energie der Daisyworld kommt auschliesslich von dem Sonnenähnlichen Stern. Je nachdem welcher Blumentyp stärker vertreten ist, verändert sich die Gesamtalbedo des Planeten. Beide Blumentypen wachsen bei Temperaturen zwischen ca. 5°C und 40°C, wobei bei 22°C ein Temperaturoptimum besteht und beide Typen gleich stark vertreten sind. Dies ist auf eine direkte Rückkopplung zwischen Leben und Klima zurückzuführen: Wird es zu kalt (Temperaturen unter 22°C), wachsen mehr schwarze Blumen, welche das Klima erwärmen. Wird es zu heiss (Temperaturen über 22°C), wachsen mehr weisse Blumen und kühlen den Planeten. Zusätzlich gibt es freie, unbewachsene Flächen auf dem Planeten, die Platz für neues Wachstum bieten, sie haben eine mittlere Albedo. So entsteht eine Art Gleichgewicht: Durch das Verhältnis der Blumentypen pendelt sich die Temperatur immer wieder um das Optimum bei 22°C ein.

Daisyworld ist deshalb wichtig, weil sie eine sehr einfache Darstellung von natürlichen Rückkopplungen ist. Sie hilft zu verstehen, wie Leben und Umwelt zusammenwirken und wie empfindlich das Klima auf äussere Veränderungen reagiert, durch eine höhere Sonneneinstrahlung oder menschliche Einflüsse. Das Modell veranschaulicht zudem die Gaia-Hypothese, ein zentrales Prinzip aus der Klimaforschung, nach der die Erde und das Leben auf ihr ein sich selbst regulierendes System bilden.


#### Wähle in der Seitenleiste die gewünschten Startbedingungen aus.
""")

st.sidebar.title("Simulationseinstellungen")

grid_size = st.sidebar.slider("Gittergrösse", 10, 100, 30)
steps = st.sidebar.slider("Anzahl Timesteps", 10, 200, 100)
white_frac = st.sidebar.slider("Weisse Daisies (Start)", 0.0, 1.0, 0.3, 0.05)
max_black = 1.0 - white_frac
black_frac = st.sidebar.slider(f"Schwarze Daisies (Start) (max: {max_black:.2f})", 0.0, max_black, min(0.3, max_black), 0.05)
empty_frac = 1.0 - white_frac - black_frac

st.sidebar.markdown("Albedo-Werte (Reflexion)")
albedo_white = st.sidebar.slider("Albedo Weiss", 0.0, 1.0, 1.0)
albedo_black = st.sidebar.slider("Albedo Schwarz", 0.0, 1.0, 0.0)
albedo_empty = st.sidebar.slider("Albedo Leer", 0.0, 1.0, 0.5)

solar_luminosity = st.sidebar.slider("Solarkonstante", 0.5, 2.0, 1.0, 0.05)
optimal_temp = st.sidebar.slider("Optimale Wachstumstemperatur (°C)", 5, 40, 22)
reproduction_rate = st.sidebar.slider("Reproduktionsrate", 0.0, 1.0, 0.3, 0.05)
death_rate = st.sidebar.slider("Sterberate", 0.0, 1.0, 0.1, 0.05)

colors = {"white": 1, "black": 0, "empty": 0.5}
daisy_types = {"white": albedo_white, "black": albedo_black, "empty": albedo_empty}

def initialize_grid(size):
    return np.random.choice(
        ["white", "black", "empty"],
        size=(size, size),
        p=[white_frac, black_frac, empty_frac]
    )

def calculate_temperature(grid):
    albedo_grid = np.vectorize(lambda x: daisy_types[x])(grid)
    global_albedo = np.mean(albedo_grid)
    return solar_luminosity * (1 - global_albedo) * (2 * optimal_temp)


def update_daisies(grid, temperature):
    new_grid = grid.copy()
    for i in range(grid.shape[0]):
        for j in range(grid.shape[1]):
            if grid[i, j] == "empty":
                if random.random() < reproduction_rate * (1 - abs(temperature - optimal_temp) / optimal_temp):
                    new_grid[i, j] = random.choice(["white", "black"])
            elif grid[i, j] in ["white", "black"]:
                if random.random() < death_rate * abs(temperature - optimal_temp) / optimal_temp:
                    new_grid[i, j] = "empty"
    return new_grid


def simulate_daisyworld(grid, steps):
    grids = []
    temperatures = []
    populations = {"white": [], "black": [], "empty": []}

    for _ in range(steps):
        temp = calculate_temperature(grid)
        temperatures.append(temp)
        populations["white"].append(np.sum(grid == "white"))
        populations["black"].append(np.sum(grid == "black"))
        populations["empty"].append(np.sum(grid == "empty"))
        grids.append(grid.copy())
        grid = update_daisies(grid, temp)

    return grids, temperatures, populations

if "last_params" not in st.session_state or st.session_state.last_params != (
    grid_size, steps, white_frac, black_frac, albedo_white, albedo_black,
    albedo_empty, solar_luminosity, optimal_temp, reproduction_rate, death_rate
):
    initial_grid = initialize_grid(grid_size)
    simulation = simulate_daisyworld(initial_grid, steps)
    st.session_state.simulation_data = simulation
    st.session_state.last_params = (
        grid_size, steps, white_frac, black_frac, albedo_white, albedo_black,
        albedo_empty, solar_luminosity, optimal_temp, reproduction_rate, death_rate
    )

grids, temperatures, populations = st.session_state.simulation_data

step = st.slider("Timestep auswählen", 0, steps - 1, 0, key="timestep_slider")

col1, col2 = st.columns([1, 1.5])

with col1:
    st.subheader(f"Daisy-Verteilung – Schritt {step}")
    image = np.vectorize(lambda x: colors[x])(grids[step])
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.imshow(image, cmap="gray", vmin=0, vmax=1)
    ax.axis("off")
    st.pyplot(fig)
    st.metric("Temperatur", f"{temperatures[step]:.2f} °C")

with col2:
    st.subheader("Populationsentwicklung & Temperatur")
    fig2, ax2 = plt.subplots(figsize=(10, 4))
    ax2.plot(populations["white"], label="White", color="skyblue")
    ax2.plot(populations["black"], label="Black", color="black")
    ax2.plot(populations["empty"], label="Empty", color="green")
    ax2.axvline(x=step, color="orange", linestyle="--", linewidth=2, label="Aktueller Schritt")
    ax2.set_xlabel("Timestep")
    ax2.set_ylabel("Anzahl Daisies")
    ax2.legend(loc="upper left")

    ax_temp = ax2.twinx()
    ax_temp.plot(temperatures, label="Temperatur", color="red", linestyle="--")
    ax_temp.set_ylabel("Temperatur (°C)", color="red")

    ax2.set_title("Populationsentwicklung & Temperatur")
    st.pyplot(fig2)

st.markdown("### Berechnungen")
st.markdown("""
Daisyworld erhält ihre Energie von einer Sonne. Die Einstrahlung berechnet sich mit:

s  =  s\u2080 ∗ q
	
wobei s\u2080 die ursprüngliche Sonnenenergie, also die maximale Sonnenenergie, die auf den Planeten treffen kann (Solarkonstante) ist und q ein Faktor, der die Veränderung der Sonnenleistung angibt (z.B. über den Tag verteilte Schwankungen).

Je nachdem, wie viele schwarze, weisse oder unbewachsene Flächen es gibt, verändert sich die Gesamtalbedo des Planeten:

A  =  a\u2091 * x\u2091  +  a\u2092 * x\u2092  +  a\u2095 * x\u2095
	
Dabei stehen a\u2091, a\u2092 und a\u2095 für die Albedo der verschiedenen Flächen und x\u2091, x\u2092 und x\u2095 für die jeweiligen Flächenanteile.

Ein Teil der Sonnenstrahlung wird also reflektiert, der Rest der Energie erwärmt den Planeten. Die absorbierte Energie berechnet sich durch:

S\u2090\u2091 = s * (1 - A)
	 
Die Temperatur wird durch das Stefan-Boltzmann-Gesetz berechnet:

T = (S\u2090\u2091/Boltzmann-Konstante)^0.25
	 
wobei Stefan-Boltzmann-Konstante = 5.67 * 10^(-8)

Je nach Temperatur wachsen die Blumen besser oder schlechter. Die Wachstumsrate ist bei 22.5°C am höchsten und nimmt bei heisserem oder kälterem Klima ab:

beta(T) = 1- 0.003265 * (T - 22.5)^2
	
Die Blumen wachsen nur zwischen ca. 5°C und 40°C. Ausserhalb dieses Bereichs sterben sie ab.

Die Veränderung des Flächenanteils schwarzer und weisser Blumen hängt von ihrer Wachstumsrate und Sterberate y ab:

d\u2093\u2097 / d\u209C = x\u2097 *(beta(T) * (x\u2095 - y))
	 
Dabei steht l für die jeweilige Blume und xu für den unbewachsenen Boden.

Für jeden Zeitschritt berechnet das Modell:

1. Planetare Albedo
	
2. Welche Temperatur sich mit der neuen Albedo berechnet
	
3. Welche Blumen wie stark wachsen
	
4. Wie sich die Flächenanteile verändern 

Daraus ergibt sich für jeden Zeitschritt eine neue Anzahl der vorhandenen Flächen, die dann sowohl im Diagramm als auch im Flächengitter dargestellt werden. 


### Quellen

https://archiv.leibniz-ipn.de/System_Erde/Daisyworld/daisyweb.html#tth_Sim2

https://personal.ems.psu.edu/~dmb53/DaveSTELLA/Daisyworld/daisyworld_model.htm

https://de.wikipedia.org/wiki/Daisyworld

https://www.pik-potsdam.de/~bloh/ 

https://ccl.northwestern.edu/netlogo/models/Daisyworld 

https://www.youtube.com/watch?v=sCxIqgZA7ag

""")
