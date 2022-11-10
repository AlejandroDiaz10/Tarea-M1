# Alejandro Díaz Villagómez - A01276769

from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import ChartModule, PieChartModule, CanvasGrid, BarChartModule

from CleaningModel import CleaningModel

N = int(input("Dame N columnas: "))  # x - width
M = int(input("Dame M filas: "))  # y - height
num_agents = int(input("Dame el número de agentes: "))
dirty_percentage = int(input("Dame el porcentaje de suciedad: "))
max_time = int(input("Dame el tiempo máx. de ejecución: "))


def agent_portrayal(agent):
    portrayal = {
        "Shape": "circle",
        "Filled": "true",
        "Layer": 0
    }

    if agent.type == 1:
        portrayal["Shape"] = "vacuum_pic.png"
        # portrayal["Color"] = ["#FF0000", "#FF9999"]
        # portrayal["stroke_color"] = "#00FF00"
        portrayal["r"] = 1,
    else:
        # portrayal["Shape"] = "garbage_pic.png"
        portrayal["Color"] = "grey"
        portrayal["r"] = 0.2

    return portrayal


grid = CanvasGrid(
    agent_portrayal,
    N,
    M,
    600,
    600
)

# Tiempo(x) vs celdas sucias(y)
chart_clean_cells = ChartModule([{
    'Label': 'Basura_Restante',
    'Color': 'Black'}],
    data_collector_name='datacollector',
    canvas_height=40,
    canvas_width=80)

# Porcentaje de celdas limpias
chart_percentage_clean = PieChartModule([
    {'Label': 'Celdas_Limpias', 'Color': 'Green'},
    {'Label': 'Celdas_Sucias', 'Color': 'Red'}],
    data_collector_name='datacollector',
    canvas_height=500,
    canvas_width=500)

# Movimientos de los agentes
chart_agents_moves = ChartModule([{
    'Label': 'Movimientos_Agentes',
    'Color': 'Black'}],
    data_collector_name='datacollector',
    canvas_height=40,
    canvas_width=80)

# Inicializamos el Modelo
model_params = {"N": num_agents, "width": N, "height": M,
                "dirty": dirty_percentage, "time": max_time}

# Elementos que se mostrarán en el servidor
server = ModularServer(
    CleaningModel,
    [grid, chart_clean_cells, chart_percentage_clean, chart_agents_moves],
    "Cleaning Model",
    model_params
)

server.port = 8521
server.launch()
