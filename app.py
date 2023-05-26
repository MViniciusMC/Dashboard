import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.express as px
import statsmodels as sm
from dash import Dash, Input, Output, dcc, html
from sklearn import datasets, linear_model
from sklearn.metrics import mean_squared_error, r2_score

##Instanciando o APP
app = Dash(external_stylesheets=[dbc.themes.MATERIA])
server = app.server
# ======================================Trabalho com DADOS===============================#
# importanto a base de dados
df = pd.read_excel("novosdadoscompiladosv1.xlsx")


# trabalhando data e emissão
df["Data"] = df["Encerramento"].dt.strftime("%Y/%m")
df["Dias"] = df["Encerramento"].dt.strftime("%d")
df["Emissão"] = df["Emissão"].dt.strftime("%d/%m/%Y")
df["Encerramento"] = df["Encerramento"].dt.strftime("%d/%m/%Y")

filtro = df["Data"] != "2021/12"
df = df[filtro]

# nova base de daos com valores sort por data
df1 = df.sort_values("Data")

# Lista de data unica
Data_unica = list(df1["Data"].unique())

# lista de serviços no mês numerados por data
c = list(df1.groupby("Data")["Serviços"].sum())
serviços_total_mês = []
for i in c:
    serviços_total_mês.append(float(f"{i:.2f}"))


# Frequencia por mês baseado no numero de os
Frequencia_por_mês = list(df1.groupby("Data")["Nro. O.S."].count())

# Meses numerados (Para previsões)
meses_numerados = []
number = 1
for i in Data_unica:
    meses_numerados.append(number)
    number += 1

# 

# mão de obra média mês passado
a = list(df1["Data"].unique())
a.sort()
filtro = df["Data"] == a[-2]
dados_ultimo_mes = df[filtro]
mão_de_obra_total_mes_passado = dados_ultimo_mes["Serviços"].sum()
frequencia_ultimo_mes = dados_ultimo_mes["Nro. O.S."].count()
valor_float = mão_de_obra_total_mes_passado / frequencia_ultimo_mes
valor = f"{valor_float:.2f}"
# mão de obra média mês atual
a = list(df1["Data"].unique())
a.sort()
filtro = df["Data"] == a[-1]
dados_ultimo_mes = df[filtro]
mão_de_obra_total_mes_passado = dados_ultimo_mes["Serviços"].sum()
frequencia_ultimo_mes = dados_ultimo_mes["Nro. O.S."].count()
mdo_medio_mes_atual_float = mão_de_obra_total_mes_passado / frequencia_ultimo_mes
mdo_medio_mes_atual = f"R$ {mdo_medio_mes_atual_float:.2f}"

# define opções
opções = a
opções.append("Todos os meses")
opções.append("Valor Todos os Meses")
opções.append("Frequencia Todos os Meses")

# apenas mês atual
df_atual = df.loc[df["Data"] == list(df1["Data"].unique())[-1], :]
# serviços do mês atual
df_atual.to_excel("DadosV1Atual.xlsx")
serviços_mês_atual = df_atual.groupby("Dias")["Serviços"].sum()
serviços_mês_atual = serviços_mês_atual.reset_index()
serviços_mês_atual.to_excel("DadosV1mesAtual.xlsx")
df2 = pd.read_excel("DadosV1mesAtual.xlsx")
# apenas mês passado
df_mes_passado = df.loc[df["Data"] == list(df1["Data"].unique())[-2], :]
serviços_mês_passado = df_mes_passado.groupby("Dias")["Serviços"].sum()
serviços_mês_passado = serviços_mês_passado.reset_index()
# pega record de vendas
serviços_do_ano = list(df.groupby("Encerramento")["Serviços"].sum())
h = 1
for i in serviços_do_ano:
    if i > h:
        maior_valor = i
        h = i
maior_valor = f"R$ {maior_valor:.2f}"
# record de vendas mês passado
apenas_serviços_mes_passado = list(df_mes_passado.groupby("Encerramento")["Serviços"].sum())
h = 1
for i in apenas_serviços_mes_passado:
    if i > h:
        maior_valor_mes_passado = i
        h = i
