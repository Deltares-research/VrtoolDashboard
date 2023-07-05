import numpy as np
import plotly.graph_objects as go

from src.linear_objects.dike_traject import DikeTraject


# def plot_pf_length_cost(vr, dsn, initial_betas, shapefile, output_dir, section_lengths=None, year=2025,
#                                standards={'Ondergrens': 1. / 10000, 'Signaleringswaarde': 1. / 30000}, mode='Length'):
def plot_pf_length_cost(dike_traject: DikeTraject, selected_year: float):
    # year_ind = np.int_(np.argwhere(initial_betas.columns == str(year - 2025))[0][0])
    fig = go.Figure()

    # if (mode == 'Length') and (section_lengths is not None):
    #     x_vr = pd.concat([pd.Series([0]), get_cum_length(vr['section_order'], section_lengths)])
    #     x_dsn = pd.concat([pd.Series([0]), get_cum_length(dsn['section_order'], section_lengths)])
    # elif (mode == 'Cost') and ('optimal_measures' in list(vr.keys())):
    #     x_vr = pd.concat([pd.Series([0]), get_cum_costs(vr['section_order'], vr['optimal_measures'])])
    #     x_dsn = pd.concat([pd.Series([0]), get_cum_costs(dsn['section_order'], dsn['optimal_measures'])])
    # else:
    #     return 'Error: no section lengths or optimal measures provided'
    # fig.add_trace(go.Scatter(x=x_vr,
    #                          y=vr['traject_probs'][:, year_ind],
    #                          customdata=vr['section_order'],
    #                          mode='markers+lines',
    #                          name='Veiligheidsrendement',
    #                          line=dict(color='red'),
    #                          marker=dict(size=6, color='red'),
    #                          hovertemplate="<b>%{customdata}</b><br><br>"
    #
    #                          ))
    # fig.add_trace(go.Scatter(x=x_dsn,
    #                          y=dsn['traject_probs'][:, year_ind],
    #                          customdata=dsn['section_order'],
    #                          mode='markers+lines',
    #                          name='Doorsnede-eisen',
    #                          line=dict(color='green'),
    #                          marker=dict(size=6, color='green'),
    #                          hovertemplate="<b>%{customdata}</b><br><br>"
    #                          ))
    # fig.add_shape(type='line', x0=0, x1=shapefile.MEAS_END.max(), y0=standards['Ondergrens'],
    #               y1=standards['Ondergrens'],
    #               line=dict(color='black', dash='dash'), name='Ondergrens')
    # fig.add_shape(type='line', x0=0, x1=shapefile.MEAS_END.max(), y0=standards['Signaleringswaarde'],
    #               y1=standards['Signaleringswaarde'],
    #               line=dict(color='black', dash='dot'), name='Signaleringswaarde')
    #
    # fig.update_yaxes(type='log')
    # if mode == 'Length':
    #     fig.update_xaxes(range=[0, shapefile.MEAS_END.max()], title='Versterkte lengte in meters')
    #     fig.update_layout(title='Faalkans i.r.t. versterkte lengte ({})'.format(year), template='plotly_white',
    #                       yaxis_title='Trajectfaalkans per jaar')
    #
    # elif mode == 'Cost':
    #     x_max_right = np.max([get_cum_costs(vr['section_order'], vr['optimal_measures']).max(),
    #                           get_cum_costs(dsn['section_order'], dsn['optimal_measures']).max()])
    #     fig.update_xaxes(range=[0, x_max_right], title="Kosten in miljoenen euro's")
    #     fig.update_layout(title='Faalkans i.r.t. kosten ({})'.format(year), yaxis_title='Trajectfaalkans per jaar')
    #
    # fig.update_yaxes(range=[1e-7, None], type='log', exponentformat='power')
    # fig.update_layout(showlegend=True, template='plotly_white')


    return fig


def get_cum_length(section_order, section_lengths):
    sections_stripped = [item.strip("DV") for item in section_order]
    cum_lengths = section_lengths.loc[sections_stripped].cumsum()
    return cum_lengths


def get_cum_costs(section_order, measure_costs):
    return measure_costs.loc[section_order]["LCC"].cumsum() / 1e6