# Alejandro Díaz Villagómez - A01276769

from random import randint
from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from mesa import batch_run
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


# Calculamos las celdas limpias y sucias
def compute_clean_cells(model):
    return model.num_cells - model.dirty_cells


def compute_dirty_cells(model):
    return model.dirty_cells


# Calculamos los movimientos totales de todos los agentes
def show_agent_moves(model):
    tot_steps = []
    for a in model.schedule.agents:
        if a.type == 1:
            # print("ID: " + str(a.unique_id) + " S: " + str(a.personal_steps))
            tot_steps.append(a.personal_steps)
    tot = sum(tot_steps)
    return tot


# AGENTE - Hay 2 tipos: basura y aspiradora
class CleaningAgent(Agent):
    def __init__(self, unique_id, model, agent_type):
        super().__init__(unique_id, model)
        self.type = agent_type
        self.personal_steps = 0

    # ¿Qué pasará en cada unidad de tiempo?
    def step(self):
        if self.type == 1:
            # Si no limpiamos, nos movemos
            if self.clean_cell() == False:
                self.move()

    # Buscamos los movimientos posibles
    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
            # Posición actual
            self.pos,
            # Vecinos en diagonal
            moore=True,
            # Puede que un agente no se mueva
            include_center=True
        )
        new_position = self.random.choice(possible_steps)
        # Checamos que la nueva posición no coincida con ningún otro cleaning agent
        cellmates = self.model.grid.get_cell_list_contents([new_position])
        if len(cellmates) > 0:
            for c in cellmates:
                if c.type == 1:
                    self.model.grid.move_agent(self, self.pos)
                    return
        # Si nos podemos mover, aumentamos el conteo de movimientos del agente
        self.personal_steps += 1
        #print("ID: " + str(self.unique_id) + " STEPS: " + str(self.personal_steps))
        self.model.grid.move_agent(self, new_position)

    # Función para limpiar las celdas sucias
    def clean_cell(self):
        # Limpia la celda en la que estoy (si está sucia)
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        if len(cellmates) > 0:
            for c in cellmates:
                if c.type == 0:
                    self.model.grid.remove_agent(c)
                    self.model.dirty_cells -= 1
                    return True
        return False


# MODELO - "Ambiente"
class CleaningModel(Model):
    def __init__(self, N, width, height, dirty, time):
        self.steps = 0
        self.maxTime = time
        self.num_cells = width * height
        self.num_agents = N
        self.dirty_cells = int((dirty * width * height) / 100)

        # Espacio físico para los agentes
        # No permitimos que se salgan del mapa
        self.grid = MultiGrid(width, height, False)
        self.schedule = RandomActivation(self)
        self.running = True

        # Creamos una lista con coordenadas únicas
        points = {(randint(0, height - 1), randint(0, width - 1))
                  for i in range(self.dirty_cells + 1)}
        while len(points) < self.dirty_cells + 1:
            points |= {(randint(0, height - 1), randint(0, width - 1))}
        points = list(list(x) for x in points)

        # Agregamos los agentes al mapa
        j = 0
        for i in range(self.num_agents + self.dirty_cells):
            if i < self.num_agents:
                a = CleaningAgent(i, self, 1)
                self.schedule.add(a)
                # Posicionamos a los agentes en la celda (1, 1)
                self.grid.place_agent(a, (1, 1))
            else:
                x = points[j][1]
                y = points[j][0]
                if x == 1 and y == 1:
                    x = points[self.dirty_cells][0]
                    y = points[self.dirty_cells][0]
                a = CleaningAgent(i, self, 0)
                self.schedule.add(a)
                self.grid.place_agent(a, (x, y))
                j += 1

        # Metrics we will measure about our model
        self.datacollector = DataCollector(
            model_reporters={
                "Basura_Restante": compute_dirty_cells,
                "Celdas_Limpias": compute_clean_cells,
                "Celdas_Sucias": compute_dirty_cells,
                "Movimientos_Agentes": show_agent_moves,
            },
        )

    # ¿Qué pasará en cada unidad de tiempo?
    def step(self):
        # Corre 1 tick en el reloj de nuestra simulación
        self.steps += 1
        self.datacollector.collect(self)
        self.schedule.step()

        if self.dirty_cells == 0:
            print("TIME NEEDED: " + str(self.steps))
            print("CLEAN CELLS: " + str(self.num_cells))
            print("PERCENTAGE CLEAN CELLS: 100.0%")
            print("AGENT MOVES: " + str(show_agent_moves(self)))
            self.datacollector.collect(self)
            self.running = False

        if self.steps == self.maxTime:
            print("TIME LIMIT: " + str(self.steps))
            print("CLEAN CELLS: " + str(self.num_cells - self.dirty_cells))
            print("PERCENTAGE CLEAN CELLS: " +
                  str(100 - (self.dirty_cells * 100 / self.num_cells)) + "%")
            print("AGENT MOVES: " + str(show_agent_moves(self)))
            self.datacollector.collect(self)
            self.running = False

    def run_model(self):
        while self.running:
            self.step()


# Parámetros para correr el modelo varias veces
model_params = {
    "N": range(5, 16, 5),
    "width": 10,
    "height": 10,
    "dirty": range(10, 51, 10),
    "time": 50
}

# Usaremos batch_run
results = batch_run(
    CleaningModel,
    parameters=model_params,
    iterations=100,
    number_processes=1,
    data_collection_period=1,
    display_progress=False,
)

# Convertimos los resultados en un DataFrame
results_df = pd.DataFrame(results)
# print(results_df.keys())

# Agrupamos la información y obtenemos solo los últimos valores
grouped_iterations = pd.DataFrame(
    columns=['iteration', 'N', 'Basura_Restante', 'Celdas_Limpias', 'Celdas_Sucias', 'Movimientos_Agentes'])

for it, group in results_df.groupby(["iteration"]):
    grouped_iterations = grouped_iterations.append(
        {'iteration': group.iloc[-1].iteration,
         'N': group.iloc[-1].N,
         'Basura_Restante': group.iloc[-1].Basura_Restante,
         'Celdas_Limpias': group.iloc[-1].Celdas_Limpias,
         'Celdas_Sucias': group.iloc[-1].Celdas_Sucias,
         'Movimientos_Agentes': group.iloc[-1].Movimientos_Agentes},
        ignore_index=True)
#print(grouped_iterations.to_string(index=False, max_rows=25))
print(grouped_iterations.to_string(index=False))


# Hacemos una gráfica que representa las celdas limpias en las 100 iteraciones
# El grid es de 10x10 (100 celdas) y el tiempo máximo es de 50 pasos
sns.set_theme()
sns.scatterplot(
    data=grouped_iterations,
    x="iteration", y="Celdas_Limpias",
)
plt.title('Celdas limpias vs Iteraciones')
plt.xlabel('Iteraciones')
plt.ylabel('Celdas limpias')
plt.show()
