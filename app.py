import streamlit as st
import pandas as pd
import numpy as np
import st_aggrid as st_ag
from st_aggrid import AgGrid, GridUpdateMode
from st_aggrid.grid_options_builder import GridOptionsBuilder

st.set_page_config(
    page_title="MY Green Ekonomi Index",
    page_icon=":earth_asia:",
    layout="wide",
    initial_sidebar_state="collapsed"
    )


odf = pd.read_csv('green_index_data.csv')
odf = odf.sort_values(['date', 'id_bbg'])
date = odf['date'].max()

st.write("# 🌏 MY Green Ekonomi Index!")
st.caption(f'date: {date} ', unsafe_allow_html=True)

sdf = odf[odf['date']==odf['date'].max()].sort_values(['cur_mkt_cap'], ascending=False)[['id_bbg','name','cur_mkt_cap']]
sdf = sdf.reset_index(drop=True)
gd = GridOptionsBuilder.from_dataframe(sdf)
gd.configure_selection(selection_mode='multiple', pre_selected_rows=sdf['id_bbg'].tolist() ,use_checkbox=True)

k_sep_formatter = st_ag.JsCode("""
    function(params) {
        return (params.value == null) ? params.value : 'RM '+ params.value.toLocaleString('en-US', {maximumFractionDigits:0}).replace(/\B(?=(\d{3})+(?!\d))/g, ","); 
    }
    """)

gd.configure_columns(['cur_mkt_cap'], editable=True, valueFormatter=k_sep_formatter)
gridoptions = gd.build()
grid_table = AgGrid(sdf, gridOptions=gridoptions,
                    update_mode=GridUpdateMode.SELECTION_CHANGED,
                    allow_unsafe_jscode=True)

selected_row = grid_table["selected_rows"]
nsdf = pd.DataFrame(selected_row)
#st.dataframe(nsdf[['id_bbg','name','cur_mkt_cap']])
if nsdf.shape[0]:
    
    df = odf[odf['id_bbg'].isin(nsdf['id_bbg'])].copy()

    df['log_market_cap'] = np.log(df['cur_mkt_cap'])
    df['total_log_market_cap'] = df.groupby(['date'])['log_market_cap'].transform('sum')
    df['return'] = df['px_last']/df['px_last_1']
    df['weight'] = df['log_market_cap']/df['total_log_market_cap']
    df['weighted_return']= (df['return']*df['weight'])
    tdf = (df.groupby(['date'])['weighted_return'].sum()).cumprod().reset_index().set_index('date')
    tdf = tdf.rename(columns={'weighted_return': 'green_index'})
    # df['cum_return'] = df.groupby(['id_bbg'])['weighted_return'].cumprod()
    # tdf = df.pivot_table(values='cum_return',index='date', columns='id_bbg')
    # tdf['green_index'] = tdf.mean(axis=1)

    import plotly.express as px
    import plotly.graph_objects as go

    fig = go.Figure()
    fig.add_scatter(x=tdf.index, y = tdf['green_index'],
                    mode = 'lines',
                    line = dict(color='#6d904f', width=5),
                    showlegend=False)
    
    fig.add_scatter(x = [fig.data[0].x[-1]], y = [fig.data[0].y[-1]],
                     mode = 'markers + text',
                     marker = {'color':'#fc4f30', 'size':10},
                     showlegend = False,
                     text = ['{:,.3f}'.format(fig.data[0].y[-1])],
                     textfont=dict(color='#fc4f30', size=22),
                     textposition='middle right')

    fig.update_layout(
            title=dict(text='MY Green Ekonomi Index', font_size=36),
            width=1200, height=600,
                xaxis=dict(
                    autorange=True,
                    showline=True,
                    showgrid=False,
                    showticklabels=True,
                    automargin=True,
                    linecolor='black',
                    linewidth=2,
                    ticks='outside',
                    tickfont=dict(
                        family='Arial',
                        size=12,
                        color='rgb(82, 82, 82)',
                    ),
                ),
                yaxis=dict(
                    title='Green Index',
                    gridcolor='#D5D8DC',
                    tickformat='.3f',
                    showgrid=True,
                    zeroline=False,
                    showline=False,
                    showticklabels=True,
                ),
                autosize=True,
                margin=dict(
                    autoexpand=True,
                    l=150,
                    r=0,
                    t=110,
                    pad=0,
                ),
                showlegend=True,
                legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.2,
                xanchor="left",
                ),
                plot_bgcolor='white')
    fig.layout.xaxis.fixedrange = True
    fig.layout.yaxis.fixedrange = True

    st.plotly_chart(fig)