maior_valor_mes_passado = f"R$ {maior_valor_mes_passado:.2f}"
# vender_por_dia
vpd = "R$ 1500,00"
# variação
variação = 100 - (valor_float * 100) / mdo_medio_mes_atual_float
variação = f"R$ {variação:.2f}%"

# Total vendido até hoje
vendido_ate_agr = df_atual["Serviços"].sum()
vendido_ate_agr_str = f"R$ {vendido_ate_agr:.2f}"
# metas
lista_de_metas = [50000, 45000, 40000]
lista_do_pie = [50000 - vendido_ate_agr, vendido_ate_agr]
porcentagem_meta_atingida = (vendido_ate_agr * 100) / 50000
dicionario_pie = {
    "meta atingida": porcentagem_meta_atingida,
    "Falta": 100 - porcentagem_meta_atingida,
}
names = ["meta atingida", "Quanto Falta meta"]
# opções deopdown vendas diarias
opções_venda_diaria = ["Frequencia", "Serviços", "Previsão serviços"]
# frequencia de serviços dia mes atual
frequencia_por_dia = df_atual.groupby("Dias")["Nro. O.S."].count()
frequencia_por_dia = frequencia_por_dia.reset_index()
# pega dia atual
lista_de_dias = list(df_atual["Dias"].unique())
dia_atual = 0
dia_util_atual = 0
for i in lista_de_dias:
    dia_util_atual += 1
    if int(i) > dia_atual:
        dia_atual = int(i)
# média vende dia

m_vendido_dia = vendido_ate_agr / dia_util_atual
m_vendido_dia = f"R$ {m_vendido_dia:.2f}"
# opções do dropdown dias
lista_de_dias_int = list(range(1, 31))
# Trabalho com sklearn
reg1 = linear_model.LinearRegression()
array1 = np.array(serviços_mês_atual["Dias"])
reg1.fit(array1.reshape(-1, 1), serviços_mês_atual)
previsão = reg1.predict([[20]])
previsão = previsão.max()
previsão = f"R$ {previsão:.2f}"
# previsão base mês
reg2 = linear_model.LinearRegression()
array2 = np.array(meses_numerados)
reg2.fit(array2.reshape(-1, 1), df.groupby("Data")["Serviços"].sum())
previsão_mes_atual = reg2.predict([[meses_numerados[-1]]])
previsão_mes_atual = previsão_mes_atual.max()
previsão_mes_atual = f"R$ {previsão_mes_atual:.2f}"
# lista de metas
lista_de_metas = [40000, 45000, 50000, 55000, 60000]


# ======================================Trabalho com Gráficos===============================#
# grafico que mostra todos os seriços feitos no mês
fig = px.bar(df1, x="Data", y="Serviços")
fig.update_layout(yaxis=dict(title="Todos os serviços"), xaxis=dict(title="Mesês"), height=350)

# grafico de serviços totais por mês
fig1 = px.bar(x=Data_unica, y=serviços_total_mês, text_auto=True)
fig1.update_layout(yaxis=dict(title="MDO Serviços"), xaxis=dict(title="Mesês"))

# Grafico frequencia por mês
fig3 = px.bar(x=Data_unica, y=Frequencia_por_mês, text_auto=True)
fig3.update_layout(yaxis=dict(title="Frequencia"), xaxis=dict(title="Mesês numerados"))

# grafico Diario
fig4 = px.scatter(serviços_mês_atual, x="Dias", y="Serviços")
fig4.update_traces(mode="lines+markers")

# grafico metas
fig5 = px.pie(df_atual, values=dicionario_pie, hole=0.6, names=names, height=200)

