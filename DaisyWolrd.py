import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import random

st.set_page_config(layout="wide")

# ==== Session-Initialisierung ====
if "sim_data" not in st.session_state:
    st.session_state.sim_data = None

# ==== UI-Bereich ====
st.title("Daisyworld Simulation")
st.markdown("""
### Projektbeschreibung:
Willkommen zur Simulation des Daisyworld-Modells!  
Diese simuliert, wie sich weiße und schwarze Daisies bei wechselnder Temperatur auf einem Planeten ausbreiten und die globale Temperatur beeinflussen.  
Durch Albedo-Effekte entsteht ein selbstregulierendes Klimasystem.

👉 **Wähle in der Seitenleiste** deine gewünschten Startbedingungen!
""")

st.sidebar.title("🔧 Simulationseinstellungen")

grid_size = st.sidebar.slider("🌐 Gittergröße", 10, 100, 30)
steps = st.sidebar.slider("🕒 Anzahl Timesteps", 10, 200, 100)
white_frac = st.sidebar.slider("⚪ Weiße Daisies (Start)", 0.0, 1.0, 0.3, 0.05)
max_black = 1.0 - white_frac
black_frac = st.sidebar.slider(f"⚫ Schwarze Daisies (Start) (max: {max_black:.2f})", 0.0, max_black, min(0.3, max_black), 0.05)
empty_frac = 1.0 - white_frac - black_frac

st.sidebar.markdown("### 🌞 Albedo-Werte (Reflexion)")
albedo_white = st.sidebar.slider("Albedo Weiß", 0.0, 1.0, 1.0)
albedo_black = st.sidebar.slider("Albedo Schwarz", 0.0, 1.0, 0.0)
albedo_empty = st.sidebar.slider("Albedo Leer", 0.0, 1.0, 0.5)

solar_luminosity = st.sidebar.slider("🔆 Solarkonstante", 0.5, 2.0, 1.0, 0.05)
optimal_temp = st.sidebar.slider("🌡️ Optimale Wachstumstemperatur (°C)", 5, 40, 22)
reproduction_rate = st.sidebar.slider("🌱 Reproduktionsrate", 0.0, 1.0, 0.3, 0.05)
death_rate = st.sidebar.slider("💀 Sterberate", 0.0, 1.0, 0.1, 0.05)

# ==== Farben und Albedo ====
colors = {"white": 1, "black": 0, "empty": 0.5}
daisy_types = {"white": albedo_white, "black": albedo_black, "empty": albedo_empty}


# ==== Simulationsfunktionen ====
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


# ==== Simulation vorberechnen ====
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

# ==== Zeitschieber ====
step = st.slider("📅 Timestep auswählen", 0, steps - 1, 0, key="timestep_slider")

# ==== Darstellung ====
col1, col2 = st.columns([1, 1.5])

with col1:
    st.subheader(f"🌍 Daisy-Verteilung – Schritt {step}")
    image = np.vectorize(lambda x: colors[x])(grids[step])
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.imshow(image, cmap="gray", vmin=0, vmax=1)
    ax.axis("off")
    st.pyplot(fig)
    st.metric("🌡️ Temperatur", f"{temperatures[step]:.2f} °C")

with col2:
    st.subheader("📈 Populationsentwicklung & Temperatur")
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

# ==== Quellen & Berechnungen ====
st.markdown("### 📚 Berechnungen & Quellen")
st.markdown("""
- Temperaturberechnung: `T = Solarkonstante × (1 - Albedo) × Skalierungsfaktor`  
- Temperaturabhängige Reproduktion und Mortalität der Daisies  
- Selbstregulierende Rückkopplung durch unterschiedliche Albedo-Effekte

**Quelle:**  
Lovelock, J. E., & Watson, A. J. (1983). The Daisyworld model. *Tellus B: Chemical and Physical Meteorology*  
""")