# ======================================Layout===============================#
app.layout = dbc.Container(
    children=[
        # linha1
        dbc.Row(
            dbc.Card(
                dbc.CardBody(
                    [
                        dbc.Row(html.Legend("Todos os serviços")),  # final ROW
                        dbc.Row(
                            [
                                dbc.Col(
                                    dbc.Card(
                                        dbc.CardBody(
                                            [
                                                html.H4(
                                                    "Mão de obra média ultimo mês",
                                                ),
                                                html.H1(
                                                    "R$ " + valor,
                                                    style={
                                                        "text-align": "center",
                                                        "font-size": "100%",
                                                    },
                                                ),
                                                html.H4("Mão de obra média mês atual"),
                                                html.H1(
                                                    mdo_medio_mes_atual,
                                                    style={
                                                        "text-align": "center",
                                                        "color": "blue",
                                                        "font-size": "100%",
                                                    },
                                                ),
                                                html.H4("Variação"),
                                                html.H1(
                                                    variação,
                                                    style={"font-size": "100%", "color": "green"},
                                                ),
                                            ]
                                        ),
                                        style={"height": "200"},
                                    ),
                                    align="center",
                                    style={
                                        "font-size": "500%",
                                        "text-align": "center",
                                        "height": "500%",
                                    },
                                ),
                                dbc.Col(
                                    dbc.Card(
                                        dbc.CardBody(
                                            [
                                                html.H4("Todos os serviços dos meses"),
                                                dcc.Dropdown(
                                                    opções,
                                                    id="dropdown grafico 1",
                                                    value="Todos os meses",
                                                ),
                                                dcc.Graph(id="Grafico1", figure=fig),
                                            ]
                                        )  # final cardbody interno
                                    )  # final Card
                                ),  # final Col
                            ],
                            className="g-2 my-auto",
                            style={"margin-top": "7px"},
                        ),  # final Row
                    ]
                )  # Final CardBody
            ),  # Final Card
            className="g-2 my-auto",
            style={"margin-top": "7px"},
        ),  # final Row
        #########
        # linha2
        dbc.Row(
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        [
                            dbc.Row(
                                [
                                    dbc.Col(
                                        dbc.Card(
                                            dbc.CardBody(
                                                [
                                                    html.H6("Diario de Venda"),
                                                    dcc.Dropdown(
                                                        opções_venda_diaria,
                                                        value="Serviços",
                                                        id="dropdown diario de vendas",
                                                    ),
                                                    dcc.Graph(id="venda_diaria", figure=fig4),
                                                ]
                                            )
                                        ),
                                        md=9,
                                        style={"height": "100%"},
                                    ),
                                    dbc.Col(
                                        dbc.Card(
                                            dbc.CardBody(
                                                [
                                                    html.H5(
                                                        "Record De Venda Dia",
                                                        style={"text-align": "center"},
                                                    ),
                                                    html.H1(
                                                        maior_valor,
                                                        style={
                                                            "text-align": "center",
                                                            "color": "blue",
                                                        },
                                                    ),
                                                    html.H5(
                                                        "Record De Venda Dia mês passado",
                                                        style={"text-align": "center"},
                                                    ),
                                                    html.H1(
                                                        maior_valor_mes_passado,
                                                        style={
                                                            "text-align": "center",
                                                            "color": "red",
                                                        },
                                                    ),
                                                    html.H5(
                                                        "Porcentagem da meta atingida",
                                                        style={"text-align": "center"},
                                                    ),
                                                    dcc.Graph(id="Grafico de pizza", figure=fig5),
                                                ]
                                            ),
                                            style={"height": "100%"},
                                        )
                                    ),
                                ]
                            )
                        ]
                    )
                )
            )
        ),
        ##############
        # linha3
        dbc.Row(
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        [
                            dbc.Row(
                                [
                                    dbc.Col(
                                        dbc.Card(
                                            dbc.CardBody(
                                                [
                                                    dcc.Dropdown(
                                                        lista_de_dias_int,
                                                        id="dropdown previsões",
                                                        value="20",
                                                    ),
                                                    html.H4(
                                                        "Média vendido por dia",
                                                        style={
                                                            "color": "blue",
                                                            "text-align": "center",
                                                        },
                                                    ),
                                                    html.H3(
                                                        m_vendido_dia,
                                                        style={
                                                            "color": "blue",
                                                            "text-align": "center",
                                                        },
                                                    ),
                                                    html.H4(
                                                        "Projeção de venda para o dia selecionado",
                                                        style={
                                                            "color": "green",
                                                            "text-align": "center",
                                                        },
                                                    ),
                                                    html.H3(
                                                        children=previsão,
                                                        id="previsão_de_venda_dia",
                                                        style={
                                                            "color": "green",
                                                            "text-align": "center",
                                                        },
                                                    ),
                                                    html.H4(
                                                        """Vendas baseado
                                                      em mêses anteriores"""
                                                    ),
                                                    html.H3(previsão_mes_atual, style={"text-align":"center"}),
                                                ]
                                            )
                                        ),
                                        sm=4,
                                        md=4,
                                    ),
                                    dbc.Col(
                                        dbc.Card(
                                            dbc.CardBody(
                                                [
                                                    html.H6("Selecionar meta"),
                                                    dcc.Dropdown(
                                                        lista_de_metas,
                                                        id="dropdown metas",
                                                        value="60000",
                                                    ),
                                                    html.H6("Selecionar dias uteis mês atual"),
                                                    dcc.Dropdown(
                                                        lista_de_dias_int,
                                                        id="dropdown dias uteis",
                                                        value="20",
                                                    ),
                                                    html.H4("Vender por dia para alcançar a meta"),
                                                    html.H3(
                                                        children=vpd,
                                                        id="vpd",
                                                    ),
                                                ]
                                            )
                                        ),
                                        sm=4,
                                        md=4,
                                        style={"height": "100%"}
                                    ),
                                    dbc.Col(
                                        dbc.Card(
                                            dbc.CardBody(
                                                [
                                                    html.H6(
                                                        """desenvolvido por
                                                            Marcos Vinícius M corrêa"""
                                                    )
                                                ]
                                            )
                                        ,style={"height": "100%"})
                                    ,style={"height": "200%"}),
                                ]
                            )
                        ]
                    )
                )
            )
        ),
    ],
    fluid=True,
    style={"height": "100vh"},
)


# ======================================Callbacks===============================#
@app.callback(Output("Grafico1", "figure"), Input("dropdown grafico 1", "value"))
def modifica_grafico1(value):
    if value == "Todos os meses":
        fig = px.bar(df1, x="Data", y="Serviços")
        fig.update_layout(
            yaxis=dict(title="Todos os serviços"), xaxis=dict(title="Mesês"), height=350
        )
    elif value == "Valor Todos os Meses":
        fig = px.bar(x=Data_unica, y=serviços_total_mês, text_auto=True)
        fig.update_layout(yaxis=dict(title="MDO Serviços"), xaxis=dict(title="Mesês"))
    elif value == "Frequencia Todos os Meses":
        fig = px.bar(x=Data_unica, y=Frequencia_por_mês, text_auto=True)
        fig.update_layout(yaxis=dict(title="Frequencia"), xaxis=dict(title="Mesês numerados"))
    else:
        tabela_filtrada = df.loc[df["Data"] == value, :]
        fig = px.bar(tabela_filtrada, x="Data", y="Serviços")
        fig.update_layout(
            yaxis=dict(title="Serviços de " + value), xaxis=dict(title="Mesês"), height=350
        )
    return fig


@app.callback(Output("venda_diaria", "figure"), Input("dropdown diario de vendas", "value"))
def diario_vendas(value):
    if value == "Frequencia":
        fig4 = px.scatter(frequencia_por_dia, x="Dias", y="Nro. O.S.")
        fig4.update_traces(mode="lines+markers")
    elif value == "Previsão serviços":
        fig4 = px.scatter(
            serviços_mês_atual,
            x="Dias",
            y="Serviços",
            trendline="ols",
            trendline_color_override="black",
        )
        fig4.update_traces(mode="lines+markers")
    else:
        fig4 = px.scatter(serviços_mês_atual, x="Dias", y="Serviços", height=400)
        fig4.update_traces(mode="lines+markers")
    return fig4


@app.callback(Output("previsão_de_venda_dia", "children"), Input("dropdown previsões", "value"))
def previsão(value):
    previsão = reg1.predict([[int(value)]])
    previsão = previsão.max()
    previsão = f"R$ {previsão:.2f}"
    return previsão


@app.callback(
    Output("vpd", "children"),
    Input("dropdown metas", "value"),
    Input("dropdown dias uteis", "value"),
)
def vender_por_dia(meta, dias_uteis):
    meta = int(meta)
    qnt_falta_meta = meta - vendido_ate_agr
    dias_uteis = int(dias_uteis)
    dias_que_faltam = dias_uteis - dia_util_atual
    vpd = qnt_falta_meta / dias_que_faltam
    vpd = f"R$ {vpd:.2f}"
    return vpd


# Rodando o APP
if __name__ == "__main__":
    app.run_server(debug=True)
